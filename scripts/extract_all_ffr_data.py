"""
Comprehensive FFR Data Extraction Script
Extracts ALL detailed data from COST Action CA19130 Final Financial Reports (FFR)

Outputs:
- meetings_participants.json - All meeting attendees with expense breakdown
- meetings_justifications.json - Travel expense justifications
- virtual_mobility_full.json - VM grants with complete titles
- itc_conference_grants.json - ITC conference grant recipients
- dissemination_grants.json - Dissemination conference grants
- training_school_attendees.json - TS trainers + trainees
- los_grants.json - Local Organiser Support
- stsm_full.json - Complete STSM data
- country_statistics_full.json - Detailed country analytics

Author: Claude Code
Date: 2026-01-02
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Paths
EXTRACTED_TEXT_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")
OUTPUT_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\COST-Fintech-AI-in-Finance\data")

# FFR files by grant period
FFR_FILES = {
    1: "AGA-CA19130-1-FFR_ID2193.txt",
    2: "AGA-CA19130-2-FFR_ID2346.txt",
    3: "AGA-CA19130-3-FFR_ID2998.txt",
    4: "AGA-CA19130-4-FFR_ID3993.txt",
    5: "AGA-CA19130-5-FFR_ID4828.txt",
}

# ITC Countries (Inclusiveness Target Countries)
ITC_COUNTRIES = {
    'AL', 'BA', 'BG', 'HR', 'CY', 'CZ', 'EE', 'EL', 'HU', 'LV',
    'LT', 'MT', 'MD', 'ME', 'MK', 'PL', 'PT', 'RO', 'RS', 'SK',
    'SI', 'TR', 'UA'
}


def parse_amount(amount_str):
    """Parse amount string with European number format (space thousands separator)"""
    if not amount_str:
        return 0.0
    # Remove spaces, replace comma with dot
    cleaned = amount_str.replace(' ', '').replace(',', '.')
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def read_ffr_file(grant_period):
    """Read FFR text file for a given grant period"""
    filepath = EXTRACTED_TEXT_DIR / FFR_FILES[grant_period]
    if not filepath.exists():
        print(f"Warning: FFR file not found for GP{grant_period}: {filepath}")
        return ""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def extract_meetings_with_participants(text, grant_period):
    """Extract all meetings with full participant lists"""
    meetings = []

    # Split by "Meeting X" headers
    meeting_sections = re.split(r'\nMeeting (\d+)\n', text)

    for i in range(1, len(meeting_sections), 2):
        if i + 1 >= len(meeting_sections):
            break

        meeting_num = int(meeting_sections[i])
        section = meeting_sections[i + 1]

        # Extract meeting metadata
        meeting = {
            'id': f"GP{grant_period}_M{meeting_num}",
            'grant_period': grant_period,
            'meeting_number': meeting_num,
        }

        # Start date
        match = re.search(r'Start date\s+(\d{2}/\d{2}/\d{4})', section)
        meeting['start_date'] = match.group(1) if match else None

        # End date
        match = re.search(r'End date\s+(\d{2}/\d{2}/\d{4})', section)
        meeting['end_date'] = match.group(1) if match else None

        # Duration
        match = re.search(r'Meeting duration \(days\)\s+(\d+)', section)
        meeting['duration_days'] = int(match.group(1)) if match else None

        # Location
        match = re.search(r'Meeting location\s+(.+?)(?:\n|$)', section)
        if match:
            loc = match.group(1).strip()
            meeting['location'] = loc
            # Extract country from location
            if '/' in loc:
                parts = loc.split('/')
                meeting['country'] = parts[-1].strip()
            else:
                meeting['country'] = loc

        # Title
        match = re.search(r'Meeting title\s+(.+?)(?:\n|$)', section)
        meeting['title'] = match.group(1).strip() if match else None

        # Type
        match = re.search(r'Meeting type\s+(.+?)(?:\n|$)', section)
        meeting['type'] = match.group(1).strip() if match else None

        # Total participants
        match = re.search(r'Total number of participants\s+(\d+)', section)
        meeting['total_participants'] = int(match.group(1)) if match else 0

        # Reimbursed participants
        match = re.search(r'Total number of reimbursed participants\s+(\d+)', section)
        meeting['reimbursed_count'] = int(match.group(1)) if match else 0

        # Extract participant list
        participants = []

        # Pattern: number name country travel_allowance daily_allowance other_expenses total
        # Example: 1 Abrol, Manmeet IE 231.94 617.10 0.00 849.04
        # Note: European format uses space as thousands separator: 1 200.00 = 1200.00
        # Use precise number pattern to avoid matching across columns
        # Number pattern: 1-3 digits, optional (space + 3 digits) for thousands, decimal + 2 digits
        euro_num = r'(\d{1,3}(?:\s\d{3})*[,\.]\d{2})'
        participant_pattern = rf'^(\d+)\s+([A-Za-z\u00C0-\u017F\s,\(\)\-\.\']+?)\s+([A-Z]{{2}})\s+{euro_num}\s+{euro_num}\s+{euro_num}\s+{euro_num}\s*$'

        for line in section.split('\n'):
            match = re.match(participant_pattern, line.strip())
            if match:
                name = match.group(2).strip()
                country = match.group(3)

                participant = {
                    'name': name,
                    'country': country,
                    'is_itc': country in ITC_COUNTRIES,
                    'travel_allowance': parse_amount(match.group(4)),
                    'daily_allowance': parse_amount(match.group(5)),
                    'other_expenses': parse_amount(match.group(6)),
                    'total': parse_amount(match.group(7)),
                }
                participants.append(participant)

        meeting['participants'] = participants

        # LOS Grant
        match = re.search(r'Local Organiser Support \(LOS\) Grant\s+Sub-total actual amounts - Paid\s+([\d\s,\.]+)', section)
        meeting['los_grant'] = parse_amount(match.group(1)) if match else 0.0

        # Calculate totals
        meeting['total_travel'] = sum(p['travel_allowance'] for p in participants)
        meeting['total_daily'] = sum(p['daily_allowance'] for p in participants)
        meeting['total_other'] = sum(p['other_expenses'] for p in participants)
        meeting['total_reimbursed'] = sum(p['total'] for p in participants)

        meetings.append(meeting)

    return meetings


def extract_justifications(text, grant_period):
    """Extract expense justifications from FFR"""
    justifications = []

    # Find justification sections
    pattern = r'Justification of other expenses\s*\n\s*List of reimbursed participants\s*\n(.*?)(?=\n(?:Meeting \d+|Training School \d+|Short-Term|Virtual Mobility|Dissemination|Inclusiveness|Local Organiser|Sub-total)|\Z)'

    matches = re.finditer(pattern, text, re.DOTALL)

    for match in matches:
        section = match.group(1)

        # Parse individual justifications
        # Pattern: number name (country)
        person_pattern = r'(\d+)\s+([A-Za-z\u00C0-\u017F\s,\(\)\-\.\']+?)\s+\(([A-Za-z\s]+)\)'

        for person_match in re.finditer(person_pattern, section):
            name = person_match.group(2).strip()
            country = person_match.group(3).strip()

            # Get the text after this match until next person or end
            start_pos = person_match.end()
            next_person = re.search(r'\n\d+\s+[A-Za-z]', section[start_pos:])
            if next_person:
                end_pos = start_pos + next_person.start()
            else:
                end_pos = len(section)

            detail_text = section[start_pos:end_pos]

            # Extract expense types and amounts
            expenses = []
            expense_pattern = r'(car|plane|train|bus|visa|taxi|other)\s+(.*?)\s+([\d\s,\.]+)\s*(?:\n|$)'
            for exp_match in re.finditer(expense_pattern, detail_text, re.IGNORECASE):
                expenses.append({
                    'type': exp_match.group(1).lower(),
                    'description': exp_match.group(2).strip()[:200],  # Truncate long descriptions
                    'amount': parse_amount(exp_match.group(3))
                })

            if expenses:
                justifications.append({
                    'name': name,
                    'country': country,
                    'grant_period': grant_period,
                    'expenses': expenses
                })

    return justifications


def extract_training_schools(text, grant_period):
    """Extract training school data with all participants"""
    schools = []

    # Split by "Training School X" headers
    ts_sections = re.split(r'\nTraining School (\d+)\n', text)

    for i in range(1, len(ts_sections), 2):
        if i + 1 >= len(ts_sections):
            break

        ts_num = int(ts_sections[i])
        section = ts_sections[i + 1]

        school = {
            'id': f"GP{grant_period}_TS{ts_num}",
            'grant_period': grant_period,
            'school_number': ts_num,
        }

        # Start date
        match = re.search(r'Start date\s+(\d{2}/\d{2}/\d{4})', section)
        school['start_date'] = match.group(1) if match else None

        # End date
        match = re.search(r'End date\s+(\d{2}/\d{2}/\d{4})', section)
        school['end_date'] = match.group(1) if match else None

        # Duration
        match = re.search(r'Training School duration \(days\)\s+(\d+)', section)
        school['duration_days'] = int(match.group(1)) if match else None

        # Location
        match = re.search(r'Training School location\s+(.+?)(?:\n|$)', section)
        if match:
            loc = match.group(1).strip()
            school['location'] = loc
            # Extract city and country
            if '/' in loc:
                parts = loc.split('/')
                school['city'] = parts[-2].strip() if len(parts) > 1 else loc
                school['country'] = parts[-1].strip()
            else:
                school['city'] = loc
                school['country'] = None

        # Title
        match = re.search(r'Training School title\s+(.+?)(?:\n|$)', section)
        school['title'] = match.group(1).strip() if match else None

        # Extract participants
        participants = []
        # Use precise European number pattern to avoid matching across columns
        euro_num = r'(\d{1,3}(?:\s\d{3})*[,\.]\d{2})'
        participant_pattern = rf'^(\d+)\s+([A-Za-z\u00C0-\u017F\s,\(\)\-\.\']+?)\s+([A-Z]{{2}})\s+{euro_num}\s+{euro_num}\s+{euro_num}\s+{euro_num}\s*$'

        for line in section.split('\n'):
            match = re.match(participant_pattern, line.strip())
            if match:
                name = match.group(2).strip()
                country = match.group(3)

                participant = {
                    'name': name,
                    'country': country,
                    'is_itc': country in ITC_COUNTRIES,
                    'travel_allowance': parse_amount(match.group(4)),
                    'daily_allowance': parse_amount(match.group(5)),
                    'other_expenses': parse_amount(match.group(6)),
                    'total': parse_amount(match.group(7)),
                }
                participants.append(participant)

        school['participants'] = participants
        school['participant_count'] = len(participants)

        # LOS Grant
        match = re.search(r'Local Organiser Support \(LOS\) Grant\s+Sub-total actual amounts - Paid\s+([\d\s,\.]+)', section)
        school['los_grant'] = parse_amount(match.group(1)) if match else 0.0

        # Calculate totals
        school['total_reimbursed'] = sum(p['total'] for p in participants)

        schools.append(school)

    return schools


def extract_stsm(text, grant_period):
    """Extract STSM (Short-Term Scientific Mission) data"""
    stsms = []

    # Find STSM section
    # GP1 format: "Short Term Scientific Mission (STSM) Expenditure"
    # GP3-5 format: "Short-Term Scientific Mission Grant Expenditure"

    stsm_section = re.search(
        r'Short-?Term Scientific Mission.*?Expenditure.*?(?:List of paid|Grantee name).*?(?=\n(?:Virtual Mobility|Dissemination|Inclusiveness|No Short-Term|\d+ of \d+))',
        text, re.DOTALL | re.IGNORECASE
    )

    if not stsm_section:
        return stsms

    section = stsm_section.group(0)

    # Pattern: number name YRI host home start_date end_date days amount
    # Example: 1 Coita, Ioana NO SK RO 06/04/2024 14/04/2024 10 1 997.00
    stsm_pattern = r'^(\d+)\s+([A-Za-z\u00C0-\u017F\s,\(\)\-\.\']+?)\s+(YES|NO|Y|N)\s+([A-Z]{2})\s+([A-Z]{2})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(\d+)\s+([\d\s,\.]+)\s*$'

    for line in section.split('\n'):
        match = re.match(stsm_pattern, line.strip())
        if match:
            yri_str = match.group(3).upper()
            yri = yri_str in ('YES', 'Y')

            stsm = {
                'id': f"GP{grant_period}_STSM{match.group(1)}",
                'grant_period': grant_period,
                'name': match.group(2).strip(),
                'yri': yri,
                'host_country': match.group(4),
                'home_country': match.group(5),
                'is_itc_home': match.group(5) in ITC_COUNTRIES,
                'is_itc_host': match.group(4) in ITC_COUNTRIES,
                'start_date': match.group(6),
                'end_date': match.group(7),
                'days': int(match.group(8)),
                'amount': parse_amount(match.group(9)),
            }
            stsms.append(stsm)

    return stsms


def extract_virtual_mobility(text, grant_period):
    """Extract Virtual Mobility grants with full titles"""
    vm_grants = []

    # Find VM section - different headers in different GPs
    vm_section = re.search(
        r'Virtual Mobility Grant Expenditure.*?(?:List of paid|Grantee name).*?(?=\n(?:Dissemination Conference|Inclusiveness Target|No Virtual Mobility|\d+ of \d+))',
        text, re.DOTALL | re.IGNORECASE
    )

    if not vm_section:
        return vm_grants

    section = vm_section.group(0)
    lines = section.split('\n')

    # Collect all VM entries with their multi-line titles
    # GP4 format: number name VM title country dates amount
    # GP5 format: number name YES/NO title country dates amount

    entries = []
    current_entry = None

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        # Skip header lines
        if re.match(r'^(Grantee|List of paid|Virtual Mobility|YRI|Type|Title|Home|Start|End|Total|Sub-total|No Virtual)', line_stripped, re.IGNORECASE):
            continue
        if 'EUR' in line_stripped and 'Total' not in line_stripped:
            continue

        # Check for new entry pattern - starts with number
        # GP4: "1 Wolfgang Härdle VM Bibvliometrics of cost members DE 30/01/2023 30/06/2023 1 500.00"
        # GP5: "1 Maria Iannario NO Advanced statistical methods... IT 01/02/2024 01/07/2024 1 500.00"

        # Pattern for line ending with: country dates amount
        entry_end_pattern = r'([A-Z]{2})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+([\d\s,\.]+)\s*$'
        end_match = re.search(entry_end_pattern, line_stripped)

        if end_match:
            # This line contains the end of an entry
            before_end = line_stripped[:end_match.start()].strip()

            # Check if this line starts a new entry (has number at start)
            new_entry_match = re.match(r'^(\d+)\s+(.+)', before_end)

            if new_entry_match:
                # Save previous entry if exists
                if current_entry:
                    entries.append(current_entry)

                entry_num = new_entry_match.group(1)
                rest = new_entry_match.group(2).strip()

                # Parse name and title - look for VM or YES/NO marker
                # GP4 format: "Wolfgang Härdle VM Bibvliometrics..."
                # GP5 format: "Maria Iannario NO Advanced statistical..."

                vm_marker_match = re.match(r'^([A-Za-z\u00C0-\u017F\s,\(\)\-\.\']+?)\s+(VM|YES|NO|Y|N)\s+(.*)$', rest)

                if vm_marker_match:
                    name = vm_marker_match.group(1).strip()
                    yri_marker = vm_marker_match.group(2).upper()
                    title_part = vm_marker_match.group(3).strip()
                    yri = yri_marker in ('YES', 'Y')
                else:
                    # Fallback - no marker found
                    name = rest
                    title_part = ''
                    yri = False

                current_entry = {
                    'num': entry_num,
                    'name': name,
                    'yri': yri,
                    'title_parts': [title_part] if title_part else [],
                    'country': end_match.group(1),
                    'start_date': end_match.group(2),
                    'end_date': end_match.group(3),
                    'amount': parse_amount(end_match.group(4)),
                }
            else:
                # This line is a continuation with the entry ending
                if current_entry:
                    current_entry['title_parts'].append(before_end)
                    current_entry['country'] = end_match.group(1)
                    current_entry['start_date'] = end_match.group(2)
                    current_entry['end_date'] = end_match.group(3)
                    current_entry['amount'] = parse_amount(end_match.group(4))
                    entries.append(current_entry)
                    current_entry = None
        else:
            # This line doesn't end an entry - might be title continuation
            if current_entry is None:
                # Check if this is a new entry that continues on next line
                new_entry_match = re.match(r'^(\d+)\s+(.+)', line_stripped)
                if new_entry_match:
                    entry_num = new_entry_match.group(1)
                    rest = new_entry_match.group(2).strip()

                    vm_marker_match = re.match(r'^([A-Za-z\u00C0-\u017F\s,\(\)\-\.\']+?)\s+(VM|YES|NO|Y|N)\s+(.*)$', rest)

                    if vm_marker_match:
                        name = vm_marker_match.group(1).strip()
                        yri_marker = vm_marker_match.group(2).upper()
                        title_part = vm_marker_match.group(3).strip()
                        yri = yri_marker in ('YES', 'Y')
                    else:
                        name = rest
                        title_part = ''
                        yri = False

                    current_entry = {
                        'num': entry_num,
                        'name': name,
                        'yri': yri,
                        'title_parts': [title_part] if title_part else [],
                        'country': None,
                        'start_date': None,
                        'end_date': None,
                        'amount': 0,
                    }
            elif current_entry:
                # Title continuation line
                if not re.match(r'^(Sub-total|Total|No Virtual)', line_stripped, re.IGNORECASE):
                    current_entry['title_parts'].append(line_stripped)

    # Don't forget the last entry
    if current_entry and current_entry.get('country'):
        entries.append(current_entry)

    # Convert entries to final format
    for entry in entries:
        title = ' '.join(entry['title_parts']).strip()
        # Clean up title - remove redundant spaces
        title = ' '.join(title.split())

        vm_grants.append({
            'id': f"GP{grant_period}_VM{entry['num']}",
            'grant_period': grant_period,
            'name': entry['name'],
            'yri': entry['yri'],
            'title': title,
            'country': entry['country'],
            'is_itc': entry['country'] in ITC_COUNTRIES if entry['country'] else False,
            'start_date': entry['start_date'],
            'end_date': entry['end_date'],
            'amount': entry['amount'],
        })

    return vm_grants


def extract_itc_conference_grants(text, grant_period):
    """Extract ITC Conference Grants"""
    grants = []

    # Find ITC Conference section
    itc_section = re.search(
        r'Inclusiveness Target Countries Conference Grant Expenditure.*?(?:List of paid|Grantee name).*?(?=\n(?:Dissemination|Virtual Networking|OERSA|No ITC|\d+ of \d+))',
        text, re.DOTALL | re.IGNORECASE
    )

    if not itc_section:
        return grants

    section = itc_section.group(0)

    # Pattern: number name YRI home conf_country conference_title start_date end_date days amount
    itc_pattern = r'^(\d+)\s+([A-Za-z\u00C0-\u017F\s,\(\)\-\.\']+?)\s+(YES|NO|Y|N)\s+([A-Z]{2})\s+([A-Z]{2})\s+(.+?)\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(\d+)\s+([\d\s,\.]+)\s*$'

    for line in section.split('\n'):
        match = re.match(itc_pattern, line.strip())
        if match:
            yri_str = match.group(3).upper()
            yri = yri_str in ('YES', 'Y')

            grant = {
                'id': f"GP{grant_period}_ITC{match.group(1)}",
                'grant_period': grant_period,
                'name': match.group(2).strip(),
                'yri': yri,
                'home_country': match.group(4),
                'conference_country': match.group(5),
                'conference_title': match.group(6).strip(),
                'start_date': match.group(7),
                'end_date': match.group(8),
                'days': int(match.group(9)),
                'amount': parse_amount(match.group(10)),
            }
            grants.append(grant)

    return grants


def extract_dissemination_grants(text, grant_period):
    """Extract Dissemination Conference Grants"""
    grants = []

    # Find Dissemination Conference section
    diss_section = re.search(
        r'Dissemination Conference Grant Expenditure.*?(?:List of paid|Grantee name).*?(?=\n(?:Inclusiveness|Virtual Networking|OERSA|No Dissemination|\d+ of \d+))',
        text, re.DOTALL | re.IGNORECASE
    )

    if not diss_section:
        return grants

    section = diss_section.group(0)

    # Pattern: number name YRI home conf_country conference_title start_date end_date days amount
    diss_pattern = r'^(\d+)\s+([A-Za-z\u00C0-\u017F\s,\(\)\-\.\']+?)\s+(YES|NO|Y|N|DCG)\s+(.+?)\s+([A-Z]{2})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+([\d\s,\.]+)\s*$'

    for line in section.split('\n'):
        match = re.match(diss_pattern, line.strip())
        if match:
            yri_str = match.group(3).upper()
            yri = yri_str in ('YES', 'Y')

            grant = {
                'id': f"GP{grant_period}_DCG{match.group(1)}",
                'grant_period': grant_period,
                'name': match.group(2).strip(),
                'yri': yri,
                'title': match.group(4).strip(),
                'country': match.group(5),
                'start_date': match.group(6),
                'end_date': match.group(7),
                'amount': parse_amount(match.group(8)),
            }
            grants.append(grant)

    return grants


def extract_vns_grants(text, grant_period):
    """Extract Virtual Networking Support grants"""
    grants = []

    # Find VNS section
    vns_section = re.search(
        r'Virtual Networking Support.*?(?:List of paid|Grantee name).*?(?=\n(?:Total Networking|FSAC|Eligible|\d+ of \d+))',
        text, re.DOTALL | re.IGNORECASE
    )

    if not vns_section:
        return grants

    section = vns_section.group(0)

    # VNS pattern varies, look for basic entries
    vns_pattern = r'^(\d+)\s+([A-Za-z\u00C0-\u017F\s,\(\)\-\.\']+?)\s+(YES|NO|Y|N)\s+(.+?)\s+([A-Z]{2})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+([\d\s,\.]+)\s*$'

    for line in section.split('\n'):
        match = re.match(vns_pattern, line.strip())
        if match:
            yri_str = match.group(3).upper()
            yri = yri_str in ('YES', 'Y')

            grant = {
                'id': f"GP{grant_period}_VNS{match.group(1)}",
                'grant_period': grant_period,
                'name': match.group(2).strip(),
                'yri': yri,
                'title': match.group(4).strip(),
                'country': match.group(5),
                'start_date': match.group(6),
                'end_date': match.group(7),
                'amount': parse_amount(match.group(8)),
            }
            grants.append(grant)

    return grants


def compute_country_statistics(all_data):
    """Compute detailed country statistics from all extracted data"""
    country_stats = defaultdict(lambda: {
        'code': '',
        'is_itc': False,
        'meeting_participants': 0,
        'meeting_reimbursements': 0.0,
        'stsm_count': 0,
        'stsm_amount': 0.0,
        'vm_count': 0,
        'vm_amount': 0.0,
        'ts_participants': 0,
        'ts_amount': 0.0,
        'itc_grants': 0,
        'total_amount': 0.0,
        'unique_participants': set(),
    })

    # Meeting participants
    for meeting in all_data['meetings']:
        for p in meeting.get('participants', []):
            country = p['country']
            country_stats[country]['code'] = country
            country_stats[country]['is_itc'] = country in ITC_COUNTRIES
            country_stats[country]['meeting_participants'] += 1
            country_stats[country]['meeting_reimbursements'] += p['total']
            country_stats[country]['unique_participants'].add(p['name'].lower())

    # STSMs
    for stsm in all_data['stsm']:
        country = stsm['home_country']
        country_stats[country]['stsm_count'] += 1
        country_stats[country]['stsm_amount'] += stsm['amount']
        country_stats[country]['unique_participants'].add(stsm['name'].lower())

    # Virtual Mobility
    for vm in all_data['virtual_mobility']:
        country = vm['country']
        country_stats[country]['vm_count'] += 1
        country_stats[country]['vm_amount'] += vm['amount']
        country_stats[country]['unique_participants'].add(vm['name'].lower())

    # Training Schools
    for ts in all_data['training_schools']:
        for p in ts.get('participants', []):
            country = p['country']
            country_stats[country]['ts_participants'] += 1
            country_stats[country]['ts_amount'] += p['total']
            country_stats[country]['unique_participants'].add(p['name'].lower())

    # ITC Grants
    for grant in all_data['itc_grants']:
        country = grant['home_country']
        country_stats[country]['itc_grants'] += 1

    # Calculate totals and convert sets to counts
    result = []
    for country, stats in country_stats.items():
        stats['total_amount'] = (
            stats['meeting_reimbursements'] +
            stats['stsm_amount'] +
            stats['vm_amount'] +
            stats['ts_amount']
        )
        stats['unique_participant_count'] = len(stats['unique_participants'])
        del stats['unique_participants']  # Remove set before JSON serialization
        result.append(stats)

    # Sort by total amount
    result.sort(key=lambda x: x['total_amount'], reverse=True)

    return result


def build_participant_master(all_data):
    """Build master list of all unique participants with their activities"""
    participants = defaultdict(lambda: {
        'name': '',
        'countries': set(),
        'meetings': [],
        'stsm': [],
        'virtual_mobility': [],
        'training_schools': [],
        'itc_conferences': [],
        'total_reimbursed': 0.0,
        'grant_periods': set(),
    })

    def normalize_name(name):
        """Normalize name for matching"""
        name = name.lower().strip()
        # Handle "Lastname, Firstname" vs "Firstname Lastname"
        if ',' in name:
            parts = name.split(',')
            if len(parts) == 2:
                name = f"{parts[1].strip()} {parts[0].strip()}"
        # Remove special characters
        name = re.sub(r'[,\(\)\-\.\']+', ' ', name)
        name = ' '.join(name.split())
        return name

    # Meeting participants
    for meeting in all_data['meetings']:
        for p in meeting.get('participants', []):
            key = normalize_name(p['name'])
            participants[key]['name'] = p['name']
            participants[key]['countries'].add(p['country'])
            participants[key]['meetings'].append({
                'meeting_id': meeting['id'],
                'title': meeting.get('title', ''),
                'date': meeting.get('start_date', ''),
                'amount': p['total']
            })
            participants[key]['total_reimbursed'] += p['total']
            participants[key]['grant_periods'].add(meeting['grant_period'])

    # STSMs
    for stsm in all_data['stsm']:
        key = normalize_name(stsm['name'])
        participants[key]['name'] = stsm['name']
        participants[key]['countries'].add(stsm['home_country'])
        participants[key]['stsm'].append({
            'id': stsm['id'],
            'host': stsm['host_country'],
            'dates': f"{stsm['start_date']} - {stsm['end_date']}",
            'days': stsm['days'],
            'amount': stsm['amount']
        })
        participants[key]['total_reimbursed'] += stsm['amount']
        participants[key]['grant_periods'].add(stsm['grant_period'])

    # Virtual Mobility
    for vm in all_data['virtual_mobility']:
        key = normalize_name(vm['name'])
        participants[key]['name'] = vm['name']
        participants[key]['countries'].add(vm['country'])
        participants[key]['virtual_mobility'].append({
            'id': vm['id'],
            'title': vm.get('title', ''),
            'dates': f"{vm['start_date']} - {vm['end_date']}",
            'amount': vm['amount']
        })
        participants[key]['total_reimbursed'] += vm['amount']
        participants[key]['grant_periods'].add(vm['grant_period'])

    # Training Schools
    for ts in all_data['training_schools']:
        for p in ts.get('participants', []):
            key = normalize_name(p['name'])
            participants[key]['name'] = p['name']
            participants[key]['countries'].add(p['country'])
            participants[key]['training_schools'].append({
                'school_id': ts['id'],
                'title': ts.get('title', ''),
                'date': ts.get('start_date', ''),
                'amount': p['total']
            })
            participants[key]['total_reimbursed'] += p['total']
            participants[key]['grant_periods'].add(ts['grant_period'])

    # ITC Conferences
    for grant in all_data['itc_grants']:
        key = normalize_name(grant['name'])
        participants[key]['name'] = grant['name']
        participants[key]['countries'].add(grant['home_country'])
        participants[key]['itc_conferences'].append({
            'id': grant['id'],
            'title': grant.get('conference_title', ''),
            'dates': f"{grant['start_date']} - {grant['end_date']}",
            'amount': grant['amount']
        })
        participants[key]['total_reimbursed'] += grant['amount']
        participants[key]['grant_periods'].add(grant['grant_period'])

    # Convert to list and clean up
    result = []
    for key, data in participants.items():
        data['countries'] = list(data['countries'])
        data['primary_country'] = data['countries'][0] if data['countries'] else None
        data['is_itc'] = data['primary_country'] in ITC_COUNTRIES if data['primary_country'] else False
        data['grant_periods'] = sorted(list(data['grant_periods']))
        data['activity_count'] = (
            len(data['meetings']) +
            len(data['stsm']) +
            len(data['virtual_mobility']) +
            len(data['training_schools']) +
            len(data['itc_conferences'])
        )
        result.append(data)

    # Sort by total reimbursed
    result.sort(key=lambda x: x['total_reimbursed'], reverse=True)

    return result


def extract_los_grants(all_data):
    """Extract all LOS (Local Organiser Support) grants"""
    los_grants = []

    # From meetings
    for meeting in all_data['meetings']:
        if meeting.get('los_grant', 0) > 0:
            los_grants.append({
                'event_type': 'meeting',
                'event_id': meeting['id'],
                'title': meeting.get('title', ''),
                'location': meeting.get('location', ''),
                'date': meeting.get('start_date', ''),
                'grant_period': meeting['grant_period'],
                'amount': meeting['los_grant']
            })

    # From training schools
    for ts in all_data['training_schools']:
        if ts.get('los_grant', 0) > 0:
            los_grants.append({
                'event_type': 'training_school',
                'event_id': ts['id'],
                'title': ts.get('title', ''),
                'location': ts.get('location', ''),
                'date': ts.get('start_date', ''),
                'grant_period': ts['grant_period'],
                'amount': ts['los_grant']
            })

    return los_grants


def main():
    """Main extraction function"""
    print("=" * 60)
    print("COST Action CA19130 - Comprehensive FFR Data Extraction")
    print("=" * 60)

    all_data = {
        'meetings': [],
        'justifications': [],
        'training_schools': [],
        'stsm': [],
        'virtual_mobility': [],
        'itc_grants': [],
        'dissemination_grants': [],
        'vns_grants': [],
    }

    # Extract from each grant period
    for gp in range(1, 6):
        print(f"\nProcessing Grant Period {gp}...")
        text = read_ffr_file(gp)

        if not text:
            continue

        # Extract meetings with participants
        meetings = extract_meetings_with_participants(text, gp)
        print(f"  Meetings: {len(meetings)}")
        for m in meetings:
            print(f"    - {m.get('title', 'N/A')}: {len(m.get('participants', []))} participants")
        all_data['meetings'].extend(meetings)

        # Extract justifications
        justifications = extract_justifications(text, gp)
        print(f"  Justifications: {len(justifications)}")
        all_data['justifications'].extend(justifications)

        # Extract training schools
        schools = extract_training_schools(text, gp)
        print(f"  Training Schools: {len(schools)}")
        all_data['training_schools'].extend(schools)

        # Extract STSMs
        stsms = extract_stsm(text, gp)
        print(f"  STSMs: {len(stsms)}")
        all_data['stsm'].extend(stsms)

        # Extract Virtual Mobility
        vm = extract_virtual_mobility(text, gp)
        print(f"  Virtual Mobility: {len(vm)}")
        all_data['virtual_mobility'].extend(vm)

        # Extract ITC Conference Grants
        itc = extract_itc_conference_grants(text, gp)
        print(f"  ITC Conference Grants: {len(itc)}")
        all_data['itc_grants'].extend(itc)

        # Extract Dissemination Grants
        diss = extract_dissemination_grants(text, gp)
        print(f"  Dissemination Grants: {len(diss)}")
        all_data['dissemination_grants'].extend(diss)

        # Extract VNS Grants
        vns = extract_vns_grants(text, gp)
        print(f"  VNS Grants: {len(vns)}")
        all_data['vns_grants'].extend(vns)

    # Compute derived data
    print("\n" + "=" * 60)
    print("Computing derived data...")

    country_stats = compute_country_statistics(all_data)
    print(f"Country statistics: {len(country_stats)} countries")

    participant_master = build_participant_master(all_data)
    print(f"Unique participants: {len(participant_master)}")

    los_grants = extract_los_grants(all_data)
    print(f"LOS grants: {len(los_grants)}")

    # Save output files
    print("\n" + "=" * 60)
    print("Saving JSON files...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Meetings with participants
    with open(OUTPUT_DIR / 'meetings_participants.json', 'w', encoding='utf-8') as f:
        json.dump(all_data['meetings'], f, indent=2, ensure_ascii=False)
    print(f"  meetings_participants.json: {len(all_data['meetings'])} meetings")

    # Justifications
    with open(OUTPUT_DIR / 'meetings_justifications.json', 'w', encoding='utf-8') as f:
        json.dump(all_data['justifications'], f, indent=2, ensure_ascii=False)
    print(f"  meetings_justifications.json: {len(all_data['justifications'])} entries")

    # Training Schools
    with open(OUTPUT_DIR / 'training_school_attendees.json', 'w', encoding='utf-8') as f:
        json.dump(all_data['training_schools'], f, indent=2, ensure_ascii=False)
    print(f"  training_school_attendees.json: {len(all_data['training_schools'])} schools")

    # STSMs
    with open(OUTPUT_DIR / 'stsm_full.json', 'w', encoding='utf-8') as f:
        json.dump(all_data['stsm'], f, indent=2, ensure_ascii=False)
    print(f"  stsm_full.json: {len(all_data['stsm'])} STSMs")

    # Virtual Mobility
    with open(OUTPUT_DIR / 'virtual_mobility_full.json', 'w', encoding='utf-8') as f:
        json.dump(all_data['virtual_mobility'], f, indent=2, ensure_ascii=False)
    print(f"  virtual_mobility_full.json: {len(all_data['virtual_mobility'])} grants")

    # ITC Conference Grants
    with open(OUTPUT_DIR / 'itc_conference_grants.json', 'w', encoding='utf-8') as f:
        json.dump(all_data['itc_grants'], f, indent=2, ensure_ascii=False)
    print(f"  itc_conference_grants.json: {len(all_data['itc_grants'])} grants")

    # Dissemination Grants
    with open(OUTPUT_DIR / 'dissemination_grants.json', 'w', encoding='utf-8') as f:
        json.dump(all_data['dissemination_grants'], f, indent=2, ensure_ascii=False)
    print(f"  dissemination_grants.json: {len(all_data['dissemination_grants'])} grants")

    # VNS Grants
    with open(OUTPUT_DIR / 'vns_grants.json', 'w', encoding='utf-8') as f:
        json.dump(all_data['vns_grants'], f, indent=2, ensure_ascii=False)
    print(f"  vns_grants.json: {len(all_data['vns_grants'])} grants")

    # Country Statistics
    with open(OUTPUT_DIR / 'country_statistics_full.json', 'w', encoding='utf-8') as f:
        json.dump(country_stats, f, indent=2, ensure_ascii=False)
    print(f"  country_statistics_full.json: {len(country_stats)} countries")

    # Participant Master
    with open(OUTPUT_DIR / 'participant_master.json', 'w', encoding='utf-8') as f:
        json.dump(participant_master, f, indent=2, ensure_ascii=False)
    print(f"  participant_master.json: {len(participant_master)} unique participants")

    # LOS Grants
    with open(OUTPUT_DIR / 'los_grants.json', 'w', encoding='utf-8') as f:
        json.dump(los_grants, f, indent=2, ensure_ascii=False)
    print(f"  los_grants.json: {len(los_grants)} grants")

    # Summary statistics
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)

    total_meeting_participants = sum(len(m.get('participants', [])) for m in all_data['meetings'])
    total_ts_participants = sum(len(ts.get('participants', [])) for ts in all_data['training_schools'])

    print(f"Total Meetings: {len(all_data['meetings'])}")
    print(f"Total Meeting Participants (with reimbursement details): {total_meeting_participants}")
    print(f"Total Training Schools: {len(all_data['training_schools'])}")
    print(f"Total Training School Participants: {total_ts_participants}")
    print(f"Total STSMs: {len(all_data['stsm'])}")
    print(f"Total Virtual Mobility Grants: {len(all_data['virtual_mobility'])}")
    print(f"Total ITC Conference Grants: {len(all_data['itc_grants'])}")
    print(f"Total Dissemination Grants: {len(all_data['dissemination_grants'])}")
    print(f"Total VNS Grants: {len(all_data['vns_grants'])}")
    print(f"Total LOS Grants: {len(los_grants)}")
    print(f"Unique Participants: {len(participant_master)}")
    print(f"Countries: {len(country_stats)}")

    print("\n" + "=" * 60)
    print("Extraction complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
