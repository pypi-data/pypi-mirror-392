import csv
import numpy as np
import os
import pandas as pd
import pyarrow
import pyarrow as pa
import pyarrow.parquet as pq
from typing import List
from datetime import datetime
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


ROW_NUM_COLUMN = "__row_nr"

CURRENT_FILE_PATH = os.path.abspath(__file__)

PYARROW_TYPE_BY_FORMAT_TYPE = {
    "STRING": pa.string(),
    "INTEGER": pa.int64(),
    "FLOAT": pa.float64(),
    "EMAIL": pa.string(),
    "DATE_ISO8601": pa.string(),
    "PHONE_NUMBER_E164": pa.string(),
    "HASH_SHA256_HEX": pa.string(),
}

TYPE_BY_FORMAT_TYPE = {
    "STRING": str,
    "INTEGER": "Int64",
    "FLOAT": pd.Float64Dtype(),
    "EMAIL": str,
    "DATE_ISO8601": str,
    "PHONE_NUMBER_E164": str,
    "HASH_SHA256_HEX": str,
}


def _get_encoded_dataset_column_names(config: ValidationConfig) -> list[str]:
    return [str(ix) for ix in range(len(config.root.config.columns))]


def find_duplicates_pandas(df: pd.DataFrame, unique_keys: List[List[int]], config: ValidationConfig):
    """Try to find duplicates in the given CSV file and report the line
    numbers of where such duplicates where found.
    """
    errors = []
    duplicated = None

    encoded_column_names = _get_encoded_dataset_column_names(config)

    for subset_columns in unique_keys:
        logger.info(f"Check duplicates w/ subset cols: {subset_columns}")
        subset_column_names = [encoded_column_names[x] for x in subset_columns]
        is_duplicated = df.duplicated(
            subset=subset_column_names,
            # Only report subsequent rows as duplicates.
            keep="first",
        )
        if duplicated is None:
            duplicated = is_duplicated
        else:
            duplicated = duplicated | is_duplicated
        duplicated_rows_subset = list(
            df.loc[is_duplicated].index[:NUM_ERRORS_RECORD_BY_KEY_TUPLE]
        )
        for row in duplicated_rows_subset:
            errors.append(
                {
                    "code": "DUPLICATE_VALUES",
                    "location": {
                        "row": row,
                        "columns": subset_columns,
                    },
                }
            )
    num_duplicates_total = sum(duplicated)
    return num_duplicates_total, errors, duplicated


def create_output_schema_from_validation_config(
    config: ValidationConfig,
) -> pyarrow.Schema:
    col_ix = 0
    col_fields = []
    for column in config.root.config.columns:
        col_name = column.name
        allow_null = column.allowNull
        if not col_name:
            col_name = f"c{col_ix}"
        if column.formatType:
            format_type = column.formatType.value
            tpe = PYARROW_TYPE_BY_FORMAT_TYPE.get(format_type, pa.string())
        else:
            tpe = pa.string()
        col_fields.append(pa.field(col_name, tpe, nullable=allow_null))
        col_ix += 1
    schema = pa.schema(col_fields)
    return schema


def _read_annotated_dataset_from_parquet(path: str, config: ValidationConfig) -> pd.DataFrame:
    encoded_column_names = _get_encoded_dataset_column_names(config)
    annotated_dataset_column_names = [ROW_NUM_COLUMN] + encoded_column_names
    columns = config.root.config.columns
    logger.info(f"Trying to read file at '{path}'")
    df = pd.read_parquet(path, columns=annotated_dataset_column_names)
    # We need to do this asinine nonsense because pandas
    for encoded_name, column in zip(encoded_column_names, columns):
        if df.dtypes[encoded_name] == np.float64 and column.formatType.value == "INTEGER":
            df[encoded_name] = df[encoded_name].astype('Int64')

    # Set the index to the uint64-based row number column
    # that was added by the Rust pipeline.
    # This will drop the `ROW_NUM_COLUMN` column from the dataframe.
    # Note that if we used `index_col=0` when reading the CSV, it would
    # read the index_column as a string instead of a uint64.
    df.set_index(ROW_NUM_COLUMN, inplace=True)
    return df


