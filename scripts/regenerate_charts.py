"""
Regenerate All Charts.

This script finds and executes all chart.py files in the repository
to regenerate chart PDFs after data updates.

Usage:
    python scripts/regenerate_charts.py
"""

import subprocess
import sys
from pathlib import Path

# Repository root
REPO_ROOT = Path(__file__).parent.parent

# Directories containing charts
CHART_DIRS = [
    REPO_ROOT / 'financial-reports' / 'charts',
    REPO_ROOT / 'work-budget-plans' / 'charts',
]


def find_chart_scripts():
    """Find all chart.py files in chart directories."""
    chart_scripts = []

    for charts_dir in CHART_DIRS:
        if charts_dir.exists():
            for chart_dir in sorted(charts_dir.iterdir()):
                if chart_dir.is_dir():
                    chart_py = chart_dir / 'chart.py'
                    if chart_py.exists():
                        chart_scripts.append(chart_py)

    return chart_scripts


def run_chart_script(script_path):
    """Run a single chart script and return success status."""
    chart_name = script_path.parent.name
    parent_dir = script_path.parent.parent.parent.name

    print(f"  Generating {parent_dir}/{chart_name}...", end=" ")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=script_path.parent  # Run from chart directory
        )

        if result.returncode == 0:
            # Check if PDF was created
            pdf_path = script_path.parent / 'chart.pdf'
            if pdf_path.exists():
                print("OK")
                return True
            else:
                print("WARN: No PDF generated")
                return False
        else:
            print("FAILED")
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}")
            return False

    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    """Main entry point."""
    print("=" * 60)
    print("COST Action CA19130 - Chart Regeneration")
    print("=" * 60)

    # Find all chart scripts
    chart_scripts = find_chart_scripts()

    if not chart_scripts:
        print("\nNo chart scripts found!")
        return 1

    print(f"\nFound {len(chart_scripts)} chart scripts")

    # Run each chart script
    print("\nRegenerating charts...")
    success_count = 0
    failed_scripts = []

    for script in chart_scripts:
        if run_chart_script(script):
            success_count += 1
        else:
            failed_scripts.append(script)

    # Summary
    print("\n" + "=" * 60)
    print(f"Chart regeneration complete: {success_count}/{len(chart_scripts)} succeeded")

    if failed_scripts:
        print(f"\nFailed charts ({len(failed_scripts)}):")
        for script in failed_scripts:
            print(f"  - {script.parent.parent.parent.name}/{script.parent.name}")
        return 1

    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
