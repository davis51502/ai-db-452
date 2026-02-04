Mini Bloomberg AI Terminal

Setup

1. Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY
```

2. Create and activate a virtualenv, then install requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run

```bash
python main.py
```

Notes

- The app uses the OpenAI Python client. Place your API key in `OPENAI_API_KEY`.
- The script initializes a small SQLite DB in the workspace and seeds sample data.
- For safety, the assistant only allows `SELECT` queries; non-SELECT SQL will be blocked.
- Examples are in `examples.md`.

Prompting strategy (for your post)

- Initial approach: Zero-Shot prompting — provide the schema in the system message and ask for SQL.
- Improvement: Include explicit data types (e.g., "wacc as a decimal") in the schema so the model interprets numeric columns correctly and avoids confusion between percentage and absolute values.

Schema diagram

- To generate a schema picture, run your `schemacrawler` command locally as you planned.
# ai-db-452
