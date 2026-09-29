\# Large-Scale Customer Analytics \& AI Platform



An end-to-end customer analytics platform that combines large-scale data processing, analytical SQL, machine learning, and an interactive business intelligence dashboard.



The system processes customer transaction data, performs data transformation and feature engineering, segments customers using K-Means clustering, predicts churn risk using a Random Forest model, and automatically presents the results through an interactive Streamlit dashboard.



\---



\## Project Overview



The platform follows this workflow:



Customer Transaction Data

&#x20;       ↓

Python Data Generation / Input

&#x20;       ↓

Polars Data Processing

&#x20;       ↓

Parquet Columnar Storage

&#x20;       ↓

DuckDB Analytical Queries

&#x20;       ↓

Customer Feature Engineering

&#x20;       ↓

Machine Learning

&#x20;  ├── K-Means Segmentation

&#x20;  └── Random Forest Churn Prediction

&#x20;       ↓

Streamlit Interactive BI Dashboard



\---



\## Key Features



\### 1. Large-Scale Data Processing



The project processes approximately:



\- 1,000,000 transaction records

\- 333,509 unique customers

\- 20,000 products

\- 32 months of transaction history



The pipeline uses:



\- Python

\- Polars

\- Parquet

\- DuckDB



Parquet provides columnar storage while Polars and DuckDB provide efficient analytical processing without requiring a distributed cluster.



\---



\## 2. Data Engineering Pipeline



The processing pipeline performs:



\- Data validation

\- Null checking

\- Positive-value validation

\- Date transformation

\- Revenue calculations

\- Discount calculations

\- Customer-level aggregation

\- Feature engineering

\- Analytical summarization



Processed datasets are stored as Parquet files.



\---



\## 3. Customer Segmentation



Customer behavior is analyzed using K-Means clustering.



Features include:



\- Total spend

\- Transaction frequency

\- Average order value

\- Quantity purchased

\- Average discount

\- Session duration

\- Pages viewed

\- Category diversity

\- Active months

\- Purchase recency



Four behavioral segments are generated:



\- High-Value Engaged

\- Regular Customers

\- Low-Engagement

\- High-Value Infrequent



These labels are interpretations of the resulting clusters rather than direct model outputs.



\---



\## 4. AI Churn Prediction



A Random Forest classifier predicts customer churn risk.



The historical churn target is constructed from customer purchasing behavior:



\- Historical features are calculated before a fixed cutoff date.

\- Future purchasing activity is used to construct the behavioral target.

\- The model is evaluated on a held-out test set.



\### Model Results



| Metric | Result |

|---|---:|

| ROC-AUC | 0.6372 |

| Accuracy | \~83% |

| Churn Recall | \~94% |



The model uses features including:



\- Session duration

\- Days since last purchase

\- Total spend

\- Average order value

\- Discount behavior

\- Pages viewed

\- Transaction count

\- Active months

\- Category count



Feature importance is displayed directly in the dashboard.



\---



\## 5. Interactive BI Dashboard



The Streamlit application automatically presents the processed analytical results.



\### Business Overview



Includes:



\- Total Revenue

\- Total Transactions

\- Average Order Value

\- Revenue by Category

\- Revenue by City

\- Monthly Revenue Trend

\- Year, category, and city filters



\### Customer Intelligence



Includes:



\- Customer segment distribution

\- Customer spend by segment

\- Transactions by segment

\- Customer value vs. transaction activity

\- Segment behavioral profiles

\- Interactive segment filtering



\### AI Predictions



Includes:



\- Churn-risk distribution

\- Churn probability distribution

\- Model performance metrics

\- Random Forest feature importance

\- High-risk customer identification

\- Customer-level churn probabilities



\---



\## Technology Stack



| Technology | Purpose |

|---|---|

| Python | Pipeline orchestration |

| Polars | Data processing |

| Parquet | Columnar data storage |

| DuckDB | Analytical SQL |

| NumPy | Numerical computation |

| Pandas | ML/dashboard data handling |

| Scikit-learn | Machine learning |

| Streamlit | Interactive dashboard |

| Plotly | Interactive visualizations |

| Git/GitHub | Version control |



\---



\## Project Structure



```text

large-scale-customer-ai/

│

├── data/

│   ├── raw/

│   └── processed/

│

├── generator/

│   └── generate\_data.py

│

├── pipeline/

│   ├── transform.py

│   ├── duckdb\_test.py

│   ├── run\_sales\_analysis.py

│   ├── customer\_features.py

│   ├── churn\_dataset.py

│   └── prepare\_powerbi.py

│

├── models/

│   ├── segmentation.py

│   ├── churn\_prediction.py

│   └── feature\_importance.py

│

├── sql/

│   └── sales\_analysis.sql

│

├── dashboard/

│   ├── app.py

│   └── pages/

│       ├── 2\_Customer\_Intelligence.py

│       └── 3\_AI\_Predictions.py

│

├── requirements.txt

├── README.md

└── .gitignore

