# Mobile Volume Index Overlay — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Overlay mobile volume indexes onto impact data so econometricians can evaluate whether mobile footfall is a useful adjustment factor for OOH audience impacts.

**Architecture:** Analyst-provided CSV (frame_id, date, hour, index) is imported into a new PostgreSQL table. New query functions LEFT JOIN this table to the existing 15-min impact data, returning both raw and indexed impacts. The Time Series and Detailed Analysis tabs show dual-line charts when a toggle is enabled. Exports include raw, index, and indexed columns.

**Tech Stack:** PostgreSQL, Python 3.11, psycopg2, pandas, Streamlit, Plotly, pytest

**Branch:** `feature/mobile-volume-index`

---

## Task 1: Create Feature Branch

**Step 1: Create and switch to feature branch**

Run: `git checkout -b feature/mobile-volume-index`

**Step 2: Verify**

Run: `git branch --show-current`
Expected: `feature/mobile-volume-index`

---

## Task 2: Date-Shifting Utility

**Files:**
- Create: `src/utils/date_shift.py`
- Create: `tests/unit/test_date_shift.py`

This utility maps 2024 dates to the same day-of-week in 2025. Wed 28 Aug 2024 -> Wed 27 Aug 2025.

**Step 1: Write failing tests**

```python
# tests/unit/test_date_shift.py
# ABOUTME: Tests for 2024-to-2025 date shifting utility
# ABOUTME: Verifies day-of-week alignment for mobile index date mapping

import pytest
from datetime import date
from src.utils.date_shift import shift_date_to_2025


class TestShiftDateTo2025:
    """Tests for shift_date_to_2025 date-shifting function."""

    def test_wednesday_maps_to_wednesday(self):
        """Wed 28 Aug 2024 -> Wed 27 Aug 2025."""
        result = shift_date_to_2025(date(2024, 8, 28))
        assert result.weekday() == 2  # Wednesday
        assert result.year == 2025

    def test_monday_maps_to_monday(self):
        """Mon 1 Jul 2024 -> Mon 30 Jun 2025."""
        result = shift_date_to_2025(date(2024, 7, 1))
        assert result.weekday() == 0  # Monday
        assert result.year == 2025

    def test_sunday_maps_to_sunday(self):
        """Sun 4 Aug 2024 -> Sun 3 Aug 2025."""
        result = shift_date_to_2025(date(2024, 8, 4))
        assert result.weekday() == 6  # Sunday
        assert result.year == 2025

    def test_preserves_iso_week(self):
        """Same ISO week number in both years."""
        original = date(2024, 8, 28)
        shifted = shift_date_to_2025(original)
        assert original.isocalendar()[1] == shifted.isocalendar()[1]

    def test_january_date(self):
        """Handles dates near year boundary."""
        result = shift_date_to_2025(date(2024, 1, 3))  # Wed
        assert result.weekday() == 2  # Wednesday
        assert result.year == 2025

    def test_december_date(self):
        """Handles late December dates."""
        result = shift_date_to_2025(date(2024, 12, 25))  # Wed
        assert result.weekday() == 2  # Wednesday
        assert result.year == 2025

    def test_saturday_maps_to_saturday(self):
        """Sat stays Sat — critical for weekday vs weekend patterns."""
        result = shift_date_to_2025(date(2024, 8, 31))  # Sat
        assert result.weekday() == 5  # Saturday
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_date_shift.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.utils.date_shift'`

**Step 3: Write minimal implementation**

```python
# src/utils/date_shift.py
# ABOUTME: Maps 2024 dates to the same day-of-week in 2025 using ISO week alignment
# ABOUTME: Used by mobile volume index import to align 2024 mobile data with 2025 playout dates

from datetime import date


def shift_date_to_2025(date_2024: date) -> date:
    """Map a 2024 date to the same day-of-week in the same ISO week in 2025.

    Args:
        date_2024: A date in 2024 to shift.

    Returns:
        The corresponding date in 2025 with the same ISO week number
        and day-of-week.

    Example:
        >>> shift_date_to_2025(date(2024, 8, 28))  # Wed, ISO week 35
        date(2025, 8, 27)  # Wed, ISO week 35
    """
    iso_year, iso_week, iso_weekday = date_2024.isocalendar()
    return date.fromisocalendar(2025, iso_week, iso_weekday)
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_date_shift.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add src/utils/date_shift.py tests/unit/test_date_shift.py
git commit -m "feat: add 2024-to-2025 date-shifting utility for mobile index import"
```

