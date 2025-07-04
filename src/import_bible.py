import json
import sqlite3

# Load NKJV JSON
with open("data/bibles/NKJV_bible.json", "r", encoding="utf-8") as f:
    bible = json.load(f)

# Connect to database
conn = sqlite3.connect("data/bible.db")
cur = conn.cursor()

# Clean out the verses table if needed
conn.execute("DELETE FROM verses")
# Insert verses
for book, chapter in bible.items():
    for chapter_num, verses_list in chapter.items():
        for verse_num, text in verses_list.items():
            # Prepare the insert statement
            sql = """
            INSERT INTO verses (book, chapter, verse, text)
            VALUES (?, ?, ?, ?)
            """
            # Execute the insert statement
            cur.execute(sql, (book, chapter_num, verse_num, text))
conn.commit()
conn.close()

print("Import complete.")
