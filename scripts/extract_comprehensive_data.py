"""
Comprehensive Data Extraction Script for COST Action CA19130
Extracts ALL details from FFR and WBP text files
"""

import re
import json
from pathlib import Path
from collections import defaultdict

# Paths
EXTRACTED_TEXT_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")
OUTPUT_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\COST-Fintech-AI-in-Finance\data")
OUTPUT_DIR.mkdir(exist_ok=True)

def read_file(filepath):
    """Read a text file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def extract_meetings_from_ffr(text, gp_number):
    """Extract all meeting details from FFR text"""
    meetings = []

    # Pattern to find meeting blocks
    meeting_pattern = r'Meeting (\d+)\nStart date (\d{2}/\d{2}/\d{4})\nEnd date (\d{2}/\d{2}/\d{4})\nMeeting duration \(days\) (\d+)\nMeeting location ([^\n]+)\nMeeting title ([^\n]+)\nMeeting type ([^\n]+)\nTotal number of participants (\d+)\nTotal number of reimbursed participants (\d+)'

    for match in re.finditer(meeting_pattern, text):
        meeting = {
            'number': int(match.group(1)),
            'start_date': match.group(2),
            'end_date': match.group(3),
            'duration_days': int(match.group(4)),
            'location': match.group(5).strip(),
            'title': match.group(6).strip(),
            'type': match.group(7).strip(),
            'total_participants': int(match.group(8)),
            'reimbursed_participants': int(match.group(9)),
            'grant_period': gp_number,
            'participants': []
        }

        # Extract participant list - look for pattern after this meeting block
        start_pos = match.end()
        next_meeting = re.search(r'Meeting \d+\nStart date', text[start_pos:])
        end_pos = start_pos + next_meeting.start() if next_meeting else start_pos + 5000
        meeting_text = text[start_pos:end_pos]

        # Pattern for participants: "1 Name, Name Country 123.45 456.78 0.00 580.23"
        participant_pattern = r'(\d+)\s+([A-Za-zÀ-ÿ\s,\(\)\-\.\']+?)\s+([A-Z]{2})\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)'

        for p_match in re.finditer(participant_pattern, meeting_text):
            name = p_match.group(2).strip()
            # Clean up name
            name = re.sub(r'\s+', ' ', name)
            if name and len(name) > 2 and not name.startswith('Sub-total'):
                participant = {
                    'name': name,
                    'country': p_match.group(3),
                    'travel_allowance': float(p_match.group(4).replace(',', '')),
                    'daily_allowance': float(p_match.group(5).replace(',', '')),
                    'other_expenses': float(p_match.group(6).replace(',', '')),
                    'total': float(p_match.group(7).replace(',', ''))
                }
                meeting['participants'].append(participant)

        meetings.append(meeting)

    return meetings

def extract_stsm_from_ffr(text, gp_number):
    """Extract all STSM details from FFR text"""
    stsms = []

    # Find the STSM section - look for the detailed expenditure section
    # Try GP3-5 format first: "Short-Term Scientific Mission Grant Expenditure"
    # Then GP1 format: "Short Term Scientific Mission (STSM) Expenditure"
    stsm_section = re.search(r'Short-Term Scientific Mission Grant Expenditure.*?Total expenditure\s+[\d\s,\.]+', text, re.DOTALL)
    if not stsm_section:
        # Try GP1 format
        stsm_section = re.search(r'Short Term Scientific Mission \(STSM\) Expenditure.*?(?:Total expenditure|No Short Term)', text, re.DOTALL)
    if not stsm_section:
        return stsms

    stsm_text = stsm_section.group()
    lines = stsm_text.split('\n')

    for line in lines:
        # Skip header and metadata lines
        if any(skip in line for skip in ['Grantee', 'List of', 'Sub-total', 'No Short', 'Short-Term', 'YRI', 'expenditure', 'accrued', 'Total', 'PAGE']):
            continue

        line = line.strip()
        if not line or not line[0].isdigit():
            continue

        # Patterns to match:
        # GP1: "1 Dr Stjepan Picek Y HR NL 11/01/2021 26/01/2021 16 NO 1 520.00"
        # GP4: "1 Shkurti (Perri), Rezarta NO IT AL 09/10/2023 13/10/2023 6 1 000.00"
        # GP5: "1 Coita, Ioana NO SK RO 06/04/2024 14/04/2024 10 1 997.00"

        # Find dates
        dates = re.findall(r'\d{2}/\d{2}/\d{4}', line)
        if len(dates) < 2:
            continue

        start_date = dates[0]
        end_date = dates[1]

        # Split line at first date
        first_date_pos = line.find(start_date)
        before_dates = line[:first_date_pos].strip()
        after_dates = line[line.find(end_date) + len(end_date):].strip()

        # Find country codes (2 letters before dates)
        country_codes = re.findall(r'\b([A-Z]{2})\b', before_dates)
        if len(country_codes) < 2:
            continue

        host = country_codes[-2]
        home = country_codes[-1]

        # Extract name and YRI
        # Remove the country codes and YES/NO from the end
        # Format: "1 Name [YES/NO/Y/N] HOST HOME"
        name_yri_part = before_dates
        for code in country_codes:
            name_yri_part = name_yri_part.replace(f' {code}', '')

        # Find YRI indicator
        yri = False
        yri_match = re.search(r'\s+(YES|NO|Y|N)\s*$', name_yri_part)
        if yri_match:
            yri = yri_match.group(1) in ['YES', 'Y']
            name_yri_part = name_yri_part[:yri_match.start()].strip()

        # Extract name (remove leading number)
        name_match = re.match(r'^\d+\s+(.+)', name_yri_part)
        if not name_match:
            continue

        name = name_match.group(1).strip()
        # Remove titles
        name = re.sub(r'^(Dr\.?|Mr\.?|Ms\.?|Mrs\.?)\s+', '', name)

        # Parse days and amount from after_dates
        # Format: "6 1 000.00" or "16 NO 1 520.00"
        # Days is first number, amount is number with decimal at the end
        days = 0
        amount = 0.0

        # Match pattern: days [optional text] amount.decimal
        # e.g., "6 1 000.00" -> days=6, amount=1000.00
        # e.g., "16 NO 1 520.00" -> days=16, amount=1520.00
        match = re.match(r'^(\d+)\s+(?:YES\s+|NO\s+)?([\d\s]+[.,]\d{2})\s*$', after_dates)
        if match:
            days = int(match.group(1))
            amount_str = match.group(2).replace(' ', '').replace(',', '')
            try:
                amount = float(amount_str)
            except:
                pass

        if name and days > 0 and amount > 0:
            stsm = {
                'name': name,
                'yri': yri,
                'host': host,
                'home': home,
                'start_date': start_date,
                'end_date': end_date,
                'days': days,
                'amount': amount,
                'grant_period': gp_number
            }
            stsms.append(stsm)

    return stsms

def extract_vm_from_ffr(text, gp_number):
    """Extract all Virtual Mobility grants from FFR text"""
    vms = []

    vm_section = re.search(r'Virtual Mobility Grant Expenditure.*?Total expenditure[\s\d,\.]+', text, re.DOTALL)
    if not vm_section:
        return vms

    vm_text = vm_section.group()

    # Pattern for VM grants
    # "1 Maria Iannario NO Advanced statistical methods... IT 01/02/2024 01/07/2024 1 500.00"
    lines = vm_text.split('\n')

    current_vm = None
    for i, line in enumerate(lines):
        # Check for start of VM entry
        match = re.match(r'^(\d+)\s+([A-Za-zÀ-ÿ\s]+?)\s+(YES|NO|VM)\s+(.+)$', line)
        if match:
            # Parse the line
            parts = line.split()
            if len(parts) >= 5:
                # Find the country code (2 letters)
                for j, part in enumerate(parts):
                    if re.match(r'^[A-Z]{2}$', part) and j > 2:
                        name = ' '.join(parts[1:3])
                        # Clean up name
                        name = re.sub(r'\s+(YES|NO|VM)$', '', name)
                        title_parts = parts[3:j]
                        title = ' '.join([p for p in title_parts if p not in ['YES', 'NO', 'VM']])
                        country = part

                        # Find dates and amount
                        remaining = ' '.join(parts[j+1:])
                        date_match = re.search(r'(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+([\d\s,\.]+)', remaining)
                        if date_match:
                            amount_str = date_match.group(3).replace(' ', '').replace(',', '')
                            try:
                                amount = float(amount_str)
                            except:
                                amount = 1500  # Default

                            vm = {
                                'name': name.strip(),
                                'title': title.strip() if title else 'Virtual Mobility Grant',
                                'country': country,
                                'start_date': date_match.group(1),
                                'end_date': date_match.group(2),
                                'amount': amount,
                                'grant_period': gp_number
                            }
                            vms.append(vm)
                        break

    return vms

def extract_training_schools_from_ffr(text, gp_number):
    """Extract all training school details from FFR text"""
    schools = []

    # Pattern to find training school blocks
    ts_pattern = r'Training School (\d+)\nStart date (\d{2}/\d{2}/\d{4})\nEnd date (\d{2}/\d{2}/\d{4})\nTraining School duration \(days\) (\d+)\nTraining School location ([^\n]+)\nTraining School title ([^\n]+)'

    for match in re.finditer(ts_pattern, text):
        school = {
            'number': int(match.group(1)),
            'start_date': match.group(2),
            'end_date': match.group(3),
            'duration_days': int(match.group(4)),
            'location': match.group(5).strip(),
            'title': match.group(6).strip(),
            'grant_period': gp_number,
            'trainees': []
        }

        # Extract trainee list
        start_pos = match.end()
        next_school = re.search(r'Training School \d+\nStart date', text[start_pos:])
        end_pos = start_pos + next_school.start() if next_school else start_pos + 5000
        school_text = text[start_pos:end_pos]

        # Pattern for trainees
        trainee_pattern = r'(\d+)\s+([A-Za-zÀ-ÿ\s,\(\)\-\.\']+?)\s+([A-Z]{2})\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)\s+([\d,\.]+)'

        for t_match in re.finditer(trainee_pattern, school_text):
            name = t_match.group(2).strip()
            name = re.sub(r'\s+', ' ', name)
            if name and len(name) > 2 and not name.startswith('Sub-total'):
                trainee = {
                    'name': name,
                    'country': t_match.group(3),
                    'travel_allowance': float(t_match.group(4).replace(',', '')),
                    'daily_allowance': float(t_match.group(5).replace(',', '')),
                    'other_expenses': float(t_match.group(6).replace(',', '')),
                    'total': float(t_match.group(7).replace(',', ''))
                }
                school['trainees'].append(trainee)

        schools.append(school)

    return schools

def extract_vns_from_ffr(text, gp_number):
    """Extract Virtual Networking Support grants from FFR text"""
    vns_list = []

    vns_section = re.search(r'Virtual Networking Support Grant Expenditure.*?Total expenditure[\s\d,\.]+', text, re.DOTALL)
    if not vns_section:
        return vns_list

    vns_text = vns_section.group()

    # Pattern for VNS: "1 Codruta MARE NO Meeting and working online... RO 10/09/2024 12/09/2024 4 000.00"
    lines = vns_text.split('\n')
    for line in lines:
        match = re.match(r'^(\d+)\s+([A-Za-zÀ-ÿ\s]+?)\s+(YES|NO|VNS)\s+(.+?)\s+([A-Z]{2})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+([\d\s,\.]+)', line)
        if match:
            amount_str = match.group(8).replace(' ', '').replace(',', '')
            try:
                amount = float(amount_str)
            except:
                amount = 4000

            vns = {
                'name': match.group(2).strip(),
                'title': match.group(4).strip(),
                'country': match.group(5),
                'start_date': match.group(6),
                'end_date': match.group(7),
                'amount': amount,
                'grant_period': gp_number
            }
            vns_list.append(vns)

    return vns_list

def extract_dissemination_from_ffr(text, gp_number):
    """Extract dissemination and communication products from FFR text"""
    dissemination = []

    diss_section = re.search(r'Dissemination and Communication Products Expenditure.*?Total expenditure[\s\d,\.]+', text, re.DOTALL)
    if not diss_section:
        return dissemination

    diss_text = diss_section.group()

    # Pattern: "1 Action Website Website Karolina Bolest 09/09/2024 2 000.00"
    pattern = r'(\d+)\s+(.+?)\s+(Website|Action Website|Graphic design[^\s]*)\s+([A-Za-zÀ-ÿ\s]+?)\s+(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})\s+([\d\s,\.]+)'

    for match in re.finditer(pattern, diss_text, re.IGNORECASE):
        amount_str = match.group(6).replace(' ', '').replace(',', '')
        try:
            amount = float(amount_str)
        except:
            amount = 0

        if amount > 0:
            item = {
                'title': match.group(2).strip(),
                'type': match.group(3).strip(),
                'provider': match.group(4).strip(),
                'date': match.group(5),
                'amount': amount,
                'grant_period': gp_number
            }
            dissemination.append(item)

    return dissemination

def extract_budget_summary(text, gp_number):
    """Extract budget summary from FFR text"""
    summary = {
        'grant_period': gp_number,
        'budget': 0,
        'actual': 0,
        'categories': {}
    }

    # Find total grant budget
    budget_match = re.search(r'Total Grant Budget EUR\s+([\d\s,\.]+)', text)
    if budget_match:
        summary['budget'] = float(budget_match.group(1).replace(' ', '').replace(',', ''))

    # Find eligible costs
    actual_match = re.search(r'Eligible costs until.*?([\d\s,\.]+)\s+0\.00\s+([\d\s,\.]+)', text)
    if actual_match:
        summary['actual'] = float(actual_match.group(2).replace(' ', '').replace(',', ''))

    # Extract category breakdown
    categories = {
        'Meetings': r'(?:Total )?Meetings?\s+([\d\s,\.]+)\s+([\d\s,\.]+)',
        'Training Schools': r'Training Schools?\s+([\d\s,\.]+)\s+([\d\s,\.]+)',
        'STSMs': r'(?:Total )?(?:STSM|Short-Term Scientific Mission)\s+([\d\s,\.]+)\s+([\d\s,\.]+)',
        'Virtual Mobility': r'Virtual Mobility\s+([\d\s,\.]+)\s+([\d\s,\.]+)',
        'Dissemination': r'(?:Total Action )?Dissemination\s+([\d\s,\.]+)\s+([\d\s,\.]+)',
        'ITC Conference': r'ITC Conference\s+([\d\s,\.]+)\s+([\d\s,\.]+)',
        'OERSA': r'(?:Total )?OERSA\s+([\d\s,\.]+)\s+([\d\s,\.]+)',
        'Virtual Networking Support': r'Virtual Networking Support\s+([\d\s,\.]+)\s+([\d\s,\.]+)',
        'FSAC': r'FSAC.*?([\d\s,\.]+)\s+([\d\s,\.]+)'
    }

    for cat_name, pattern in categories.items():
        match = re.search(pattern, text)
        if match:
            try:
                actual = float(match.group(2).replace(' ', '').replace(',', ''))
                summary['categories'][cat_name] = actual
            except:
                pass

    return summary

def extract_participants_unique(all_meetings, all_stsms, all_training_schools, all_vms):
    """Extract unique participants from all activities"""
    participants = {}

    # From meetings
    for meeting in all_meetings:
        for p in meeting.get('participants', []):
            name = p['name']
            country = p['country']
            key = f"{name}_{country}"
            if key not in participants:
                participants[key] = {
                    'name': name,
                    'country': country,
                    'activities': [],
                    'total_reimbursed': 0
                }
            participants[key]['activities'].append(f"Meeting: {meeting['title'][:50]}...")
            participants[key]['total_reimbursed'] += p.get('total', 0)

    # From STSMs
    for stsm in all_stsms:
        name = stsm['name']
        country = stsm['home']
        key = f"{name}_{country}"
        if key not in participants:
            participants[key] = {
                'name': name,
                'country': country,
                'activities': [],
                'total_reimbursed': 0
            }
        participants[key]['activities'].append(f"STSM to {stsm['host']}")
        participants[key]['total_reimbursed'] += stsm.get('amount', 0)

    # From training schools
    for school in all_training_schools:
        for t in school.get('trainees', []):
            name = t['name']
            country = t['country']
            key = f"{name}_{country}"
            if key not in participants:
                participants[key] = {
                    'name': name,
                    'country': country,
                    'activities': [],
                    'total_reimbursed': 0
                }
            participants[key]['activities'].append(f"Training School: {school['title'][:30]}...")
            participants[key]['total_reimbursed'] += t.get('total', 0)

    # From VMs
    for vm in all_vms:
        name = vm['name']
        country = vm.get('country', 'Unknown')
        key = f"{name}_{country}"
        if key not in participants:
            participants[key] = {
                'name': name,
                'country': country,
                'activities': [],
                'total_reimbursed': 0
            }
        participants[key]['activities'].append(f"VM: {vm.get('title', 'Virtual Mobility')[:30]}...")
        participants[key]['total_reimbursed'] += vm.get('amount', 0)

    return list(participants.values())

def main():
    """Main extraction function"""
    print("=" * 60)
    print("COST CA19130 Comprehensive Data Extraction")
    print("=" * 60)

    all_meetings = []
    all_stsms = []
    all_training_schools = []
    all_vms = []
    all_vns = []
    all_dissemination = []
    all_budgets = []

    # Process each FFR file
    ffr_files = {
        1: 'AGA-CA19130-1-FFR_ID2193.txt',
        2: 'AGA-CA19130-2-FFR_ID2346.txt',
        3: 'AGA-CA19130-3-FFR_ID2998.txt',
        4: 'AGA-CA19130-4-FFR_ID3993.txt',
        5: 'AGA-CA19130-5-FFR_ID4828.txt'
    }

    for gp, filename in ffr_files.items():
        filepath = EXTRACTED_TEXT_DIR / filename
        if filepath.exists():
            print(f"\nProcessing GP{gp}: {filename}")
            text = read_file(filepath)

            # Extract data
            meetings = extract_meetings_from_ffr(text, gp)
            print(f"  - Found {len(meetings)} meetings")
            all_meetings.extend(meetings)

            stsms = extract_stsm_from_ffr(text, gp)
            print(f"  - Found {len(stsms)} STSMs")
            all_stsms.extend(stsms)

            training_schools = extract_training_schools_from_ffr(text, gp)
            print(f"  - Found {len(training_schools)} training schools")
            all_training_schools.extend(training_schools)

            vms = extract_vm_from_ffr(text, gp)
            print(f"  - Found {len(vms)} Virtual Mobility grants")
            all_vms.extend(vms)

            vns = extract_vns_from_ffr(text, gp)
            print(f"  - Found {len(vns)} VNS grants")
            all_vns.extend(vns)

            dissemination = extract_dissemination_from_ffr(text, gp)
            print(f"  - Found {len(dissemination)} dissemination items")
            all_dissemination.extend(dissemination)

            budget = extract_budget_summary(text, gp)
            all_budgets.append(budget)

    # Extract unique participants
    participants = extract_participants_unique(all_meetings, all_stsms, all_training_schools, all_vms)
    print(f"\nTotal unique participants: {len(participants)}")

    # Count participants by country
    country_counts = defaultdict(int)
    for p in participants:
        country_counts[p['country']] += 1

    # Save all data to JSON files
    print("\n" + "=" * 60)
    print("Saving data files...")

    # Meetings with full details
    with open(OUTPUT_DIR / 'meetings_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(all_meetings, f, indent=2, ensure_ascii=False)
    print(f"  - meetings_detailed.json: {len(all_meetings)} meetings")

    # STSMs
    with open(OUTPUT_DIR / 'stsm_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(all_stsms, f, indent=2, ensure_ascii=False)
    print(f"  - stsm_detailed.json: {len(all_stsms)} STSMs")

    # Training Schools
    with open(OUTPUT_DIR / 'training_schools_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(all_training_schools, f, indent=2, ensure_ascii=False)
    print(f"  - training_schools_detailed.json: {len(all_training_schools)} schools")

    # Virtual Mobility
    with open(OUTPUT_DIR / 'virtual_mobility_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(all_vms, f, indent=2, ensure_ascii=False)
    print(f"  - virtual_mobility_detailed.json: {len(all_vms)} grants")

    # Virtual Networking Support
    with open(OUTPUT_DIR / 'vns_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(all_vns, f, indent=2, ensure_ascii=False)
    print(f"  - vns_detailed.json: {len(all_vns)} grants")

    # Dissemination
    with open(OUTPUT_DIR / 'dissemination_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(all_dissemination, f, indent=2, ensure_ascii=False)
    print(f"  - dissemination_detailed.json: {len(all_dissemination)} items")

    # Participants
    with open(OUTPUT_DIR / 'participants_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(participants, f, indent=2, ensure_ascii=False)
    print(f"  - participants_detailed.json: {len(participants)} participants")

    # Country statistics
    country_stats = [{'country': k, 'count': v} for k, v in sorted(country_counts.items(), key=lambda x: -x[1])]
    with open(OUTPUT_DIR / 'country_statistics.json', 'w', encoding='utf-8') as f:
        json.dump(country_stats, f, indent=2, ensure_ascii=False)
    print(f"  - country_statistics.json: {len(country_stats)} countries")

    # Budget summaries
    with open(OUTPUT_DIR / 'budget_summaries.json', 'w', encoding='utf-8') as f:
        json.dump(all_budgets, f, indent=2, ensure_ascii=False)
    print(f"  - budget_summaries.json: {len(all_budgets)} grant periods")

    # Summary statistics
    summary = {
        'total_meetings': len(all_meetings),
        'total_stsms': len(all_stsms),
        'total_training_schools': len(all_training_schools),
        'total_trainees': sum(len(s.get('trainees', [])) for s in all_training_schools),
        'total_virtual_mobility': len(all_vms),
        'total_vns': len(all_vns),
        'total_participants': len(participants),
        'total_countries': len(country_stats),
        'total_budget': sum(b['budget'] for b in all_budgets),
        'total_actual': sum(b['actual'] for b in all_budgets),
        'meetings_by_gp': {gp: len([m for m in all_meetings if m['grant_period'] == gp]) for gp in range(1, 6)},
        'stsms_by_gp': {gp: len([s for s in all_stsms if s['grant_period'] == gp]) for gp in range(1, 6)}
    }

    with open(OUTPUT_DIR / 'summary_statistics.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total Meetings: {summary['total_meetings']}")
    print(f"Total STSMs: {summary['total_stsms']}")
    print(f"Total Training Schools: {summary['total_training_schools']}")
    print(f"Total Trainees: {summary['total_trainees']}")
    print(f"Total Virtual Mobility Grants: {summary['total_virtual_mobility']}")
    print(f"Total VNS Grants: {summary['total_vns']}")
    print(f"Total Unique Participants: {summary['total_participants']}")
    print(f"Total Countries: {summary['total_countries']}")
    print(f"Total Budget: EUR {summary['total_budget']:,.2f}")
    print(f"Total Actual: EUR {summary['total_actual']:,.2f}")
    print("=" * 60)

if __name__ == '__main__':
    main()
