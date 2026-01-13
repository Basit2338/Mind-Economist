import sqlite3
import os

# Connect to the database
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'blog.db')

if not os.path.exists(db_path):
    # Fallback to older location if instance folder structure wasn't used strictly before
    db_path = os.path.join(basedir, 'blog.db')

print(f"Connecting to database at: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Add views column to Post table
    print("Adding views column to post table...")
    try:
        cursor.execute("ALTER TABLE post ADD COLUMN views INTEGER DEFAULT 0")
        print("views column added.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("views column already exists.")
        else:
            raise e

    # Add total_seconds_read column to Post table
    print("Adding total_seconds_read column to post table...")
    try:
        cursor.execute("ALTER TABLE post ADD COLUMN total_seconds_read INTEGER DEFAULT 0")
        print("total_seconds_read column added.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("total_seconds_read column already exists.")
        else:
            raise e

    # Create active_page_viewer table
    print("Creating active_page_viewer table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS active_page_viewer (
        id INTEGER PRIMARY KEY,
        post_id INTEGER NOT NULL,
        viewer_id VARCHAR(100) NOT NULL,
        last_heartbeat DATETIME,
        FOREIGN KEY(post_id) REFERENCES post(id)
    )
    """)
    print("active_page_viewer table created.")

    conn.commit()
    print("Migration completed successfully.")

except Exception as e:
    print(f"An error occurred: {e}")
    conn.rollback()
finally:
    conn.close()
