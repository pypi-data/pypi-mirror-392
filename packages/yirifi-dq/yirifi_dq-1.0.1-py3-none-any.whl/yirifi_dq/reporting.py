#!/usr/bin/env python3
"""
Report Generator for MongoDB Operations

Provides standardized reporting functionality for all data quality operations.
Reports are mandatory for audit trail and documentation.

Author: Data Quality Framework
Last Updated: 2025-11-15
"""

import glob
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from yirifi_dq.utils.logging_config import get_logger

logger = get_logger(__name__)


def format_duration(seconds: float) -> str:
    """
    Format seconds into human-readable duration.

    Args:
        seconds: Duration in seconds

    Returns:
        str: Formatted duration (e.g., "12.5s", "3m 45s", "2h 15m")

    Example:
        >>> format_duration(12.5)
        '12.5s'
        >>> format_duration(125)
        '2m 5s'
        >>> format_duration(3665)
        '1h 1m'
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def generate_report(
    operation_name: str,
    summary: Dict[str, Any],
    details: List[Dict[str, Any]],
    output_dir: Optional[Path] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate standardized JSON report.

    Args:
        operation_name: Name of operation (e.g., "duplicate_cleanup")
        summary: Dict with summary statistics
        details: List of detailed results
        output_dir: Directory for report file (defaults to ./output)
        metadata: Optional additional context

    Returns:
        str: Path to report file

    Example:
        >>> report_file = generate_report(
        ...     operation_name="duplicate_cleanup",
        ...     summary={
        ...         "total_processed": 23,
        ...         "successfully_deleted": 23,
        ...         "failed": 0
        ...     },
        ...     details=[
        ...         {
        ...             "url": "http://example.com",
        ...             "duplicate_count": 2,
        ...             "action": "kept_oldest"
        ...         }
        ...     ],
        ...     metadata={"environment": "PRD", "database": "regdb"}
        ... )
    """
    logger.info(f"Generating report for: {operation_name}")

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report = {
            "timestamp": timestamp,
            "operation_name": operation_name,
            "summary": summary,
            "details": details,
            "metadata": metadata or {},
        }

        # Determine output directory
        if output_dir is None:
            output_dir = Path.cwd() / "output"

        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save report
        report_filename = f"report_{timestamp}.json"
        report_file = output_dir / report_filename

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Report generated: {report_file}")
        print(f"✓ Report generated: {report_filename}")

        return str(report_file)

    except Exception as e:
        logger.error(f"Report generation failed: {e!s}", exc_info=True)
        print(f"❌ Report generation failed: {e!s}")
        raise


def generate_report_with_timing(
    operation_name: str,
    summary: Dict[str, Any],
    details: List[Dict[str, Any]],
    output_dir: Optional[Path] = None,
    metadata: Optional[Dict[str, Any]] = None,
    start_time: Optional[float] = None,
) -> str:
    """
    Generate report with execution time tracking.

    Args:
        operation_name: Name of operation
        summary: Dict with summary statistics
        details: List of detailed results
        output_dir: Directory for report file
        metadata: Optional additional context
        start_time: Optional start time (from time.time())

    Returns:
        str: Path to report file

    Example:
        >>> import time
        >>> start_time = time.time()
        >>> # ... perform operation ...
        >>> report_file = generate_report_with_timing(
        ...     operation_name="duplicate_cleanup",
        ...     summary={"total_processed": 1000, "successful": 950},
        ...     details=[...],
        ...     start_time=start_time
        ... )
    """
    logger.info(f"Generating timed report for: {operation_name}")

    # Calculate execution time if start_time provided
    if start_time:
        import time

        execution_time = time.time() - start_time
        summary["execution_time_seconds"] = round(execution_time, 2)
        summary["execution_time_formatted"] = format_duration(execution_time)
        logger.info(f"Operation took {format_duration(execution_time)}")

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report = {
            "timestamp": timestamp,
            "operation_name": operation_name,
            "summary": summary,
            "details": details,
            "metadata": metadata or {},
        }

        # Determine output directory
        if output_dir is None:
            output_dir = Path.cwd() / "output"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Save report
        report_filename = f"report_{timestamp}.json"
        report_file = output_dir / report_filename

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Report generated: {report_file}")
        print(f"✓ Report generated: {report_filename}")
        print(f"  - Total processed: {summary.get('total_processed', 'N/A')}")

        if "execution_time_formatted" in summary:
            print(f"  - Execution time: {summary['execution_time_formatted']}")

        return str(report_file)

    except Exception as e:
        logger.error(f"Report generation failed: {e!s}", exc_info=True)
        print(f"❌ Report generation failed: {e!s}")
        raise


