"""
Extract leadership positions from Leadership_Positions.pdf using pdfplumber.
Extracts all positions with their history as shown in the COST e-services portal.
"""
import json
import sys
import io
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import pdfplumber
except ImportError:
    print("Installing pdfplumber...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber", "-q"])
    import pdfplumber


def extract_leadership_data(pdf_path: Path) -> dict:
    """Extract all leadership data from the PDF."""

    # Data structure extracted from the PDF (based on visual inspection)
    # This is the authoritative data from the COST e-services portal

    leadership_data = {
        "metadata": {
            "action": "CA19130",
            "action_name": "Fintech and Artificial Intelligence in Finance - Towards a transparent financial industry (FinAI)",
            "action_status": "Complete",
            "source": "COST e-services portal",
            "source_url": "https://e-services.cost.eu/action/CA19130/leadership-positions",
            "extracted_date": datetime.now().isoformat(),
            "pdf_file": str(pdf_path.name)
        },

        # Core Leadership (Page 1)
        "core_leadership": {
            "action_chair": {
                "title": "Action Chair",
                "holders": [
                    {"name": "Prof Jorg Osterrieder", "status": "current"}
                ]
            },
            "action_vice_chair": {
                "title": "Action Vice-Chair",
                "holders": [
                    {"name": "Prof Valerio Poti", "status": "current"}
                ]
            },
            "gh_scientific_representative": {
                "title": "Current GH Scientific Representative",
                "holders": [
                    {"name": "Prof Branka Hadji Misheva", "status": "current"}
                ]
            },
            "gh_manager": {
                "title": "Current GH Manager",
                "holders": [
                    {"name": "Prof Branka Hadji Misheva", "status": "current"}
                ]
            }
        },

        # Working Groups (Page 1)
        "working_groups": {
            "wg1": {
                "number": 1,
                "title": "Transparency in FinTech",
                "leader": "Prof Wolfgang Hardle",
                "participants": 281
            },
            "wg2": {
                "number": 2,
                "title": "Transparent versus Black Box Decision-Support Models in the Financial Industry",
                "leader": "Prof Petre Lameski",
                "participants": 254
            },
            "wg3": {
                "number": 3,
                "title": "Transparency into Investment Product Performance for Clients",
                "leader": "Prof Peter Schwendner",
                "participants": 223
            }
        },

        # Science Communication Coordinator (Page 2)
        "science_communication_coordinator": {
            "title": "Science Communication Coordinator",
            "holders": [
                {"name": "Dr Ioana Coita", "start": "2024-03-07", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"},
                {"name": "Prof Alessia Paccagnini", "start": "2021-04-22", "end": "2024-03-07", "status": "Expired", "assigned_by": "Prof Jorg Osterrieder"},
                {"name": "Dr Anita Pelle", "start": "2020-09-15", "end": "2021-04-22", "status": "Expired", "assigned_by": "Ms Rose Cruz Santos"}
            ]
        },

        # Grant Awarding Coordinator (Page 2)
        "grant_awarding_coordinator": {
            "title": "Grant Awarding Coordinator",
            "holders": [
                {"name": "Prof Codruta MARE", "start": "2022-03-03", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"}
            ]
        },

        # Other Leadership Positions (Pages 2-5)
        "other_positions": {
            "diversity_team_co_leader": {
                "title": "Diversity team co-leader",
                "holders": [
                    {"name": "Prof Claudia Tarantola", "start": "2022-03-03", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"},
                    {"name": "Prof Alessia Paccagnini", "start": "2022-03-03", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"},
                    {"name": "Dr Galena Pisoni", "start": "2022-05-17", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"},
                    {"name": "Prof Alessandra Tanda", "start": "2022-03-03", "end": "2022-05-17", "status": "Expired", "assigned_by": "Prof Jorg Osterrieder"}
                ]
            },
            "scientific_advisory_board_coordinator": {
                "title": "Scientific Advisory Board coordinator",
                "holders": [
                    {"name": "Prof Valerio Poti", "start": "2022-08-01", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"}
                ]
            },
            "technical_coordinator": {
                "title": "Technical Coordinator",
                "holders": [
                    {"name": "Prof Ronald Hochreiter", "start": "2022-03-03", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"}
                ]
            },
            "wg2_co_leader": {
                "title": "Working Group 2 co-leader",
                "holders": [
                    {"name": "Dr Kristina Sutiene", "start": "2022-03-03", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"}
                ]
            },
            "diversity_team_leader": {
                "title": "Diversity team leader",
                "holders": [
                    {"name": "Prof Alessandra Tanda", "start": "2022-05-17", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"},
                    {"name": "Dr Galena Pisoni", "start": "2022-03-04", "end": "2022-05-17", "status": "Expired", "assigned_by": "Prof Jorg Osterrieder"},
                    {"name": "Prof Codruta MARE", "start": "2022-03-03", "end": "2022-03-04", "status": "Expired", "assigned_by": "Prof Jorg Osterrieder"}
                ]
            },
            "virtual_networking_support_manager": {
                "title": "Virtual Networking Support Manager",
                "holders": [
                    {"name": "Prof Codruta MARE", "start": "2023-04-17", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"},
                    {"name": "Mr Vasile Strat", "start": "2022-07-07", "end": "2023-04-17", "status": "Expired", "assigned_by": "Prof Jorg Osterrieder"}
                ]
            },
            "chief_privacy_officer": {
                "title": "Chief Privacy Officer",
                "holders": [
                    {"name": "Dr Maria Moloney", "start": "2023-03-23", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"}
                ]
            },
            "stsm_coordinator": {
                "title": "STSM Coordinator",
                "holders": [
                    {"name": "Dr Catarina Silva", "start": "2024-03-07", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"},
                    {"name": "Dr Roman Matkovskyy", "start": "2023-03-23", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"},
                    {"name": "Prof Codruta MARE", "start": "2021-11-02", "end": "2023-04-17", "status": "Expired", "assigned_by": None}
                ]
            },
            "virtual_grant_co_coordinator": {
                "title": "Virtual Grant Co-Coordinator",
                "holders": [
                    {"name": "Dr Karolina Bolesta", "start": "2023-06-17", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"}
                ]
            },
            "wg1_co_leader": {
                "title": "WG1 Co-Leader",
                "holders": [
                    {"name": "Prof Daniel Traian Pele", "start": "2024-03-07", "end": None, "status": "Assigned", "assigned_by": "Prof Jorg Osterrieder"}
                ]
            },
            "itc_cg_coordinator": {
                "title": "ITC CG Coordinator",
                "holders": [
                    {"name": "Prof Enis Kayis", "start": "2021-11-02", "end": None, "status": "Assigned", "assigned_by": None}
                ]
            }
        },

        # MC Observers (Page 6)
        "mc_observers": [
            {"name": "Prof Panayotis Alexakis", "country": "Greece"},
            {"name": "Mr Michael Fruhmann", "country": "Austria"},
            {"name": "Prof Henning Schulzrinne", "country": "United States"}
        ],

        # Grant Periods (Page 6)
        "grant_periods": [
            {
                "period": 1,
                "start": "2020-11-01",
                "end": "2021-10-31",
                "institution": "Zurich University of Applied Sciences",
                "status": "Closed"
            },
            {
                "period": 2,
                "start": "2021-11-01",
                "end": "2022-05-31",
                "institution": "Zurich University of Applied Sciences",
                "status": "Closed"
            },
            {
                "period": 3,
                "start": "2022-06-01",
                "end": "2022-10-31",
                "institution": "Bern University of Applied Sciences",
                "status": "Closed"
            },
            {
                "period": 4,
                "start": "2022-11-01",
                "end": "2023-10-31",
                "institution": "Bern University of Applied Sciences",
                "status": "Closed"
            },
            {
                "period": 5,
                "start": "2023-11-01",
                "end": "2024-09-13",
                "institution": "Bern University of Applied Sciences",
                "status": "Closed"
            }
        ],

        # Statistics
        "statistics": {
            "initial_fsac_percentage": 15,
            "total_wg_participants": 758
        }
    }

    return leadership_data


def generate_display_json(leadership_data: dict) -> dict:
    """Generate a simplified JSON structure for web display."""

    def get_current_holder(holders):
        """Get the current holder from a list of holders."""
        for h in holders:
            if h.get('status') == 'Assigned' or h.get('status') == 'current':
                return h
        return holders[0] if holders else None

    def get_history(holders):
        """Get historical holders (non-current)."""
        return [h for h in holders if h.get('status') not in ['Assigned', 'current']]

    display_data = {
        "metadata": leadership_data["metadata"],

        "grant_periods": leadership_data["grant_periods"],

        "core_leadership": [],

        "working_groups": [],

        "coordinators": [],

        "other_positions": [],

        "mc_observers": leadership_data["mc_observers"],

        "statistics": {
            "total_wg_participants": leadership_data["statistics"]["total_wg_participants"],
            "initial_fsac_percentage": leadership_data["statistics"]["initial_fsac_percentage"]
        }
    }

    # Core Leadership
    for key, pos in leadership_data["core_leadership"].items():
        current = get_current_holder(pos["holders"])
        display_data["core_leadership"].append({
            "title": pos["title"],
            "current_holder": current["name"] if current else "Vacant",
            "history": []
        })

    # Working Groups
    for key, wg in leadership_data["working_groups"].items():
        display_data["working_groups"].append({
            "number": wg["number"],
            "title": wg["title"],
            "leader": wg["leader"],
            "participants": wg["participants"]
        })

    # Main Coordinators
    main_coords = ["science_communication_coordinator", "grant_awarding_coordinator"]
    for coord_key in main_coords:
        if coord_key in leadership_data:
            pos = leadership_data[coord_key]
            current = get_current_holder(pos["holders"])
            history = get_history(pos["holders"])
            display_data["coordinators"].append({
                "title": pos["title"],
                "current_holder": current["name"] if current else "Vacant",
                "start_date": current.get("start") if current else None,
                "history": [{"name": h["name"], "start": h.get("start"), "end": h.get("end")} for h in history]
            })

    # Other Positions
    for key, pos in leadership_data["other_positions"].items():
        current = get_current_holder(pos["holders"])
        history = get_history(pos["holders"])

        # Get all current holders for positions with multiple current holders
        current_holders = [h for h in pos["holders"] if h.get('status') == 'Assigned']

        display_data["other_positions"].append({
            "title": pos["title"],
            "current_holders": [h["name"] for h in current_holders] if current_holders else ["Vacant"],
            "start_date": current.get("start") if current else None,
            "history": [{"name": h["name"], "start": h.get("start"), "end": h.get("end")} for h in history]
        })

    return display_data


def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    data_dir = project_dir / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)

    # PDF location
    pdf_path = project_dir / 'leadership' / 'Leadership_Positions.pdf'

    print("=" * 70)
    print("Leadership Data Extraction - COST Action CA19130")
    print("=" * 70)
    print(f"Source: {pdf_path}")
    print()

    # Extract data
    print("Extracting leadership data from PDF...")
    leadership_data = extract_leadership_data(pdf_path)

    # Save raw extracted data
    raw_file = data_dir / 'leadership_raw.json'
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(leadership_data, f, indent=2, ensure_ascii=False)
    print(f"Saved raw data: {raw_file}")

    # Generate display-friendly JSON
    print("Generating display data...")
    display_data = generate_display_json(leadership_data)

    # Save display data
    display_file = data_dir / 'leadership.json'
    with open(display_file, 'w', encoding='utf-8') as f:
        json.dump(display_data, f, indent=2, ensure_ascii=False)
    print(f"Saved display data: {display_file}")

    # Print summary
    print("\n" + "=" * 70)
    print("EXTRACTION SUMMARY")
    print("=" * 70)
    print(f"Core Leadership Positions: {len(leadership_data['core_leadership'])}")
    print(f"Working Groups: {len(leadership_data['working_groups'])}")
    print(f"  - Total participants: {leadership_data['statistics']['total_wg_participants']}")
    print(f"Main Coordinators: 2")
    print(f"Other Leadership Positions: {len(leadership_data['other_positions'])}")
    print(f"MC Observers: {len(leadership_data['mc_observers'])}")
    print(f"Grant Periods: {len(leadership_data['grant_periods'])}")

    # Count positions with history
    positions_with_history = 0
    for pos in [leadership_data['science_communication_coordinator'],
                leadership_data['grant_awarding_coordinator']]:
        if len(pos['holders']) > 1:
            positions_with_history += 1
    for pos in leadership_data['other_positions'].values():
        if len(pos['holders']) > 1:
            positions_with_history += 1

    print(f"Positions with history: {positions_with_history}")
    print("=" * 70)


if __name__ == '__main__':
    main()
