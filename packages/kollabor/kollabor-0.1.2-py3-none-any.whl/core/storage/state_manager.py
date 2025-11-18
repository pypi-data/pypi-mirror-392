"""State management system for Kollabor CLI."""

import json
import logging
import sqlite3
import threading
from typing import Any

logger = logging.getLogger(__name__)


class StateManager:
    """SQLite-based state management system.
    
    Provides persistent storage for application and plugin state.
    """
    
    def __init__(self, db_path: str) -> None:
        """Initialize the state manager.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._lock = threading.Lock()
        self._init_database()
        logger.info(f"State manager initialized with database: {db_path}")
    
    def _init_database(self) -> None:
        """Initialize the database schema."""
        cursor = self.conn.cursor()
        
        # Main state table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        logger.debug("Database schema initialized")
    
    def set(self, key: str, value: Any) -> None:
        """Set a state value.
        
        Args:
            key: State key.
            value: Value to store (will be JSON serialized).
        """
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO state (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, json.dumps(value)))
            self.conn.commit()
            logger.debug(f"Set state: {key}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value.
        
        Args:
            key: State key.
            default: Default value if key not found.
            
        Returns:
            The stored value or default.
        """
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT value FROM state WHERE key = ?', (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return default
    
    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")