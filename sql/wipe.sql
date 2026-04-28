-- Full wipe: clear all data, keep schema.
-- Run before re-scraping with the patched paginated scraper.

TRUNCATE deaths CASCADE;
TRUNCATE token_panel CASCADE;
TRUNCATE tokens RESTART IDENTITY CASCADE;
TRUNCATE cmc_snapshots RESTART IDENTITY CASCADE;
TRUNCATE scrape_log RESTART IDENTITY CASCADE;

-- Confirm everything is empty
SELECT 'cmc_snapshots' AS tbl, COUNT(*) FROM cmc_snapshots
UNION ALL SELECT 'tokens',       COUNT(*) FROM tokens
UNION ALL SELECT 'token_panel',  COUNT(*) FROM token_panel
UNION ALL SELECT 'deaths',       COUNT(*) FROM deaths
UNION ALL SELECT 'scrape_log',   COUNT(*) FROM scrape_log;
