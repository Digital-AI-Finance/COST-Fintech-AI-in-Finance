"""
Test Training Schools category totals.

Verifies training school expenditure across FFR -> JSON -> HTML chain.
Note: Training schools only occurred in GP4 and GP5.
"""

import pytest
from decimal import Decimal


class TestTrainingSchoolsTotals:
    """Tests for Training Schools category totals."""

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_ffr_ts_extraction(self, ffr_parser, gp):
        """FFR parser extracts training schools category correctly."""
        data = ffr_parser.parse_grant_period(gp)

        # Training schools category should exist
        assert 'training_schools' in data.categories, f"GP{gp}: training_schools not found"

        ts_actual = data.categories['training_schools'].actuals

        # GP1-3 should have 0, GP4-5 should have positive amounts
        if gp <= 3:
            assert ts_actual == Decimal("0.00"), \
                f"GP{gp}: Training schools should be 0, got {ts_actual}"
        else:
            assert ts_actual > Decimal("0.00"), \
                f"GP{gp}: Training schools should be positive, got {ts_actual}"

    @pytest.mark.parametrize("gp,expected", [
        (4, Decimal("49401.09")),  # GP4 training schools
        (5, Decimal("59414.96")),  # GP5 training schools
    ])
    def test_ts_known_values(self, ffr_parser, gp, expected):
        """Verify known training school values from FFR files."""
        data = ffr_parser.parse_grant_period(gp)

        if 'training_schools' in data.categories:
            actual = data.categories['training_schools'].actuals
            assert abs(actual - expected) <= Decimal("100.00"), \
                f"GP{gp}: TS actual {actual} != expected {expected}"

    def test_ts_total_across_all_gps(self, all_ffr_data):
        """Sum of training schools should match expected grand total."""
        total_ts = sum(
            data.categories.get('training_schools', type('', (), {'actuals': Decimal("0.00")})()).actuals
            for data in all_ffr_data.values()
        )

        # Expected: 108,816.05 EUR total
        expected = Decimal("108816.05")
        tolerance = Decimal("500.00")

        diff = abs(total_ts - expected)
        assert diff <= tolerance, f"TS total {total_ts} differs from expected {expected} by {diff}"


class TestTrainingSchoolsJSON:
    """Tests for training school data in JSON files."""

    def test_json_ts_count(self, training_schools):
        """JSON should contain expected number of training schools."""
        # Expected: 7 training schools
        assert len(training_schools) >= 6, f"Too few TSs in JSON: {len(training_schools)}"
        assert len(training_schools) <= 10, f"Too many TSs in JSON: {len(training_schools)}"

    @pytest.mark.skip(reason="JSON lacks attendees/trainees data - needs data extraction")
    def test_json_ts_trainees_count(self, training_schools):
        """Total trainees should match expected count.

        NOTE: The training_school_attendees.json currently lacks attendee lists.
        Training school records have: id, grant_period, school_number, dates, etc.
        But no 'attendees' or 'trainees' array with individual trainee data.

        This test is skipped until trainee data is extracted from FFR source.
        """
        total_trainees = sum(
            len(ts.get('attendees', ts.get('trainees', [])))
            for ts in training_schools
        )

        # Expected: 96 trainees total
        assert total_trainees >= 80, f"Too few trainees: {total_trainees}"