def read_annotated_dataset_from_parquet(path: str, config: ValidationConfig) -> pd.DataFrame:
    if not os.path.exists(path):
        # Create an empty annotated dataset
        schema = {ROW_NUM_COLUMN: pd.Series(dtype=np.uint64)}
        columns = config.root.config.columns
        encoded_names = _get_encoded_dataset_column_names(config)
        for encoded_name, column in zip(encoded_names, columns):
            schema[encoded_name] = pd.Series(dtype=TYPE_BY_FORMAT_TYPE.get(column.formatType.value, str))
        df = pd.DataFrame(schema)
        df.set_index(ROW_NUM_COLUMN, inplace=True)
        return df

    df = _read_annotated_dataset_from_parquet(path, config)
    return df


def run(
    annotated_dataset_path: str,
    config_path: str,
    report_path: str,
    output_path: str,
    should_write_parquet: bool,
    should_check_uniqueness: bool,
    drop_invalid_rows: bool = False,
):
    config = read_config(config_path)

    # Read the annotated output of the validation pipeline that indicates
    # for each row whether it was valid and the original row number.
    logger.info(f"Reading input file at {annotated_dataset_path}")
    before = datetime.now()
    df = read_annotated_dataset_from_parquet(annotated_dataset_path, config)
    if df.shape[0] == 0:
        logger.info(f"Dataframe as output by validation pipeline is empty")
    after = datetime.now()
    logger.info(f"Reading of file took {(after - before).total_seconds()} s")

    # Check for duplicated rows if necessary
    if should_check_uniqueness:
        assert config.root.config.table is not None
        assert config.root.config.table.uniqueness is not None
        before = datetime.now()
        unique_keys: list[list[int]] = [
            [ix for ix in tpl.columns]
            for tpl in config.root.config.table.uniqueness.uniqueKeys
        ]
        logger.info(f"Checking uniqueness for keys: {unique_keys}")
        num_duplication_errors_total, duplication_errors, duplicated = find_duplicates_pandas(
            df, unique_keys, config
        )
        update_report_with_uniqueness_check_result(
            report_path, duplication_errors, num_duplication_errors_total
        )
        after = datetime.now()
        logger.info(f"Uniqueness check took {(after - before).total_seconds()} s")

    if drop_invalid_rows:
        if should_check_uniqueness:
            before = datetime.now()
            logger.info("Dropping duplicate rows")
            num_duplicates = sum(duplicated)
            df.drop(df[duplicated].index, inplace=True)
            update_report_with_duplicated_row_removal_result(report_path, num_duplicates)
            after = datetime.now()
            logger.info(f"Dropping duplicate rows took {(after - before).total_seconds()} s")
        else:
            update_report_with_duplicated_row_removal_result(report_path, 0)
        update_report_passed(report_path)
    else:
        update_report_with_no_drop_invalid_rows(report_path)

    is_passed = get_report_outcome(report_path) == ValidationOutcome.PASSED
    if is_passed:
        # Copy over the input data so that downstream computations can read it.
        before = datetime.now()
        df = df.reset_index()
        df = df.drop(columns=ROW_NUM_COLUMN)
        if should_write_parquet:
            schema = create_output_schema_from_validation_config(config)
            df.columns = schema.names
            table = pa.Table.from_pandas(df, schema=schema)
            pq.write_table(table, output_path)
        else:
            if len(config.root.config.columns) == 1:
                # https://github.com/pandas-dev/pandas/issues/59116
                df.dropna(inplace=True)

            df.to_csv(
                output_path,
                index=False,
                header=False,
                sep=",",
                na_rep='',
                quoting=csv.QUOTE_MINIMAL,
                lineterminator="\n",
                doublequote=True,
                encoding="utf-8",
                decimal=".",
            )
        after = datetime.now()
        fmt = "parquet" if should_write_parquet else "csv"
        logger.info(f"Writing out {fmt} file took {(after - before).total_seconds()} s")
