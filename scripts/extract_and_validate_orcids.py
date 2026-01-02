"""
Extract and validate all ORCIDs from COST Action CA19130 member data.
Performs format validation and optional API validation.

Tests:
1. Format validation (XXXX-XXXX-XXXX-XXXX or XXXX-XXXX-XXXX-XXXY)
2. Checksum validation (ORCID uses ISO 7064 Mod 11-2)
3. Optional: API validation (checks if ORCID exists)

Usage:
    python extract_and_validate_orcids.py [--validate-api]
"""
import pandas as pd
import json
import re
import sys
import time
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import urllib.request
import urllib.error


def calculate_orcid_checksum(orcid_digits: str) -> str:
    """
    Calculate ORCID checksum using ISO 7064 Mod 11-2 algorithm.
    Returns expected check digit (0-9 or X).
    """
    total = 0
    for digit in orcid_digits[:15]:  # First 15 digits
        total = (total + int(digit)) * 2
    remainder = total % 11
    result = (12 - remainder) % 11
    return 'X' if result == 10 else str(result)


def validate_orcid_format(orcid: str) -> Tuple[bool, str]:
    """
    Validate ORCID format and checksum.
    Returns (is_valid, error_message).
    """
    if not orcid:
        return False, "Empty ORCID"

    orcid = str(orcid).strip()

    # Check format: XXXX-XXXX-XXXX-XXXX or XXXX-XXXX-XXXX-XXXY
    pattern = r'^(\d{4})-(\d{4})-(\d{4})-(\d{3}[\dX])$'
    match = re.match(pattern, orcid)

    if not match:
        return False, f"Invalid format: {orcid}"

    # Extract digits and check digit
    digits = ''.join(match.groups())
    check_digit = digits[-1]

    # Validate checksum
    expected_check = calculate_orcid_checksum(digits)
    if check_digit != expected_check:
        return False, f"Invalid checksum: expected {expected_check}, got {check_digit}"

    return True, "Valid"


def validate_orcid_api(orcid: str, timeout: int = 10) -> Tuple[bool, str]:
    """
    Validate ORCID exists via ORCID public API.
    Returns (exists, message).
    """
    url = f"https://pub.orcid.org/v3.0/{orcid}"
    headers = {"Accept": "application/json"}

    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                name = data.get('person', {}).get('name', {})
                given = name.get('given-names', {}).get('value', '')
                family = name.get('family-name', {}).get('value', '')
                return True, f"Found: {given} {family}".strip()
            return False, f"HTTP {response.status}"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, "ORCID not found (404)"
        return False, f"HTTP Error {e.code}"
    except urllib.error.URLError as e:
        return False, f"URL Error: {e.reason}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def extract_orcids_from_excel(excel_path: Path) -> List[Dict]:
    """
    Extract all ORCIDs with member info from Excel file.
    Returns list of dicts with member info and ORCID.
    """
    df = pd.read_excel(excel_path)

    members_with_orcids = []
    members_without_orcids = []

    for idx, row in df.iterrows():
        first_name = str(row.get('First Name', '')).strip() if pd.notna(row.get('First Name')) else ''
        last_name = str(row.get('Last Name', '')).strip() if pd.notna(row.get('Last Name')) else ''

        if not first_name and not last_name:
            continue

        member = {
            'row': idx + 2,  # Excel row (1-indexed + header)
            'firstName': first_name,
            'lastName': last_name,
            'name': f"{first_name} {last_name}".strip(),
            'affiliation': str(row.get('Affiliation', '')).strip() if pd.notna(row.get('Affiliation')) else None,
            'country': str(row.get('Country', '')).strip() if pd.notna(row.get('Country')) else None,
            'email': str(row.get('Email', '')).strip() if pd.notna(row.get('Email')) else None,
        }

        orcid = row.get('Orcid')
        if pd.notna(orcid) and str(orcid).strip():
            member['orcid'] = str(orcid).strip()
            members_with_orcids.append(member)
        else:
            member['orcid'] = None
            members_without_orcids.append(member)

    return members_with_orcids, members_without_orcids


