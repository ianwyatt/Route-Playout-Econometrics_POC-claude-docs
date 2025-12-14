# Campaign Browser Enhancement Plan (Phase 10.5.1-10.5.4)

**Date**: November 15, 2025
**Requested By**: Doctor Biz
**Status**: Planning Phase

---

## Executive Summary

Enhance the campaign browser to provide:
1. **Materialized View** for fast campaign listing with brand information
2. **Brand Display** in campaign selector
3. **Sortable/Searchable Table** instead of simple dropdown
4. **AI Natural Language Search** capability (future)

---

## Current State Analysis

### Existing Data Sources

**Materialized Views:**
- `mv_playout_15min` - 15-minute aggregated playout data by campaign
- `mv_playout_15min_brands` - Per-brand playout data (has `spacebrandid`)

**Cache Tables:**
- `cache_space_brands` - Brand names lookup (entity_id → name)
- `cache_space_buyers` - Buyer names lookup
- `cache_space_agencies` - Agency names lookup
- `cache_space_media_owners` - Media owner names lookup
- `cache_campaign_brand_reach` - Campaign-brand-reach relationships

### Current Campaign Browser (Phase 10.5)

**Implementation:**
- Uses `get_all_campaigns_sync()` to query `mv_playout_15min`
- Returns: campaign_id, total_frames, total_spots, start_date, end_date
- Displays in dropdown: `"ID | playouts | frames | date range"`
- Cached for 5 minutes via `@st.cache_data(ttl=300)`

**Limitations:**
1. No brand information displayed
2. Dropdown not sortable by column
3. No search/filter capability
4. Limited to 100 campaigns (hard-coded limit)

---

## Enhancement 1: Materialized View for Campaign Browser

### Objective
Create a dedicated materialized view (`mv_campaign_browser`) that pre-aggregates all campaign metadata for fast loading.

### Proposed Schema

```sql
CREATE MATERIALIZED VIEW mv_campaign_browser AS
SELECT
    p.buyercampaignref AS campaign_id,

    -- Playout statistics
    COUNT(DISTINCT p.frameid) AS total_frames,
    SUM(p.spot_count) AS total_playouts,
    MIN(p.time_window_start) AS start_date,
    MAX(p.time_window_start) AS end_date,
    COUNT(DISTINCT DATE(p.time_window_start)) AS days_active,
    ROUND(AVG(p.playout_length_seconds), 1) AS avg_spot_length,

    -- Brand information (aggregated from mv_playout_15min_brands)
    ARRAY_AGG(DISTINCT COALESCE(b.name, 'Unknown'))
        FILTER (WHERE pb.spacebrandid IS NOT NULL) AS brand_names,
    COUNT(DISTINCT pb.spacebrandid) AS brand_count,

    -- Primary brand (most common brand by playout count)
    (
        SELECT COALESCE(csb.name, 'Unknown')
        FROM mv_playout_15min_brands pb2
        LEFT JOIN cache_space_brands csb ON pb2.spacebrandid = csb.entity_id
        WHERE pb2.buyercampaignref = p.buyercampaignref
        GROUP BY pb2.spacebrandid, csb.name
        ORDER BY SUM(pb2.spots_for_brand) DESC
        LIMIT 1
    ) AS primary_brand,

    -- Media owner information
    p.spacemediaownerid AS media_owner_id,
    mo.name AS media_owner_name,

    -- Buyer information (if available from cache)
    p.spacebuyerid AS buyer_id,
    bu.name AS buyer_name,

    -- Computed fields for sorting/filtering
    (MAX(p.time_window_start) - MIN(p.time_window_start)) AS campaign_duration,
    MAX(p.time_window_start) AS last_activity,

    -- Metadata for caching
    NOW() AS refreshed_at

FROM mv_playout_15min p

-- Join brand data
LEFT JOIN mv_playout_15min_brands pb
    ON p.buyercampaignref = pb.buyercampaignref
LEFT JOIN cache_space_brands b
    ON pb.spacebrandid = b.entity_id

-- Join SPACE API cache tables
LEFT JOIN cache_space_media_owners mo
    ON p.spacemediaownerid = mo.entity_id
LEFT JOIN cache_space_buyers bu
    ON p.spacebuyerid = bu.entity_id

WHERE p.buyercampaignref IS NOT NULL

GROUP BY
    p.buyercampaignref,
    p.spacemediaownerid,
    mo.name,
    p.spacebuyerid,
    bu.name

ORDER BY MAX(p.time_window_start) DESC;

-- Create indexes for fast sorting/filtering
CREATE INDEX idx_mv_campaign_browser_campaign_id
    ON mv_campaign_browser(campaign_id);
CREATE INDEX idx_mv_campaign_browser_last_activity
    ON mv_campaign_browser(last_activity DESC);
CREATE INDEX idx_mv_campaign_browser_total_playouts
    ON mv_campaign_browser(total_playouts DESC);
CREATE INDEX idx_mv_campaign_browser_total_frames
    ON mv_campaign_browser(total_frames DESC);
CREATE INDEX idx_mv_campaign_browser_primary_brand
    ON mv_campaign_browser(primary_brand);
```

