import json
import tempfile
import shutil
import functools

import os
from typing import List
from datetime import datetime
from . import validate

from .spark_utils import spark_session
import pyspark.sql.functions as F
from pyspark.sql import DataFrame, Window
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    FloatType,
    BooleanType,
    DoubleType,
    LongType,
)
from pyspark.storagelevel import StorageLevel
from .schemas import ValidationConfig
from .error import ValidationError
from .schemas import *
from .config import *
from .utils import (
    read_config,
    get_report_outcome,
    update_report_with_uniqueness_check_result,
    update_report_with_duplicated_row_removal_result,
    update_report_with_no_drop_invalid_rows,
    update_report_passed,
)
from .logger import logger


HAS_ERROR_COL = "__has_error"

ROW_NUM_COLUMN = "__row_nr"

CURRENT_FILE_PATH = os.path.abspath(__file__)

SPARK_TYPE_BY_FORMAT_TYPE = {
    "STRING": StringType(),
    "INTEGER": LongType(),
    "FLOAT": DoubleType(),
    "EMAIL": StringType(),
    "DATE_ISO8601": StringType(),
    "PHONE_NUMBER_E164": StringType(),
    "HASH_SHA256_HEX": StringType(),
}


def write_df_as_single_file(df: DataFrame, path: str, temp_dir: str):
    """Write a dataframe into a single CSV file and store the result at `path`"""
    filename = os.path.basename(path)
    with tempfile.TemporaryDirectory(dir=temp_dir) as d:
        csv_parts_dir = os.path.join(d, filename)
        # Make sure to escape quotes within strings by repeating the quote character
        # (as it is done by Pandas and Excel).
        (
            df.write
              .option("header", "false")
              .option("quote", '"')
              .option("escape", '"')
              .csv(csv_parts_dir, header=None)
        )
        csv_parts = [
            os.path.join(csv_parts_dir, f)
            for f in os.listdir(csv_parts_dir)
            if f.endswith(".csv")
        ]
        logger.info(f"Will merge {len(csv_parts)} CSV part files")
        temp_merged_path = os.path.join(d, "__temp-merged.csv")
        with open(temp_merged_path, "wb") as temp_out:
            for ix, part in enumerate(csv_parts):
                with open(part, "rb") as f:
                    shutil.copyfileobj(f, temp_out)
                os.remove(part)  # delete the part file to free up space
                logger.debug(
                    f"Moved part file '{part}' into '{temp_merged_path}' ({ix + 1} / {len(csv_parts)})"
                )
        shutil.move(temp_merged_path, path)


def add_erroneous_row_ids(df: DataFrame, row_nrs_df: DataFrame) -> DataFrame:
    df = (
        df.join(
            row_nrs_df.withColumn(HAS_ERROR_COL, F.lit(True)),
            on=ROW_NUM_COLUMN,
            how="left_outer",
        )
        .na.fill(False, subset=[HAS_ERROR_COL])
    )
    return df


def create_output_dataset_schema(
    config: ValidationConfig
) -> StructType:
    col_fields = []
    for ix, column in enumerate(config.root.config.columns):
        col_name = column.name or f"c{ix}"
        allow_null = column.allowNull
        if column.formatType:
            format_type = column.formatType.value
            spark_type = (
                SPARK_TYPE_BY_FORMAT_TYPE.get(format_type, StringType())
            )
        else:
            spark_type = StringType()
        col_fields.append(StructField(col_name, spark_type, allow_null))
    return StructType(col_fields)


def create_annotated_dataset_schema(
    config: ValidationConfig
) -> StructType:
    col_fields = [
        StructField(ROW_NUM_COLUMN, StringType(), False)
    ]
    for ix, column in enumerate(config.root.config.columns):
        col_name = str(ix)
        allow_null = column.allowNull
        if column.formatType:
            format_type = column.formatType.value
            spark_type = (
                SPARK_TYPE_BY_FORMAT_TYPE.get(format_type, StringType())
            )
        else:
            spark_type = StringType()
        col_fields.append(StructField(col_name, spark_type, allow_null))
    return StructType(col_fields)


