"""
WBP Regex Patterns - Regular expression patterns for extracting data from WBP text files.

Each pattern is designed to handle the various formats found across WBP1-WBP5 documents.
"""

import re
from typing import Pattern

# =============================================================================
# ACTION PROFILE PATTERNS (Page 1)
# =============================================================================

# Action code pattern - e.g., "CA19130"
ACTION_CODE: Pattern = re.compile(r'Action\s+(CA\d+)', re.IGNORECASE)

# Total Grant pattern - e.g., "Total Grant (B+C) 270,315.26"
TOTAL_GRANT: Pattern = re.compile(
    r'Total Grant.*?([\d,]+\.?\d*)\s*$',
    re.IGNORECASE | re.MULTILINE
)

# Grant Period dates - e.g., "01/11/2023" to "13/09/2024"
DATE_PATTERN: Pattern = re.compile(r'(\d{2}/\d{2}/\d{4})')

# Participating countries counts
PARTICIPATING_COUNTRIES: Pattern = re.compile(
    r'COST Countries\s+(\d+).*?Near Neighbour Countries\s+(\d+).*?International Partner Countries\s+(\d+)',
    re.DOTALL | re.IGNORECASE
)

# =============================================================================
# WORKING GROUP PATTERNS (Page 2)
# =============================================================================

# Working group header - e.g., "WG1: Financial Applications"
WORKING_GROUP_HEADER: Pattern = re.compile(
    r'(WG\s*\d+)\s*[:\-]?\s*(.+?)(?=\n|WG\s*\d+|$)',
    re.IGNORECASE
)

# WG Leader pattern
WG_LEADER: Pattern = re.compile(
    r'Leader\s*[:\-]?\s*([^,\n]+),?\s*(.+?)(?=\n|$)',
    re.IGNORECASE
)

# =============================================================================
# BUDGET SUMMARY PATTERNS (Page 7)
# =============================================================================

# Budget category patterns - handles format: "(1) Meetings 151,674.75"
# Using flexible patterns that match amounts at end of line
BUDGET_MEETINGS: Pattern = re.compile(
    r'\(1\)\s*Meetings?\s+([\d,\.]+)',
    re.IGNORECASE
)

BUDGET_TRAINING_SCHOOLS: Pattern = re.compile(
    r'\(2\)\s*Training Schools?\s+([\d,\.]+)',
    re.IGNORECASE
)

# GP1-3 format: STSM and ITC separately
BUDGET_STSM_OLD: Pattern = re.compile(
    r'\(3\)\s*Short[\s\-]?Term.*?([\d,\.]+)',
    re.IGNORECASE
)

BUDGET_ITC_OLD: Pattern = re.compile(
    r'\(4\)\s*ITC Conference.*?([\d,\.]+)',
    re.IGNORECASE
)

# GP4-5 format: Mobility (combined) and Conference Presentations
BUDGET_MOBILITY: Pattern = re.compile(
    r'\(3\)\s*Mobility.*?([\d,\.]+)',
    re.IGNORECASE
)

# "Presentation at Conferences organised by Third Parties" or "Conference Presentations"
BUDGET_CONFERENCE_PRESENTATIONS: Pattern = re.compile(
    r'\(4\)\s*(?:Presentation at Conferences|Conference).*?([\d,\.]+)',
    re.IGNORECASE
)

BUDGET_DISSEMINATION: Pattern = re.compile(
    r'\(5\)\s*Dissemination.*?([\d,\.]+)',
    re.IGNORECASE
)

# "Other Expenses Related to Scientific Activities (OERSA)"
BUDGET_OERSA: Pattern = re.compile(
    r'\(6\)\s*(?:Other Expenses|OERSA).*?([\d,\.]+)',
    re.IGNORECASE
)

# "B. Total Science Expenditure (sum of (1) to (6)) 235,056.75"
BUDGET_TOTAL_SCIENCE: Pattern = re.compile(
    r'Total Science Expenditure[^\d]*([\d,]+\.\d{2})',
    re.IGNORECASE
)

# "C. Financial and Scientific Administration and Coordination (FSAC) (max. of 35,258.51"
BUDGET_FSAC: Pattern = re.compile(
    r'Financial and Scientific Administration.*?([\d,]+\.\d{2})',
    re.IGNORECASE
)

# =============================================================================
# MEETINGS PATTERNS (Pages 8-20)
# =============================================================================

# Meeting title and type line
MEETING_TITLE: Pattern = re.compile(
    r'^([A-Za-z][\w\s\-,\.&\'\"]+?)\s+((?:Core Group|Working Group|Management Committee|Workshop[s]?(?:/Conference)?)[^0-9]*)',
    re.MULTILINE | re.IGNORECASE
)

# Meeting dates - "24/04/2024 - 25/04/2024" or "24/04/2024"
MEETING_DATES: Pattern = re.compile(
    r'(\d{2}/\d{2}/\d{4})\s*[\-–]?\s*(\d{2}/\d{2}/\d{4})?'
)