def run_validation(validate_api: bool = False):
    """
    Run full ORCID extraction and validation.
    """
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    excel_path = project_dir / 'working_groups_members' / 'CA19130-WG-members.xlsx'
    output_dir = project_dir / 'data'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("COST Action CA19130 - ORCID Extraction and Validation")
    print("=" * 70)
    print(f"\nSource: {excel_path}")
    print(f"API Validation: {'Enabled' if validate_api else 'Disabled'}")
    print()

    # Extract ORCIDs
    print("Step 1: Extracting ORCIDs from Excel...")
    members_with_orcids, members_without_orcids = extract_orcids_from_excel(excel_path)

    total_members = len(members_with_orcids) + len(members_without_orcids)
    print(f"  Total members: {total_members}")
    print(f"  Members with ORCID: {len(members_with_orcids)}")
    print(f"  Members without ORCID: {len(members_without_orcids)}")

    # Format validation
    print("\nStep 2: Validating ORCID formats...")
    valid_format = []
    invalid_format = []

    for member in members_with_orcids:
        is_valid, message = validate_orcid_format(member['orcid'])
        member['format_valid'] = is_valid
        member['format_message'] = message

        if is_valid:
            valid_format.append(member)
        else:
            invalid_format.append(member)

    print(f"  Valid format: {len(valid_format)}")
    print(f"  Invalid format: {len(invalid_format)}")

    if invalid_format:
        print("\n  Invalid format ORCIDs:")
        for m in invalid_format:
            print(f"    Row {m['row']}: {m['name']} - {m['orcid']} ({m['format_message']})")

    # API validation (optional)
    api_validated = []
    api_failed = []

    if validate_api and valid_format:
        print(f"\nStep 3: Validating ORCIDs via API ({len(valid_format)} to check)...")
        print("  This may take a few minutes...")

        for i, member in enumerate(valid_format):
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{len(valid_format)}")

            exists, message = validate_orcid_api(member['orcid'])
            member['api_valid'] = exists
            member['api_message'] = message

            if exists:
                api_validated.append(member)
            else:
                api_failed.append(member)

            # Rate limiting: 1 request per second
            time.sleep(0.5)

        print(f"\n  API validated: {len(api_validated)}")
        print(f"  API failed: {len(api_failed)}")

        if api_failed:
            print("\n  Failed API validation:")
            for m in api_failed[:10]:  # Show first 10
                print(f"    {m['name']} - {m['orcid']} ({m['api_message']})")
            if len(api_failed) > 10:
                print(f"    ... and {len(api_failed) - 10} more")

    # Create output
    print("\nStep 4: Generating output files...")

    # Prepare validated ORCIDs list
    validated_orcids = api_validated if validate_api else valid_format

    # Create output with all info
    output_data = {
        'metadata': {
            'source': str(excel_path),
            'total_members': total_members,
            'members_with_orcid': len(members_with_orcids),
            'members_without_orcid': len(members_without_orcids),
            'valid_format': len(valid_format),
            'invalid_format': len(invalid_format),
            'api_validated': len(api_validated) if validate_api else None,
            'api_failed': len(api_failed) if validate_api else None,
            'validation_date': pd.Timestamp.now().isoformat()
        },
        'validated_orcids': [
            {
                'orcid': m['orcid'],
                'name': m['name'],
                'firstName': m['firstName'],
                'lastName': m['lastName'],
                'affiliation': m['affiliation'],
                'country': m['country']
            }
            for m in validated_orcids
        ],
        'invalid_orcids': [
            {
                'orcid': m['orcid'],
                'name': m['name'],
                'error': m['format_message']
            }
            for m in invalid_format
        ],
        'members_without_orcid': [
            {
                'name': m['name'],
                'affiliation': m['affiliation'],
                'country': m['country']
            }
            for m in members_without_orcids
        ]
    }

    # Save main output
    output_file = output_dir / 'validated_orcids.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {output_file}")

    # Save simple ORCID list for publication fetching
    orcid_list_file = output_dir / 'orcid_list.json'
    orcid_list = [
        {'orcid': m['orcid'], 'name': m['name']}
        for m in validated_orcids
    ]
    with open(orcid_list_file, 'w', encoding='utf-8') as f:
        json.dump(orcid_list, f, indent=2, ensure_ascii=False)
    print(f"  Saved: {orcid_list_file}")

    # Print summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total members:           {total_members}")
    print(f"Members with ORCID:      {len(members_with_orcids)} ({100*len(members_with_orcids)/total_members:.1f}%)")
    print(f"Valid ORCIDs:            {len(valid_format)}")
    print(f"Invalid ORCIDs:          {len(invalid_format)}")
    if validate_api:
        print(f"API Validated:           {len(api_validated)}")
        print(f"API Failed:              {len(api_failed)}")
    print(f"\nORCIDs ready for publication fetch: {len(validated_orcids)}")
    print("=" * 70)

    # Return success status
    return len(invalid_format) == 0


def test_orcid_validation():
    """
    Unit tests for ORCID validation functions.
    """
    print("\n" + "=" * 70)
    print("RUNNING ORCID VALIDATION TESTS")
    print("=" * 70)

    tests_passed = 0
    tests_failed = 0

    # Test cases: (orcid, expected_valid, description)
    test_cases = [
        # Valid ORCIDs (real examples)
        ("0000-0002-9648-4438", True, "Valid ORCID with checksum 8"),
        ("0000-0001-5000-0007", True, "Valid ORCID with checksum 7"),
        ("0000-0002-1825-0097", True, "Valid ORCID - ORCID example"),
        ("0000-0002-1694-233X", True, "Valid ORCID with X checksum"),

        # Invalid ORCIDs
        ("0000-0002-9648-4439", False, "Invalid checksum"),
        ("0000-0002-9648-443", False, "Too short"),
        ("0000-0002-9648-44388", False, "Too long"),
        ("0000-0002-9648-443A", False, "Invalid character A"),
        ("000-0002-9648-4438", False, "Missing digit in first group"),
        ("0000-0002-96484438", False, "Missing hyphen"),
        ("", False, "Empty string"),
        ("invalid", False, "Not an ORCID"),
    ]

    for orcid, expected_valid, description in test_cases:
        is_valid, message = validate_orcid_format(orcid)

        if is_valid == expected_valid:
            status = "PASS"
            tests_passed += 1
        else:
            status = "FAIL"
            tests_failed += 1

        print(f"  [{status}] {description}")
        print(f"         ORCID: {orcid}")
        print(f"         Expected: {'Valid' if expected_valid else 'Invalid'}, Got: {'Valid' if is_valid else 'Invalid'}")
        if not is_valid:
            print(f"         Message: {message}")
        print()

    print("-" * 70)
    print(f"Tests passed: {tests_passed}/{tests_passed + tests_failed}")
    print("-" * 70)

    return tests_failed == 0


if __name__ == '__main__':
    # Run unit tests first
    tests_ok = test_orcid_validation()

    if not tests_ok:
        print("\nERROR: Unit tests failed. Please fix before proceeding.")
        sys.exit(1)

    # Check for API validation flag
    validate_api = '--validate-api' in sys.argv

    # Run main validation
    success = run_validation(validate_api=validate_api)

    sys.exit(0 if success else 1)