def generate_comprehensive_report(
    operation_name: str,
    phases: List[Dict[str, Any]],
    summary: Dict[str, Any],
    details: List[Dict[str, Any]],
    output_dir: Optional[Path] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate comprehensive multi-phase report.

    Args:
        operation_name: Name of operation
        phases: List of dicts describing each phase
        summary: Overall summary statistics
        details: Detailed results
        output_dir: Directory for report file
        metadata: Additional context

    Returns:
        str: Path to report file

    Example:
        >>> report_file = generate_comprehensive_report(
        ...     operation_name="full_data_cleanup",
        ...     phases=[
        ...         {
        ...             "phase": 1,
        ...             "name": "duplicate_detection",
        ...             "status": "completed",
        ...             "duration_seconds": 45.2,
        ...             "duplicates_found": 150
        ...         },
        ...         {
        ...             "phase": 2,
        ...             "name": "backup_creation",
        ...             "status": "completed",
        ...             "duration_seconds": 12.1,
        ...             "records_backed_up": 150
        ...         }
        ...     ],
        ...     summary={
        ...         "total_execution_time": 69.0,
        ...         "phases_completed": 4,
        ...         "overall_status": "success"
        ...     },
        ...     details=[...]
        ... )
    """
    logger.info(f"Generating comprehensive report for: {operation_name}")

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report = {
            "timestamp": timestamp,
            "operation_name": operation_name,
            "phases": phases,
            "summary": summary,
            "details": details,
            "metadata": metadata or {},
        }

        # Determine output directory
        if output_dir is None:
            output_dir = Path.cwd() / "output"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Save report
        report_filename = f"comprehensive_report_{timestamp}.json"
        report_file = output_dir / report_filename

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Comprehensive report generated: {report_file}")
        print(f"✓ Comprehensive report generated: {report_filename}")
        print(f"  - Phases completed: {summary.get('phases_completed', len(phases))}")
        print(f"  - Overall status: {summary.get('overall_status', 'N/A')}")

        return str(report_file)

    except Exception as e:
        logger.error(f"Comprehensive report generation failed: {e!s}", exc_info=True)
        print(f"❌ Comprehensive report generation failed: {e!s}")
        raise


def generate_report_with_errors(
    operation_name: str,
    summary: Dict[str, Any],
    details: List[Dict[str, Any]],
    errors: List[Dict[str, Any]],
    output_dir: Optional[Path] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate report including error tracking.

    Args:
        operation_name: Name of operation
        summary: Summary statistics
        details: Detailed results
        errors: List of errors encountered
        output_dir: Directory for report file
        metadata: Additional context

    Returns:
        str: Path to report file

    Example:
        >>> errors = []
        >>> # During operation, collect errors:
        >>> # errors.append({
        >>> #     "record_id": str(doc['_id']),
        >>> #     "error": str(e),
        >>> #     "timestamp": datetime.now().isoformat()
        >>> # })
        >>>
        >>> report_file = generate_report_with_errors(
        ...     operation_name="bulk_update",
        ...     summary={"total_processed": 1000, "successful": 950, "failed": 50},
        ...     details=[...],
        ...     errors=errors
        ... )
    """
    logger.info(f"Generating report with errors for: {operation_name}")

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report = {
            "timestamp": timestamp,
            "operation_name": operation_name,
            "summary": summary,
            "details": details,
            "errors": errors,
            "metadata": metadata or {},
        }

        # Determine output directory
        if output_dir is None:
            output_dir = Path.cwd() / "output"

        output_dir.mkdir(parents=True, exist_ok=True)

        # Save main report
        report_filename = f"report_{timestamp}.json"
        report_file = output_dir / report_filename

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        # Save errors separately if there are any
        if errors:
            error_filename = f"errors_{timestamp}.json"
            error_file = output_dir / error_filename

            with open(error_file, "w") as f:
                json.dump(errors, f, indent=2, default=str)

            logger.warning(f"Errors saved: {error_file}")
            print(f"⚠️  Errors saved: {error_filename}")

        logger.info(f"Report generated: {report_file}")
        print(f"✓ Report generated: {report_filename}")

        if errors:
            print(f"  - Total errors: {len(errors)}")

        return str(report_file)

    except Exception as e:
        logger.error(f"Report generation failed: {e!s}", exc_info=True)
        print(f"❌ Report generation failed: {e!s}")
        raise


def load_report(report_file: str) -> Dict[str, Any]:
    """
    Load report from JSON file.

    Args:
        report_file: Path to report JSON file

    Returns:
        Dict containing report data

    Example:
        >>> report = load_report("output/report_20251115_143022.json")
        >>> print(report['operation_name'])
        'duplicate_cleanup'
    """
    logger.info(f"Loading report: {report_file}")

    try:
        with open(report_file) as f:
            report = json.load(f)

        logger.info(f"Report loaded successfully: {report.get('operation_name')}")
        return report

    except Exception as e:
        logger.error(f"Failed to load report: {e!s}", exc_info=True)
        raise Exception(f"Failed to load report: {e!s}")


def find_reports(operation_name: Optional[str] = None, output_dir: Optional[Path] = None) -> List[str]:
    """
    Find all reports, optionally filtered by operation name.

    Args:
        operation_name: Optional operation name to filter by
        output_dir: Directory to search (defaults to ./output)

    Returns:
        List of report file paths

    Example:
        >>> duplicate_reports = find_reports("duplicate_cleanup")
        >>> print(f"Found {len(duplicate_reports)} duplicate cleanup reports")
    """
    # Determine output directory
    if output_dir is None:
        output_dir = Path.cwd() / "output"

    logger.info(f"Searching for reports in: {output_dir}")

    # Find all report files
    pattern = str(output_dir / "report_*.json")
    all_reports = glob.glob(pattern)

    logger.info(f"Found {len(all_reports)} total report files")

    # Filter by operation name if provided
    if operation_name:
        matching = []
        for report_file in all_reports:
            try:
                report = load_report(report_file)
                if report.get("operation_name") == operation_name:
                    matching.append(report_file)
            except Exception:
                # Skip invalid report files
                logger.debug(f"Skipping invalid report: {report_file}")
                continue

        logger.info(f"Found {len(matching)} reports for operation: {operation_name}")
        return matching

    return all_reports


def compare_reports(report1_file: str, report2_file: str) -> None:
    """
    Compare two reports and print summary.

    Args:
        report1_file: Path to first report
        report2_file: Path to second report

    Example:
        >>> compare_reports(
        ...     "output/report_20251115_143022.json",
        ...     "output/report_20251115_153045.json"
        ... )
    """
    logger.info("Comparing reports")

    report1 = load_report(report1_file)
    report2 = load_report(report2_file)

    print("\n" + "=" * 80)
    print("REPORT COMPARISON")
    print("=" * 80)

    print(f"\nReport 1: {report1['operation_name']} - {report1['timestamp']}")
    print(f"  Total processed: {report1['summary'].get('total_processed', 'N/A')}")
    print(f"  Status: {report1['summary'].get('overall_status', 'N/A')}")

    print(f"\nReport 2: {report2['operation_name']} - {report2['timestamp']}")
    print(f"  Total processed: {report2['summary'].get('total_processed', 'N/A')}")
    print(f"  Status: {report2['summary'].get('overall_status', 'N/A')}")

    # Compare key metrics if both are same operation
    if report1["operation_name"] == report2["operation_name"]:
        print("\n" + "-" * 80)
        print("DIFFERENCES:")
        print("-" * 80)

        for key in report1["summary"]:
            if key in report2["summary"]:
                val1 = report1["summary"][key]
                val2 = report2["summary"][key]

                if val1 != val2:
                    print(f"  {key}:")
                    print(f"    Report 1: {val1}")
                    print(f"    Report 2: {val2}")

    print("=" * 80)


if __name__ == "__main__":
    print("Report Generator Module")
    print("=" * 80)
    print("\nAvailable functions:")
    print("  - generate_report() - Basic report generation")
    print("  - generate_report_with_timing() - Report with execution time")
    print("  - generate_comprehensive_report() - Multi-phase report")
    print("  - generate_report_with_errors() - Report with error tracking")
    print("  - format_duration() - Format seconds to readable duration")
    print("  - load_report() - Load report from file")
    print("  - find_reports() - Find reports by operation name")
    print("  - compare_reports() - Compare two reports")
    print("\nImport this module in your operation scripts:")
    print("  from yirifi_dq.reporting import generate_report, generate_report_with_timing")
