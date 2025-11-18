"""CSV validation module with detailed error reporting."""

import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ValidationError(Exception):
    """CSV validation error with detailed information."""

    def __init__(self, message: str, line_number: Optional[int] = None):
        """Initialize validation error.

        Args:
            message: Error message describing the validation failure
            line_number: Line number where error occurred (if applicable)
        """
        self.message = message
        self.line_number = line_number
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with line number if available.

        Returns:
            Formatted error message
        """
        if self.line_number:
            return f"Line {self.line_number}: {self.message}"
        return self.message


def validate_file_exists(file_path: str) -> Path:
    """Validate that the CSV file exists.

    Args:
        file_path: Path to CSV file

    Returns:
        Path object for the file

    Raises:
        ValidationError: If file does not exist
    """
    path = Path(file_path)
    if not path.exists():
        raise ValidationError(f"File does not exist: {file_path}")
    return path


def validate_file_readable(file_path: Path) -> None:
    """Validate that the CSV file is readable.

    Args:
        file_path: Path to CSV file

    Raises:
        ValidationError: If file is not readable
    """
    if not file_path.is_file():
        raise ValidationError(f"Path is not a file: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1)
    except PermissionError:
        raise ValidationError(f"File is not readable (permission denied): {file_path}")
    except UnicodeDecodeError:
        raise ValidationError(f"File is not valid UTF-8 encoded text: {file_path}")
    except Exception as e:
        raise ValidationError(f"Cannot read file: {str(e)}")


def validate_csv_structure(file_path: Path) -> Tuple[List[str], str]:
    """Validate CSV structure and detect dialect.

    Args:
        file_path: Path to CSV file

    Returns:
        Tuple of (column headers, delimiter)

    Raises:
        ValidationError: If CSV structure is invalid
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sample = f.read(8192)
            if not sample:
                raise ValidationError("File is empty")

            try:
                dialect = csv.Sniffer().sniff(sample)
                delimiter = dialect.delimiter
            except csv.Error:
                delimiter = ','

            f.seek(0)
            reader = csv.reader(f, delimiter=delimiter)

            try:
                headers = next(reader)
            except StopIteration:
                raise ValidationError("File has no header row")

            if not headers:
                raise ValidationError("Header row is empty")

            if any(not h.strip() for h in headers):
                raise ValidationError("Header contains empty column names")

            if len(headers) != len(set(headers)):
                duplicates = [h for h in headers if headers.count(h) > 1]
                raise ValidationError(
                    f"Header contains duplicate column names: {', '.join(set(duplicates))}"
                )

            return headers, delimiter
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Failed to parse CSV: {str(e)}")


def validate_row_consistency(
    file_path: Path,
    expected_columns: int,
    delimiter: str
) -> None:
    """Validate that all rows have consistent number of columns.

    Args:
        file_path: Path to CSV file
        expected_columns: Expected number of columns
        delimiter: CSV delimiter character

    Raises:
        ValidationError: If any row has inconsistent column count
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=delimiter)
        next(reader)

        for line_num, row in enumerate(reader, start=2):
            if len(row) != expected_columns:
                raise ValidationError(
                    f"Expected {expected_columns} columns but found {len(row)}",
                    line_number=line_num
                )


def get_table_name(file_path: Path) -> str:
    """Extract table name from file path.

    Args:
        file_path: Path to CSV file

    Returns:
        Valid PostgreSQL table name derived from filename
    """
    name = file_path.stem.lower()
    name = ''.join(c if c.isalnum() else '_' for c in name)
    if name[0].isdigit():
        name = f"table_{name}"
    return name


def validate_csv(file_path: str) -> Dict[str, any]:
    """Validate CSV file and return metadata.

    Args:
        file_path: Path to CSV file

    Returns:
        Dictionary containing validation results and metadata:
        - valid: bool
        - headers: List[str]
        - delimiter: str
        - table_name: str
        - row_count: int (approximate, from file)

    Raises:
        ValidationError: If validation fails with detailed error information
    """
    path = validate_file_exists(file_path)
    validate_file_readable(path)
    headers, delimiter = validate_csv_structure(path)
    validate_row_consistency(path, len(headers), delimiter)

    with open(path, 'r', encoding='utf-8') as f:
        row_count = sum(1 for _ in f) - 1

    return {
        "valid": True,
        "headers": headers,
        "delimiter": delimiter,
        "table_name": get_table_name(path),
        "row_count": row_count
    }
