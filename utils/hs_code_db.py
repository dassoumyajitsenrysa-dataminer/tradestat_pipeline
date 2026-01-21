"""
SQLite-based HS Code manager.
Replaces text file approach for better performance with 10,000+ codes.

Benefits:
- O(1) lookups instead of O(n)
- Better tracking of HS code status
- Easy to add metadata
- Query-able
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import sqlite3
from config.settings import DATA_DIR
from utils.logger import get_logger

logger = get_logger("HS_CODE_DB")

DB_PATH = DATA_DIR / "hs_codes.db"


class HSCodeDatabase:
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hs_codes (
                    hs_code TEXT PRIMARY KEY,
                    status TEXT DEFAULT 'pending',
                    last_scraped_at TIMESTAMP,
                    export_status TEXT DEFAULT 'pending',
                    import_status TEXT DEFAULT 'pending',
                    export_scraped_at TIMESTAMP,
                    import_scraped_at TIMESTAMP,
                    error_count INTEGER DEFAULT 0,
                    last_error TEXT
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status ON hs_codes(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_export_status ON hs_codes(export_status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_import_status ON hs_codes(import_status)
            """)
            conn.commit()
    
    def load_from_text_file(self, file_path: Path):
        """Import HS codes from existing text file (one-time migration)"""
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return
        
        with open(file_path, "r", encoding="utf-8") as f:
            codes = [line.strip() for line in f if line.strip()]
        
        self.bulk_insert(codes)
        logger.info(f"Imported {len(codes)} HS codes from text file")
    
    def bulk_insert(self, hs_codes: list):
        """Insert multiple HS codes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                "INSERT OR IGNORE INTO hs_codes (hs_code, status) VALUES (?, ?)",
                [(code, "pending") for code in hs_codes]
            )
            conn.commit()
        logger.info(f"Inserted {len(hs_codes)} HS codes")
    
    def get_all(self) -> list:
        """Get all HS codes"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT hs_code FROM hs_codes")
            return [row[0] for row in cursor.fetchall()]
    
    def get_pending(self) -> list:
        """Get only pending HS codes (not yet scraped)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT hs_code FROM hs_codes WHERE status = 'pending'"
            )
            return [row[0] for row in cursor.fetchall()]
    
    def get_pending_export(self) -> list:
        """Get HS codes where export data is still pending"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT hs_code FROM hs_codes WHERE export_status = 'pending'"
            )
            return [row[0] for row in cursor.fetchall()]
    
    def get_pending_import(self) -> list:
        """Get HS codes where import data is still pending"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT hs_code FROM hs_codes WHERE import_status = 'pending'"
            )
            return [row[0] for row in cursor.fetchall()]
    
    def mark_completed(self, hs_code: str):
        """Mark both export and import as completed"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE hs_codes 
                SET status = 'completed',
                    export_status = 'completed',
                    import_status = 'completed',
                    last_scraped_at = CURRENT_TIMESTAMP
                WHERE hs_code = ?
                """,
                (hs_code,)
            )
            conn.commit()
    
    def mark_export_completed(self, hs_code: str):
        """Mark export as completed"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE hs_codes 
                SET export_status = 'completed',
                    export_scraped_at = CURRENT_TIMESTAMP
                WHERE hs_code = ?
                """,
                (hs_code,)
            )
            conn.commit()
    
    def mark_import_completed(self, hs_code: str):
        """Mark import as completed"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE hs_codes 
                SET import_status = 'completed',
                    import_scraped_at = CURRENT_TIMESTAMP
                WHERE hs_code = ?
                """,
                (hs_code,)
            )
            conn.commit()
    
    def mark_failed(self, hs_code: str, error: str, trade_mode: str = None):
        """Mark as failed with error message"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if trade_mode == "export":
                cursor.execute(
                    """
                    UPDATE hs_codes 
                    SET export_status = 'failed',
                        error_count = error_count + 1,
                        last_error = ?
                    WHERE hs_code = ?
                    """,
                    (error, hs_code)
                )
            elif trade_mode == "import":
                cursor.execute(
                    """
                    UPDATE hs_codes 
                    SET import_status = 'failed',
                        error_count = error_count + 1,
                        last_error = ?
                    WHERE hs_code = ?
                    """,
                    (error, hs_code)
                )
            else:
                cursor.execute(
                    """
                    UPDATE hs_codes 
                    SET status = 'failed',
                        error_count = error_count + 1,
                        last_error = ?
                    WHERE hs_code = ?
                    """,
                    (error, hs_code)
                )
            conn.commit()
    
    def get_stats(self) -> dict:
        """Get overall statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM hs_codes")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM hs_codes WHERE status = 'completed'")
            completed = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM hs_codes WHERE status = 'pending'")
            pending = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM hs_codes WHERE export_status = 'completed'")
            export_completed = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM hs_codes WHERE import_status = 'completed'")
            import_completed = cursor.fetchone()[0]
            
            return {
                "total": total,
                "completed": completed,
                "pending": pending,
                "export_completed": export_completed,
                "import_completed": import_completed,
                "completion_rate": f"{(completed/total*100):.1f}%" if total > 0 else "0%"
            }


# Convenience functions
def get_pending_hs_codes() -> list:
    """Get all pending HS codes"""
    db = HSCodeDatabase()
    return db.get_pending()


def mark_hs_completed(hs_code: str):
    """Mark HS code as completed"""
    db = HSCodeDatabase()
    db.mark_completed(hs_code)


if __name__ == "__main__":
    # Example usage
    db = HSCodeDatabase()
    
    # One-time import from text file
    text_file = Path("input/hs_codes.txt")
    if text_file.exists():
        db.load_from_text_file(text_file)
    
    # Show stats
    stats = db.get_stats()
    print("\nHS Code Database Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\nPending HS codes: {len(db.get_pending())}")
    print(f"Pending Export: {len(db.get_pending_export())}")
    print(f"Pending Import: {len(db.get_pending_import())}")
