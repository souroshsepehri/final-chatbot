"""
FAQ service backed by SQLite for persistent, self-editable FAQs.
"""

import os
import sqlite3
import random
from typing import Optional, Dict, List
from datetime import datetime


class FAQService:
    """Service to handle FAQ storage and lookups using SQLite."""

    def __init__(self, db_path: str = "data/faqs.db"):
        """
        Initialize the FAQ service and ensure the database is ready.

        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        
        # Debug: Show actual paths being used
        abs_db_path = os.path.abspath(self.db_path)
        print(f"🔍 FAQ Service: Using database at {abs_db_path}")
        print(f"🔍 FAQ Service: Current working directory: {os.getcwd()}")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS faqs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL UNIQUE,
                    answer TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'general',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()
        # Ensure migration: add category column if missing
        try:
            with self._connect() as conn:
                cols = conn.execute("PRAGMA table_info(faqs)").fetchall()
                col_names = {c[1] for c in cols}
                if "category" not in col_names:
                    conn.execute("ALTER TABLE faqs ADD COLUMN category TEXT NOT NULL DEFAULT 'general'")
                    conn.commit()
        except Exception as e:
            print(f"Warning: Failed to migrate FAQs table (category column): {e}")
        # Seed from JSON on first run if DB is empty
        self._seed_from_json_if_empty()

    def _seed_from_json_if_empty(self) -> None:
        json_path = os.path.join(os.path.dirname(self.db_path), "custom_faq.json")
        try:
            # Only seed if database is empty
            with self._connect() as conn:
                count = conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
                if count > 0:
                    print(f"Database already has {count} FAQs, skipping JSON seeding")
                    return
            
            if not os.path.exists(json_path):
                print("No custom_faq.json found, skipping seeding")
                return
                
            import json
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            faqs = data.get("faqs", [])
            now = datetime.utcnow().isoformat()
            
            with self._connect() as conn:
                # Insert all FAQs from JSON (no DELETE since we know it's empty)
                for faq in faqs:
                    q = str(faq.get("question", "")).strip()
                    a = str(faq.get("answer", "")).strip()
                    c = str(faq.get("category", "general")).strip()
                    if not q or not a:
                        continue
                    try:
                        conn.execute(
                            "INSERT INTO faqs (question, answer, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                            (q, a, c, now, now),
                        )
                    except Exception:
                        # ignore seed errors per row
                        pass
                conn.commit()
                print(f"Seeded {len(faqs)} FAQs from JSON (database was empty)")
        except Exception as e:
            print(f"Warning: Failed to seed FAQs from JSON: {e}")
    
    def reload_from_json(self) -> int:
        """Manually reload all FAQs from JSON file. Returns number of FAQs loaded."""
        json_path = os.path.join(os.path.dirname(self.db_path), "custom_faq.json")
        try:
            if not os.path.exists(json_path):
                print("No custom_faq.json found for reload")
                return 0
                
            import json
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            faqs = data.get("faqs", [])
            now = datetime.utcnow().isoformat()
            
            with self._connect() as conn:
                # Clear existing data first
                conn.execute("DELETE FROM faqs")
                
                # Insert all FAQs from JSON
                for faq in faqs:
                    q = str(faq.get("question", "")).strip()
                    a = str(faq.get("answer", "")).strip()
                    c = str(faq.get("category", "general")).strip()
                    if not q or not a:
                        continue
                    try:
                        conn.execute(
                            "INSERT INTO faqs (question, answer, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                            (q, a, c, now, now),
                        )
                    except Exception:
                        # ignore seed errors per row
                        pass
                conn.commit()
                print(f"Reloaded {len(faqs)} FAQs from JSON")
                return len(faqs)
        except Exception as e:
            print(f"Error: Failed to reload FAQs from JSON: {e}")
            return 0

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, str]:
        return {
            "id": row["id"],
            "question": row["question"],
            "answer": row["answer"],
            "category": row["category"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def get_all_faqs(self, category: Optional[str] = None) -> List[Dict[str, str]]:
        """Return all FAQs, optionally filtered by category, sorted by latest update."""
        with self._connect() as conn:
            if category:
                rows = conn.execute(
                    "SELECT id, question, answer, category, created_at, updated_at FROM faqs WHERE lower(category) = lower(?) ORDER BY updated_at DESC",
                    (category,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, question, answer, category, created_at, updated_at FROM faqs ORDER BY updated_at DESC"
                ).fetchall()
            return [self._row_to_dict(row) for row in rows]

    def add_faq(self, question: str, answer: str, category: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Insert a new FAQ. Returns the created row, or None on failure."""
        now = datetime.utcnow().isoformat()
        cat = (category or "general").strip() or "general"
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    "INSERT INTO faqs (question, answer, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (question.strip(), answer.strip(), cat, now, now),
                )
                faq_id = cur.lastrowid
                row = conn.execute(
                    "SELECT id, question, answer, category, created_at, updated_at FROM faqs WHERE id = ?",
                    (faq_id,),
                ).fetchone()
                return self._row_to_dict(row) if row else None
        except sqlite3.IntegrityError:
            # If question already exists, update the answer instead
            return self.update_faq_by_question(question, answer, category=cat)
        except Exception as e:
            print(f"Error: Failed to add FAQ: {e}")
            return None

    def update_faq(self, faq_id: int, question: str, answer: str, category: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Update an existing FAQ by id. Returns the updated row."""
        now = datetime.utcnow().isoformat()
        cat = (category or "general").strip() or "general"
        with self._connect() as conn:
            conn.execute(
                "UPDATE faqs SET question = ?, answer = ?, category = ?, updated_at = ? WHERE id = ?",
                (question.strip(), answer.strip(), cat, now, faq_id),
            )
            row = conn.execute(
                "SELECT id, question, answer, category, created_at, updated_at FROM faqs WHERE id = ?",
                (faq_id,),
            ).fetchone()
            return self._row_to_dict(row) if row else None

    def update_faq_by_question(self, question: str, answer: str, category: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Upsert behavior: update by question if exists, otherwise insert."""
        now = datetime.utcnow().isoformat()
        cat = (category or "general").strip() or "general"
        with self._connect() as conn:
            # Try to update first
            conn.execute(
                "UPDATE faqs SET answer = ?, category = ?, updated_at = ? WHERE lower(question) = lower(?)",
                (answer.strip(), cat, now, question.strip()),
            )
            row = conn.execute(
                "SELECT id, question, answer, category, created_at, updated_at FROM faqs WHERE lower(question) = lower(?)",
                (question.strip(),),
            ).fetchone()
            if row:
                return self._row_to_dict(row)
            # Insert if not found
            cur = conn.execute(
                "INSERT INTO faqs (question, answer, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (question.strip(), answer.strip(), cat, now, now),
            )
            faq_id = cur.lastrowid
            row = conn.execute(
                "SELECT id, question, answer, category, created_at, updated_at FROM faqs WHERE id = ?",
                (faq_id,),
            ).fetchone()
            return self._row_to_dict(row) if row else None

    def delete_faq(self, faq_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM faqs WHERE id = ?", (faq_id,))
            return cur.rowcount > 0

    def search_faq(self, question: str) -> Optional[str]:
        """Search for FAQ answer with multiple matching strategies."""
        question = question.strip().lower()
        
        # First try exact match
        with self._connect() as conn:
            row = conn.execute(
                "SELECT answer FROM faqs WHERE lower(question) = lower(?)",
                (question,),
            ).fetchone()
            if row:
                return row[0]
        
        # Then try partial match (more flexible)
        return self.search_faq_partial(question)
    
    def is_greeting(self, message: str) -> bool:
        """Check if the message is a greeting."""
        greetings = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
            'سلام', 'درود', 'خوش آمدید', 'سلام علیکم', 'صبخ بخیر', 'عصر بخیر',
            'start', 'begin', 'شروع', 'آغاز', 'چت', 'chat'
        ]
        
        message_lower = message.lower().strip()
        return any(greeting in message_lower for greeting in greetings)
    
    def get_greeting_response(self) -> str:
        """Get a random greeting response."""
        greetings = [
            "سلام! 👋 خوش آمدید! چطور می‌تونم کمکتون کنم؟",
            "درود! 😊 من بات هوشمند زیمر هستم. چطور می‌تونم کمکتون کنم؟",
            "سلام علیکم! 🌟 خوشحالم که با شما صحبت می‌کنم. چطور می‌تونم کمکتون کنم؟",
            "Hi there! 👋 Welcome! How can I help you today?",
            "Hello! 😊 I'm your AI assistant. How can I be of service?"
        ]
        
        return random.choice(greetings)

    def search_faq_partial(self, question: str) -> Optional[str]:
        """Enhanced partial matching with multiple strategies."""
        q = question.strip().lower()
        
        with self._connect() as conn:
            # Strategy 1: Check if user question contains FAQ question
            row = conn.execute(
                """
                SELECT answer, question FROM faqs
                WHERE lower(?) LIKE '%' || lower(question) || '%'
                LIMIT 1
                """,
                (q,),
            ).fetchone()
            if row:
                return row[0]
            
            # Strategy 2: Check if FAQ question contains user question
            row = conn.execute(
                """
                SELECT answer, question FROM faqs
                WHERE lower(question) LIKE '%' || lower(?) || '%'
                LIMIT 1
                """,
                (q,),
            ).fetchone()
            if row:
                return row[0]
            
            # Strategy 3: Check for word overlap (more flexible)
            words = q.split()
            if len(words) > 1:
                for word in words:
                    if len(word) > 2:  # Only check words longer than 2 characters
                        row = conn.execute(
                            """
                            SELECT answer, question FROM faqs
                            WHERE lower(question) LIKE '%' || lower(?) || '%'
                            LIMIT 1
                            """,
                            (word,),
                        ).fetchone()
                        if row:
                            return row[0]
        
        return None

    def list_categories(self) -> List[str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT DISTINCT category FROM faqs ORDER BY lower(category)").fetchall()
            return [r[0] for r in rows]
