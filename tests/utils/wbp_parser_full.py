"""
WBP Full Parser - Complete extraction of Work and Budget Plan data.

This parser extracts ALL available data from WBP text files, including:
- Budget summary
- Meeting details
- Training school details
- GAPG (Grant Period Goals)
- MoU Objectives
- And more...
"""

import re
from pathlib import Path
from datetime import date
from decimal import Decimal
from typing import Optional
from dataclasses import asdict

from .wbp_models import (
    ActionProfile, WorkingGroup, MoUObjective, Deliverable,
    GrantPeriodGoal, BudgetSummary, MeetingPlan, TrainingSchoolPlan,
    STSMPlan, VirtualMobilityPlan, ConferencePresentationPlan,
    DisseminationProduct, OERSAItem, WBPFullExtraction
)
from .wbp_patterns import (
    TOTAL_GRANT, DATE_PATTERN, BUDGET_MEETINGS, BUDGET_TRAINING_SCHOOLS,
    BUDGET_MOBILITY, BUDGET_CONFERENCE_PRESENTATIONS, BUDGET_DISSEMINATION,
    BUDGET_OERSA, BUDGET_TOTAL_SCIENCE, BUDGET_FSAC, BUDGET_STSM_OLD,
    BUDGET_ITC_OLD, MEETING_COST, PAGE_BOUNDARY, parse_eur_amount, parse_date
)


WBP_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")

WBP_FILES = {
    1: "WBP-AGA-CA19130-1_13682.txt",
    2: "WBP-AGA-CA19130-2_14713.txt",
    3: "WBP-AGA-CA19130-3_14714.txt",
    4: "WBP-AGA-CA19130-4_15816.txt",
    5: "WBP-AGA-CA19130-5_16959.txt",
}

# Grant period dates (hardcoded as reference)
GP_DATES = {
    1: (date(2020, 11, 1), date(2021, 10, 31)),
    2: (date(2021, 11, 1), date(2022, 5, 31)),
    3: (date(2022, 6, 1), date(2022, 10, 31)),
    4: (date(2022, 11, 1), date(2023, 10, 31)),
    5: (date(2023, 11, 1), date(2024, 9, 13)),
}


