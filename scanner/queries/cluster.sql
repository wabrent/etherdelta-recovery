-- ============================================================
-- Дедупликация по коду: одинаковый байткод = один аудит.
-- Запускается ПОСЛЕ stuck_contracts.sql. Результат первого запроса
-- сохрани как таблицу (Save Results -> BigQuery table -> dataset: my_results,
-- table: candidates) и подставь её имя ниже.
--
-- Это экономит часы: если 200 контрактов — это 3 кластера одинакового кода,
-- аудировать нужно 3 раза, а не 200.
-- ============================================================

SELECT
  code_fp,
  COUNT(*) AS n_contracts,
  SUM(eth_balance) / 1e18 AS total_eth,
  ARRAY_AGG(address LIMIT 3) AS example_addresses
FROM `my_project.my_results.candidates`
GROUP BY code_fp
ORDER BY n_contracts DESC;
