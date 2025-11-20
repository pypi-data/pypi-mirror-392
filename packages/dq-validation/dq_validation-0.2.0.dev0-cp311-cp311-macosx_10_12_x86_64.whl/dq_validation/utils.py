import json
import glob
import os

from .schemas import ValidationConfig, ValidationReport
from .schemas import *
from .logger import logger


def read_config(path: str) -> ValidationConfig:
    with open(path, "r") as file:
        data = json.load(file)
        return ValidationConfig(**data)


def read_report(path: str) -> ValidationReport:
    with open(path, "r") as file:
        data = json.load(file)
        return ValidationReport(**data)


def update_report_outcome(path: str, outcome: ValidationOutcome):
    with open(path, "r") as file:
        data = json.load(file)
        report = ValidationReport(**data)
        report.root.report.outcome = outcome
    with open(path, "w") as file:
        file.write(report.model_dump_json(by_alias=True))


def get_report_outcome(path: str) -> ValidationOutcome:
    report = read_report(path)
    return report.root.report.outcome


def is_report_passed(path: str) -> bool:
    return read_report(path).root.report.outcome == ValidationOutcome.PASSED


def update_report_with_uniqueness_check_result(
    report_path: str, duplication_errors, num_duplication_errors_total: int
):
    logger.info(f"Found {num_duplication_errors_total} rows with duplicate values")
    with open(report_path, "r") as f:
        report = json.load(f)
    report["report"]["numInvalidRowsTotal"] += num_duplication_errors_total
    report["report"]["uniqueness"] = {
        "recordedErrors": duplication_errors,
        "numErrorsTotal": num_duplication_errors_total,
    }
    if num_duplication_errors_total and num_duplication_errors_total > 0:
        report["report"]["outcome"] = "FAILED"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)


def update_report_with_duplicated_row_removal_result(
    report_path: str, num_duplicates: int
):
    logger.info(f"Dropped {num_duplicates} duplicate rows")
    with open(report_path, "r") as f:
        report = json.load(f)
    report["report"]["dropInvalidRows"] = {"numInvalidRowsDropped": report["report"]["numInvalidRowsTotal"]}
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

def update_report_passed(
    report_path: str
):
    with open(report_path, "r") as f:
        report = json.load(f)
    report["report"]["outcome"] = "PASSED"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

def update_report_with_no_drop_invalid_rows(
    report_path: str
):
    with open(report_path, "r") as f:
        report = json.load(f)
    report["report"].pop("dropInvalidRows", None)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)


def update_report_with_passed_outcome(
    report_path: str,
):
    logger.info("Marking report as passed")
    with open(report_path, "r") as f:
        report = json.load(f)
    report["report"]["outcome"] = "PASSED"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
