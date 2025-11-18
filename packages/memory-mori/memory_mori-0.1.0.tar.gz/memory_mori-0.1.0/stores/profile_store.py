"""
Profile Store Abstraction
Provides a clean interface to SQLite for profile fact storage
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class ProfileStore:
    """
    Persistent key-value store for user profile information using SQLite.

    Stores facts with categories: role, preference, project, skill, context
    """

    VALID_CATEGORIES = ['role', 'preference', 'project', 'skill', 'context']

    def __init__(self, db_path: str = "./memory_mori_profile.db"):
        """
        Initialize the profile store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profile_facts (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                confidence REAL NOT NULL DEFAULT 1.0,
                access_count INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                CHECK(category IN ('role', 'preference', 'project', 'skill', 'context')),
                CHECK(confidence >= 0.0 AND confidence <= 1.0)
            )
        ''')

        # Create indices for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category ON profile_facts(category)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON profile_facts(timestamp DESC)
        ''')

        conn.commit()
        conn.close()

    def set(
        self,
        key: str,
        value: str,
        category: str,
        confidence: float = 1.0
    ) -> bool:
        """
        Add or update a profile fact.

        Args:
            key: Unique identifier for the fact
            value: The value to store
            category: Category (role, preference, project, skill, context)
            confidence: Confidence score 0.0-1.0

        Returns:
            True if successful
        """
        if category not in self.VALID_CATEGORIES:
            raise ValueError(f"Invalid category: {category}. Must be one of {self.VALID_CATEGORIES}")

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {confidence}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if key exists
        cursor.execute('SELECT confidence FROM profile_facts WHERE key = ?', (key,))
        existing = cursor.fetchone()

        timestamp = datetime.now().isoformat()

        if existing:
            old_confidence = existing[0]

            # Update strategy: Keep higher confidence or most recent if confidence is equal
            if confidence >= old_confidence:
                cursor.execute('''
                    UPDATE profile_facts
                    SET value = ?, category = ?, timestamp = ?, confidence = ?
                    WHERE key = ?
                ''', (value, category, timestamp, confidence, key))
        else:
            # Insert new fact
            cursor.execute('''
                INSERT INTO profile_facts (key, value, category, timestamp, confidence, access_count, created_at)
                VALUES (?, ?, ?, ?, ?, 1, ?)
            ''', (key, value, category, timestamp, confidence, timestamp))

        conn.commit()
        conn.close()
        return True

    def get(self, key: str) -> Optional[Dict]:
        """
        Retrieve a single fact by key.

        Args:
            key: The key to look up

        Returns:
            Dictionary with fact details or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT key, value, category, timestamp, confidence, access_count, created_at
            FROM profile_facts WHERE key = ?
        ''', (key,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'key': row[0],
                'value': row[1],
                'category': row[2],
                'timestamp': row[3],
                'confidence': row[4],
                'access_count': row[5],
                'created_at': row[6]
            }
        return None

    def get_all(self, min_confidence: float = 0.0, category: Optional[str] = None) -> List[Dict]:
        """
        Retrieve facts from the profile.

        Args:
            min_confidence: Only return facts with confidence >= this value
            category: Optional category filter

        Returns:
            List of fact dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if category:
            if category not in self.VALID_CATEGORIES:
                raise ValueError(f"Invalid category: {category}")

            cursor.execute('''
                SELECT key, value, category, timestamp, confidence, access_count, created_at
                FROM profile_facts
                WHERE category = ? AND confidence >= ?
                ORDER BY confidence DESC, timestamp DESC
            ''', (category, min_confidence))
        else:
            cursor.execute('''
                SELECT key, value, category, timestamp, confidence, access_count, created_at
                FROM profile_facts
                WHERE confidence >= ?
                ORDER BY category, confidence DESC, timestamp DESC
            ''', (min_confidence,))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                'key': row[0],
                'value': row[1],
                'category': row[2],
                'timestamp': row[3],
                'confidence': row[4],
                'access_count': row[5],
                'created_at': row[6]
            }
            for row in rows
        ]

    def delete(self, key: str) -> bool:
        """
        Delete a fact by key.

        Args:
            key: The key to delete

        Returns:
            True if deleted, False if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM profile_facts WHERE key = ?', (key,))
        deleted = cursor.rowcount > 0

        conn.commit()
        conn.close()

        return deleted