class WBPParserFull:
    """Full WBP Parser for extracting all data from WBP text files."""

    def __init__(self, gp: int):
        """
        Initialize parser for a specific grant period.

        Args:
            gp: Grant period number (1-5)
        """
        if gp not in WBP_FILES:
            raise ValueError(f"Invalid grant period: {gp}. Must be 1-5.")

        self.gp = gp
        self.filepath = WBP_DIR / WBP_FILES[gp]
        self.content = ""
        self._load_content()

    def _load_content(self):
        """Load WBP text file content."""
        self.content = self.filepath.read_text(encoding="utf-8")

    def extract_total_grant(self) -> Decimal:
        """Extract Total Grant amount from WBP."""
        match = TOTAL_GRANT.search(self.content)
        if match:
            return Decimal(str(parse_eur_amount(match.group(1))))
        return Decimal("0")

    def extract_budget_summary(self) -> BudgetSummary:
        """Extract budget summary from Page 7."""
        # Find the budget section - starts with "Work and Budget Plan Summary"
        # or "A. COST Networking Tools"
        budget_start = self.content.find("A. COST Networking Tools")
        if budget_start == -1:
            budget_start = self.content.find("Work and Budget Plan Summary")
        if budget_start == -1:
            budget_start = self.content.find("(1) Meetings")
        if budget_start == -1:
            budget_start = 0

        # Budget section extends to "Total Grant" + a bit more
        budget_end = self.content.find("PAGE 8", budget_start)
        if budget_end == -1:
            budget_end = budget_start + 3000

        budget_section = self.content[budget_start:budget_end]

        def get_amount(pattern) -> Decimal:
            match = pattern.search(budget_section)
            if match:
                return Decimal(str(parse_eur_amount(match.group(1))))
            return Decimal("0")

        # Different patterns for GP1-3 vs GP4-5
        if self.gp <= 3:
            # Old format: separate STSM and ITC
            stsm = get_amount(BUDGET_STSM_OLD)
            itc = get_amount(BUDGET_ITC_OLD)
            mobility = stsm  # For compatibility
            conf_pres = itc
        else:
            # New format: combined Mobility and Conference Presentations
            mobility = get_amount(BUDGET_MOBILITY)
            conf_pres = get_amount(BUDGET_CONFERENCE_PRESENTATIONS)
            stsm = None
            itc = None

        return BudgetSummary(
            grant_period=self.gp,
            total_grant=self.extract_total_grant(),
            meetings=get_amount(BUDGET_MEETINGS),
            training_schools=get_amount(BUDGET_TRAINING_SCHOOLS),
            mobility=mobility,
            conference_presentations=conf_pres,
            dissemination=get_amount(BUDGET_DISSEMINATION),
            oersa=get_amount(BUDGET_OERSA),
            total_science=get_amount(BUDGET_TOTAL_SCIENCE),
            fsac=get_amount(BUDGET_FSAC),
            stsm=stsm,
            itc_grants=itc,
        )

    def extract_meetings_overview(self) -> list[dict]:
        """
        Extract meetings from the Overview table on Pages 8-9.
        Returns list of meeting dictionaries with basic info.
        """
        meetings = []

        # Find Meetings Overview section
        overview_start = self.content.find("Meetings\nOverview")
        if overview_start == -1:
            overview_start = self.content.find("Meetings")

        if overview_start == -1:
            return meetings

        # Find end of overview (before Details)
        details_start = self.content.find("Details", overview_start)
        if details_start == -1:
            details_start = overview_start + 5000

        overview = self.content[overview_start:details_start]

        # Look for lines ending with EUR amounts (meeting costs)
        lines = overview.split('\n')
        current_meeting = {}

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Check for cost at end of line
            cost_match = re.search(r'([\d,\.]+)\s*$', line)
            if cost_match:
                cost = parse_eur_amount(cost_match.group(1))
                if cost > 100:  # Likely a meeting cost
                    current_meeting['cost'] = cost
                    if current_meeting:
                        meetings.append(current_meeting)
                        current_meeting = {}
                    continue

            # Check for date patterns (meeting dates)
            date_match = re.search(r'(\d{2}/\d{2}/\d{4})\s*[-–]?\s*(\d{2}/\d{2}/\d{4})?', line)
            if date_match:
                current_meeting['start_date'] = date_match.group(1)
                current_meeting['end_date'] = date_match.group(2) or date_match.group(1)
                continue

            # Check for location and ITC status
            loc_match = re.search(r'([A-Za-z][\w\s\-]+?)\s+(Yes|No)\s*$', line)
            if loc_match:
                current_meeting['location'] = loc_match.group(1).strip()
                current_meeting['itc'] = loc_match.group(2) == 'Yes'
                continue

        return meetings

    def extract_meetings_details(self) -> list[MeetingPlan]:
        """
        Extract detailed meeting information from Details section.
        Returns list of MeetingPlan objects.
        """
        meetings = []

        # Find Details section (after meetings overview)
        # First find "Details" that comes after "Meetings" section
        meetings_idx = self.content.find("Meetings\n")
        if meetings_idx == -1:
            meetings_idx = 0

        details_start = self.content.find("Details\n", meetings_idx)
        if details_start == -1:
            details_start = self.content.find("Title of the Meeting", meetings_idx)

        if details_start == -1:
            return meetings

        # Find end of meetings section - look for Training School section
        training_start = self.content.find("Training Schools\n", details_start)
        if training_start == -1:
            training_start = self.content.find("Training School\n", details_start)
        if training_start == -1:
            training_start = len(self.content)

        details_section = self.content[details_start:training_start]

        # Split by "Title of the Meeting" to get individual meeting blocks
        meeting_blocks = re.split(r'Title of the Meeting\s+', details_section)

        # Process blocks (skip first which is before first meeting)
        for i, block in enumerate(meeting_blocks[1:], start=1):
            meeting = self._parse_meeting_block_new(i, block)
            if meeting:
                meetings.append(meeting)

        return meetings

    def _parse_meeting_block_new(self, num: int, block: str) -> Optional[MeetingPlan]:
        """Parse a single meeting detail block in new WBP format."""
        # Title is the first line (everything before newline)
        lines = block.split('\n')
        title = lines[0].strip() if lines else f"Meeting {num}"

        # Extract meeting type - "Meeting Type(s) ..."
        type_match = re.search(r'Meeting Type\(s\)\s+(.+)', block, re.IGNORECASE)
        meeting_type = type_match.group(1).strip() if type_match else "Unknown"

        # Extract location and ITC status - "Location ... ITC Yes/No"
        loc_match = re.search(r'Location\s+(.+?)\s+ITC\s+(Yes|No)', block, re.IGNORECASE)
        if loc_match:
            location_full = loc_match.group(1).strip()
            itc_status = loc_match.group(2).lower() == 'yes'
        else:
            location_full = "Unknown"
            itc_status = False

        # Parse location (City) and country from "City (Country)" format
        loc_country_match = re.match(r'(.+?)\s*\(([^)]+)\)', location_full)
        if loc_country_match:
            location = loc_country_match.group(1).strip()
            country = loc_country_match.group(2).strip()
        else:
            location = location_full
            country = "Unknown"

        # Extract dates - "Start Date YYYY-MM-DD ... End Date YYYY-MM-DD"
        start_match = re.search(r'Start Date\s+(\d{4}-\d{2}-\d{2})', block, re.IGNORECASE)
        end_match = re.search(r'End Date\s+(\d{4}-\d{2}-\d{2})', block, re.IGNORECASE)

        if start_match:
            parts = start_match.group(1).split('-')
            start_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
        else:
            # Try DD/MM/YYYY format
            alt_match = re.search(r'(\d{2}/\d{2}/\d{4})', block)
            if alt_match:
                start_date = parse_date(alt_match.group(1))
            else:
                return None

        if end_match:
            parts = end_match.group(1).split('-')
            end_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
        else:
            end_date = start_date

        # Extract participants
        part_match = re.search(r'Total number of expected\s+(\d+)', block)
        reimb_match = re.search(r'Number of participants expected.*?(\d+)', block, re.DOTALL)

        expected_participants = int(part_match.group(1)) if part_match else 0
        expected_reimbursed = int(reimb_match.group(1)) if reimb_match else 0

        # Extract cost - "Total cost of the meeting (EUR)" or "Total Cost"
        cost_match = re.search(r'Total cost of the meeting\s*\(EUR\)\s*([\d,\.\s]+)', block, re.IGNORECASE)
        if not cost_match:
            cost_match = re.search(r'Total Cost.*?([\d,\.\s]+)', block, re.IGNORECASE)
        if not cost_match:
            # Look for last EUR amount on its own line
            cost_match = re.search(r'([\d,]+\.\d{2})\s*$', block, re.MULTILINE)

        planned_cost = Decimal(str(parse_eur_amount(cost_match.group(1)))) if cost_match else Decimal("0")

        # Extract description
        desc_match = re.search(r'Description\s+(.+?)(?=Output\(s\)|Location|$)', block, re.DOTALL | re.IGNORECASE)
        description = desc_match.group(1).strip() if desc_match else None

        # Extract outputs
        output_match = re.search(r'Output\(s\)\s+(.+?)(?=Location|$)', block, re.DOTALL | re.IGNORECASE)
        outputs = output_match.group(1).strip() if output_match else None

        return MeetingPlan(
            meeting_number=num,
            title=title,
            meeting_type=meeting_type,
            start_date=start_date,
            end_date=end_date,
            location=location,
            country=country,
            itc_country=itc_status,
            planned_cost=planned_cost,
            expected_participants=expected_participants,
            expected_reimbursed=expected_reimbursed,
            grant_period=self.gp,
            description=description,
            expected_outputs=outputs,
        )

    def _parse_meeting_block(self, num: int, block: str) -> Optional[MeetingPlan]:
        """Parse a single meeting detail block (legacy format)."""
        # Extract title
        title_match = re.search(r'Meeting title\s+(.+)', block)
        title = title_match.group(1).strip() if title_match else f"Meeting {num}"

        # Extract type
        type_match = re.search(r'Meeting type\s+(.+)', block)
        meeting_type = type_match.group(1).strip() if type_match else "Unknown"

        # Extract dates
        start_match = re.search(r'Start date\s+(\d{2}/\d{2}/\d{4})', block)
        end_match = re.search(r'End date\s+(\d{2}/\d{2}/\d{4})', block)

        start_date = parse_date(start_match.group(1)) if start_match else None
        end_date = parse_date(end_match.group(1)) if end_match else start_date

        if not start_date:
            return None

        # Extract location
        loc_match = re.search(r'Meeting location\s+(.+)', block)
        location_full = loc_match.group(1).strip() if loc_match else "Unknown"

        # Parse location/country
        loc_parts = location_full.split('/')
        location = loc_parts[0].strip() if loc_parts else location_full
        country = loc_parts[-1].strip() if len(loc_parts) > 1 else "Unknown"

        # Extract participants
        part_match = re.search(r'Total number of expected\s+(\d+)', block)
        reimb_match = re.search(r'Number of participants expected.*?(\d+)', block, re.DOTALL)

        expected_participants = int(part_match.group(1)) if part_match else 0
        expected_reimbursed = int(reimb_match.group(1)) if reimb_match else 0

        # Extract cost - look for Total Cost (EUR) in the block
        cost_match = re.search(r'Total Cost.*?([\d,\s\.]+)', block)
        if not cost_match:
            cost_match = re.search(r'([\d,]+\.\d{2})\s*$', block, re.MULTILINE)

        planned_cost = Decimal(str(parse_eur_amount(cost_match.group(1)))) if cost_match else Decimal("0")

        # Determine ITC status based on country code
        ITC_COUNTRIES = {
            'Albania', 'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus',
            'Czech Republic', 'Czechia', 'Estonia', 'Greece', 'Hungary', 'Latvia',
            'Lithuania', 'Malta', 'Moldova', 'Montenegro', 'North Macedonia',
            'Poland', 'Portugal', 'Romania', 'Serbia', 'Slovakia', 'Slovenia',
            'Turkey', 'Türkiye', 'Ukraine'
        }
        itc_country = country in ITC_COUNTRIES

        return MeetingPlan(
            meeting_number=num,
            title=title,
            meeting_type=meeting_type,
            start_date=start_date,
            end_date=end_date,
            location=location,
            country=country,
            itc_country=itc_country,
            planned_cost=planned_cost,
            expected_participants=expected_participants,
            expected_reimbursed=expected_reimbursed,
            grant_period=self.gp,
        )

    def extract_training_schools(self) -> list[TrainingSchoolPlan]:
        """Extract training school information."""
        schools = []

        # Find Training Schools section
        ts_start = self.content.find("Training Schools\n")
        if ts_start == -1:
            ts_start = self.content.find("Training School\n")
        if ts_start == -1:
            return schools

        # Find end of training school section - look for mobility/STSM section
        next_section = self.content.find("Short-Term", ts_start + 100)
        if next_section == -1:
            next_section = self.content.find("Short Term", ts_start + 100)
        if next_section == -1:
            next_section = self.content.find("Mobility\n", ts_start + 100)
        if next_section == -1:
            next_section = self.content.find("STSM", ts_start + 100)
        if next_section == -1:
            next_section = ts_start + 15000

        ts_section = self.content[ts_start:next_section]

        # Split by "Title of the Training" followed by title text (after Details section)
        # The format is "Title of the Training <actual title>\nSchool" due to PDF word wrap
        details_idx = ts_section.find("Details\n")
        if details_idx != -1:
            ts_section = ts_section[details_idx:]

        # Pattern matches "Title of the Training " followed by the actual title
        # Note: "School" appears on next line due to word wrap from "Training School"
        school_blocks = re.split(r'Title of the Training\s+', ts_section)

        # Process blocks (skip first which is before first school)
        for i, block in enumerate(school_blocks[1:], start=1):
            school = self._parse_training_school_block_new(i, block)
            if school:
                schools.append(school)

        return schools

    def _parse_training_school_block_new(self, num: int, block: str) -> Optional[TrainingSchoolPlan]:
        """Parse a single training school detail block in new WBP format."""
        # Title is the first line(s) - may include wrapped "School" on next line
        lines = block.split('\n')
        title = lines[0].strip() if lines else f"Training School {num}"

        # If next line is just "School", that's part of "Training School" wrap - skip it
        # and any following line fragments of the title
        title_parts = [title]
        idx = 1
        while idx < len(lines) and lines[idx].strip() and not lines[idx].strip().startswith('Grant Period'):
            line = lines[idx].strip()
            if line == 'School':
                idx += 1
                continue
            title_parts.append(line)
            idx += 1
            # Limit to avoid going too far
            if idx > 4:
                break
        title = ' '.join(title_parts)

        # Extract location and ITC status - "Location ... ITC Yes/No"
        loc_match = re.search(r'Location\s+(.+?)\s+ITC\s+(Yes|No)', block, re.IGNORECASE)
        if loc_match:
            location_full = loc_match.group(1).strip()
            itc_status = loc_match.group(2).lower() == 'yes'
        else:
            location_full = "Unknown"
            itc_status = False

        # Parse location (City) and country from "City (Country)" format
        loc_country_match = re.match(r'(.+?)\s*\(([^)]+)\)', location_full)
        if loc_country_match:
            location = loc_country_match.group(1).strip()
            country = loc_country_match.group(2).strip()
        else:
            location = location_full
            country = "Unknown"

        # Extract dates - "Start Date YYYY-MM-DD ... End Date YYYY-MM-DD"
        start_match = re.search(r'Start Date\s+(\d{4}-\d{2}-\d{2})', block, re.IGNORECASE)
        end_match = re.search(r'End Date\s+(\d{4}-\d{2}-\d{2})', block, re.IGNORECASE)

        if start_match:
            parts = start_match.group(1).split('-')
            start_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
        else:
            # Try DD/MM/YYYY format
            alt_match = re.search(r'(\d{2}/\d{2}/\d{4})', block)
            if alt_match:
                start_date = parse_date(alt_match.group(1))
            else:
                return None

        if end_match:
            parts = end_match.group(1).split('-')
            end_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
        else:
            end_date = start_date

        # Extract trainers/trainees from table
        # "Total number of expected trainers/trainees 10 10"
        trainers_match = re.search(r'Total number of expected trainers/trainees\s+(\d+)\s+(\d+)', block)
        if trainers_match:
            expected_trainers = int(trainers_match.group(1))
            expected_trainees = int(trainers_match.group(2))
        else:
            expected_trainers = 0
            expected_trainees = 0

        # Extract cost - "Total cost of the Training School (EUR)"
        cost_match = re.search(r'Total cost of the Training\s*School\s*\(EUR\)\s*([\d,\.\s]+)', block, re.IGNORECASE)
        if not cost_match:
            cost_match = re.search(r'Total Cost.*?([\d,\.\s]+)', block, re.IGNORECASE)
        if not cost_match:
            cost_match = re.search(r'([\d,]+\.\d{2})\s*$', block, re.MULTILINE)

        planned_cost = Decimal(str(parse_eur_amount(cost_match.group(1)))) if cost_match else Decimal("0")

        # Try to find institution from description
        institution = ""

        # Extract description
        desc_match = re.search(r'Description\s+(.+?)(?=Output\(s\)|Location|$)', block, re.DOTALL | re.IGNORECASE)
        description = desc_match.group(1).strip() if desc_match else None

        # Extract topics
        topics_match = re.search(r'Output\(s\)\s+(.+?)(?=Location|$)', block, re.DOTALL | re.IGNORECASE)
        topics = topics_match.group(1).strip() if topics_match else None

        return TrainingSchoolPlan(
            school_number=num,
            title=title,
            institution=institution,
            location=location,
            country=country,
            start_date=start_date,
            end_date=end_date,
            planned_cost=planned_cost,
            expected_trainers=expected_trainers,
            expected_trainees=expected_trainees,
            grant_period=self.gp,
            description=description,
            topics=topics,
        )

    def _parse_training_school_block(self, num: int, block: str) -> Optional[TrainingSchoolPlan]:
        """Parse a single training school detail block (legacy format)."""
        # Extract title
        title_match = re.search(r'Training School title\s+(.+)', block)
        title = title_match.group(1).strip() if title_match else f"Training School {num}"

        # Extract location
        loc_match = re.search(r'Training School location\s+(.+)', block)
        location_full = loc_match.group(1).strip() if loc_match else "Unknown"

        # Parse institution/location/country
        loc_parts = location_full.split('/')
        institution = loc_parts[0].strip() if loc_parts else ""
        location = loc_parts[1].strip() if len(loc_parts) > 1 else location_full
        country = loc_parts[-1].strip() if len(loc_parts) > 2 else "Unknown"

        # Extract dates
        start_match = re.search(r'Start date\s+(\d{2}/\d{2}/\d{4})', block)
        end_match = re.search(r'End date\s+(\d{2}/\d{2}/\d{4})', block)

        start_date = parse_date(start_match.group(1)) if start_match else None
        end_date = parse_date(end_match.group(1)) if end_match else start_date

        if not start_date:
            return None

        # Extract trainers/trainees
        trainers_match = re.search(r'(?:expected|number of)\s*trainers?\s*[:\-]?\s*(\d+)', block, re.IGNORECASE)
        trainees_match = re.search(r'(?:expected|number of)\s*trainees?\s*[:\-]?\s*(\d+)', block, re.IGNORECASE)

        expected_trainers = int(trainers_match.group(1)) if trainers_match else 0
        expected_trainees = int(trainees_match.group(1)) if trainees_match else 0

        # Extract cost
        cost_match = re.search(r'Total Cost.*?([\d,\s\.]+)', block)
        planned_cost = Decimal(str(parse_eur_amount(cost_match.group(1)))) if cost_match else Decimal("0")

        return TrainingSchoolPlan(
            school_number=num,
            title=title,
            institution=institution,
            location=location,
            country=country,
            start_date=start_date,
            end_date=end_date,
            planned_cost=planned_cost,
            expected_trainers=expected_trainers,
            expected_trainees=expected_trainees,
            grant_period=self.gp,
        )

    def parse_full(self) -> WBPFullExtraction:
        """
        Parse the complete WBP document and return all extracted data.
        """
        start_date, end_date = GP_DATES[self.gp]

        # Create minimal action profile (would need more parsing for complete)
        action_profile = ActionProfile(
            action_code="CA19130",
            action_title="Fintech and Artificial Intelligence in Finance",
            chair_name="Joerg Osterrieder",
            chair_institution="ZHAW",
            chair_country="Switzerland",
            grant_period=self.gp,
            start_date=start_date,
            end_date=end_date,
            total_grant=self.extract_total_grant(),
            participating_cost_countries=0,
            participating_near_neighbour_countries=0,
            participating_international_partner_countries=0,
        )

        return WBPFullExtraction(
            grant_period=self.gp,
            action_profile=action_profile,
            working_groups=[],  # Would need additional parsing
            mou_objectives=[],  # Would need additional parsing
            deliverables=[],  # Would need additional parsing
            gapgs=[],  # Would need additional parsing
            budget_summary=self.extract_budget_summary(),
            meetings=self.extract_meetings_details(),
            training_schools=self.extract_training_schools(),
            source_file=WBP_FILES[self.gp],
        )

    def to_dict(self) -> dict:
        """Convert full extraction to dictionary for JSON serialization."""
        extraction = self.parse_full()
        return asdict(extraction)


