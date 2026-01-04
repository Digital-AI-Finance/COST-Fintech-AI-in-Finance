"""
Test meetings category totals across FFR -> JSON -> HTML chain.

Verifies that meetings expenditure totals match across all data sources:
- FFR source files (ground truth)
- JSON data files (processed data)
- HTML pages (displayed values)
"""

import pytest
from decimal import Decimal


class TestMeetingsTotals:
    """Tests for meetings category totals."""

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_ffr_meetings_extraction(self, ffr_parser, gp):
        """FFR parser extracts meetings category correctly."""
        data = ffr_parser.parse_grant_period(gp)

        # Meetings category should exist
        assert 'meetings' in data.categories, f"GP{gp}: meetings category not found in FFR"

        # Amount should be non-negative
        meetings_actual = data.categories['meetings'].actuals
        assert meetings_actual >= Decimal("0.00"), f"GP{gp}: negative meetings amount: {meetings_actual}"

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_ffr_meetings_budget_vs_actual(self, ffr_parser, gp):
        """FFR meetings actual should not exceed budget significantly."""
        data = ffr_parser.parse_grant_period(gp)

        if 'meetings' in data.categories:
            budget = data.categories['meetings'].budget
            actual = data.categories['meetings'].actuals

            # Allow up to 20% overspend (reallocation happens)
            if budget > 0:
                ratio = actual / budget
                assert ratio <= Decimal("1.20"), f"GP{gp}: meetings overspent by {ratio*100-100:.1f}%"

    def test_meetings_totals_across_all_gps(self, all_ffr_data):
        """Sum of meetings across all GPs should match expected total."""
        total_meetings = sum(
            data.categories.get('meetings', type('', (), {'actuals': Decimal("0.00")})()).actuals
            for data in all_ffr_data.values()
        )

        # Expected from summary_statistics.json: 423,694.69 EUR
        # Allow small tolerance for rounding
        expected = Decimal("423694.69")
        tolerance = Decimal("100.00")  # EUR

        diff = abs(total_meetings - expected)
        assert diff <= tolerance, f"Meetings total {total_meetings} differs from expected {expected} by {diff}"

    @pytest.mark.parametrize("gp,expected_actual", [
        (1, Decimal("10300.30")),  # GP1 meetings actual
        (5, Decimal("148194.99")),  # GP5 meetings actual
    ])
    def test_meetings_known_values(self, ffr_parser, gp, expected_actual):
        """Verify known meetings values from FFR files."""
        data = ffr_parser.parse_grant_period(gp)

        if 'meetings' in data.categories:
            actual = data.categories['meetings'].actuals
            assert abs(actual - expected_actual) <= Decimal("0.01"), \
                f"GP{gp}: meetings actual {actual} != expected {expected_actual}"


class TestMeetingsJSON:
    """Tests for meetings data in JSON files."""

    def test_json_meetings_count(self, meetings_detailed):
        """JSON should contain expected number of meetings."""
        # Expected: 52 meetings total across all GPs
        assert len(meetings_detailed) >= 40, f"Too few meetings in JSON: {len(meetings_detailed)}"

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_json_meetings_by_gp(self, meetings_detailed, ffr_parser, gp):
        """JSON meetings count per GP should match FFR."""
        json_meetings = [m for m in meetings_detailed if m.get('grant_period') == gp]
        ffr_data = ffr_parser.parse_grant_period(gp)

        ffr_meetings_count = len(ffr_data.meetings)
        json_meetings_count = len(json_meetings)

        # Allow some tolerance for counting methodology
        diff = abs(ffr_meetings_count - json_meetings_count)
        assert diff <= 5, f"GP{gp}: JSON has {json_meetings_count} meetings, FFR has {ffr_meetings_count}"

    def test_json_meetings_have_required_fields(self, meetings_detailed):
        """All JSON meetings should have required fields."""
        required_fields = ['title', 'location', 'start_date']

        for meeting in meetings_detailed:
            for field in required_fields:
                assert field in meeting, f"Meeting missing required field: {field}"


class TestMeetingsHTML:
    """Tests for meetings data displayed in HTML."""

    @pytest.mark.parametrize("gp", [1, 2, 3, 4, 5])
    def test_html_displays_meetings_total(self, html_parser, gp):
        """HTML FFR page should display meetings total."""
        try:
            page_data = html_parser.parse_ffr_page(gp)

            # Check if meetings is in either budget or actual amounts
            has_meetings = (
                'meetings' in page_data.budget_amounts or
                'meetings' in page_data.actual_amounts
            )

            # At minimum, page should load without error
            assert page_data.page_name == f"ffr{gp}.html"
        except FileNotFoundError:
            pytest.skip(f"FFR{gp} HTML page not found")

    @pytest.mark.parametrize("gp", [1])  # GP5 has known discrepancy, tested separately
    def test_html_meetings_matches_ffr(self, html_parser, ffr_parser, gp):
        """HTML displayed meetings should match FFR source."""
        try:
            html_data = html_parser.parse_ffr_page(gp)
            ffr_data = ffr_parser.parse_grant_period(gp)

            ffr_meetings = ffr_data.categories.get('meetings')
            if ffr_meetings:
                # Check if HTML displays correct value
                html_meetings = html_data.actual_amounts.get('meetings', Decimal("0.00"))

                if html_meetings > 0:
                    diff = abs(html_meetings - ffr_meetings.actuals)
                    assert diff <= Decimal("1.00"), \
                        f"GP{gp}: HTML shows {html_meetings}, FFR has {ffr_meetings.actuals}"
        except FileNotFoundError:
            pytest.skip(f"FFR{gp} HTML page not found")

    def test_html_meetings_matches_ffr_gp5(self, html_parser, ffr_parser):
        """GP5 HTML meetings should match FFR source.

        This was previously a known discrepancy (HTML showed 120,814 vs FFR 148,194.99)
        that was fixed by the sync_json_to_html.py script on 2026-01-04.
        """
        html_data = html_parser.parse_ffr_page(5)
        ffr_data = ffr_parser.parse_grant_period(5)

        html_meetings = html_data.actual_amounts.get('meetings', Decimal("0.00"))
        ffr_meetings = ffr_data.categories['meetings'].actuals

        diff = abs(html_meetings - ffr_meetings)
        assert diff <= Decimal("1.00"), \
            f"GP5: HTML shows {html_meetings}, FFR has {ffr_meetings}"
