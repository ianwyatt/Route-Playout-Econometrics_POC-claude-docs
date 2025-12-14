-- Verification Queries for Cache Data Investigation
-- Date: November 15, 2025
-- Purpose: Monitor cache coverage and backfill progress

-- ============================================================================
-- 1. CURRENT CACHE COVERAGE SUMMARY
-- ============================================================================

-- Overall cache coverage statistics
SELECT
    'Cache Coverage Summary' as report,
    COUNT(DISTINCT mcb.campaign_id) as total_campaigns,
    COUNT(DISTINCT ccrf.campaign_id) as campaigns_with_reach,
    COUNT(DISTINCT mcb.campaign_id) - COUNT(DISTINCT ccrf.campaign_id) as campaigns_missing_reach,
    ROUND(100.0 * COUNT(DISTINCT ccrf.campaign_id) / COUNT(DISTINCT mcb.campaign_id), 1) as reach_coverage_pct,
    COUNT(DISTINCT CASE WHEN mcb.total_impacts_all_adults > 0 THEN mcb.campaign_id END) as campaigns_with_impacts,
    COUNT(DISTINCT CASE WHEN mcb.total_impacts_all_adults = 0 THEN mcb.campaign_id END) as campaigns_missing_impacts,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN mcb.total_impacts_all_adults > 0 THEN mcb.campaign_id END) / COUNT(DISTINCT mcb.campaign_id), 1) as impacts_coverage_pct
FROM mv_campaign_browser mcb
LEFT JOIN cache_campaign_reach_full ccrf ON mcb.campaign_id = ccrf.campaign_id;

-- ============================================================================
-- 2. MISSING REACH BY CAMPAIGN SIZE
-- ============================================================================

-- Categorize missing reach campaigns by size
WITH missing_campaigns AS (
    SELECT
        mcb.campaign_id,
        mcb.total_playouts,
        mcb.total_frames,
        mcb.days_active,
        mcb.start_date,
        mcb.end_date
    FROM mv_campaign_browser mcb
    LEFT JOIN cache_campaign_reach_full ccrf ON mcb.campaign_id = ccrf.campaign_id
    WHERE ccrf.campaign_id IS NULL
)
SELECT
    CASE
        WHEN total_playouts < 1000000 THEN 'Small (<1M playouts)'
        WHEN total_playouts < 10000000 THEN 'Medium (1M-10M playouts)'
        WHEN total_playouts < 50000000 THEN 'Large (10M-50M playouts)'
        ELSE 'Very Large (>50M playouts)'
    END as campaign_size,
    COUNT(*) as campaign_count,
    MIN(total_playouts) as min_playouts,
    MAX(total_playouts) as max_playouts,
    MIN(start_date) as earliest_start,
    MAX(start_date) as latest_start
FROM missing_campaigns
GROUP BY
    CASE
        WHEN total_playouts < 1000000 THEN 'Small (<1M playouts)'
        WHEN total_playouts < 10000000 THEN 'Medium (1M-10M playouts)'
        WHEN total_playouts < 50000000 THEN 'Large (10M-50M playouts)'
        ELSE 'Very Large (>50M playouts)'
    END
ORDER BY MIN(total_playouts);

-- ============================================================================
-- 3. RECENT CAMPAIGNS MISSING CACHE DATA
-- ============================================================================

-- Find recent campaigns that should have been cached but aren't
SELECT
    mcb.campaign_id,
    mcb.total_playouts,
    mcb.total_frames,
    mcb.days_active,
    mcb.start_date,
    mcb.end_date,
    mcb.last_activity,
    CASE WHEN ccrf.campaign_id IS NULL THEN 'MISSING' ELSE 'OK' END as reach_status,
    CASE WHEN mcb.total_impacts_all_adults = 0 THEN 'MISSING' ELSE 'OK' END as impacts_status
FROM mv_campaign_browser mcb
LEFT JOIN cache_campaign_reach_full ccrf ON mcb.campaign_id = ccrf.campaign_id
WHERE mcb.start_date >= '2025-09-01'  -- Recent campaigns
  AND (ccrf.campaign_id IS NULL OR mcb.total_impacts_all_adults = 0)
  AND mcb.total_playouts < 10000000  -- Should be small enough for API
ORDER BY mcb.start_date DESC;

-- ============================================================================
-- 4. VERIFY CAMPAIGNS EXIST IN SOURCE DATA
-- ============================================================================

-- Check if missing campaigns exist in playout_data (they should)
SELECT
    'Source Data Verification' as check_type,
    TRIM(BOTH FROM pd.buyercampaignref) as campaign_id,
    COUNT(*) as playout_records,
    MIN(pd.startdate) as earliest_playout,
    MAX(pd.startdate) as latest_playout,
    COUNT(DISTINCT pd.frameid) as unique_frames,
    CASE WHEN ccrf.campaign_id IS NULL THEN 'MISSING FROM CACHE' ELSE 'IN CACHE' END as reach_cache_status
FROM playout_data pd
LEFT JOIN cache_campaign_reach_full ccrf
    ON TRIM(BOTH FROM pd.buyercampaignref) = ccrf.campaign_id
