-- ============================================================
-- Stuck contracts scanner v1 (BigQuery public dataset)
-- Run: https://console.cloud.google.com/bigquery (needs a Google account,
-- free tier 1 TB of processed data per month — that is enough).
-- Cost of this query: ~200-400 GB (shown in the console before running).
--
-- Logic:
--   1) take all contracts deployed before 2020 whose bytecode
--      contains at least one "withdrawal" selector (refund/claim/withdraw/...);
--   2) join the balance from crypto_ethereum.balances (updated daily);
--   3) drop contracts that sent anything out in the last 12 months;
--   4) compute a code fingerprint for deduplication (identical code = one audit).
--
-- Export the result: SAVE RESULTS button -> CSV -> file results.csv
-- Next: python scanner/rank.py results.csv
-- ============================================================

DECLARE min_eth FLOAT64 DEFAULT 0.25;   -- minimum ETH on the contract
DECLARE max_deploy TIMESTAMP DEFAULT TIMESTAMP('2020-01-01');  -- older than this year
DECLARE dormant_months INT64 DEFAULT 12;  -- no outgoing transactions for N months

WITH recent_outgoing AS (
  SELECT from_address, MAX(block_timestamp) AS last_out
  FROM `bigquery-public-data.crypto_ethereum.transactions`
  WHERE block_timestamp >= TIMESTAMP(DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH))
  GROUP BY from_address
)
SELECT
  c.address,
  b.eth_balance,
  b.eth_balance / 1e18 AS eth,
  c.block_timestamp AS deployed_at,
  c.block_number,
  SUBSTR(TO_BASE64(SHA1(SUBSTR(c.bytecode, 1, 65536))), 1, 16) AS code_fp,
  ARRAY_TO_STRING(c.function_sighashes, ',') AS sighashes,
  r.last_out
FROM `bigquery-public-data.crypto_ethereum.contracts` AS c
JOIN `bigquery-public-data.crypto_ethereum.balances` AS b
  ON b.address = c.address
LEFT JOIN recent_outgoing AS r
  ON r.from_address = c.address
WHERE c.block_timestamp < TIMESTAMP('2020-01-01')
  AND b.eth_balance >= 0.25
  AND EXISTS (
    SELECT 1
    FROM UNNEST(c.function_sighashes) AS fs
    WHERE fs IN (
      '0x590e1ae3','0x278ecde1','0x38e771ab','0x4e71d92d','0x379607f5',
      '0x48c54b9d','0x46e04a2f','0xd1058e59','0x3ccfd60b','0x2e1a7d4d',
      '0x853828b6','0x4bb278f3','0x78abfbeb','0xe9fad8ee','0x41c0e1b5',
      '0x9890220b','0xa69df4b5','0xf968f493','0x86d1a69f','0xa96f8668',
      '0x80e9071b','0x84054d3d','0xb2d5ae44','0xe84f7054','0x110f8874',
      '0x4311de8f','0x33f707d1','0xdb2e21bc','0x5641ec03','0x1fbe1979',
      '0xdd8c2e0f','0x35faa416','0x8925dbcc','0xb79550be','0xb77f39fe',
      '0xe5225381','0x8433acd1','0x7362377b','0xe086e5ec'
    )
  )
  AND r.from_address IS NULL              -- no outgoing tx for 12 months
ORDER BY b.eth_balance DESC
LIMIT 500;
