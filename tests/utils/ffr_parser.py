"""
FFR (Final Financial Report) Parser for COST Action CA19130.

Parses FFR text files extracted from PDFs to extract:
- Budget summary (by category)
- Actual expenditure (by category)
- Individual items (STSMs, meetings, VM grants)
- Participant reimbursements

Handles format variations across Grant Periods:
- GP1: Uses "Total STSM", "Total Action Dissemination"
- GP5: Uses "Short-Term Scientific Mission", "Dissemination and Communication Products"
"""

import re
from pathlib import Path
from decimal import Decimal
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .amount_parser import parse_eur_amount


@dataclass
class CategoryData:
    """Budget category with budget, actual, and delta amounts."""
    name: str
    budget: Decimal = Decimal("0.00")
    actuals: Decimal = Decimal("0.00")
    accruals: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")
    delta: Decimal = Decimal("0.00")


@dataclass
class STSMRecord:
    """Individual STSM grant record."""
    index: int
    grantee_name: str
    eci: str  # Y/N
    home_country: str
    host_country: str
    start_date: str
    end_date: str
    days: int
    prepayment: str  # YES/NO
    amount: Decimal


@dataclass
class MeetingRecord:
    """Individual meeting record."""
    index: int
    location: str
    meeting_type: str
    title: str
    start_date: str
    end_date: str
    participants: int
    reimbursed_participants: int
    actuals: Decimal
    accruals: Decimal
    total: Decimal
    participant_details: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class VMRecord:
    """Virtual Mobility grant record."""
    index: int
    grantee_name: str
    eci: str
    country: str
    start_date: str
    end_date: str
    days: int
    amount: Decimal


@dataclass
class FFRData:
    """Complete FFR data structure."""
    grant_period: int
    period_start: str
    period_end: str
    grant_budget: Decimal
    total_eligible: Decimal
    categories: Dict[str, CategoryData]
    stsms: List[STSMRecord]
    meetings: List[MeetingRecord]
    virtual_mobility: List[VMRecord]
    raw_text: str = ""


