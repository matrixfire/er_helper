# er-helper

A CLI tool that connects to a MySQL database, inspects its schema, and generates a [Mermaid](https://mermaid.js.org/) ER diagram — then automatically copies it to your clipboard so you can paste it straight into [mermaid.live](https://mermaid.live/).

## Features

- Reflects your full MySQL schema using SQLAlchemy (tables, columns, types, PKs, FKs)
- Generates valid Mermaid `erDiagram` syntax
- Auto-copies the output to your clipboard via `pyperclip`

## Requirements

- Python >= 3.13
- A running MySQL database

## Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install dependencies
uv sync
```

If you prefer pip:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DB=your_database
```

## Usage

```bash
uv run python generate_er.py
```

The diagram will be printed to the terminal and automatically copied to your clipboard. Just open [mermaid.live](https://mermaid.live/) and paste.

## Example Output

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

## License

MIT
