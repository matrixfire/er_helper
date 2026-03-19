import os
import argparse
import pyperclip
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData

class MermaidERGenerator:
    """
    Connects to a database, inspects its schema, and generates a Mermaid ER diagram.
    """
    def __init__(self, db_uri: str):
        # Create an engine to connect to the database
        self.engine = create_engine(db_uri)
        self.metadata = MetaData()
        
    def generate_diagram(self) -> str:
        """Reflects the database and builds the Mermaid syntax string."""
        # Reflect reads the database schema and populates the MetaData object
        self.metadata.reflect(bind=self.engine)
        
        mermaid_lines = ["erDiagram"]
        
        # 1. Document the Tables and Columns
        for table_name, table in self.metadata.tables.items():
            mermaid_lines.append(f"    {table_name} {{")
            
            for column in table.columns:
                # Format the data type (cleaning up parentheses for Mermaid compatibility)
                col_type = str(column.type).split('(')[0].replace(" ", "_")
                
                # Determine keys
                key_marker = ""
                if column.primary_key:
                    key_marker = " PK"
                elif column.foreign_keys:
                    key_marker = " FK"
                
                mermaid_lines.append(f"        {col_type} {column.name}{key_marker}")
                
            mermaid_lines.append("    }")

        # 2. Document the Relationships (Foreign Keys)
        for table_name, table in self.metadata.tables.items():
            for fk in table.foreign_keys:
                # Extract the parent table name from the foreign key target
                parent_table = fk.column.table.name
                
                # Mermaid syntax for Many-to-One relationship
                # Assuming standard normalized tables: Child }o--|| Parent
                relationship = f"    {table_name} }}o--|| {parent_table} : \"{fk.parent.name} references {fk.column.name}\""
                mermaid_lines.append(relationship)

        return "\n".join(mermaid_lines)


def main():
    # Setup Argument Parser for future command-line usage
    parser = argparse.ArgumentParser(description="Generate a Mermaid ER diagram from a MySQL database.")
    parser.parse_args()

    # Load credentials from .env file
    load_dotenv()
    
    # Safely get environment variables
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    host = os.getenv("MYSQL_HOST")
    port = os.getenv("MYSQL_PORT")
    db = os.getenv("MYSQL_DB")

    if not all([user, password, host, port, db]):
        print("Error: Missing database configuration in .env file.")
        return

    # Construct the SQLAlchemy Database URI
    # Using pymysql as the driver
    db_uri = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"

    try:
        print(f"Connecting to {db} at {host}...")
        generator = MermaidERGenerator(db_uri)
        mermaid_code = generator.generate_diagram()
        
        print("\n--- Mermaid ER Diagram Generated Successfully ---\n")
        print(mermaid_code)
        print("\n-------------------------------------------------")
        
        # Auto-copy to clipboard so you can paste directly into mermaid.live
        pyperclip.copy(mermaid_code)
        print("✅ Diagram copied to clipboard! Paste it into: https://mermaid.live/")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()