---

## Task 3: CSV Import Script

**Files:**
- Create: `scripts/import_mobile_index.py`
- Create: `tests/unit/test_import_mobile_index.py`

**Step 1: Write failing tests**

```python
# tests/unit/test_import_mobile_index.py
# ABOUTME: Tests for mobile volume index CSV import and date-shifting logic
# ABOUTME: Verifies CSV parsing, date mapping, and SQL generation

import pytest
import csv
import os
from datetime import date
from pathlib import Path
from scripts.import_mobile_index import parse_mobile_index_csv


class TestParseMobileIndexCSV:
    """Tests for CSV parsing with date-shifting."""

    def test_parses_csv_with_date_shift(self, tmp_path):
        """Parses CSV and shifts dates from 2024 to 2025."""
        csv_file = tmp_path / "test_index.csv"
        csv_file.write_text(
            "frameid,date,hour,index_value\n"
            "1234571069,2024-08-28,14,1.23\n"
            "1234571069,2024-08-28,15,0.87\n"
        )
        rows = parse_mobile_index_csv(str(csv_file))
        assert len(rows) == 2
        assert rows[0]["frameid"] == 1234571069
        assert rows[0]["date_2024"] == date(2024, 8, 28)
        assert rows[0]["date_2025"].weekday() == 2  # Wednesday
        assert rows[0]["date_2025"].year == 2025
        assert rows[0]["hour"] == 14
        assert rows[0]["index_value"] == 1.23

    def test_handles_index_below_one(self, tmp_path):
        """Index values below 1.0 are valid (below average)."""
        csv_file = tmp_path / "test_index.csv"
        csv_file.write_text(
            "frameid,date,hour,index_value\n"
            "1234571069,2024-08-28,3,0.12\n"
        )
        rows = parse_mobile_index_csv(str(csv_file))
        assert rows[0]["index_value"] == 0.12

    def test_empty_csv_returns_empty_list(self, tmp_path):
        """Empty CSV (header only) returns empty list."""
        csv_file = tmp_path / "test_index.csv"
        csv_file.write_text("frameid,date,hour,index_value\n")
        rows = parse_mobile_index_csv(str(csv_file))
        assert rows == []
```

**Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_import_mobile_index.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write implementation**

```python
# scripts/import_mobile_index.py
# ABOUTME: Imports mobile volume index CSV into PostgreSQL mobile_volume_index table
# ABOUTME: Handles CSV parsing, 2024-to-2025 date shifting, and bulk database insert

import argparse
import csv
import logging
import sys
from datetime import date
from typing import List, Dict

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

from src.db.queries.connection import get_db_connection
from src.utils.date_shift import shift_date_to_2025

load_dotenv()
logger = logging.getLogger(__name__)


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS mobile_volume_index (
    frameid BIGINT NOT NULL,
    date_2024 DATE NOT NULL,
    hour SMALLINT NOT NULL,
    index_value NUMERIC NOT NULL,
    date_2025 DATE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_mobile_volume_index_lookup
    ON mobile_volume_index (frameid, date_2025, hour);
"""

TRUNCATE_SQL = "TRUNCATE TABLE mobile_volume_index;"

INSERT_SQL = """
INSERT INTO mobile_volume_index (frameid, date_2024, hour, index_value, date_2025)
VALUES %s
"""


def parse_mobile_index_csv(csv_path: str) -> List[Dict]:
    """Parse mobile index CSV and shift dates to 2025.

    Args:
        csv_path: Path to CSV file with columns: frameid, date, hour, index_value

    Returns:
        List of dicts with keys: frameid, date_2024, hour, index_value, date_2025
    """
    rows = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_2024 = date.fromisoformat(row["date"])
            rows.append({
                "frameid": int(row["frameid"]),
                "date_2024": date_2024,
                "hour": int(row["hour"]),
                "index_value": float(row["index_value"]),
                "date_2025": shift_date_to_2025(date_2024),
            })
    return rows


def import_to_database(rows: List[Dict], use_primary: bool = None) -> int:
    """Import parsed rows into mobile_volume_index table.

    Creates the table if it doesn't exist. Truncates before insert (re-runnable).

    Args:
        rows: Parsed CSV rows from parse_mobile_index_csv()
        use_primary: Database selection

    Returns:
        Number of rows inserted
    """
    conn = get_db_connection(use_primary)
    try:
        with conn.cursor() as cursor:
            cursor.execute(CREATE_TABLE_SQL)
            cursor.execute(TRUNCATE_SQL)

            # Bulk insert in batches of 10,000
            batch_size = 10000
            tuples = [
                (r["frameid"], r["date_2024"], r["hour"], r["index_value"], r["date_2025"])
                for r in rows
            ]

            for i in range(0, len(tuples), batch_size):
                batch = tuples[i:i + batch_size]
                psycopg2.extras.execute_values(cursor, INSERT_SQL, batch)
                logger.info(
                    "Inserted batch %d-%d of %d",
                    i, min(i + batch_size, len(tuples)), len(tuples),
                )

            conn.commit()
            return len(tuples)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Import mobile volume index CSV")
    parser.add_argument("csv_path", help="Path to the mobile index CSV file")
    parser.add_argument("--primary", action="store_true", help="Use primary database")
    args = parser.parse_args()

    logger.info("Parsing CSV: %s", args.csv_path)
    rows = parse_mobile_index_csv(args.csv_path)
    logger.info("Parsed %d rows", len(rows))

    count = import_to_database(rows, use_primary=args.primary)
    logger.info("Imported %d rows into mobile_volume_index", count)
```

**Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_import_mobile_index.py -v`
Expected: All PASS

**Step 5: Commit**

```bash
git add scripts/import_mobile_index.py tests/unit/test_import_mobile_index.py
git commit -m "feat: add mobile volume index CSV import script with date shifting"
```

---

## Task 4: Mobile Index Query Functions

**Files:**
- Create: `src/db/queries/mobile_index.py`
- Modify: `src/db/queries/__init__.py` — add re-exports
- Modify: `src/db/streamlit_queries.py` — add re-exports
- Create: `tests/unit/test_mobile_index_queries.py`

**Step 1: Write failing tests**

Test the coverage check function (can run against local DB even without mobile data):

```python
# tests/unit/test_mobile_index_queries.py
# ABOUTME: Tests for mobile volume index query functions
# ABOUTME: Verifies index availability check and coverage calculation

import pytest
from src.db.queries.mobile_index import mobile_index_table_exists


class TestMobileIndexAvailability:
    """Tests for mobile index table availability check."""

    def test_table_exists_returns_bool(self):
        """Function returns a boolean."""
        result = mobile_index_table_exists(use_primary=False)
        assert isinstance(result, bool)
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_mobile_index_queries.py -v`
Expected: FAIL — `ModuleNotFoundError`

**Step 3: Write implementation**

```python
# src/db/queries/mobile_index.py
# ABOUTME: Mobile volume index database queries for impact adjustment overlay
# ABOUTME: Provides daily and hourly impacts with mobile index applied at frame level

import psycopg2
import psycopg2.extras
from typing import List, Dict, Optional, Tuple
from .connection import get_db_connection


def mobile_index_table_exists(use_primary: bool = None) -> bool:
    """Check whether the mobile_volume_index table exists and has data.

    Args:
        use_primary: Database selection

    Returns:
        True if the table exists and contains at least one row
    """
    query = """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = 'mobile_volume_index'
        )
    """
    conn = get_db_connection(use_primary)
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            table_exists = cursor.fetchone()[0]
            if not table_exists:
                return False
            cursor.execute("SELECT EXISTS (SELECT 1 FROM mobile_volume_index LIMIT 1)")
            return cursor.fetchone()[0]
    finally:
        conn.close()


