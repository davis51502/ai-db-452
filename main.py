import sqlite3
import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import sys

# Load .env if present
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not set. Edit .env or export environment variable.")
    print("See README.md for instructions.")
    sys.exit(1)

client = OpenAI()

DB_NAME = "bloomberg_mini.db"

SCHEMA_PROMPT = """
Table: Companies
- ticker (TEXT, Primary Key): The stock symbol (e.g., 'AAPL')
- name (TEXT): Full company name
- sector (TEXT): Industry sector

Table: Financials
- id (INTEGER, Primary Key)
- ticker (TEXT, Foreign Key -> Companies.ticker)
- revenue (REAL): Total annual revenue
- net_income (REAL): Total annual profit
- fcf (REAL): Free Cash Flow
- period_end_date (TEXT): Date of the filing

Table: Valuations
- ticker (TEXT, Primary Key, Foreign Key -> Companies.ticker)
- implied_value (REAL): Calculated DCF share price
- wacc (REAL): Weighted Average Cost of Capital (as a decimal, e.g., 0.08)
- upside_percent (REAL): Percentage difference to current price
"""

# Database initialization
def init_db(db_path: str = DB_NAME):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS Companies (ticker TEXT PRIMARY KEY, name TEXT, sector TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS Financials (id INTEGER PRIMARY KEY, ticker TEXT, revenue REAL, net_income REAL, fcf REAL, period_end_date TEXT, FOREIGN KEY(ticker) REFERENCES Companies(ticker))")
    cursor.execute("CREATE TABLE IF NOT EXISTS Valuations (ticker TEXT PRIMARY KEY, implied_value REAL, wacc REAL, upside_percent REAL, FOREIGN KEY(ticker) REFERENCES Companies(ticker))")

    companies = [('AAPL', 'Apple Inc.', 'Technology'), ('TSLA', 'Tesla Inc.', 'Automotive'), ('NVDA', 'NVIDIA Corp.', 'Technology')]
    financials = [
        (1, 'AAPL', 394000, 99000, 111000, '2025-09-30'),
        (2, 'TSLA', 96000, 15000, 7500, '2025-12-31'),
        (3, 'NVDA', 60000, 29000, 26000, '2025-10-30')
    ]
    vals = [('AAPL', 215.0, 0.08, 12.0), ('TSLA', 180.0, 0.10, -5.0), ('NVDA', 900.0, 0.09, 15.5)]

    cursor.executemany("INSERT OR REPLACE INTO Companies VALUES (?,?,?)", companies)
    cursor.executemany("INSERT OR REPLACE INTO Financials VALUES (?,?,?,?,?,?)", financials)
    cursor.executemany("INSERT OR REPLACE INTO Valuations VALUES (?,?,?,?)", vals)

    conn.commit()
    conn.close()

# AI helpers
def ask_ai_for_sql(question: str) -> str:
    sys_msg = f"You are a SQL expert. Use this schema: {SCHEMA_PROMPT}. Return ONLY the SQL query for SQLite. Use valid column names and types. Answer with a single SQL statement and nothing else."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": question}
        ],
        max_tokens=512
    )
    sql = response.choices[0].message.content
    # Strip markdown fences if present
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

# Friendly answer generator
def ask_ai_for_friendly_answer(question: str, sql_query: str, results) -> str:
    prompt = f"User asked: {question}\nSQL used: {sql_query}\nResults: {results}\nGive a friendly, concise answer."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256
    )
    return response.choices[0].message.content

# Very small safety check: only allow SELECT queries
def is_safe_select(sql: str) -> bool:
    sql_stripped = sql.strip().lower()
    # allow common leading parentheses or with-clause space
    sql_start = sql_stripped.split(None, 1)[0] if sql_stripped else ""
    return sql_start == 'select' or sql_stripped.startswith('with ')

def run_query(sql: str, db_path: str = DB_NAME):
    if not is_safe_select(sql):
        raise ValueError("Unsafe SQL detected. Only SELECT queries are allowed.")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    columns = [description[0] for description in cur.description] if cur.description else []
    conn.close()
    return columns, rows

# CLI
def main():
    db_path = DB_NAME
    init_db(db_path)
    print('--- Mini-Bloomberg AI Terminal ---')
    print('Type "quit" or "exit" to leave.')

    while True:
        user_q = input('\nQuestion: ').strip()
        if not user_q:
            continue
        if user_q.lower() in ('quit', 'exit'):
            print('Goodbye.')
            break

        try:
            sql = ask_ai_for_sql(user_q)
            print(f"\n[Generated SQL]: {sql}")

            if not is_safe_select(sql):
                print('\n[Error]: AI-generated SQL is not a safe SELECT. Aborting.')
                continue

            cols, rows = run_query(sql, db_path)
            print('\n[Raw Results]:')
            if rows:
                # print as simple table
                header = ' | '.join(cols) if cols else ''
                print(header)
                for r in rows:
                    print(' | '.join(str(x) for x in r))
            else:
                print('No rows returned.')

            friendly = ask_ai_for_friendly_answer(user_q, sql, rows)
            print(f"\n[AI Answer]: {friendly}\n")

        except Exception as e:
            print(f"\n[Error]: {e}\n")

if __name__ == '__main__':
    main()
