-- Overall business performance

SELECT
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT product_id) AS unique_products,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(revenue), 2) AS average_transaction_value,
    ROUND(AVG(discount) * 100, 2) AS average_discount_percent
FROM 'data/processed/transactions_processed.parquet';


-- Revenue by category

SELECT
    category,
    COUNT(*) AS transactions,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(AVG(revenue), 2) AS average_transaction_value
FROM 'data/processed/transactions_processed.parquet'
GROUP BY category
ORDER BY revenue DESC;


-- Revenue by city

SELECT
    city,
    COUNT(*) AS transactions,
    ROUND(SUM(revenue), 2) AS revenue
FROM 'data/processed/transactions_processed.parquet'
GROUP BY city
ORDER BY revenue DESC;


-- Monthly revenue trend

SELECT
    year,
    month,
    COUNT(*) AS transactions,
    ROUND(SUM(revenue), 2) AS revenue
FROM 'data/processed/transactions_processed.parquet'
GROUP BY year, month
ORDER BY year, month;