### Benefits
- **Performance**: Pre-aggregated data, <50ms query time
- **Brand Data**: Includes brand names without runtime joins
- **Sortable**: Indexes support efficient sorting by any column
- **Searchable**: Can use `WHERE primary_brand ILIKE '%pattern%'`
- **Complete**: All metadata needed for campaign browser in one view

### Refresh Strategy

**Daily Refresh** (Recommended):
```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_campaign_browser;
```

**Trigger**:
- Run after playout data import (2am UTC)
- Run after SPACE API cache updates
- Can be triggered manually via `REFRESH MATERIALIZED VIEW`

**Pipeline Team Handover Required**:
- Add refresh to daily ETL pipeline
- Document in pipeline handover materials
- Coordinate with existing materialized view refreshes

---

## Enhancement 2: Brand Information Display

### UI Changes

**Current Display Format:**
```
"16932 | 962,150 playouts | 42 frames | Aug 06 - Oct 13, 2025"
```

**Enhanced Display Format:**
```
"16932 | Uber | 962,150 playouts | 42 frames | Aug 06 - Oct 13, 2025"
```

**For Multi-Brand Campaigns:**
```
"16932 | Uber (+2 brands) | 962,150 playouts | 42 frames | Aug 06 - Oct 13, 2025"
```

### Implementation

**Updated `format_campaign_display()` function:**
```python
def format_campaign_display(campaign: Dict) -> str:
    """Format campaign for display with brand information."""
    campaign_id = campaign['buyercampaignref']
    total_spots = campaign.get('total_playouts', 0)
    total_frames = campaign.get('total_frames', 0)
    start_date = campaign.get('start_date')
    end_date = campaign.get('end_date')

    # Brand information
    primary_brand = campaign.get('primary_brand', 'Unknown')
    brand_count = campaign.get('brand_count', 0)

    # Format brand display
    if brand_count > 1:
        brand_display = f"{primary_brand} (+{brand_count-1} brands)"
    elif primary_brand and primary_brand != 'Unknown':
        brand_display = primary_brand
    else:
        brand_display = "No brand"

    # Date range
    if start_date and end_date:
        date_range = f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    else:
        date_range = "Unknown dates"

    return f"{campaign_id} | {brand_display} | {total_spots:,} playouts | {total_frames} frames | {date_range}"
```

---

## Enhancement 3: Sortable/Searchable Table UI

### Objective
Replace dropdown with interactive table supporting:
- Column sorting (click column headers)
- Text search/filter
- Pagination
- Multi-select (future)

### UI Design

**Component**: Streamlit `st.dataframe` with interactive features

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🔍 Search Campaigns                                                         │
│ [Search box: "Enter campaign ID, brand, or keyword..."]          [Search] │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ Campaign Browser (826 campaigns)                                            │
├──────────┬────────────┬──────────┬────────┬─────────────────────────────────┤
│ Campaign │ Brand      │ Playouts │ Frames │ Date Range                      │
│ ID ↓     │            │          │        │                                 │
├──────────┼────────────┼──────────┼────────┼─────────────────────────────────┤
│ 18295    │ Uber       │ 19.3M    │ 125    │ Aug 06 - Oct 13, 2025           │
│ 16932    │ Sony (+2)  │ 962,150  │ 42     │ Aug 15 - Sep 30, 2025           │
│ 15885    │ Nike       │ 543,200  │ 38     │ Jul 10 - Aug 20, 2025           │
│ ...      │ ...        │ ...      │ ...    │ ...                             │
└──────────┴────────────┴──────────┴────────┴─────────────────────────────────┘

