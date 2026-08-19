-- ============================================================
-- Deduplication by code: identical bytecode = one audit.
-- Runs AFTER stuck_contracts.sql. Save the result of the first query
-- as a table (Save Results -> BigQuery table -> dataset: my_results,
-- table: candidates) and substitute its name below.
--
-- This saves hours: if 200 contracts are 3 clusters of identical code,
-- you need to audit 3 times, not 200.
-- ============================================================

SELECT
  code_fp,
  COUNT(*) AS n_contracts,
  SUM(eth_balance) / 1e18 AS total_eth,
  ARRAY_AGG(address LIMIT 3) AS example_addresses
FROM `my_project.my_results.candidates`
GROUP BY code_fp
ORDER BY n_contracts DESC;
