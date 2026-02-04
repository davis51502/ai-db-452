# Natural Language to SQL: Financial Terminal Examples

### 1. Selection
**Question:** "What is the name and sector of Apple?"
**SQL:** `SELECT name, sector FROM Companies WHERE ticker = 'AAPL';`
**Status:** Worked.

### 2. Aggregation
**Question:** "What is the average revenue across all companies?"
**SQL:** `SELECT AVG(revenue) AS average_revenue FROM Financials;`
**Status:** Worked.

### 3. Join Logic
**Question:** "Show me the revenue for Tesla."
**SQL:** `SELECT revenue FROM Financials JOIN Companies ON Financials.ticker = Companies.ticker WHERE name = 'Tesla Inc.';`
**Status:** Worked.

### 4. Sorting & Filtering
**Question:** "Top 3 companies by net income."
**SQL:** `SELECT c.ticker, c.name, f.net_income FROM Companies c JOIN Financials f ON c.ticker = f.ticker ORDER BY f.net_income DESC LIMIT 3;`
**Status:** Worked.

### 5. Complex Financial Logic
**Question:** "Which company has a WACC lower than 9% and positive upside?"
**SQL:** `SELECT name FROM Companies JOIN Valuations ON Companies.ticker = Valuations.ticker WHERE Valuations.wacc < 0.09 AND Valuations.upside_percent > 0;`
**Status:** Worked.

### 6. Failed Example
**Question:** "who is the CEO of telsa."
**SQL:** `I'm sorry, I can only provide SQL query responses related to the given database schema.`
**Result:** **Failed.** AI-generated SQL is not a safe SELECT. Aborting.