def get_mobile_index_coverage_sync(
    campaign_id: str, use_primary: bool = None
) -> Tuple[int, int]:
    """Get mobile index coverage for a campaign's frames.

    Args:
        campaign_id: Campaign reference
        use_primary: Database selection

    Returns:
        Tuple of (frames_with_index, total_frames)
    """
    query = """
        SELECT
            COUNT(DISTINCT CASE WHEN m.frameid IS NOT NULL THEN c.frameid END) as matched_frames,
            COUNT(DISTINCT c.frameid) as total_frames
        FROM cache_route_impacts_15min_by_demo c
        LEFT JOIN mobile_volume_index m ON c.frameid = m.frameid
        WHERE c.campaign_id = %s
          AND c.demographic_segment = 'all_adults'
    """
    conn = get_db_connection(use_primary)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, (campaign_id,))
            result = cursor.fetchone()
            if result:
                return (int(result["matched_frames"]), int(result["total_frames"]))
            return (0, 0)
    finally:
        conn.close()


def get_daily_impacts_with_mobile_index_sync(
    campaign_id: str, demographic: str = "all_adults", use_primary: bool = None
) -> List[Dict]:
    """Get daily impacts with both raw and mobile-indexed values.

    Joins 15-min impact data to mobile_volume_index at frame/date/hour grain.
    Frames without a matching index default to 1.0 (no adjustment).

    Args:
        campaign_id: Campaign reference
        demographic: Demographic segment
        use_primary: Database selection

    Returns:
        List of dicts with: date, raw_impacts, indexed_impacts
    """
    query = """
        SELECT
            DATE(c.time_window_start) as date,
            SUM(c.impacts) as raw_impacts,
            SUM(c.impacts * COALESCE(m.index_value, 1.0)) as indexed_impacts
        FROM cache_route_impacts_15min_by_demo c
        LEFT JOIN mobile_volume_index m
            ON c.frameid = m.frameid
            AND DATE(c.time_window_start) = m.date_2025
            AND EXTRACT(HOUR FROM c.time_window_start)::int = m.hour
        WHERE c.campaign_id = %s
          AND c.demographic_segment = %s
        GROUP BY DATE(c.time_window_start)
        ORDER BY date
    """
    conn = get_db_connection(use_primary)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, (campaign_id, demographic))
            return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_hourly_impacts_with_mobile_index_sync(
    campaign_id: str, demographic: str = "all_adults", use_primary: bool = None
) -> List[Dict]:
    """Get hourly impacts (day-of-week x hour) with both raw and mobile-indexed values.

    Args:
        campaign_id: Campaign reference
        demographic: Demographic segment
        use_primary: Database selection

    Returns:
        List of dicts with: day_of_week, hour, raw_avg_impacts, indexed_avg_impacts,
                            raw_total_impacts, indexed_total_impacts, count
    """
    query = """
        SELECT
            EXTRACT(DOW FROM c.time_window_start)::int as day_of_week,
            EXTRACT(HOUR FROM c.time_window_start)::int as hour,
            AVG(c.impacts) as raw_avg_impacts,
            AVG(c.impacts * COALESCE(m.index_value, 1.0)) as indexed_avg_impacts,
            SUM(c.impacts) as raw_total_impacts,
            SUM(c.impacts * COALESCE(m.index_value, 1.0)) as indexed_total_impacts,
            COUNT(*) as count
        FROM cache_route_impacts_15min_by_demo c
        LEFT JOIN mobile_volume_index m
            ON c.frameid = m.frameid
            AND DATE(c.time_window_start) = m.date_2025
            AND EXTRACT(HOUR FROM c.time_window_start)::int = m.hour
        WHERE c.campaign_id = %s
          AND c.demographic_segment = %s
        GROUP BY day_of_week, hour
        ORDER BY day_of_week, hour
    """
    conn = get_db_connection(use_primary)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, (campaign_id, demographic))
            return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_weekly_impacts_with_mobile_index_sync(
    campaign_id: str, demographic: str = "all_adults", use_primary: bool = None
) -> List[Dict]:
    """Get weekly impacts with both raw and mobile-indexed values.

    Args:
        campaign_id: Campaign reference
        demographic: Demographic segment
        use_primary: Database selection

    Returns:
        List of dicts with: iso_week, week_start, raw_impacts, indexed_impacts
    """
    query = """
        SELECT
            EXTRACT(ISOYEAR FROM c.time_window_start)::int as iso_year,
            EXTRACT(WEEK FROM c.time_window_start)::int as iso_week,
            MIN(DATE(c.time_window_start)) as week_start,
            SUM(c.impacts) as raw_impacts,
            SUM(c.impacts * COALESCE(m.index_value, 1.0)) as indexed_impacts
        FROM cache_route_impacts_15min_by_demo c
        LEFT JOIN mobile_volume_index m
            ON c.frameid = m.frameid
            AND DATE(c.time_window_start) = m.date_2025
            AND EXTRACT(HOUR FROM c.time_window_start)::int = m.hour
        WHERE c.campaign_id = %s
          AND c.demographic_segment = %s
        GROUP BY iso_year, iso_week
        ORDER BY iso_year, iso_week
    """
    conn = get_db_connection(use_primary)
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute(query, (campaign_id, demographic))
            return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