[< Previous]  Page 1 of 9  [Next >]

[Analyse Selected Campaign]
```

### Implementation Approach

**Option 1: Streamlit `st.dataframe` (Recommended)**
```python
def render_campaign_table():
    """Render interactive campaign table."""
    # Load campaigns
    campaigns = load_campaigns_from_mv(limit=1000, use_ms01=use_ms01)

    # Convert to DataFrame
    df = pd.DataFrame(campaigns)

    # Format columns
    df['playouts_formatted'] = df['total_playouts'].apply(lambda x: f"{x:,}")
    df['brand_display'] = df.apply(format_brand_column, axis=1)
    df['date_range'] = df.apply(format_date_range, axis=1)

    # Display columns
    display_df = df[[
        'campaign_id',
        'brand_display',
        'playouts_formatted',
        'total_frames',
        'date_range'
    ]]

    # Rename for display
    display_df.columns = ['Campaign ID', 'Brand', 'Playouts', 'Frames', 'Date Range']

    # Interactive dataframe with selection
    event = st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row"
    )

    # Get selected campaign
    if event.selection.rows:
        selected_idx = event.selection.rows[0]
        selected_campaign_id = df.iloc[selected_idx]['campaign_id']

        if st.button("Analyse Selected Campaign", type="primary"):
            st.session_state.selected_campaign_id = selected_campaign_id
            st.session_state.show_analysis = True
            st.rerun()
```

**Option 2: AG Grid (More Features, External Dependency)**
- Pros: Advanced sorting, filtering, grouping
- Cons: Requires `streamlit-aggrid` package
- Consider for Phase 12+ if Streamlit dataframe insufficient

### Search/Filter Implementation

```python
def render_campaign_search():
    """Render search interface."""
    col1, col2 = st.columns([4, 1])

    with col1:
        search_query = st.text_input(
            "Search",
            placeholder="Enter campaign ID, brand, or keyword...",
            key="campaign_search",
            label_visibility="collapsed"
        )

    with col2:
        search_column = st.selectbox(
            "Search in",
            options=["All", "Campaign ID", "Brand", "Media Owner"],
            key="search_column",
            label_visibility="collapsed"
        )

    return search_query, search_column

def filter_campaigns(campaigns: List[Dict], query: str, column: str) -> List[Dict]:
    """Filter campaigns by search query."""
    if not query:
        return campaigns

    query_lower = query.lower()

    if column == "All":
        return [
            c for c in campaigns
            if (query_lower in str(c.get('campaign_id', '')).lower() or
                query_lower in str(c.get('primary_brand', '')).lower() or
                query_lower in str(c.get('media_owner_name', '')).lower())
        ]
    elif column == "Campaign ID":
        return [c for c in campaigns if query_lower in str(c.get('campaign_id', '')).lower()]
    elif column == "Brand":
        return [c for c in campaigns if query_lower in str(c.get('primary_brand', '')).lower()]
    elif column == "Media Owner":
        return [c for c in campaigns if query_lower in str(c.get('media_owner_name', '')).lower()]

    return campaigns
