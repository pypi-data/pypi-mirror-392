import pandas as pd
import pytest
import click
from methurator.config_utils.validation_utils import (
    validate_read_summary,
    validate_cpgs_summary,
)


def test_validate_read_summary_valid(tmp_path):
    """Test that a valid CSV with all required columns passes validation."""
    file_path = tmp_path / "reads_summary.csv"
    df = pd.DataFrame(columns=["Sample", "Percentage", "Read_Count"])
    df.to_csv(file_path, index=False)

    # Should not raise
    validate_read_summary(str(file_path))


def test_validate_read_summary_wrong_extension(tmp_path):
    """Test that a non-CSV file raises a UsageError."""
    file_path = tmp_path / "reads_summary.txt"
    file_path.write_text("Sample,Percentage,Read_Count\n")

    with pytest.raises(click.UsageError, match="not a CSV file"):
        validate_read_summary(str(file_path))


def test_validate_read_summary_missing_columns(tmp_path):
    """Test that missing columns raise a UsageError."""
    file_path = tmp_path / "reads_summary.csv"
    df = pd.DataFrame(columns=["Sample", "Read_Count"])  # Missing 'Percentage'
    df.to_csv(file_path, index=False)

    with pytest.raises(click.UsageError, match="Missing required columns"):
        validate_read_summary(str(file_path))


def test_validate_cpgs_summary_valid(tmp_path):
    """Test that a valid CSV with all required columns passes validation."""
    file_path = tmp_path / "cpgs_summary.csv"
    df = pd.DataFrame(columns=["Sample", "Percentage", "Coverage", "CpG_Count"])
    df.to_csv(file_path, index=False)

    # Should not raise
    validate_cpgs_summary(str(file_path))


def test_validate_cpgs_summary_wrong_extension(tmp_path):
    """Test that a non-CSV file raises a UsageError."""
    file_path = tmp_path / "cpgs_summary.tsv"
    file_path.write_text("Sample,Percentage,Coverage,CpG_Count\n")

    with pytest.raises(click.UsageError, match="not a CSV file"):
        validate_cpgs_summary(str(file_path))


def test_validate_cpgs_summary_missing_columns(tmp_path):
    """Test that missing columns raise a UsageError."""
    file_path = tmp_path / "cpgs_summary.csv"
    df = pd.DataFrame(
        columns=["Sample", "Percentage", "CpG_Count"]
    )  # Missing 'Coverage'
    df.to_csv(file_path, index=False)

    with pytest.raises(click.UsageError, match="Missing required columns"):
        validate_cpgs_summary(str(file_path))