```

**Step 4: Update re-exports in `src/db/queries/__init__.py`**

Add to the imports section:

```python
# Mobile index queries
from .mobile_index import (
    mobile_index_table_exists,
    get_mobile_index_coverage_sync,
    get_daily_impacts_with_mobile_index_sync,
    get_hourly_impacts_with_mobile_index_sync,
    get_weekly_impacts_with_mobile_index_sync,
)
```

Add to `__all__`:

```python
    # Mobile index queries
    "mobile_index_table_exists",
    "get_mobile_index_coverage_sync",
    "get_daily_impacts_with_mobile_index_sync",
    "get_hourly_impacts_with_mobile_index_sync",
    "get_weekly_impacts_with_mobile_index_sync",
```

**Step 5: Update re-exports in `src/db/streamlit_queries.py`**

Add same imports and `__all__` entries (matching the pattern in `__init__.py`).

**Step 6: Run tests**

Run: `uv run pytest tests/unit/test_mobile_index_queries.py -v`
Expected: All PASS

**Step 7: Commit**

```bash
git add src/db/queries/mobile_index.py src/db/queries/__init__.py src/db/streamlit_queries.py tests/unit/test_mobile_index_queries.py
git commit -m "feat: add mobile index query functions with frame-level LEFT JOIN"
```

---

## Task 5: Time Series Tab — Dual-Line Charts

**Files:**
- Modify: `src/ui/tabs/time_series.py`

**Context:** The current `render_time_series_tab()` function at `time_series.py:22` fetches `daily_data` and `hourly_data`, builds a DataFrame, and renders Plotly charts. We need to:

1. Check if mobile index data is available (call `mobile_index_table_exists`)
2. Show a toggle checkbox if available
3. When toggled on, fetch dual data and add a second line to the daily chart
4. Add a weekly chart with dual lines
5. Show a coverage statistic

**Step 1: Add mobile index toggle and coverage display**

At the top of `render_time_series_tab()`, after the existing demographic selector setup (~line 84), add:

```python
    # Mobile index toggle (only shown if table exists)
    show_mobile_index = False
    if mobile_index_table_exists(use_primary=use_primary):
        show_mobile_index = st.checkbox(
            "Show mobile-indexed impacts",
            key="time_series_mobile_index_toggle",
            help="Overlay mobile volume-adjusted impacts alongside raw impacts",
        )
        if show_mobile_index:
            matched, total = get_mobile_index_coverage_sync(
                campaign_id, use_primary=use_primary
            )
            coverage_pct = (matched / total * 100) if total > 0 else 0
            st.info(
                f"Mobile volume index applied — showing adjusted impacts alongside raw. "
                f"Coverage: {coverage_pct:.0f}% of frames ({matched:,} / {total:,})"
            )