def find_duplicates_spark(
    df: DataFrame, unique_keys: List[List[int]]
):
    """
    Try to find duplicates in the given DataFrame and report the
    line numbers of where such duplicates where found.
    """
    errors = []
    num_duplicates_total = 0
    before = datetime.now()

    duplicated_dfs = []
    for subset_columns_ix in unique_keys:
        df_columns = [
            column
            for column in df.columns
            if column != ROW_NUM_COLUMN
        ]
        subset_columns = [df_columns[col_ix] for col_ix in subset_columns_ix]

        # Check for duplicates based on the subset of columns
        window_spec = Window.partitionBy(*subset_columns)
        min_row_nr_column = f"{ROW_NUM_COLUMN}_min"
        df_with_dup_flag = (
            df.withColumn(min_row_nr_column, F.min(ROW_NUM_COLUMN).over(window_spec))
            .withColumn(
                "is_duplicated", F.col(ROW_NUM_COLUMN) > F.col(min_row_nr_column)
            )
            .drop(min_row_nr_column)
        )

        # Filter duplicates
        duplicated_df = (
            df_with_dup_flag.filter("is_duplicated == true")
            .select(ROW_NUM_COLUMN)
            .persist(StorageLevel.DISK_ONLY)
        )

        # Collect the row numbers of duplicates (limited to NUM_ERRORS_RECORD_BY_KEY_TUPLE)
        duplicated_rows_subset = (
            duplicated_df.sort(ROW_NUM_COLUMN)
            .limit(NUM_ERRORS_RECORD_BY_KEY_TUPLE)
            .collect()
        )

        duplicated_dfs.append(duplicated_df)

        for row in duplicated_rows_subset:
            errors.append(
                {
                    "code": "DUPLICATE_VALUES",
                    "location": {
                        "row": row[ROW_NUM_COLUMN],
                        "columns": subset_columns_ix,
                    },
                }
            )

    after = datetime.now()
    logger.info(f"Finding duplicates took {(after - before).total_seconds() / 60} min")

    duplicated_df = functools.reduce(lambda a, b: a.union(b), duplicated_dfs).distinct()
    duplicated_df = duplicated_df.persist(StorageLevel.DISK_ONLY)
    num_duplicates_total = duplicated_df.count()
    for df in duplicated_dfs:
        df.unpersist()

    return duplicated_df, num_duplicates_total, errors


