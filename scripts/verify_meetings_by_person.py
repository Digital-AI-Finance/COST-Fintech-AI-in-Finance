#!/usr/bin/env python3
"""
Verify meeting reimbursements by person and event.
Cross-checks individual participant amounts against meeting sub-totals.
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

def main():
    # Load meetings data
    meetings_path = DATA_DIR / "meetings_detailed.json"
    with open(meetings_path, 'r', encoding='utf-8') as f:
        meetings = json.load(f)

    print("=" * 80)
    print("MEETING REIMBURSEMENTS - VERIFICATION BY PERSON AND EVENT")
    print("=" * 80)

    # Statistics
    total_participants = 0
    total_amount = 0.0
    participant_totals = defaultdict(lambda: {"count": 0, "total": 0.0, "meetings": []})
    country_totals = defaultdict(lambda: {"count": 0, "total": 0.0})
    meeting_verification = []

    # Process each meeting
    for m in meetings:
        if m["total_expenditure"] == 0:
            continue

        meeting_id = m["id"]
        city = m["city"] or "Unknown"
        country = m["country"] or "Unknown"
        date = m["start_date"] or "Unknown"
        gp = m["grant_period"]

        # Sum participant amounts
        participant_sum = sum(p["total"] for p in m["participants"])
        los = m["los_grant"]
        expected_total = m["participant_subtotal"] + los

        # Verify
        diff = abs(participant_sum - m["participant_subtotal"])
        status = "OK" if diff < 1.0 else "MISMATCH"

        meeting_verification.append({
            "id": meeting_id,
            "gp": gp,
            "city": city,
            "date": date,
            "participants": len(m["participants"]),
            "participant_sum": participant_sum,
            "reported_subtotal": m["participant_subtotal"],
            "los": los,
            "total": m["total_expenditure"],
            "diff": diff,
            "status": status
        })

        # Aggregate by participant
        for p in m["participants"]:
            name = p["name"]
            participant_totals[name]["count"] += 1
            participant_totals[name]["total"] += p["total"]
            participant_totals[name]["meetings"].append({
                "meeting": f"{city} ({date})",
                "amount": p["total"]
            })
            participant_totals[name]["country"] = p["country"]

            country_totals[p["country"]]["count"] += 1
            country_totals[p["country"]]["total"] += p["total"]

            total_participants += 1
            total_amount += p["total"]

    # Print meeting-level verification
    print(f"\n{'=' * 80}")
    print("VERIFICATION BY MEETING")
    print(f"{'=' * 80}")
    print(f"{'Meeting ID':<12} {'City':<20} {'Date':<12} {'#Part':>6} {'Sum':>12} {'Subtotal':>12} {'LOS':>10} {'Status':<8}")
    print("-" * 100)

    all_ok = True
    for v in meeting_verification:
        status_marker = "OK" if v["status"] == "OK" else "FAIL"
        if v["status"] != "OK":
            all_ok = False
        print(f"{v['id']:<12} {v['city']:<20} {v['date']:<12} {v['participants']:>6} "
              f"{v['participant_sum']:>12,.2f} {v['reported_subtotal']:>12,.2f} {v['los']:>10,.2f} {status_marker:<8}")

    print("-" * 100)
    print(f"{'TOTAL':<12} {'':<20} {'':<12} {total_participants:>6} {total_amount:>12,.2f}")

    # Print top participants by reimbursement
    print(f"\n{'=' * 80}")
    print("TOP 30 PARTICIPANTS BY TOTAL REIMBURSEMENT")
    print(f"{'=' * 80}")
    print(f"{'Rank':>4} {'Name':<40} {'Country':>8} {'#Meetings':>10} {'Total EUR':>12}")
    print("-" * 80)

    sorted_participants = sorted(participant_totals.items(), key=lambda x: x[1]["total"], reverse=True)
    for i, (name, data) in enumerate(sorted_participants[:30], 1):
        print(f"{i:>4} {name:<40} {data['country']:>8} {data['count']:>10} {data['total']:>12,.2f}")

    # Print by country
    print(f"\n{'=' * 80}")
    print("REIMBURSEMENTS BY COUNTRY")
    print(f"{'=' * 80}")
    print(f"{'Country':<10} {'#Reimbursements':>15} {'Total EUR':>15} {'Avg EUR':>12}")
    print("-" * 60)

    sorted_countries = sorted(country_totals.items(), key=lambda x: x[1]["total"], reverse=True)
    for country, data in sorted_countries:
        avg = data["total"] / data["count"] if data["count"] > 0 else 0
        print(f"{country:<10} {data['count']:>15} {data['total']:>15,.2f} {avg:>12,.2f}")

    # Print detailed per-person breakdown for first 50 participants
    print(f"\n{'=' * 80}")
    print("DETAILED REIMBURSEMENT LOG (All Participants)")
    print(f"{'=' * 80}")

    # Create full participant log
    all_reimbursements = []
    for m in meetings:
        for p in m["participants"]:
            all_reimbursements.append({
                "name": p["name"],
                "country": p["country"],
                "meeting": m["city"] or "Unknown",
                "date": m["start_date"] or "Unknown",
                "gp": m["grant_period"],
                "travel": p["travel_allowance"],
                "daily": p["daily_allowance"],
                "other": p["other_expenses"],
                "total": p["total"]
            })

    # Sort by name, then by date
    all_reimbursements.sort(key=lambda x: (x["name"], x["date"]))

    print(f"{'Name':<35} {'Country':>4} {'GP':>3} {'Meeting':<15} {'Date':<12} {'Travel':>10} {'Daily':>10} {'Other':>8} {'Total':>10}")
    print("-" * 120)

    for r in all_reimbursements:
        meeting_short = r["meeting"][:15] if r["meeting"] else "Unknown"
        print(f"{r['name']:<35} {r['country']:>4} {r['gp']:>3} {meeting_short:<15} {r['date']:<12} "
              f"{r['travel']:>10,.2f} {r['daily']:>10,.2f} {r['other']:>8,.2f} {r['total']:>10,.2f}")

    print("-" * 120)
    print(f"{'GRAND TOTAL':<35} {'':<4} {'':<3} {'':<15} {'':<12} "
          f"{sum(r['travel'] for r in all_reimbursements):>10,.2f} "
          f"{sum(r['daily'] for r in all_reimbursements):>10,.2f} "
          f"{sum(r['other'] for r in all_reimbursements):>8,.2f} "
          f"{sum(r['total'] for r in all_reimbursements):>10,.2f}")

    # Save report
    report = {
        "generated": datetime.now().isoformat(),
        "summary": {
            "total_meetings_with_costs": len(meeting_verification),
            "total_reimbursements": total_participants,
            "total_amount": total_amount,
            "unique_participants": len(participant_totals),
            "all_meetings_verified": all_ok
        },
        "by_meeting": meeting_verification,
        "by_participant": [
            {
                "name": name,
                "country": data["country"],
                "reimbursement_count": data["count"],
                "total_amount": data["total"],
                "meetings": data["meetings"]
            }
            for name, data in sorted_participants
        ],
        "by_country": [
            {
                "country": country,
                "reimbursement_count": data["count"],
                "total_amount": data["total"]
            }
            for country, data in sorted_countries
        ],
        "all_reimbursements": all_reimbursements
    }

    report_path = REPORTS_DIR / "meetings_by_person_verification.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nDetailed report saved to: {report_path}")

    # Final summary
    print(f"\n{'=' * 80}")
    print("VERIFICATION SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total Meetings with Costs: {len(meeting_verification)}")
    print(f"Total Reimbursements: {total_participants}")
    print(f"Unique Participants: {len(participant_totals)}")
    print(f"Total Amount: {total_amount:,.2f} EUR")
    print(f"All Meetings Verified: {'YES' if all_ok else 'NO'}")

    return report


if __name__ == "__main__":
    main()