```

**Step 2: Fetch indexed data when toggle is on**

In the data loading section (~line 87), alongside the existing `daily_data` and `hourly_data` fetches:

```python
    # Fetch mobile-indexed data if toggle is on
    mobile_daily_data = None
    mobile_hourly_data = None
    mobile_weekly_data = None
    if show_mobile_index:
        mobile_daily_data = get_daily_impacts_with_mobile_index_sync(
            campaign_id, demographic=selected_demographic, use_primary=use_primary
        )
        mobile_hourly_data = get_hourly_impacts_with_mobile_index_sync(
            campaign_id, demographic=selected_demographic, use_primary=use_primary
        )
        mobile_weekly_data = get_weekly_impacts_with_mobile_index_sync(
            campaign_id, demographic=selected_demographic, use_primary=use_primary
        )
```

**Step 3: Modify daily chart to show dual lines**

In the daily line chart section (~line 222-243), when `mobile_daily_data` is available, add a second trace:

```python
        if mobile_daily_data:
            df_mobile_daily = pd.DataFrame(mobile_daily_data)
            df_mobile_daily["date"] = pd.to_datetime(df_mobile_daily["date"])
            df_mobile_daily = fill_date_gaps_with_boundary_zeros(
                df_mobile_daily, value_column="indexed_impacts"
            )
            fig_line.add_trace(
                go.Scatter(
                    x=df_mobile_daily["date"],
                    y=df_mobile_daily["indexed_impacts"],
                    mode="lines+markers",
                    name="Mobile-Indexed",
                    line=dict(color="#F18F01", width=2, dash="dash"),
                    marker=dict(size=5),
                    hovertemplate="%{x|%a %d %b}<br>Indexed: %{y:,.0f}k<extra></extra>",
                )
            )
            fig_line.update_layout(showlegend=True)
```

**Step 4: Add weekly chart section**

After the daily trends section, add a new "Weekly Trends" section when mobile data is available:

```python
    if mobile_weekly_data:
        st.divider()
        st.markdown("##### Weekly Trends (Raw vs Mobile-Indexed)")
        df_weekly = pd.DataFrame(mobile_weekly_data)
        df_weekly["week_start"] = pd.to_datetime(df_weekly["week_start"])

        fig_weekly = go.Figure()
        fig_weekly.add_trace(
            go.Scatter(
                x=df_weekly["week_start"],
                y=df_weekly["raw_impacts"],
                mode="lines+markers",
                name="Raw Impacts",
                line=dict(color="#2E86AB", width=2),
                marker=dict(size=6),
                hovertemplate="Week of %{x|%d %b}<br>Raw: %{y:,.0f}k<extra></extra>",
            )
        )
        fig_weekly.add_trace(
            go.Scatter(
                x=df_weekly["week_start"],
                y=df_weekly["indexed_impacts"],
                mode="lines+markers",
                name="Mobile-Indexed",
                line=dict(color="#F18F01", width=2, dash="dash"),
                marker=dict(size=5),
                hovertemplate="Week of %{x|%d %b}<br>Indexed: %{y:,.0f}k<extra></extra>",
            )
        )
        fig_weekly.update_layout(
            title="Weekly Impacts — Raw vs Mobile-Indexed (000s)",
            height=350,
            xaxis_title="Week Starting",
            yaxis_title="Impacts (000s)",
            hovermode="x unified",
            showlegend=True,
        )
        st.plotly_chart(fig_weekly, use_container_width=True)