```

---

## Enhancement 4: AI Natural Language Search (Future)

### Objective
Allow users to search campaigns using natural language queries:
- "Show me Uber campaigns from August"
- "Find campaigns with more than 1 million playouts"
- "List all campaigns for Nike in London"

### Architecture Plan

**Phase 1: Query Parser (Rule-Based)**
```python
class CampaignQueryParser:
    """Parse natural language queries into database filters."""

    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parse query into structured filters.

        Examples:
        - "Uber campaigns from August" → {brand: "Uber", month: "August"}
        - "campaigns with >1M playouts" → {min_playouts: 1000000}
        - "Nike in London" → {brand: "Nike", location: "London"}
        """
        filters = {}

        # Brand extraction
        if brand := self._extract_brand(query):
            filters['brand'] = brand

        # Date extraction
        if date_range := self._extract_date_range(query):
            filters['date_range'] = date_range

        # Metric filters
        if playout_filter := self._extract_playout_filter(query):
            filters['playouts'] = playout_filter

        # Location
        if location := self._extract_location(query):
            filters['location'] = location

        return filters

    def _extract_brand(self, query: str) -> Optional[str]:
        """Extract brand name from query."""
        # Use SPACE brands cache to match against known brands
        known_brands = self._get_known_brands()
        query_lower = query.lower()

        for brand in known_brands:
            if brand.lower() in query_lower:
                return brand

        return None

    def _extract_date_range(self, query: str) -> Optional[Tuple[date, date]]:
        """Extract date range from query."""
        # Pattern matching for dates, months, years
        # "August" → August 1-31 of current year
        # "Q3 2025" → Jul 1 - Sep 30, 2025
        # "last 30 days" → (today - 30 days, today)
        pass

    def _extract_playout_filter(self, query: str) -> Optional[Dict]:
        """Extract playout count filters."""
        # ">1M" → {"min": 1000000}
        # "<50k" → {"max": 50000}
        # "between 100k and 500k" → {"min": 100000, "max": 500000}
        pass
```

**Phase 2: LLM Integration (OpenAI/Claude/Deepseek)**
```python
class AIQueryTranslator:
    """Use LLM to translate natural language to SQL/filters."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = OpenAI()  # or Anthropic, Deepseek

    def translate(self, query: str) -> str:
        """
        Translate natural language to SQL query.

        Uses few-shot prompting with examples:
        - "Uber campaigns from August" → SELECT ... WHERE brand = 'Uber' AND month = 8
        - "campaigns with >1M playouts" → SELECT ... WHERE total_playouts > 1000000
        """
        prompt = self._build_prompt(query)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1  # Low temperature for consistent output
        )

        sql = response.choices[0].message.content
        return self._validate_sql(sql)  # Safety: validate before execution

    def _get_system_prompt(self) -> str:
        """System prompt with schema and examples."""
        return """
        You are a SQL query generator for a campaign database.

        Schema: mv_campaign_browser
        - campaign_id (varchar)
        - primary_brand (varchar)
        - total_playouts (bigint)
        - total_frames (int)
        - start_date (date)
        - end_date (date)
        - media_owner_name (varchar)
        - buyer_name (varchar)

        Generate PostgreSQL SELECT queries based on natural language.
        Always include: campaign_id, primary_brand, total_playouts, total_frames, start_date, end_date

        Examples:
        User: "Uber campaigns from August 2025"
        SQL: SELECT campaign_id, primary_brand, total_playouts, total_frames, start_date, end_date
             FROM mv_campaign_browser
             WHERE primary_brand = 'Uber'
               AND EXTRACT(YEAR FROM start_date) = 2025
               AND EXTRACT(MONTH FROM start_date) = 8;

        User: "campaigns with more than 1 million playouts"
        SQL: SELECT campaign_id, primary_brand, total_playouts, total_frames, start_date, end_date
             FROM mv_campaign_browser
             WHERE total_playouts > 1000000
             ORDER BY total_playouts DESC;
        """
```

**Phase 3: UI Integration**
```python
def render_ai_search():
    """Render AI search interface."""
    st.markdown("### 🤖 AI Search (Beta)")
    st.info("Try: 'Show me Uber campaigns from August' or 'Find campaigns with >1M playouts'")

    query = st.text_input(
        "Ask in natural language:",
        placeholder="e.g., Show me Nike campaigns from last month",
        key="ai_search_query"
    )

    if st.button("Search with AI", type="secondary"):
        with st.spinner("Translating query..."):
            translator = AIQueryTranslator()
            sql = translator.translate(query)

            # Show generated SQL (transparency)
            with st.expander("🔍 Generated Query"):
                st.code(sql, language="sql")

            # Execute query
            results = execute_safe_query(sql)  # Safety wrapper

            # Display results
            if results:
                render_campaign_table(results)
            else:
                st.warning("No campaigns found matching your query.")
