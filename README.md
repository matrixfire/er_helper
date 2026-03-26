# er-helper

A CLI tool that connects to a **MySQL** or **PostgreSQL** database, reflects its schema, and generates:

- A [Mermaid](https://mermaid.js.org/) ER diagram — paste directly into [mermaid.live](https://mermaid.live/)
- A SQL `CREATE TABLE` data schema

Both outputs are automatically copied to your clipboard.

## Features

- Supports MySQL and PostgreSQL
- Reflects full schema: tables, columns, types, PKs, FKs
- Generates Mermaid `erDiagram` syntax
- Generates SQL `CREATE TABLE` DDL schema
- Auto-copies output to clipboard via `pyperclip`

## Requirements

- Python >= 3.13
- A running MySQL or PostgreSQL database

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
uv sync
```

Or with pip:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=your_database
```

## Usage

```bash
# MySQL (default), generate both ER diagram + SQL schema
uv run python generate_er.py

# PostgreSQL
uv run python generate_er.py --db postgres

# Only ER diagram
uv run python generate_er.py --output er

# Only SQL schema
uv run python generate_er.py --output schema

# PostgreSQL, only ER diagram
uv run python generate_er.py --db postgres --output er
```

Output is printed to the terminal and copied to your clipboard automatically.

## Example Output

**ER Diagram:**
```
erDiagram
    users {
        INTEGER id PK
        VARCHAR name
        VARCHAR email
    }
    orders {
        INTEGER id PK
        INTEGER user_id FK
        DECIMAL total
    }
    orders }o--|| users : "user_id references id"
```

**SQL Schema:**
```sql
CREATE TABLE users (
    id INTEGER NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL
);

CREATE TABLE orders (
    id INTEGER NOT NULL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    total DECIMAL(10, 2),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## License

MIT
