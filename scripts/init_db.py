import sqlite3
import os

def init_database():
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Connect to SQLite database (creates it if it doesn't exist)
    conn = sqlite3.connect('data/documents.db')
    cursor = conn.cursor()

    # Create table for document chunks
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS document_chunks (
        id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        date DATE NOT NULL,
        version TEXT NOT NULL,
        security TEXT NOT NULL,
        source TEXT NOT NULL,
        chunk_id INTEGER NOT NULL,
        total_chunks INTEGER NOT NULL
    )
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully")