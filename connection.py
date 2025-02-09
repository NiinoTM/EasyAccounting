# connection.py
import os
import sqlite3
from pathlib import Path
from typing import Optional
from datetime import datetime

class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass

class DatabaseConnection:
    """Singleton database connection manager."""
    _instance = None
    DATE_FORMAT = "%Y-%m-%d"
    
    def __new__(cls, database_path: str = "data/financas.db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.database_path = Path(database_path)
            cls._instance.conn = None
            cls._instance.cursor = None
            cls._instance.init_database()
        return cls._instance

    def init_database(self) -> None:
        """Initialize database directory and connection."""
        try:
            # Create the database directory if it doesn't exist
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Initialize the connection
            self.conn = sqlite3.connect(self.database_path)
            self.cursor = self.conn.cursor()
            self.create_schema()
        except sqlite3.Error as e:
            raise DatabaseError(f"Error connecting to database: {e}")

    def create_schema(self):
        """Create the complete database schema if it doesn't exist."""
        try:
            # Account Categories table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS account_categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    normalized_name TEXT NOT NULL UNIQUE,
                    description TEXT
                );
            """)
            
            # Account Types table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS account_types (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    normal_balance TEXT CHECK(normal_balance IN ('debito', 'credito'))
                );
            """)
            
            # Accounts table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    normalized_name TEXT NOT NULL UNIQUE,
                    type TEXT CHECK(type IN ('debito', 'credito')),
                    specific_type TEXT,
                    specific_subtype TEXT,
                    category_id INTEGER,
                    balance REAL DEFAULT 0,
                    FOREIGN KEY (category_id) REFERENCES account_categories(id)
                );
            """)
            
            # Transactions table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    description TEXT,
                    debit_account INTEGER,
                    credit_account INTEGER,
                    amount REAL NOT NULL,
                    FOREIGN KEY (debit_account) REFERENCES accounts(id),
                    FOREIGN KEY (credit_account) REFERENCES accounts(id)
                );
            """)
            
            # Transaction Templates table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_templates (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    details TEXT,
                    debit_account INTEGER,
                    credit_account INTEGER,
                    amount REAL,
                    description TEXT,
                    FOREIGN KEY (debit_account) REFERENCES accounts(id),
                    FOREIGN KEY (credit_account) REFERENCES accounts(id)
                );
            """)
            
            # Fiscal Periods table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS fiscal_periods (
                    id INTEGER PRIMARY KEY,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    interval_days INTEGER NOT NULL,
                    is_closed BOOLEAN DEFAULT 0,
                    closing_date TEXT
                );
            """)
            
            # Depreciation Methods table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS depreciation_methods (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    annual_rate REAL
                );
            """)
            
            # Assets table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    acquisition_date TEXT NOT NULL,
                    acquisition_value REAL NOT NULL,
                    depreciation_method_id INTEGER,
                    useful_life_years INTEGER,
                    salvage_value REAL,
                    start_depreciation_date TEXT NOT NULL,
                    account_id INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (depreciation_method_id) REFERENCES depreciation_methods(id),
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
                );
            """)
            
            # Asset Depreciation History table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS asset_depreciation_history (
                    id INTEGER PRIMARY KEY,
                    asset_id INTEGER,
                    depreciation_date TEXT NOT NULL,
                    depreciation_amount REAL NOT NULL,
                    accumulated_depreciation REAL NOT NULL,
                    book_value REAL NOT NULL,
                    FOREIGN KEY (asset_id) REFERENCES assets(id)
                );
            """)
            
            # Commit all changes
            self.conn.commit()
            
            # Prepopulate essential data
            self._prepopulate_initial_data()
            
        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"Error creating schema: {e}")
            
    def _prepopulate_initial_data(self):
        """Prepopulate essential data in the database."""
        try:
            # Prepopulate account types
            self.cursor.execute("""
                INSERT OR IGNORE INTO account_types (name, normal_balance) VALUES 
                ('despesas', 'debito'),
                ('ativos', 'debito'),
                ('compras', 'debito'),
                ('passivos', 'credito'),
                ('entradas', 'credito'),
                ('vendas', 'credito'),
                ('patrimonio', 'credito');
            """)
            
            # Prepopulate depreciation methods
            self.cursor.execute("""
                INSERT OR IGNORE INTO depreciation_methods (name, description, annual_rate) VALUES 
                ('Linear', 'Depreciation is spread evenly across the asset''s useful life', 0),
                ('Declining Balance', 'Accelerated depreciation with higher initial amounts', 2),
                ('Sum of Years Digits', 'Accelerated depreciation based on remaining life', 0);
            """)
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"Error prepopulating data: {e}")

    def execute(self, sql: str, parameters: tuple = ()) -> sqlite3.Cursor:
        """Execute a SQL query and return the cursor."""
        try:
            self.cursor.execute(sql, parameters)
            self.conn.commit()
            return self.cursor
        except sqlite3.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"Error executing query: {e}")

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()