# Meeting location and ITC status
MEETING_LOCATION: Pattern = re.compile(
    r'([A-Za-z][\w\s\-\.]+?)\s+(Yes|No)\s+([\d\s,\.]+)$',
    re.MULTILINE
)

# Expected participants
MEETING_PARTICIPANTS: Pattern = re.compile(
    r'Total number of expected\s+(\d+)\s+Number of participants expected.*?(\d+)',
    re.DOTALL
)

# Meeting cost - EUR amount at end of line
MEETING_COST: Pattern = re.compile(
    r'([\d\s,]+\.\d{2})\s*$',
    re.MULTILINE
)

# =============================================================================
# TRAINING SCHOOL PATTERNS (Pages 21-25)
# =============================================================================

# Training school header
TRAINING_SCHOOL_HEADER: Pattern = re.compile(
    r'Training School\s*(\d+)?',
    re.IGNORECASE
)

# Institution/location line
TRAINING_SCHOOL_LOCATION: Pattern = re.compile(
    r'([A-Za-z][\w\s\-\.]+?)\s*/\s*([A-Za-z][\w\s\-\.]+?)\s*/\s*([A-Za-z]+)',
    re.IGNORECASE
)

# Expected trainers/trainees
TRAINING_SCHOOL_COUNTS: Pattern = re.compile(
    r'(?:trainers?\s*[:\-]?\s*(\d+))|(?:trainees?\s*[:\-]?\s*(\d+))',
    re.IGNORECASE
)

# =============================================================================
# MOBILITY PATTERNS (Page 26)
# =============================================================================

# STSM budget and count
STSM_BUDGET: Pattern = re.compile(
    r'STSM\s*(?:budget|allocation)?\s*[:\-]?\s*([\d\s,\.]+)',
    re.IGNORECASE
)

STSM_COUNT: Pattern = re.compile(
    r'(?:expected|planned)\s*(?:number of)?\s*STSM\s*[:\-]?\s*(\d+)',
    re.IGNORECASE
)

# Virtual Mobility budget
VM_BUDGET: Pattern = re.compile(
    r'Virtual Mobility\s*(?:budget|allocation)?\s*[:\-]?\s*([\d\s,\.]+)',
    re.IGNORECASE
)

# =============================================================================
# GAPG PATTERNS (Pages 5-6)
# =============================================================================

# GAPG header and title
GAPG_HEADER: Pattern = re.compile(
    r'GAPG\s*(\d+)\s*[:\-]?\s*(.+?)(?=\n|GAPG|\Z)',
    re.IGNORECASE | re.DOTALL
)

# MoU objective references
MOU_OBJECTIVE_REF: Pattern = re.compile(
    r'(?:MoU\s*)?Objective\s*#?\s*(\d+)',
    re.IGNORECASE
)

# =============================================================================
# DISSEMINATION PATTERNS (Page 28)
# =============================================================================

DISSEMINATION_PRODUCT: Pattern = re.compile(
    r'(\d+)\s+(\w+)\s+(.+?)\s+([\d\s,\.]+)$',
    re.MULTILINE
)

# =============================================================================
# OERSA PATTERNS (Page 29)
# =============================================================================

OERSA_ITEM: Pattern = re.compile(
    r'(.+?)\s+([\d\s,\.]+)$',
    re.MULTILINE
)

# =============================================================================
# UTILITY PATTERNS
# =============================================================================

# Clean EUR amount - removes spaces, handles comma as decimal/thousands
EUR_AMOUNT: Pattern = re.compile(r'([\d\s,]+\.?\d*)')

# Page boundary
PAGE_BOUNDARY: Pattern = re.compile(r'={10,}\nPAGE\s+(\d+)\n={10,}')

# Section headers
SECTION_MEETINGS: Pattern = re.compile(r'^Meetings\s*$', re.MULTILINE)
SECTION_TRAINING: Pattern = re.compile(r'^Training Schools?\s*$', re.MULTILINE)
SECTION_MOBILITY: Pattern = re.compile(r'^(?:Mobility|STSM|Short[\s\-]?Term)', re.MULTILINE | re.IGNORECASE)
SECTION_DISSEMINATION: Pattern = re.compile(r'^Dissemination', re.MULTILINE | re.IGNORECASE)
SECTION_OERSA: Pattern = re.compile(r'^(?:OERSA|Other Expenses)', re.MULTILINE | re.IGNORECASE)


def parse_eur_amount(text: str) -> float:
    """
    Parse EUR amount from text, handling various formats.

    Examples:
    - "151,674.75" -> 151674.75
    - "151 674.75" -> 151674.75
    - "151674.75" -> 151674.75
    - "1,000" -> 1000.0
    """
    if not text:
        return 0.0
    # Remove spaces (used as thousands separator)
    clean = text.replace(" ", "").replace(",", "")
    try:
        return float(clean)
    except ValueError:
        return 0.0


def parse_date(text: str):
    """Parse date from DD/MM/YYYY format to date object."""
    from datetime import date
    match = DATE_PATTERN.search(text)
    if match:
        parts = match.group(1).split('/')
        return date(int(parts[2]), int(parts[1]), int(parts[0]))
    return None
