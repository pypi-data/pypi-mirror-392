#!/usr/bin/env python3
"""
Apply schema migrations to state.db
"""

import sqlite3
import sys
from pathlib import Path


def apply_migration():
    """Apply schema migration to add INDEX.json fields"""

    # Paths
    project_root = Path(__file__).parent.parent
    db_path = project_root / "yirifi_dq" / "db" / "state.db"
    migration_path = project_root / "yirifi_dq" / "db" / "migrations" / "001_add_index_json_fields.sql"

    print("🔧 Applying schema migration...")
    print(f"   Database: {db_path}")
    print(f"   Migration: {migration_path}")

    # Backup database first
    backup_path = db_path.with_suffix(".db.backup")
    if db_path.exists():
        import shutil

        shutil.copy2(db_path, backup_path)
        print(f"✓ Backup created: {backup_path}")

    # Read migration SQL
    with open(migration_path) as f:
        migration_sql = f.read()

    # Apply migration
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute each statement separately (SQLite requires this for ALTER TABLE)
        statements = migration_sql.split(";")
        executed_count = 0

        for statement in statements:
            statement = statement.strip()
            # Skip empty lines and comments
            if not statement or statement.startswith("--"):
                continue

            try:
                cursor.execute(statement)
                executed_count += 1
                # Show progress for ALTER TABLE statements
                if "ALTER TABLE" in statement.upper():
                    column_name = statement.split("ADD COLUMN")[1].split()[0] if "ADD COLUMN" in statement else "?"
                    print(f"   ✓ Added column: {column_name}")
            except sqlite3.OperationalError as e:
                # Ignore "duplicate column name" errors (migration already applied)
                if "duplicate column name" in str(e).lower():
                    print("   ⚠ Column already exists (skipping)")
                else:
                    raise

        conn.commit()
        print(f"✓ Migration applied successfully ({executed_count} statements)")

        # Verify new columns exist
        cursor.execute("PRAGMA table_info(operations)")
        columns = [row[1] for row in cursor.fetchall()]

        required_columns = [
            "summary",
            "tags",
            "learnings",
            "execution_details",
            "related_collections",
            "next_actions",
        ]
        missing_columns = [col for col in required_columns if col not in columns]

        if missing_columns:
            print(f"❌ Migration incomplete! Missing columns: {missing_columns}")
            conn.close()
            return False

        print(f"✓ Verified all {len(required_columns)} new columns exist:")
        for col in required_columns:
            print(f"   - {col}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print(f"   You can restore from backup: {backup_path}")
        return False


if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)