def run(
    annotated_dataset_path: str,
    config_path: str,
    report_path: str,
    output_path: str,
    should_write_parquet: bool,
    should_check_uniqueness: bool,
    temp_dir: str = "/scratch",
    drop_invalid_rows: bool = False,
):
    config = read_config(config_path)

    spark_settings = {}

    if bool(os.environ.get("VALIDATION_SPARK_NUM_PARTITIONS")):
        num_partitions = os.environ["VALIDATION_SPARK_NUM_PARTITIONS"]
        spark_settings["spark.sql.shuffle.partitions"] = num_partitions
        spark_settings["spark.default.parallelism"] = num_partitions
    for env, key in [
        ("VALIDATION_SPARK_DRIVER_MEMORY", "spark.driver.memory"),
        ("VALIDATION_SPARK_MEMORY_FRACTION", "spark.memory.fraction"),
        ("VALIDATION_SPARK_MEMORY_STORAGE_FRACTION", "spark.memory.storageFraction"),
        ("VALIDATION_SPARK_DRIVER_CORES", "spark.driver.cores"),
        ("VALIDATION_SPARK_DRIVER_EXTRA_JAVA_OPTIONS", "spark.driver.extraJavaOptions"),
        ("VALIDATION_SPARK_DRIVER_MEMORY_OVERHEAD", "spark.driver.memoryOverhead"),
        (
            "VALIDATION_SPARK_DRIVER_MEMORY_OVERHEAD_FACTOR",
            "spark.driver.memoryOverheadFactor",
        ),
    ]:
        if bool(os.environ.get(env)):
            spark_settings[key] = os.environ[env]
    spark_settings["spark.shuffle.compress"] = "true"
    spark_settings["spark.io.compression.codec"] = "zstd"

    with spark_session(
        temp_dir,
        name="Validation",
        config=list(spark_settings.items()),
    ) as ss:
        annotated_dataset_schema = create_annotated_dataset_schema(config)
        # It might happen that the input is empty, in this case we still might
        # need to store a parquet file so the pipeline should proceed as usual.
        if os.path.exists(annotated_dataset_path):
            df = ss.read.parquet(annotated_dataset_path)
        else:
            df = ss.createDataFrame([], annotated_dataset_schema)

        if should_check_uniqueness:
            if config.root.config.table is None:
                raise ValidationError("Table validation settings must be defined")
            if config.root.config.table.uniqueness is None:
                raise ValidationError("Uniqueness validations settings must be defined")
            before = datetime.now()
            unique_keys: list[list[int]] = [
                [ix for ix in tpl.columns]
                for tpl in config.root.config.table.uniqueness.uniqueKeys
            ]
            logger.info(f"Checking uniqueness for keys: {unique_keys}")
            duplicate_row_nrs_df, num_duplication_errors_total, duplication_errors = (
                find_duplicates_spark(df, unique_keys)
            )
            update_report_with_uniqueness_check_result(
                report_path, duplication_errors, num_duplication_errors_total
            )
            after = datetime.now()
            logger.info(
                f"Uniqueness check took {(after - before).total_seconds() / 60} min"
            )
            df = add_erroneous_row_ids(df, duplicate_row_nrs_df)

        if drop_invalid_rows:
            if should_check_uniqueness:
                num_duplicates = df.filter(F.col(HAS_ERROR_COL) == True).count()
                df = df.filter(F.col(HAS_ERROR_COL) == False)
                update_report_with_duplicated_row_removal_result(report_path, num_duplicates)
            else:
                update_report_with_duplicated_row_removal_result(report_path, 0)
            update_report_passed(report_path)
        else:
            # Adjust the report as first phase always drops invalid rows, however if
            # drop_invalid_rows=False then we don't want to report this
            update_report_with_no_drop_invalid_rows(report_path)

        is_passed = get_report_outcome(report_path) == ValidationOutcome.PASSED
        if is_passed:
            # Rename encoded columns of annotated dataset to the ones found in the validation config.
            output_dataset_schema = create_output_dataset_schema(config)
            encoded_column_names = [
                field.name
                for field in annotated_dataset_schema.fields
                if field.name != ROW_NUM_COLUMN
            ]
            recast_columns = []
            for encoded_name, target_field in zip(encoded_column_names, output_dataset_schema.fields):
                recast_columns.append(
                    F.col(encoded_name).cast(target_field.dataType).alias(target_field.name)
                )
            df = df.select(*recast_columns)

            # Copy over the input data so that downstream computations can read it.
            before = datetime.now()
            if should_write_parquet:
                logger.info("Write table to parquet file")
                with tempfile.TemporaryDirectory(dir=temp_dir) as d:
                    temp_output_path = os.path.join(d, "_temp-dataset.parquet")
                    df.write.parquet(temp_output_path)
                    shutil.copytree(temp_output_path, output_path)
            else:
                logger.info("Write table to CSV file")
                write_df_as_single_file(df, output_path, temp_dir=temp_dir)
            after = datetime.now()

            fmt = "parquet" if should_write_parquet else "csv"
            logger.info(
                f"Writing out {fmt} file took {(after - before).total_seconds() / 60} min"
            )
