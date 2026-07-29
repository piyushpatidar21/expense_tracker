"""
One-time helper: drops and recreates all tables using the current models.

Run this whenever models.py changes and you get column-mismatch errors like
`column users.created_at does not exist`. create_all() only creates tables
that don't exist yet -- it never alters existing ones -- so after a schema
change on an existing database you need to rebuild the tables.

WARNING: this deletes all existing rows in `users` and `expenses`.
Only run this against a database you're OK wiping (e.g. during development).

Usage:
    python reset_db.py
"""

from database import base, engine
import models  # noqa: F401  (registers User + Expenses with Base.metadata)

if __name__ == "__main__":
    confirm = input(
        "This will DROP and recreate the 'users' and 'expenses' tables. "
        "All existing data will be lost. Type 'yes' to continue: "
    )
    if confirm.strip().lower() != "yes":
        print("Aborted.")
    else:
        base.metadata.drop_all(bind=engine)
        base.metadata.create_all(bind=engine)
        print("Done. Tables recreated with the current schema.")