```

### Security Considerations
1. **SQL Injection Prevention**: Parameterized queries only, validate generated SQL
2. **Query Limits**: Always include `LIMIT` clause, max 1000 results
3. **Rate Limiting**: Limit AI API calls per user/session
4. **Cost Management**: Use smaller models (gpt-4o-mini, claude-haiku) for query translation
5. **Fallback**: If AI translation fails, fall back to rule-based parser

### AI Provider Options

| Provider | Model | Cost/1M Tokens | Latency | Recommendation |
|----------|-------|----------------|---------|----------------|
| OpenAI | gpt-4o-mini | $0.15 / $0.60 | ~500ms | **Recommended** - Fast, cheap |
| Anthropic | claude-haiku-3.5 | $0.80 / $4.00 | ~800ms | Good accuracy, higher cost |
| Deepseek | deepseek-chat | $0.14 / $0.28 | ~1000ms | Cheapest, slower |
| Local | llama-3.1-8B | Free | Variable | Requires GPU, complex setup |

**Recommendation**: Start with OpenAI gpt-4o-mini for MVP, evaluate others in Phase 12+

---

## Implementation Roadmap

### Phase 10.5.1: Materialized View Design ✅ (Current)
- [x] Analyze database schema
- [x] Design `mv_campaign_browser` schema
- [x] Document refresh strategy
- [ ] Create SQL migration file
- [ ] Test query performance

### Phase 10.5.2: SQL Migration & Handover
- [ ] Create migration file: `migrations/003_mv_campaign_browser.sql`
- [ ] Test on local database
- [ ] Document for pipeline team
- [ ] Create handover document for pipeline team
- [ ] Coordinate refresh schedule

### Phase 10.5.3: UI Enhancement - Sortable Table
- [ ] Update `load_campaigns()` to query new materialized view
- [ ] Implement sortable table with `st.dataframe`
- [ ] Add search/filter functionality
- [ ] Update `format_campaign_display()` with brand info
- [ ] Test with 1000+ campaigns
- [ ] Performance optimization

### Phase 10.5.4: AI Search Planning
- [ ] Evaluate AI providers (OpenAI, Anthropic, Deepseek)
- [ ] Prototype rule-based query parser
- [ ] Design few-shot prompts for LLM
- [ ] Security review (SQL injection, rate limiting)
- [ ] Cost analysis
- [ ] User testing plan

---

## Pipeline Team Handover Requirements

### Materialized View Refresh

**Action Required**:
Add `mv_campaign_browser` refresh to daily ETL pipeline

**Refresh SQL**:
```sql
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_campaign_browser;
```

**Timing**:
- Run after playout data import (currently 2am UTC)
- Run after SPACE API cache updates
- Estimated duration: ~30-60 seconds for 800+ campaigns

**Dependencies**:
- Requires `mv_playout_15min` to be refreshed first
- Requires `mv_playout_15min_brands` to be refreshed first
- Requires SPACE API caches to be populated

**Monitoring**:
- Track refresh duration
- Alert if refresh fails
- Alert if row count drops significantly

**Handover Document Location**:
- `docs/pipeline-handover/MV_CAMPAIGN_BROWSER_REFRESH.md` (to be created)

---

## Performance Targets

### Current Performance (Phase 10.5)
- Campaign list load: <1 second (100 campaigns, cached)
- Dropdown rendering: Instant
- Memory usage: Low (~1MB cached data)

### Target Performance (After Enhancements)
- Campaign list load: <500ms (1000 campaigns, from materialized view)
- Table rendering: <1 second (pandas DataFrame)
- Search/filter: <200ms (client-side filtering)
- Sort by column: Instant (pandas built-in)
- AI query translation: <2 seconds (OpenAI API call)

### Scalability
- Support 5,000+ campaigns without performance degradation
- Pagination for >1000 campaigns
- Virtualization for large tables (if needed)

---

## Testing Plan

### Unit Tests
- [ ] Test `mv_campaign_browser` query correctness
- [ ] Test brand aggregation logic
- [ ] Test search/filter functions
- [ ] Test AI query parser (rule-based)
- [ ] Test SQL injection prevention

### Integration Tests
- [ ] Test materialized view refresh
- [ ] Test UI with 1000+ campaigns
- [ ] Test sorting by each column
- [ ] Test search across all fields
- [ ] Test AI query translation end-to-end

### User Testing
- [ ] Test campaign discovery workflow
- [ ] Test brand-based filtering
- [ ] Test natural language search usability
- [ ] Gather feedback on table vs dropdown preference

---

## Cost Estimation

### Development Time
- Phase 10.5.1: 2 hours (Design) ✅
- Phase 10.5.2: 3 hours (SQL + Testing)
- Phase 10.5.3: 4 hours (UI Implementation)
- Phase 10.5.4: 6 hours (AI Planning + Prototype)
- **Total**: ~15 hours

### Infrastructure Costs
- Database: No additional cost (existing PostgreSQL)
- AI API (if implemented):
  - Estimated queries: 50/day
  - Cost per query: $0.0003 (gpt-4o-mini, ~200 tokens avg)
  - Monthly cost: ~$0.45
- **Total**: Negligible additional cost

### Maintenance
- Materialized view refresh: Automated (no ongoing cost)
- AI model updates: Quarterly review recommended

---

## Risk Assessment

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Materialized view refresh slow | Medium | Low | Use CONCURRENTLY, optimize query |
| Brand data incomplete | Medium | Medium | Show "Unknown" for missing brands |
| AI generates invalid SQL | High | Medium | Validate SQL before execution, parameterize |
| Large campaigns slow UI | Medium | Low | Pagination, virtualization |

### Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| User confusion with AI search | Low | Medium | Clear examples, fallback to traditional search |
| Pipeline team unavailable | Medium | Low | Provide complete documentation, manual refresh option |
| Brand names change | Low | Medium | SPACE API cache update handles this |

---

## Success Metrics

### Phase 10.5.2 (Materialized View)
- ✅ Materialized view created successfully
- ✅ Refresh completes in <60 seconds
- ✅ All campaigns have brand information
- ✅ Query performance <500ms for 1000 campaigns

### Phase 10.5.3 (UI Enhancement)
- ✅ Users can sort by any column
- ✅ Search finds campaigns in <200ms
- ✅ Brand information displayed for 90%+ campaigns
- ✅ User feedback: "Easier to find campaigns"

### Phase 10.5.4 (AI Search)
- ✅ AI correctly translates 80%+ of test queries
- ✅ No SQL injection vulnerabilities
- ✅ Query translation <2 seconds
- ✅ User feedback: "Natural language search is helpful"

---

## Next Steps (Immediate)

1. **Create SQL Migration** (Phase 10.5.2)
   - Write `migrations/003_mv_campaign_browser.sql`
   - Test on local database
   - Validate query performance

2. **Update Database Query Function** (Phase 10.5.3)
   - Modify `get_all_campaigns_sync()` to query `mv_campaign_browser`
   - Include brand fields in response

3. **Implement Table UI** (Phase 10.5.3)
   - Replace dropdown with `st.dataframe`
   - Add search box
   - Add column sorting

4. **Pipeline Team Coordination** (Phase 10.5.2)
   - Create handover document
   - Schedule meeting to discuss refresh integration

---

## Open Questions for Doctor Biz

1. **Priority**: Should we implement all 4 enhancements in sequence, or prioritize certain ones?
2. **AI Search**: Is AI natural language search a must-have for Phase 10, or can it wait until Phase 12?
3. **Brand Display**: For multi-brand campaigns, show primary brand only or all brands (comma-separated)?
4. **Sorting Default**: Sort by date (most recent first) or by playouts (largest first)?
5. **Search Scope**: Search all fields by default, or require user to select field?
6. **Pagination**: Show 100, 500, or 1000 campaigns per page?

---

**Document Status**: Draft - Awaiting Doctor Biz Approval
**Next Action**: Review plan, answer open questions, proceed with Phase 10.5.2
