import sqlite3

conn = sqlite3.connect('instance/blog.db')
cursor = conn.cursor()

try:
    print("Adding image_url to submission table...")
    cursor.execute('ALTER TABLE submission ADD COLUMN image_url TEXT')
    conn.commit()
    print("Success: image_url column added.")
except Exception as e:
    print(f"Migration note: {e}")
finally:
    conn.close()