def extract_all_wbp() -> dict[int, WBPFullExtraction]:
    """Extract data from all WBP files."""
    results = {}
    for gp in range(1, 6):
        parser = WBPParserFull(gp)
        results[gp] = parser.parse_full()
    return results


if __name__ == "__main__":
    # Test extraction
    for gp in range(1, 6):
        print(f"\n{'='*60}")
        print(f"WBP GP{gp} Extraction")
        print(f"{'='*60}")

        parser = WBPParserFull(gp)

        # Budget summary
        budget = parser.extract_budget_summary()
        print(f"\nBudget Summary:")
        print(f"  Total Grant: {budget.total_grant:,.2f}")
        print(f"  Meetings: {budget.meetings:,.2f}")
        print(f"  Training Schools: {budget.training_schools:,.2f}")
        print(f"  Mobility: {budget.mobility:,.2f}")
        print(f"  Total Science: {budget.total_science:,.2f}")
        print(f"  FSAC: {budget.fsac:,.2f}")

        # Meetings
        meetings = parser.extract_meetings_details()
        print(f"\nMeetings: {len(meetings)} found")
        for m in meetings[:3]:
            print(f"  {m.meeting_number}. {m.title[:40]} - {m.location}")

        # Training schools
        schools = parser.extract_training_schools()
        print(f"\nTraining Schools: {len(schools)} found")
        for s in schools:
            print(f"  {s.school_number}. {s.title[:40]} - {s.location}")