```

**Step 5: Add imports at top of file**

```python
from src.db.streamlit_queries import (
    # ... existing imports ...
    mobile_index_table_exists,
    get_mobile_index_coverage_sync,
    get_daily_impacts_with_mobile_index_sync,
    get_hourly_impacts_with_mobile_index_sync,
    get_weekly_impacts_with_mobile_index_sync,
)
```

**Step 6: Test manually**

Run: `startstream local` (or appropriate start command)
- Without mobile index table: verify no toggle appears, tab works as before
- With table: verify toggle, dual lines, weekly chart, coverage stat

**Step 7: Commit**

```bash
git add src/ui/tabs/time_series.py
git commit -m "feat: add mobile index dual-line charts to Time Series tab"
```

---

## Task 6: Detailed Analysis Tab — Dual Heatmap

**Files:**
- Modify: `src/ui/tabs/detailed_analysis.py`

**Context:** The Detailed Analysis tab (`detailed_analysis.py`) shows frame-level audience data — daily and hourly tables. The hourly heatmap lives in the Time Series tab. For Detailed Analysis, we need to add mobile-indexed columns to the regional and environment breakdown tables.

Note: Review the actual Detailed Analysis tab content at implementation time. The tab focuses on frame audiences rather than aggregated impacts. The mobile index may apply via the regional/environment impacts that appear in other views. The implementer should check which impact queries the tab calls and add indexed columns where applicable.

**Step 1: Review tab content and identify where indexed data fits**

Read `src/ui/tabs/detailed_analysis.py` fully. Identify calls to impact query functions.

**Step 2: Add mobile index toggle (matching Time Series pattern)**

Same pattern as Task 5 — checkbox, coverage stat, info banner.

**Step 3: Where frame-level daily data is displayed, add indexed columns**

For any table showing impacts, add `indexed_impacts` column when toggle is on.

**Step 4: Test manually and commit**

```bash
git add src/ui/tabs/detailed_analysis.py
git commit -m "feat: add mobile index columns to Detailed Analysis tab"
```

---

## Task 7: Export — Three Columns When Mobile Index Active

**Files:**
- Modify: `src/ui/utils/export/data.py`

**Context:** `gather_campaign_data()` in `data.py:37` collects all datasets into DataFrames. When mobile index is active, the daily and hourly datasets need three columns instead of one.

**Step 1: Modify daily impacts gathering (~line 76-85)**

```python
    # 3. Daily Impacts (Time Series tab)
    try:
        mobile_index_active = False
        try:
            import streamlit as st
            mobile_index_active = st.session_state.get("time_series_mobile_index_toggle", False)
        except Exception:
            pass

        if mobile_index_active and mobile_index_table_exists(use_primary=use_primary):
            daily_data = get_daily_impacts_with_mobile_index_sync(
                campaign_id, use_primary=use_primary
            )
            if daily_data:
                df = pd.DataFrame(daily_data)
                # Rename for export clarity
                df = df.rename(columns={
                    "raw_impacts": "impacts",
                    "indexed_impacts": "impacts_mobile_indexed",
                })
                # Calculate the index value for transparency
                df["mobile_index"] = (
                    df["impacts_mobile_indexed"] / df["impacts"]
                ).where(df["impacts"] > 0, 1.0)
                datasets["daily_impacts"] = df
        else:
            daily_data = get_daily_impacts_sync(campaign_id, use_primary=use_primary)
            if daily_data:
                df = pd.DataFrame(daily_data)
                if "intervals" in df.columns:
                    df = df.drop(columns=["intervals"])
                datasets["daily_impacts"] = df
    except Exception as e:
        logger.warning("Failed to gather daily impacts for campaign %s: %s", campaign_id, e)
```

**Step 2: Apply same pattern to hourly impacts (~line 87-100)**

Same approach — if mobile index active, use `get_hourly_impacts_with_mobile_index_sync` and include three columns.

**Step 3: Add imports**

```python
from src.db.streamlit_queries import (
    # ... existing imports ...
    mobile_index_table_exists,
    get_daily_impacts_with_mobile_index_sync,
    get_hourly_impacts_with_mobile_index_sync,
)
```

**Step 4: Test export manually**

Start app, enable mobile index toggle, export a campaign, verify Excel contains three impact columns.

**Step 5: Commit**

```bash
git add src/ui/utils/export/data.py
git commit -m "feat: include raw/index/indexed columns in export when mobile index active"
```

---

## Task 8: Integration Tests

**Files:**
- Create: `tests/integration/test_mobile_index_integration.py`

**Step 1: Write integration tests**

```python
# tests/integration/test_mobile_index_integration.py
# ABOUTME: Integration tests for mobile volume index feature end-to-end
# ABOUTME: Tests CSV import, query functions, and data flow against local database

import pytest
from src.db.queries.mobile_index import (
    mobile_index_table_exists,
    get_mobile_index_coverage_sync,
    get_daily_impacts_with_mobile_index_sync,
    get_hourly_impacts_with_mobile_index_sync,
    get_weekly_impacts_with_mobile_index_sync,
)


