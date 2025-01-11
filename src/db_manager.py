import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
from packaging import version
from .pdf_processor import load_pdfs_from_directory

class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect('./data/documents.db')
        self.cursor = self.conn.cursor()
        self._ensure_tables_exist()
    
    def _ensure_tables_exist(self):
        """Ensure required tables exist"""
        self.cursor.execute('''
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
        self.conn.commit()

    def store_document_chunk(self, content: str, metadata: Dict) -> bool:
        """Store a document chunk with its metadata"""
        try:
            # Validate date format
            try:
                date_obj = datetime.strptime(metadata['date'], '%Y-%m-%d')
                formatted_date = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                print(f"Invalid date format in metadata: {metadata['date']}")
                return False

            # Validate version format
            try:
                _ = version.parse(metadata['version'])
            except version.InvalidVersion:
                print(f"Invalid version format in metadata: {metadata['version']}")
                return False

            # Create unique ID from content and metadata
            id_string = f"{content}{formatted_date}{metadata['version']}{metadata['chunk_id']}"
            doc_id = hashlib.md5(id_string.encode()).hexdigest()

            self.cursor.execute('''
                INSERT INTO document_chunks 
                (id, content, date, version, security, source, chunk_id, total_chunks)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_id,
                content,
                formatted_date,
                metadata['version'],
                metadata['security'],
                metadata['source'],
                metadata['chunk_id'],
                metadata['total_chunks']
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error storing document chunk: {e}")
            return False

    def store_initial_documents(self) -> None:
        """Store documents from PDFs with chunking"""
        # Check if documents already exist
        self.cursor.execute('SELECT COUNT(*) FROM document_chunks')
        if self.cursor.fetchone()[0] > 0:
            print("\nDocuments already exist in the database")
            return

        # Load and chunk documents from PDFs
        documents = load_pdfs_from_directory()
    
        print("\nStoring document chunks...")
        for doc in documents:
            success = self.store_document_chunk(
                content=doc["content"],
                metadata=doc["metadata"]
            )
            if success:
                print(f"Stored chunk {doc['metadata']['chunk_id']} from {doc['metadata']['source']}")


    def find_closest_date_documents(self, target_date: str) -> Optional[Dict]:
   
        try:
        # Find documents with closest date and get all their details
            self.cursor.execute('''
                WITH ClosestDate AS (
                    SELECT date
                    FROM document_chunks
                    GROUP BY date
                    ORDER BY ABS(julianday(date) - julianday(?))
                    LIMIT 1
                )
                SELECT * 
                FROM document_chunks d
                WHERE d.date = (SELECT date FROM ClosestDate)
            ''', (target_date,))
            
            results = self.cursor.fetchall()
            if not results:
                return None

            # If multiple docs exist for same date, get the latest version
            if len(results) > 1:
                latest_doc = max(results, key=lambda x: version.parse(x[3]))
                results = [latest_doc]

            chunks = []
            for result in results:
                chunks.append({
                    'content': result[1],
                    'metadata': {
                        'date': result[2],
                        'version': result[3],
                        'security': result[4],
                        'source': result[5],
                        'chunk_id': result[6],
                        'total_chunks': result[7]
                    }
                })

            return {
                'chunks': chunks,
                'total_chunks': len(chunks),
                'document_metadata': {
                    'date': results[0][2],
                    'version': results[0][3],
                    'security': results[0][4],
                    'source': results[0][5]
                }
            }

        except Exception as e:
            print(f"Error finding documents: {e}")
            return None


    def search_with_security(self, target_date: str, security_level: str) -> Optional[Dict]:
        """Find documents with specified security level closest to target date"""
        try:
            # Find closest date document with matching security
            self.cursor.execute('''
                WITH ClosestSecureDoc AS (
                    SELECT DISTINCT date, source 
                    FROM document_chunks
                    WHERE security = ?
                    ORDER BY ABS(julianday(date) - julianday(?))
                    LIMIT 1
                )
                SELECT *
                FROM document_chunks d
                WHERE d.date = (SELECT date FROM ClosestSecureDoc)
                AND d.source = (SELECT source FROM ClosestSecureDoc)
                AND d.security = ?
                ORDER BY d.chunk_id
            ''', (security_level, target_date, security_level))
            
            results = self.cursor.fetchall()
            if not results:
                return None

            
            chunks = []
            for result in results:
                chunks.append({
                    'content': result[1],
                    'metadata': {
                        'date': result[2],
                        'version': result[3],
                        'security': result[4],
                        'source': result[5],
                        'chunk_id': result[6],
                        'total_chunks': result[7]
                    }
                })

            return {
                'chunks': chunks,
                'total_chunks': len(chunks),
                'document_metadata': {
                    'date': results[0][2],
                    'version': results[0][3],
                    'security': results[0][4],
                    'source': results[0][5]
                }
            }

        except Exception as e:
            print(f"Error searching documents: {e}")
            return None

    def view_all_documents(self) -> List[Dict]:
        """Retrieve all documents from the database"""
        try:
            self.cursor.execute('SELECT * FROM document_chunks ORDER BY date, version DESC')
            results = self.cursor.fetchall()
            return [{
                'content': result[1],
                'metadata': {
                    'date': result[2],
                    'version': result[3],
                    'security': result[4],
                    'source': result[5],
                    'chunk_id': result[6],
                    'total_chunks': result[7]
                }
            } for result in results]
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []

    def clear_database(self) -> bool:
        """Clear all documents from the database"""
        try:
            self.cursor.execute('DELETE FROM document_chunks')
            self.conn.commit()
            print("\nDatabase cleared successfully")
            return True
        except Exception as e:
            print(f"\nError clearing database: {e}")
            return False

    def __del__(self):
        """Ensure connection is closed when object is destroyed"""
        self.conn.close()