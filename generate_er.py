import os
import argparse
import pyperclip
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData


class DBSchemaGenerator:
    """
    Connects to a MySQL or PostgreSQL database, reflects its schema,
    and generates both a Mermaid ER diagram and a SQL data schema.
    """

    def __init__(self, db_uri: str):
        self.engine = create_engine(db_uri)
        self.metadata = MetaData()

    def _reflect(self):
        if not self.metadata.tables:
            self.metadata.reflect(bind=self.engine)

    def generate_er_diagram(self) -> str:
        """Builds Mermaid erDiagram syntax from the reflected schema."""
        self._reflect()
        lines = ["erDiagram"]

        # Tables and columns
        for table_name, table in self.metadata.tables.items():
            lines.append(f"    {table_name} {{")
            for col in table.columns:
                col_type = str(col.type).split("(")[0].replace(" ", "_")
                marker = " PK" if col.primary_key else (" FK" if col.foreign_keys else "")
                lines.append(f"        {col_type} {col.name}{marker}")
            lines.append("    }")

        # Relationships
        for table_name, table in self.metadata.tables.items():
            for fk in table.foreign_keys:
                parent = fk.column.table.name
                lines.append(
                    f"    {table_name} }}o--|| {parent} : \"{fk.parent.name} references {fk.column.name}\""
                )

        return "\n".join(lines)

    def generate_data_schema(self) -> str:
        """Builds a SQL CREATE TABLE schema from the reflected metadata."""
        self._reflect()
        statements = []

        for table_name, table in self.metadata.tables.items():
            col_defs = []
            for col in table.columns:
                col_type = str(col.type)
                nullable = "" if col.nullable else " NOT NULL"
                pk = " PRIMARY KEY" if col.primary_key and len(table.primary_key.columns) == 1 else ""
                default = f" DEFAULT {col.default.arg}" if col.default and not callable(col.default.arg) else ""
                col_defs.append(f"    {col.name} {col_type}{nullable}{pk}{default}")

            # Composite PK
            if len(table.primary_key.columns) > 1:
                pk_cols = ", ".join(c.name for c in table.primary_key.columns)
                col_defs.append(f"    PRIMARY KEY ({pk_cols})")

            # Foreign keys
            for fk in table.foreign_keys:
                col_defs.append(
                    f"    FOREIGN KEY ({fk.parent.name}) REFERENCES {fk.column.table.name}({fk.column.name})"
                )

            block = f"CREATE TABLE {table_name} (\n" + ",\n".join(col_defs) + "\n);"
            statements.append(block)

        return "\n\n".join(statements)


def build_uri(db_type: str) -> str:
    """Constructs the SQLAlchemy URI based on the selected db type."""
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    db = os.getenv("DB_NAME")

    if not all([host, port, user, password, db]):
        raise ValueError("Missing database configuration in .env file.")

    if db_type == "postgres":
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    else:
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"


def main():
    parser = argparse.ArgumentParser(
        description="Generate Mermaid ER diagram and SQL schema from a database."
    )
    parser.add_argument(
        "--db",
        choices=["mysql", "postgres"],
        default="mysql",
        help="Database type to connect to (default: mysql)",
    )
    parser.add_argument(
        "--output",
        choices=["er", "schema", "both"],
        default="both",
        help="What to generate: er diagram, sql schema, or both (default: both)",
    )
    args = parser.parse_args()

    load_dotenv()

    try:
        db_uri = build_uri(args.db)
        print(f"Connecting via {args.db.upper()}...")
        gen = DBSchemaGenerator(db_uri)

        clipboard_parts = []

        if args.output in ("er", "both"):
            er = gen.generate_er_diagram()
            print("\n--- Mermaid ER Diagram ---\n")
            print(er)
            clipboard_parts.append(("ER Diagram", er))

        if args.output in ("schema", "both"):
            schema = gen.generate_data_schema()
            print("\n--- SQL Data Schema ---\n")
            print(schema)
            clipboard_parts.append(("SQL Schema", schema))

        # Copy to clipboard
        if len(clipboard_parts) == 1:
            pyperclip.copy(clipboard_parts[0][1])
            print(f"\n✅ {clipboard_parts[0][0]} copied to clipboard!")
        else:
            combined = "\n\n".join(f"-- {label} --\n{content}" for label, content in clipboard_parts)
            pyperclip.copy(combined)
            print("\n✅ Both ER diagram and SQL schema copied to clipboard!")

        if args.output in ("er", "both"):
            print("   Paste the ER diagram into: https://mermaid.live/")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