WHERE TRIM(BOTH FROM pd.buyercampaignref) IN (
    SELECT campaign_id
    FROM mv_campaign_browser mcb
    LEFT JOIN cache_campaign_reach_full ccrf2 ON mcb.campaign_id = ccrf2.campaign_id
    WHERE ccrf2.campaign_id IS NULL
    LIMIT 10  -- Sample of missing campaigns
)
GROUP BY TRIM(BOTH FROM pd.buyercampaignref), ccrf.campaign_id
ORDER BY COUNT(*) ASC;

-- ============================================================================
-- 5. CACHE FRESHNESS CHECK
-- ============================================================================

-- Check when cache tables were last updated (if timestamp columns exist)
-- Note: Adjust column names if your cache tables have different timestamp fields

-- Check if cache_campaign_reach_full has recent data
SELECT
    'Reach Cache Freshness' as cache_type,
    COUNT(*) as total_records,
    MIN(reach) as min_reach,
    MAX(reach) as max_reach,
    COUNT(*) FILTER (WHERE reach = 0) as zero_reach_count
FROM cache_campaign_reach_full;

-- Check cache_route_impacts_15min_by_demo freshness
SELECT
    'Impacts Cache Freshness' as cache_type,
    COUNT(DISTINCT campaign_id) as unique_campaigns,
    COUNT(*) as total_records,
    COUNT(DISTINCT demographic_segment) as demographics_count,
    SUM(impacts) as total_impacts_thousands
FROM cache_route_impacts_15min_by_demo;

-- ============================================================================
-- 6. CAMPAIGNS WITH IMPACTS BUT NO REACH (ILLOGICAL)
-- ============================================================================

-- These campaigns are illogical - can't have impacts without reach
SELECT
    mcb.campaign_id,
    mcb.total_playouts,
    mcb.total_frames,
    mcb.total_reach_all_adults as reach_thousands,
    mcb.total_impacts_all_adults as impacts_thousands,
    mcb.start_date,
    mcb.end_date,
    mcb.primary_brand
FROM mv_campaign_browser mcb
LEFT JOIN cache_campaign_reach_full ccrf ON mcb.campaign_id = ccrf.campaign_id
WHERE ccrf.campaign_id IS NULL  -- No reach
  AND mcb.total_impacts_all_adults > 0  -- But has impacts
ORDER BY mcb.total_impacts_all_adults DESC
LIMIT 20;

-- ============================================================================
-- 7. MONITOR BACKFILL PROGRESS
-- ============================================================================

-- Run this query before and after backfill to track progress
SELECT
    'Backfill Progress' as report_type,
    NOW() as report_timestamp,
    COUNT(DISTINCT mcb.campaign_id) as total_campaigns,
    COUNT(DISTINCT CASE WHEN ccrf.campaign_id IS NOT NULL THEN mcb.campaign_id END) as cached_campaigns,
    COUNT(DISTINCT CASE WHEN ccrf.campaign_id IS NULL THEN mcb.campaign_id END) as uncached_campaigns,
    COUNT(DISTINCT CASE
        WHEN ccrf.campaign_id IS NULL
        AND mcb.total_playouts < 10000000
        THEN mcb.campaign_id
    END) as priority_uncached,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN ccrf.campaign_id IS NOT NULL THEN mcb.campaign_id END) / COUNT(DISTINCT mcb.campaign_id), 2) as coverage_pct
FROM mv_campaign_browser mcb
LEFT JOIN cache_campaign_reach_full ccrf ON mcb.campaign_id = ccrf.campaign_id;

-- ============================================================================
-- 8. SPECIFIC CAMPAIGN DEEP DIVE
-- ============================================================================

-- Replace '18856' with campaign ID to investigate
WITH campaign_detail AS (
    SELECT
        mcb.campaign_id,
        mcb.total_playouts,
        mcb.total_frames,
        mcb.days_active,
        mcb.start_date,
        mcb.end_date,
        mcb.total_reach_all_adults,
        mcb.total_impacts_all_adults,
        ccrf.reach as reach_in_cache,
        COUNT(DISTINCT cri.demographic_segment) as demographics_in_impacts_cache
    FROM mv_campaign_browser mcb
    LEFT JOIN cache_campaign_reach_full ccrf ON mcb.campaign_id = ccrf.campaign_id
    LEFT JOIN cache_route_impacts_15min_by_demo cri ON mcb.campaign_id = cri.campaign_id
    WHERE mcb.campaign_id = '18856'
    GROUP BY mcb.campaign_id, mcb.total_playouts, mcb.total_frames, mcb.days_active,
             mcb.start_date, mcb.end_date, mcb.total_reach_all_adults,
             mcb.total_impacts_all_adults, ccrf.reach
)
SELECT
    cd.*,
    CASE WHEN cd.reach_in_cache IS NULL THEN 'MISSING FROM CACHE' ELSE 'IN CACHE' END as reach_status,
    CASE WHEN cd.demographics_in_impacts_cache = 0 THEN 'MISSING FROM CACHE' ELSE 'IN CACHE' END as impacts_status,
    -- Check source data
    (SELECT COUNT(*) FROM playout_data WHERE TRIM(BOTH FROM buyercampaignref) = cd.campaign_id) as playout_records_in_source
FROM campaign_detail cd;