class FFRParser:
    """Parser for FFR (Final Financial Report) text files."""

    # FFR files by grant period
    FFR_FILES = {
        1: "AGA-CA19130-1-FFR_ID2193.txt",
        2: "AGA-CA19130-2-FFR_ID2346.txt",
        3: "AGA-CA19130-3-FFR_ID2998.txt",
        4: "AGA-CA19130-4-FFR_ID3993.txt",
        5: "AGA-CA19130-5-FFR_ID4828.txt",
    }

    # Category name mappings (normalize variations across grant periods)
    CATEGORY_MAPPINGS = {
        # Meetings
        "total meetings": "meetings",
        "meetings": "meetings",
        # Training Schools
        "total schools": "training_schools",
        "training schools": "training_schools",
        # STSMs
        "total stsm": "stsm",
        "short-term scientific mission": "stsm",
        "short term scientific mission": "stsm",
        # Virtual Mobility / Networking
        "total virtual networking tool": "virtual_mobility",
        "virtual mobility": "virtual_mobility",
        "virtual networking support": "virtual_networking_support",
        # ITC Conference Grants
        "total itc conference grants": "itc_conference",
        "itc conference": "itc_conference",
        # Dissemination
        "total action dissemination": "dissemination",
        "dissemination and communication products": "dissemination",
        "dissemination conference": "dissemination_conference",
        # OERSA
        "total oersa": "oersa",
        "oersa": "oersa",
        # FSAC
        "fsac (max 15%)": "fsac",
        "fsac": "fsac",
        # Totals
        "total networking expenditure": "total_networking",
        "eligible networking expenditure": "eligible_networking",
        "total eligible expenditure": "total_eligible",
    }

    def __init__(self, source_dir: str):
        """
        Initialize parser with source directory.

        Args:
            source_dir: Directory containing FFR text files
        """
        self.source_dir = Path(source_dir)

    def parse_grant_period(self, gp: int) -> FFRData:
        """
        Parse FFR file for a specific grant period.

        Args:
            gp: Grant period number (1-5)

        Returns:
            FFRData object with all parsed data
        """
        if gp not in self.FFR_FILES:
            raise ValueError(f"Invalid grant period: {gp}. Must be 1-5.")

        filepath = self.source_dir / self.FFR_FILES[gp]
        if not filepath.exists():
            raise FileNotFoundError(f"FFR file not found: {filepath}")

        content = filepath.read_text(encoding='utf-8')

        # Extract categories first so we can use them for total_eligible
        categories = self._extract_categories(content)

        # Get total_eligible from categories if available, otherwise use pattern matching
        total_eligible = Decimal("0.00")
        if 'total_eligible' in categories:
            total_eligible = categories['total_eligible'].total
        else:
            total_eligible = self._extract_total_eligible(content)

        return FFRData(
            grant_period=gp,
            period_start=self._extract_period_start(content),
            period_end=self._extract_period_end(content),
            grant_budget=self._extract_grant_budget(content),
            total_eligible=total_eligible,
            categories=categories,
            stsms=self._extract_stsms(content),
            meetings=self._extract_meetings(content),
            virtual_mobility=self._extract_vm(content),
            raw_text=content
        )

    def parse_all(self) -> Dict[int, FFRData]:
        """
        Parse all FFR files.

        Returns:
            Dictionary mapping grant period to FFRData
        """
        return {gp: self.parse_grant_period(gp) for gp in self.FFR_FILES.keys()}

    def _extract_period_start(self, content: str) -> str:
        """Extract reporting period start date."""
        match = re.search(r'Period of reporting from (\d{2}/\d{2}/\d{4})', content)
        return match.group(1) if match else ""

    def _extract_period_end(self, content: str) -> str:
        """Extract reporting period end date."""
        match = re.search(r'Period of reporting from \d{2}/\d{2}/\d{4} to (\d{2}/\d{2}/\d{4})', content)
        return match.group(1) if match else ""

    def _extract_grant_budget(self, content: str) -> Decimal:
        """Extract total grant budget."""
        match = re.search(r'Total Grant Budget\s+EUR\s+([\d\s,\.]+)', content)
        if match:
            return parse_eur_amount(match.group(1))
        return Decimal("0.00")

    def _extract_total_eligible(self, content: str) -> Decimal:
        """Extract total eligible expenditure from summary table."""
        # Look for "Total eligible expenditure" line with amounts
        # Use pattern that handles space-separated thousands
        pattern = r'Total eligible expenditure\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)'
        match = re.search(pattern, content)
        if match:
            # Return the 'Total' column (index 3, which is d=b+c)
            return parse_eur_amount(match.group(4))
        return Decimal("0.00")

    def _extract_categories(self, content: str) -> Dict[str, CategoryData]:
        """Extract all budget categories from summary table on page 2."""
        categories = {}

        # Find page 2 section (expenditure summary)
        page2_start = content.find("PAGE 2")
        if page2_start == -1:
            return categories

        page3_start = content.find("PAGE 3")
        if page3_start == -1:
            page3_start = len(content)

        page2_content = content[page2_start:page3_start]

        # Known category patterns and their expected actuals (from FFR files)
        # We use more targeted patterns because space-separated thousands make generic parsing difficult
        category_patterns = [
            # GP1 format: "Total Meetings 37 200.00 10 300.30 0.00 10 300.30 -26 899.70"
            (r'Total Meetings\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'meetings'),
            (r'^Meetings\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'meetings'),
            (r'Total Schools\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'training_schools'),
            (r'Training Schools\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'training_schools'),
            (r'Total STSM\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'stsm'),
            (r'Short-Term Scientific Mission\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'stsm'),
            (r'Total ITC Conference Grants\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'itc_conference'),
            (r'ITC Conference\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'itc_conference'),
            (r'Total Virtual Networking Tool\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'virtual_mobility'),
            (r'Virtual Mobility\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'virtual_mobility'),
            (r'Virtual Networking Support\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'virtual_networking_support'),
            (r'Total Action Dissemination\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'dissemination'),
            (r'Dissemination and Communication Products\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'dissemination'),
            (r'Dissemination Conference\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'dissemination_conference'),
            (r'Total OERSA\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'oersa'),
            (r'^OERSA\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'oersa'),
            (r'FSAC \(max 15%\)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'fsac'),
            (r'Total Networking expenditure\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'total_networking'),
            (r'Eligible Networking expenditure\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'eligible_networking'),
            (r'Total eligible expenditure\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+([\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)', 'total_eligible'),
        ]

        for pattern, cat_name in category_patterns:
            if cat_name in categories:
                continue  # Skip if already found

            match = re.search(pattern, page2_content, re.MULTILINE | re.IGNORECASE)
            if match:
                categories[cat_name] = CategoryData(
                    name=cat_name,
                    budget=parse_eur_amount(match.group(1)),
                    actuals=parse_eur_amount(match.group(2)),
                    accruals=parse_eur_amount(match.group(3)),
                    total=parse_eur_amount(match.group(4)),
                    delta=parse_eur_amount(match.group(5))
                )

        return categories

    def _extract_stsms(self, content: str) -> List[STSMRecord]:
        """Extract individual STSM records."""
        stsms = []

        # Find STSM section - try multiple headers
        # GP1: "Short Term Scientific Mission (STSM) Expenditure"
        # GP3/GP4/GP5: "Short-Term Scientific Mission Grant Expenditure"
        stsm_start = content.find("Short-Term Scientific Mission Grant Expenditure")
        if stsm_start == -1:
            stsm_start = content.find("Short Term Scientific Mission (STSM) Expenditure")
        if stsm_start == -1:
            stsm_start = content.find("Short Term Scientific Mission")
        if stsm_start == -1:
            stsm_start = content.find("Short-Term Scientific Mission")
        if stsm_start == -1:
            return stsms

        # Find the end of STSM section - look for the next section marker
        stsm_end = content.find("Virtual Mobility Grant Expenditure", stsm_start)
        if stsm_end == -1:
            stsm_end = content.find("Virtual Networking", stsm_start)
        if stsm_end == -1:
            stsm_end = content.find("ITC Conference", stsm_start + 100)
        if stsm_end == -1:
            stsm_end = content.find("PAGE", stsm_start + 100)
        if stsm_end == -1:
            stsm_end = len(content)

        stsm_section = content[stsm_start:stsm_end]

        # Pattern 1: GP1 format with YES/NO prepayment
        # "1 Dr Stjepan Picek Y HR NL 11/01/2021 26/01/2021 16 NO 1 520.00"
        stsm_pattern_gp1 = r'^(\d+)\s+(.+?)\s+([YN])\s+([A-Z]{2})\s+([A-Z]{2})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(\d+)\s+(YES|NO)\s+([\d\s,\.]+)\s*$'

        # Pattern 2: GP3/GP4/GP5 format without prepayment, column order is YRI Host Home
        # "1 Pele, Daniel Traian NO DE RO 26/09/2022 04/10/2022 10 1 800.00"
        stsm_pattern_gp3 = r'^(\d+)\s+(.+?)\s+(YES|NO)\s+([A-Z]{2})\s+([A-Z]{2})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(\d+)\s+([\d\s,\.]+)\s*$'

        for line in stsm_section.split('\n'):
            line = line.strip()

            # Try GP1 format first
            match = re.match(stsm_pattern_gp1, line)
            if match:
                stsms.append(STSMRecord(
                    index=int(match.group(1)),
                    grantee_name=match.group(2).strip(),
                    eci=match.group(3),
                    home_country=match.group(4),
                    host_country=match.group(5),
                    start_date=match.group(6),
                    end_date=match.group(7),
                    days=int(match.group(8)),
                    prepayment=match.group(9),
                    amount=parse_eur_amount(match.group(10))
                ))
                continue

            # Try GP3/GP4/GP5 format (YRI column is YES/NO, Host before Home)
            match = re.match(stsm_pattern_gp3, line)
            if match:
                # Note: In GP3/GP4, the column order is Host, Home (reversed)
                stsms.append(STSMRecord(
                    index=int(match.group(1)),
                    grantee_name=match.group(2).strip(),
                    eci='Y' if match.group(3) == 'YES' else 'N',
                    home_country=match.group(5),  # Home is second
                    host_country=match.group(4),  # Host is first
                    start_date=match.group(6),
                    end_date=match.group(7),
                    days=int(match.group(8)),
                    prepayment='N/A',  # Not available in this format
                    amount=parse_eur_amount(match.group(9))
                ))

        return stsms

    def _extract_meetings(self, content: str) -> List[MeetingRecord]:
        """Extract individual meeting records with participant details."""
        meetings = []

        # Find meetings section
        meetings_start = content.find("Meetings Expenditure")
        if meetings_start == -1:
            return meetings

        # Extract basic meeting list first
        meeting_section_end = content.find("Meeting 1", meetings_start)
        if meeting_section_end == -1:
            meeting_section_end = len(content)

        meeting_list_section = content[meetings_start:meeting_section_end]

        # Pattern for meeting list entries - handles space-separated amounts
        # Format: "index location / country type, actuals accruals total"
        # Examples:
        #   "1 online / Switzerland Management Committee, 0.00 0.00 0.00"
        #   "1 Skopje / North Macedonia Working Group, 4 271.19 0.00 4 271.19"
        #   "1 Cluj-Napoca / Romania Core Group, Working Group, 14 651.21 0.00 14 651.21"
        #
        # Improved pattern: capture index, location+type, then parse amounts from end
        # Match: index, everything before amounts, then 3 amounts at end
        meeting_line_pattern = r'^(\d+)\s+(.+?)\s+(-?[\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)\s+(-?[\d\s]+\.?\d*)\s*$'

        for line in meeting_list_section.split('\n'):
            line = line.strip()
            match = re.match(meeting_line_pattern, line)
            if match:
                # Parse the description to extract location and type
                description = match.group(2).strip()
                # Split on last comma before amounts
                if ',' in description:
                    # Find the location/country (contains /)
                    parts = description.split('/')
                    if len(parts) >= 2:
                        location = parts[0].strip() + ' / ' + parts[1].split()[0]
                        # Meeting type is the rest
                        type_start = len(parts[0]) + len(parts[1].split()[0]) + 4
                        meeting_type = description[type_start:].strip().rstrip(',')
                    else:
                        location = description
                        meeting_type = ""
                else:
                    location = description
                    meeting_type = ""

                meetings.append(MeetingRecord(
                    index=int(match.group(1)),
                    location=location,
                    meeting_type=meeting_type,
                    title="",  # Will be filled from detailed section
                    start_date="",
                    end_date="",
                    participants=0,
                    reimbursed_participants=0,
                    actuals=parse_eur_amount(match.group(3)),
                    accruals=parse_eur_amount(match.group(4)),
                    total=parse_eur_amount(match.group(5))
                ))

        # Now parse detailed meeting sections
        meeting_details = self._extract_meeting_details(content)
        for meeting in meetings:
            if meeting.index in meeting_details:
                details = meeting_details[meeting.index]
                meeting.title = details.get('title', '')
                meeting.start_date = details.get('start_date', '')
                meeting.end_date = details.get('end_date', '')
                meeting.participants = details.get('participants', 0)
                meeting.reimbursed_participants = details.get('reimbursed_participants', 0)
                meeting.participant_details = details.get('participant_details', [])

        return meetings

    def _extract_meeting_details(self, content: str) -> Dict[int, Dict]:
        """Extract detailed meeting information."""
        details = {}

        # Find each "Meeting N" section
        meeting_pattern = r'Meeting\s+(\d+)\s*\n'
        matches = list(re.finditer(meeting_pattern, content))

        for i, match in enumerate(matches):
            meeting_num = int(match.group(1))
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content)

            section = content[start_pos:end_pos]

            # Extract meeting details
            info = {'participants_list': []}

            # Start date
            start_match = re.search(r'Start date\s+(\d{2}/\d{2}/\d{4})', section)
            if start_match:
                info['start_date'] = start_match.group(1)

            # End date
            end_match = re.search(r'End date\s+(\d{2}/\d{2}/\d{4})', section)
            if end_match:
                info['end_date'] = end_match.group(1)

            # Title
            title_match = re.search(r'Meeting title\s+(.+?)(?:\n|Meeting type)', section, re.DOTALL)
            if title_match:
                info['title'] = title_match.group(1).strip()

            # Total participants
            participants_match = re.search(r'Total number of participants\s+(\d+)', section)
            if participants_match:
                info['participants'] = int(participants_match.group(1))

            # Reimbursed participants
            reimbursed_match = re.search(r'Total number of reimbursed participants\s+(\d+)', section)
            if reimbursed_match:
                info['reimbursed_participants'] = int(reimbursed_match.group(1))

            # Participant reimbursement details
            info['participant_details'] = self._extract_participant_reimbursements(section)

            details[meeting_num] = info

        return details

    def _extract_participant_reimbursements(self, section: str) -> List[Dict]:
        """Extract participant reimbursement details from a meeting section."""
        participants = []

        # Find "List of reimbursed participants" section
        list_start = section.find("List of reimbursed participants")
        if list_start == -1:
            return participants

        list_section = section[list_start:]

        # Find end (Sub-total or next section)
        list_end = list_section.find("Sub-total")
        if list_end == -1:
            list_end = list_section.find("Justification")
        if list_end == -1:
            list_end = len(list_section)

        participant_text = list_section[:list_end]

        # Pattern for participant lines
        # "1 Abrol, Manmeet IE 231.94 617.10 0.00 849.04"
        participant_pattern = r'^(\d+)\s+(.+?)\s+([A-Z]{2})\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s+([\d\s,\.]+)\s*$'

        for line in participant_text.split('\n'):
            line = line.strip()
            match = re.match(participant_pattern, line)
            if match:
                participants.append({
                    'index': int(match.group(1)),
                    'name': match.group(2).strip(),
                    'country': match.group(3),
                    'travel_allowance': parse_eur_amount(match.group(4)),
                    'daily_allowance': parse_eur_amount(match.group(5)),
                    'other_expenses': parse_eur_amount(match.group(6)),
                    'total': parse_eur_amount(match.group(7))
                })

        return participants

    def _extract_vm(self, content: str) -> List[VMRecord]:
        """Extract Virtual Mobility grant records."""
        vm_grants = []

        # Find VM section
        vm_start = content.find("Virtual Mobility Grant")
        if vm_start == -1:
            vm_start = content.find("Virtual Networking")
        if vm_start == -1:
            return vm_grants

        vm_end = content.find("PAGE", vm_start + 100)
        if vm_end == -1:
            vm_end = len(content)

        vm_section = content[vm_start:vm_end]

        # Pattern for VM grant lines
        vm_pattern = r'^(\d+)\s+(.+?)\s+([YN])\s+([A-Z]{2})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(\d+)\s+([\d\s,\.]+)\s*$'

        for line in vm_section.split('\n'):
            line = line.strip()
            match = re.match(vm_pattern, line)
            if match:
                vm_grants.append(VMRecord(
                    index=int(match.group(1)),
                    grantee_name=match.group(2).strip(),
                    eci=match.group(3),
                    country=match.group(4),
                    start_date=match.group(5),
                    end_date=match.group(6),
                    days=int(match.group(7)),
                    amount=parse_eur_amount(match.group(8))
                ))

        return vm_grants

    def get_category_total(self, gp: int, category: str) -> Decimal:
        """
        Get actual expenditure for a category in a grant period.

        Args:
            gp: Grant period (1-5)
            category: Category name (normalized)

        Returns:
            Actual expenditure amount
        """
        data = self.parse_grant_period(gp)
        if category in data.categories:
            return data.categories[category].actuals
        return Decimal("0.00")

    def get_grand_total(self, gp: int) -> Decimal:
        """
        Get total eligible expenditure for a grant period.

        Args:
            gp: Grant period (1-5)

        Returns:
            Total eligible expenditure
        """
        data = self.parse_grant_period(gp)
        return data.total_eligible
