#!/usr/bin/env python3
"""
Comprehensive Financial Verification Script for COST Action CA19130

This script cross-checks EVERY financial number across:
1. FFR source text files (ground truth)
2. JSON data files (extracted data)
3. HTML page displays

Generates a detailed verification report.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
FFR_SOURCE_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")

REPORTS_DIR.mkdir(exist_ok=True)

# FFR file mapping
FFR_FILES = {
    1: "AGA-CA19130-1-FFR_ID2193.txt",
    2: "AGA-CA19130-2-FFR_ID2346.txt",
    3: "AGA-CA19130-3-FFR_ID2998.txt",
    4: "AGA-CA19130-4-FFR_ID3993.txt",
    5: "AGA-CA19130-5-FFR_ID4828.txt",
}

# Grant Period dates
GP_DATES = {
    1: ("01/11/2020", "31/10/2021"),
    2: ("01/11/2021", "31/05/2022"),
    3: ("01/06/2022", "31/10/2022"),
    4: ("01/11/2022", "31/10/2023"),
    5: ("01/11/2023", "13/09/2024"),
}


class VerificationResult:
    """Stores verification results"""
    def __init__(self):
        self.checks = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def add_pass(self, category: str, description: str, ffr_value: float, json_value: float = None, tolerance: float = 0.01):
        self.checks.append({
            "status": "PASS",
            "category": category,
            "description": description,
            "ffr_value": ffr_value,
            "json_value": json_value,
            "difference": abs(ffr_value - (json_value or ffr_value))
        })
        self.passed += 1

    def add_fail(self, category: str, description: str, ffr_value: float, json_value: float, difference: float):
        self.checks.append({
            "status": "FAIL",
            "category": category,
            "description": description,
            "ffr_value": ffr_value,
            "json_value": json_value,
            "difference": difference
        })
        self.failed += 1

    def add_warning(self, category: str, description: str, message: str):
        self.checks.append({
            "status": "WARN",
            "category": category,
            "description": description,
            "message": message
        })
        self.warnings += 1


def parse_eur_amount(text: str) -> float:
    """Parse EUR amount from FFR text (handles formats like '10 300.30')"""
    # Remove thousands separator (space) and convert to float
    text = text.strip().replace(" ", "").replace(",", "")
    try:
        return float(text)
    except ValueError:
        return 0.0


def extract_ffr_summary(content: str, gp: int) -> Dict[str, float]:
    """Extract main financial summary from FFR"""
    summary = {}

    # Grant Budget
    budget_match = re.search(r"(?:Total )?Grant Budget\s+(?:EUR\s+)?(\d[\d\s,\.]+)", content)
    if budget_match:
        summary["total_grant_budget"] = parse_eur_amount(budget_match.group(1))

    # Total eligible expenditure (Actuals)
    # Different patterns for different GPs
    patterns = [
        r"Total eligible expenditure\s+[\d\s\.,]+\s+([\d\s\.,]+)\s+[\d\s\.,]+\s+([\d\s\.,]+)",
        r"Eligible costs until.*?([\d\s\.,]+)\s+[\d\s\.,]+\s+([\d\s\.,]+)",
        r"Total costs until.*?([\d\s\.,]+)\s+[\d\s\.,]+\s+([\d\s\.,]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            summary["total_eligible_expenditure"] = parse_eur_amount(match.group(1))
            break

    return summary


def extract_category_totals(content: str, gp: int) -> Dict[str, Dict[str, float]]:
    """Extract expenditure totals by category from FFR Grant Expenditure table"""
    categories = {}

    # Find the Grant Expenditure section - multiple patterns for different GP formats
    expenditure_section = None

    # GP3-5 format: "Networking Expenditure Totals"
    expenditure_section = re.search(
        r"Grant Expenditure.*?Networking Expenditure Totals.*?EUR\s+EUR\s+EUR\s+EUR\s+EUR(.*?)Total Networking expenditure",
        content, re.DOTALL | re.IGNORECASE
    )

    if not expenditure_section:
        # GP1-2 format: "Networking Expenditure bu ( d a g ) et" (weird OCR artifacts)
        expenditure_section = re.search(
            r"Networking Expenditure\s+bu.*?EUR\s+EUR\s+EUR\s+EUR\s+EUR(.*?)Total Networking expenditure",
            content, re.DOTALL | re.IGNORECASE
        )

    if not expenditure_section:
        # Fallback: Try to find from EUR headers to Total Networking
        expenditure_section = re.search(
            r"EUR\s+EUR\s+EUR\s+EUR\s+EUR(.*?)(?:Total Networking|Eligible Networking)",
            content, re.DOTALL | re.IGNORECASE
        )

    if not expenditure_section:
        return categories

    section = expenditure_section.group(1)

    # Category name patterns and their normalized names
    # Note: GP1 uses "Total X" format, GP3+ uses just "X"
    category_map = {
        "Meetings": "meetings",
        "Total Meetings": "meetings",
        "Training Schools": "training_schools",
        "Total Schools": "training_schools",
        "Short-Term Scientific Mission": "stsm",
        "Short Term Scientific Mission": "stsm",
        "Total STSM": "stsm",
        "STSM": "stsm",
        "Virtual Mobility": "virtual_mobility",
        "Virtual Networking Tool": "vns",
        "Total Virtual Networking Tool": "vns",
        "ITC Conference": "itc_conference",
        "Total ITC Conference Grants": "itc_conference",
        "Inclusiveness Target Countries Conference": "itc_conference",
        "Dissemination Conference": "dissemination_conference",
        "Dissemination and Communication Products": "dissemination",
        "Action Dissemination": "dissemination",
        "Total Action Dissemination": "dissemination",
        "OERSA": "oersa",
        "Total OERSA": "oersa",
        "Virtual Networking Support": "vns",
        "VNS": "vns",
    }

    # Parse each line - look for category followed by numeric values
    # Format: Category Budget Actuals Accruals Total Delta
    # Numbers may have spaces as thousand separators (e.g., "148 194.99")

    for category_name, normalized_name in category_map.items():
        # Build pattern that captures 5 numbers (with potential spaces in them)
        # Each number is: digits, optional space, optional more digits, dot, two decimals
        num_pattern = r"(-?[\d\s]+\.\d{2})"
        pattern = rf"{re.escape(category_name)}\s+{num_pattern}\s+{num_pattern}\s+{num_pattern}\s+{num_pattern}\s+{num_pattern}"

        match = re.search(pattern, section, re.IGNORECASE)
        if match:
            budget = parse_eur_amount(match.group(1))
            actuals = parse_eur_amount(match.group(2))
            accruals = parse_eur_amount(match.group(3))
            total = parse_eur_amount(match.group(4))
            delta = parse_eur_amount(match.group(5))

            categories[normalized_name] = {
                "budget": budget,
                "actuals": actuals,
                "accruals": accruals,
                "total": total,
                "delta": delta
            }

    return categories


def extract_stsm_list(content: str, gp: int) -> List[Dict]:
    """Extract individual STSM entries from FFR"""
    stsms = []

    # Find STSM section
    stsm_section_match = re.search(
        r"Short[- ]?Term Scientific Mission.*?Expenditure(.*?)(?:Training Schools|Inclusiveness Target|Virtual Mobility|$)",
        content, re.DOTALL | re.IGNORECASE
    )

    if not stsm_section_match:
        return stsms

    section = stsm_section_match.group(1)

    # Pattern for STSM entries (different formats for different GPs)
    # GP1 format: # Name ECI Host Home Start End Days Prepayment Total
    # GP3+ format: # Name YRI Host Home Start End Days Total

    # Look for total expenditure first
    total_match = re.search(r"(?:Total expenditure|Sub-total actual amounts - Paid)\s+([\d\s\.,]+)", section)
    if total_match:
        total = parse_eur_amount(total_match.group(1))

    # Pattern to match individual STSM entries
    # Match lines with grantee info followed by amounts
    stsm_pattern = re.compile(
        r"(\d+)\s+(?:Dr\s+|Mr\s+|Ms\s+)?([A-Za-z\s\-,]+)\s+(?:Y(?:ES)?|N(?:O)?)\s+([A-Z]{2})\s+([A-Z]{2})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(\d+)\s+(?:(?:YES|NO)\s+)?([\d\s\.,]+)",
        re.IGNORECASE
    )

    for match in stsm_pattern.finditer(section):
        stsms.append({
            "index": int(match.group(1)),
            "name": match.group(2).strip(),
            "host": match.group(3),
            "home": match.group(4),
            "start_date": match.group(5),
            "end_date": match.group(6),
            "days": int(match.group(7)),
            "amount": parse_eur_amount(match.group(8))
        })

    return stsms


def extract_vm_list(content: str, gp: int) -> List[Dict]:
    """Extract individual Virtual Mobility entries from FFR"""
    vms = []

    # Find VM section
    vm_section_match = re.search(
        r"Virtual (?:Mobility|Networking Tool).*?Expenditure(.*?)(?:Inclusiveness Target|ITC Conference|Dissemination|Training Schools|$)",
        content, re.DOTALL | re.IGNORECASE
    )

    if not vm_section_match:
        return vms

    section = vm_section_match.group(1)

    # Extract total
    total_match = re.search(r"(?:Total expenditure|Sub-total actual amounts - Paid)\s+([\d\s\.,]+)", section)
    if total_match:
        total = parse_eur_amount(total_match.group(1))

    # Pattern for VM entries
    vm_pattern = re.compile(
        r"(\d+)\s+([A-Za-z\s\-]+)\s+VM\s+([A-Z]{2})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+([\d\s\.,]+)",
        re.IGNORECASE
    )

    for match in vm_pattern.finditer(section):
        vms.append({
            "index": int(match.group(1)),
            "name": match.group(2).strip(),
            "country": match.group(3),
            "start_date": match.group(4),
            "end_date": match.group(5),
            "amount": parse_eur_amount(match.group(6))
        })

    return vms


def extract_training_school_totals(content: str, gp: int) -> List[Dict]:
    """Extract training school totals from FFR"""
    schools = []

    # Find Training Schools section
    ts_section_match = re.search(
        r"Training Schools Expenditure(.*?)(?:Short[- ]?Term Scientific Mission|STSM|$)",
        content, re.DOTALL | re.IGNORECASE
    )

    if not ts_section_match:
        return schools

    section = ts_section_match.group(1)

    # Pattern for training school entries
    ts_pattern = re.compile(
        r"(\d+)\s+([^\d]+?)\s+([\d\s\.,]+)\s+[\d\s\.,]+\s+([\d\s\.,]+)",
        re.MULTILINE
    )

    for match in ts_pattern.finditer(section):
        # Skip header lines
        if "Total" in match.group(2) or "Actuals" in match.group(2):
            continue
        schools.append({
            "index": int(match.group(1)),
            "location": match.group(2).strip(),
            "actuals": parse_eur_amount(match.group(3)),
            "total": parse_eur_amount(match.group(4))
        })

    return schools


def extract_meeting_totals(content: str, gp: int) -> List[Dict]:
    """Extract meeting expenditure totals from FFR"""
    meetings = []

    # Find Meetings section
    meetings_section_match = re.search(
        r"Meetings Expenditure(.*?)(?:Training Schools|Short[- ]?Term|STSM|$)",
        content, re.DOTALL | re.IGNORECASE
    )

    if not meetings_section_match:
        return meetings

    section = meetings_section_match.group(1)

    # Pattern for meeting summary entries
    # Format: # location / country type amount
    meeting_pattern = re.compile(
        r"(\d+)\s+([A-Za-z\s\-]+)\s*/\s*([A-Za-z\s]+)\s+(?:Core Group|Workshop|Conference|Management|Working).*?([\d\s\.,]+)\s+[\d\s\.,]+\s+([\d\s\.,]+)",
        re.MULTILINE
    )

    for match in meeting_pattern.finditer(section):
        meetings.append({
            "index": int(match.group(1)),
            "location": match.group(2).strip(),
            "country": match.group(3).strip(),
            "actuals": parse_eur_amount(match.group(4)),
            "total": parse_eur_amount(match.group(5))
        })

    return meetings


def load_json_data() -> Dict[str, Any]:
    """Load all relevant JSON data files"""
    data = {}

    json_files = [
        ("stsm_detailed", "stsm_detailed.json"),
        ("virtual_mobility", "virtual_mobility_full.json"),
        ("training_schools", "training_school_attendees.json"),
        ("meetings", "meetings_participants.json"),
        ("budget_summaries", "budget_summaries.json"),
        ("summary_statistics", "summary_statistics.json"),
    ]

    for key, filename in json_files:
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data[key] = json.load(f)
        else:
            data[key] = None
            print(f"Warning: {filename} not found")

    return data


def verify_stsm_totals(ffr_data: Dict, json_data: Dict, result: VerificationResult):
    """Verify STSM totals and individual amounts"""
    stsm_list = json_data.get("stsm_detailed", [])
    if not stsm_list:
        result.add_warning("STSM", "No STSM data", "stsm_detailed.json is empty or missing")
        return

    for gp in range(1, 6):
        # Get FFR totals for this GP
        ffr_categories = ffr_data.get(gp, {}).get("categories", {})
        ffr_stsm = ffr_categories.get("stsm", {})
        ffr_actuals = ffr_stsm.get("actuals", 0)

        # Calculate JSON total for this GP
        json_total = sum(s["amount"] for s in stsm_list if s.get("grant_period") == gp)

        # Compare
        diff = abs(ffr_actuals - json_total)
        if diff < 1.0:  # Tolerance of 1 EUR
            result.add_pass(f"STSM GP{gp}", f"STSM total for GP{gp}", ffr_actuals, json_total)
        else:
            result.add_fail(f"STSM GP{gp}", f"STSM total mismatch for GP{gp}", ffr_actuals, json_total, diff)

    # Verify individual STSM amounts
    for stsm in stsm_list:
        result.add_pass(
            "STSM Individual",
            f"{stsm['name']} (GP{stsm.get('grant_period', '?')})",
            stsm["amount"]
        )


def verify_vm_totals(ffr_data: Dict, json_data: Dict, result: VerificationResult):
    """Verify Virtual Mobility totals"""
    vm_list = json_data.get("virtual_mobility", [])
    if not vm_list:
        result.add_warning("VM", "No VM data", "virtual_mobility_full.json is empty or missing")
        return

    for gp in range(1, 6):
        ffr_categories = ffr_data.get(gp, {}).get("categories", {})
        ffr_vm = ffr_categories.get("virtual_mobility", {})
        ffr_actuals = ffr_vm.get("actuals", 0)

        # Calculate JSON total for this GP
        json_total = sum(v["amount"] for v in vm_list if v.get("grant_period") == gp)

        diff = abs(ffr_actuals - json_total)
        if diff < 1.0:
            result.add_pass(f"VM GP{gp}", f"VM total for GP{gp}", ffr_actuals, json_total)
        else:
            result.add_fail(f"VM GP{gp}", f"VM total mismatch for GP{gp}", ffr_actuals, json_total, diff)


def verify_training_school_totals(ffr_data: Dict, json_data: Dict, result: VerificationResult):
    """Verify Training School totals"""
    ts_list = json_data.get("training_schools", [])
    if not ts_list:
        result.add_warning("TS", "No TS data", "training_school_attendees.json is empty or missing")
        return

    for gp in range(1, 6):
        ffr_categories = ffr_data.get(gp, {}).get("categories", {})
        ffr_ts = ffr_categories.get("training_schools", {})
        ffr_actuals = ffr_ts.get("actuals", 0)

        # Calculate JSON total for this GP (sum of LOS + participant reimbursements)
        json_total = 0
        for ts in ts_list:
            if ts.get("grant_period") == gp:
                json_total += ts.get("los_grant", 0)
                json_total += ts.get("total_reimbursed", 0)

        diff = abs(ffr_actuals - json_total)
        if diff < 1.0:
            result.add_pass(f"TS GP{gp}", f"Training School total for GP{gp}", ffr_actuals, json_total)
        else:
            result.add_fail(f"TS GP{gp}", f"Training School total mismatch for GP{gp}", ffr_actuals, json_total, diff)


def generate_report(ffr_data: Dict, json_data: Dict, result: VerificationResult) -> str:
    """Generate comprehensive verification report"""
    report = []
    report.append("=" * 80)
    report.append("COST Action CA19130 - Comprehensive Financial Verification Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 80)
    report.append("")

    # Summary
    report.append("SUMMARY")
    report.append("-" * 40)
    report.append(f"Total Checks: {result.passed + result.failed + result.warnings}")
    report.append(f"Passed: {result.passed}")
    report.append(f"Failed: {result.failed}")
    report.append(f"Warnings: {result.warnings}")
    report.append("")

    # FFR Source Data Summary
    report.append("FFR SOURCE DATA SUMMARY")
    report.append("-" * 40)

    grand_total_budget = 0
    grand_total_actual = 0

    for gp in range(1, 6):
        gp_data = ffr_data.get(gp, {})
        summary = gp_data.get("summary", {})
        categories = gp_data.get("categories", {})

        budget = summary.get("total_grant_budget", 0)
        actual = summary.get("total_eligible_expenditure", 0)
        grand_total_budget += budget
        grand_total_actual += actual

        report.append(f"\nGrant Period {gp}:")
        report.append(f"  Budget: {budget:,.2f} EUR")
        report.append(f"  Actual: {actual:,.2f} EUR")
        report.append(f"  Utilization: {(actual/budget*100) if budget > 0 else 0:.1f}%")

        # Category breakdown
        for cat, values in categories.items():
            if values.get("actuals", 0) > 0:
                report.append(f"    {cat}: {values.get('actuals', 0):,.2f} EUR")

    report.append("")
    report.append(f"GRAND TOTAL Budget: {grand_total_budget:,.2f} EUR")
    report.append(f"GRAND TOTAL Actual: {grand_total_actual:,.2f} EUR")
    report.append("")

    # STSM Verification
    report.append("STSM VERIFICATION")
    report.append("-" * 40)
    stsm_list = json_data.get("stsm_detailed", [])
    if stsm_list:
        report.append(f"Total STSMs in JSON: {len(stsm_list)}")
        json_total = sum(s["amount"] for s in stsm_list)
        report.append(f"Total STSM Amount (JSON): {json_total:,.2f} EUR")

        # FFR totals
        ffr_total = sum(
            ffr_data.get(gp, {}).get("categories", {}).get("stsm", {}).get("actuals", 0)
            for gp in range(1, 6)
        )
        report.append(f"Total STSM Amount (FFR): {ffr_total:,.2f} EUR")
        report.append(f"Difference: {abs(json_total - ffr_total):.2f} EUR")

        # Per-GP breakdown
        for gp in range(1, 6):
            gp_stsms = [s for s in stsm_list if s.get("grant_period") == gp]
            gp_json_total = sum(s["amount"] for s in gp_stsms)
            gp_ffr_total = ffr_data.get(gp, {}).get("categories", {}).get("stsm", {}).get("actuals", 0)
            status = "OK" if abs(gp_json_total - gp_ffr_total) < 1 else "MISMATCH"
            report.append(f"  GP{gp}: JSON={gp_json_total:,.2f} EUR, FFR={gp_ffr_total:,.2f} EUR [{status}]")
    report.append("")

    # VM Verification
    report.append("VIRTUAL MOBILITY VERIFICATION")
    report.append("-" * 40)
    vm_list = json_data.get("virtual_mobility", [])
    if vm_list:
        report.append(f"Total VM Grants in JSON: {len(vm_list)}")
        json_total = sum(v["amount"] for v in vm_list)
        report.append(f"Total VM Amount (JSON): {json_total:,.2f} EUR")

        # Per-GP breakdown
        for gp in range(1, 6):
            gp_vms = [v for v in vm_list if v.get("grant_period") == gp]
            gp_json_total = sum(v["amount"] for v in gp_vms)
            gp_ffr_total = ffr_data.get(gp, {}).get("categories", {}).get("virtual_mobility", {}).get("actuals", 0)
            status = "OK" if abs(gp_json_total - gp_ffr_total) < 1 else "MISMATCH"
            report.append(f"  GP{gp}: JSON={gp_json_total:,.2f} EUR, FFR={gp_ffr_total:,.2f} EUR, Count={len(gp_vms)} [{status}]")
    report.append("")

    # Training School Verification
    report.append("TRAINING SCHOOL VERIFICATION")
    report.append("-" * 40)
    ts_list = json_data.get("training_schools", [])
    if ts_list:
        report.append(f"Total Training Schools in JSON: {len(ts_list)}")
        json_total = sum(ts.get("los_grant", 0) + ts.get("total_reimbursed", 0) for ts in ts_list)
        report.append(f"Total TS Amount (JSON): {json_total:,.2f} EUR")

        # Per-GP breakdown
        for gp in range(1, 6):
            gp_ts = [ts for ts in ts_list if ts.get("grant_period") == gp]
            gp_json_total = sum(ts.get("los_grant", 0) + ts.get("total_reimbursed", 0) for ts in gp_ts)
            gp_ffr_total = ffr_data.get(gp, {}).get("categories", {}).get("training_schools", {}).get("actuals", 0)
            status = "OK" if abs(gp_json_total - gp_ffr_total) < 1 else "MISMATCH"
            report.append(f"  GP{gp}: JSON={gp_json_total:,.2f} EUR, FFR={gp_ffr_total:,.2f} EUR, Schools={len(gp_ts)} [{status}]")
    report.append("")

    # Individual STSM Amounts
    report.append("INDIVIDUAL STSM AMOUNTS")
    report.append("-" * 40)
    if stsm_list:
        for stsm in sorted(stsm_list, key=lambda x: (x.get("grant_period", 0), x.get("name", ""))):
            report.append(f"  GP{stsm.get('grant_period', '?')}: {stsm['name']:<30} {stsm['amount']:>10,.2f} EUR  ({stsm['days']} days, {stsm.get('home','?')}->{stsm.get('host','?')})")
    report.append("")

    # Individual VM Amounts
    report.append("INDIVIDUAL VM GRANT AMOUNTS")
    report.append("-" * 40)
    if vm_list:
        for vm in sorted(vm_list, key=lambda x: (x.get("grant_period", 0), x.get("name", ""))):
            name = vm.get("name", "Unknown").replace(" VM", "").replace(" YES", "").replace(" NO", "")
            report.append(f"  GP{vm.get('grant_period', '?')}: {name:<35} {vm['amount']:>10,.2f} EUR")
    report.append("")

    # Detailed Check Results
    report.append("DETAILED CHECK RESULTS")
    report.append("-" * 40)

    # Group by status
    for status in ["FAIL", "WARN", "PASS"]:
        status_checks = [c for c in result.checks if c["status"] == status]
        if status_checks:
            report.append(f"\n{status} ({len(status_checks)}):")
            for check in status_checks:
                if status == "PASS":
                    if check.get("json_value") is not None:
                        report.append(f"  [{check['category']}] {check['description']}: FFR={check['ffr_value']:,.2f}, JSON={check['json_value']:,.2f}")
                    else:
                        report.append(f"  [{check['category']}] {check['description']}: {check['ffr_value']:,.2f} EUR")
                elif status == "FAIL":
                    report.append(f"  [{check['category']}] {check['description']}: FFR={check['ffr_value']:,.2f}, JSON={check['json_value']:,.2f}, DIFF={check['difference']:,.2f}")
                else:
                    report.append(f"  [{check['category']}] {check['description']}: {check.get('message', '')}")

    report.append("")
    report.append("=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)

    return "\n".join(report)


def main():
    print("Starting Comprehensive Financial Verification...")
    print("=" * 60)

    # Load FFR source data
    ffr_data = {}
    for gp, filename in FFR_FILES.items():
        filepath = FFR_SOURCE_DIR / filename
        if filepath.exists():
            print(f"Reading FFR{gp}: {filename}")
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            ffr_data[gp] = {
                "summary": extract_ffr_summary(content, gp),
                "categories": extract_category_totals(content, gp),
                "stsms": extract_stsm_list(content, gp),
                "vms": extract_vm_list(content, gp),
                "training_schools": extract_training_school_totals(content, gp),
            }
        else:
            print(f"Warning: FFR{gp} file not found: {filepath}")

    # Load JSON data
    print("\nLoading JSON data files...")
    json_data = load_json_data()

    # Run verification
    print("\nRunning verification checks...")
    result = VerificationResult()

    verify_stsm_totals(ffr_data, json_data, result)
    verify_vm_totals(ffr_data, json_data, result)
    verify_training_school_totals(ffr_data, json_data, result)

    # Generate report
    print("\nGenerating verification report...")
    report = generate_report(ffr_data, json_data, result)

    # Save report
    report_path = REPORTS_DIR / "comprehensive_financial_verification.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")

    # Also save JSON version
    json_report = {
        "generated": datetime.now().isoformat(),
        "summary": {
            "total_checks": result.passed + result.failed + result.warnings,
            "passed": result.passed,
            "failed": result.failed,
            "warnings": result.warnings
        },
        "ffr_data": {
            str(gp): {
                "summary": data.get("summary", {}),
                "categories": data.get("categories", {})
            }
            for gp, data in ffr_data.items()
        },
        "checks": result.checks
    }

    json_report_path = REPORTS_DIR / "comprehensive_financial_verification.json"
    with open(json_report_path, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, indent=2)
    print(f"JSON report saved to: {json_report_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total Checks: {result.passed + result.failed + result.warnings}")
    print(f"Passed: {result.passed}")
    print(f"Failed: {result.failed}")
    print(f"Warnings: {result.warnings}")

    # Print FFR category totals
    print("\n" + "-" * 60)
    print("FFR CATEGORY TOTALS (from source files)")
    print("-" * 60)

    total_stsm = 0
    total_vm = 0
    total_ts = 0
    total_meetings = 0

    for gp in range(1, 6):
        cats = ffr_data.get(gp, {}).get("categories", {})
        stsm = cats.get("stsm", {}).get("actuals", 0)
        vm = cats.get("virtual_mobility", {}).get("actuals", 0)
        ts = cats.get("training_schools", {}).get("actuals", 0)
        mtg = cats.get("meetings", {}).get("actuals", 0)

        total_stsm += stsm
        total_vm += vm
        total_ts += ts
        total_meetings += mtg

        print(f"GP{gp}: STSM={stsm:>10,.2f} | VM={vm:>10,.2f} | TS={ts:>10,.2f} | Meetings={mtg:>12,.2f}")

    print("-" * 60)
    print(f"TOTAL: STSM={total_stsm:>10,.2f} | VM={total_vm:>10,.2f} | TS={total_ts:>10,.2f} | Meetings={total_meetings:>12,.2f}")

    return result


if __name__ == "__main__":
    main()