class TestMobileIndexIntegration:
    """Integration tests that run against the local database."""

    def test_table_exists_check(self):
        """mobile_index_table_exists returns without error."""
        result = mobile_index_table_exists(use_primary=False)
        assert isinstance(result, bool)

    def test_daily_query_returns_list(self):
        """Daily query returns a list (may be empty if no mobile data loaded)."""
        result = get_daily_impacts_with_mobile_index_sync(
            "16699", use_primary=False
        )
        assert isinstance(result, list)

    def test_hourly_query_returns_list(self):
        """Hourly query returns a list."""
        result = get_hourly_impacts_with_mobile_index_sync(
            "16699", use_primary=False
        )
        assert isinstance(result, list)

    def test_weekly_query_returns_list(self):
        """Weekly query returns a list."""
        result = get_weekly_impacts_with_mobile_index_sync(
            "16699", use_primary=False
        )
        assert isinstance(result, list)

    def test_coverage_returns_tuple(self):
        """Coverage check returns (matched, total) tuple."""
        result = get_mobile_index_coverage_sync("16699", use_primary=False)
        assert isinstance(result, tuple)
        assert len(result) == 2
```

**Step 2: Run integration tests**

Run: `uv run pytest tests/integration/test_mobile_index_integration.py -v`
Expected: All PASS (queries work even if mobile index table doesn't exist yet — they'll return empty results)

**Step 3: Commit**

```bash
git add tests/integration/test_mobile_index_integration.py
git commit -m "test: add integration tests for mobile volume index queries"
```

---

## Task 9: Documentation

**Files:**
- Create: `Claude/docs/Documentation/MOBILE_VOLUME_INDEX.md`
- Modify: `Claude/todo/upcoming_tasks.md`

**Step 1: Write usage documentation**

Cover:
- What the mobile index is and why it exists
- CSV format specification (columns, types, example rows)
- Import command: `uv run python scripts/import_mobile_index.py <csv_path> --primary`
- How the UI toggle works
- How exports change when toggle is on
- Date-shifting logic explanation

**Step 2: Update todo**

Add "Completed: Mobile Volume Index Overlay" section with date and summary.

**Step 3: Commit**

```bash
git add Claude/docs/Documentation/MOBILE_VOLUME_INDEX.md Claude/todo/upcoming_tasks.md
git commit -m "docs: add mobile volume index usage documentation"
```

---

## Task 10: End-to-End Test with Sample Data

**Files:**
- Create: `tests/fixtures/sample_mobile_index.csv`

**Step 1: Create a small sample CSV**

A few rows matching known frames in the database for manual E2E verification:

```csv
frameid,date,hour,index_value
1234571069,2024-08-28,8,1.35
1234571069,2024-08-28,9,1.42
1234571069,2024-08-28,10,1.28
1234571069,2024-08-28,14,0.95
1234571069,2024-08-28,15,0.87
1234571070,2024-08-28,8,1.15
1234571070,2024-08-28,9,1.22
```

**Step 2: Import sample data to local DB**

Run: `uv run python scripts/import_mobile_index.py tests/fixtures/sample_mobile_index.csv`

**Step 3: Verify in app**

Run: `startstream local`
- Toggle should now appear
- Enable toggle on a campaign that includes these frames
- Verify dual lines appear
- Export and verify three columns

**Step 4: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: All PASS

**Step 5: Final commit**

```bash
git add tests/fixtures/sample_mobile_index.csv
git commit -m "test: add sample mobile index CSV for E2E verification"
```

---

## Summary

| Task | Description | Estimated |
|------|-------------|-----------|
| 1 | Create feature branch | 1 min |
| 2 | Date-shifting utility + tests | 15 min |
| 3 | CSV import script + tests | 25 min |
| 4 | Query functions + re-exports | 30 min |
| 5 | Time Series tab dual-line charts | 30 min |
| 6 | Detailed Analysis tab indexed columns | 20 min |
| 7 | Export three columns | 20 min |
| 8 | Integration tests | 15 min |
| 9 | Documentation | 15 min |
| 10 | E2E test with sample data | 15 min |

**Total: ~3 hours**

---

*Plan created: 5 March 2026*
