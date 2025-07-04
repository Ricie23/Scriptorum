import sqlite3

def connect():
    return sqlite3.connect("data/bible.db")

def search_verses(keyword: str) -> list[tuple]:
    conn = connect()
    curr = conn.cursor()
    # select the four columns
    curr.execute(
        """
        SELECT book, chapter, verse, text
          FROM verses
         WHERE text LIKE ?
      ORDER BY book, chapter, verse
        """,
        (f"%{keyword}%",)
    )
    return curr.fetchall()


def get_books():
    conn = connect()
    curr = conn.cursor()
    curr.execute("""
        SELECT DISTINCT book FROM verses ORDER BY book
        """)
    results = curr.fetchall()
    conn.close()
    return [row[0] for row in results]

def get_chapters(book_name):
    conn = connect()
    curr = conn.cursor()
    curr.execute("""
    SELECT DISTINCT chapter FROM verses WHERE book = ? ORDER BY chapter
    """, (book_name,))
    results = curr.fetchall()
    conn.close()
    return [row[0] for row in results]

def get_verses(book_name, chapter_num):
    conn = connect()
    curr = conn.cursor()
    curr.execute("""
    SELECT DISTINCT verse FROM verses WHERE book = ? AND chapter = ? ORDER BY verse
    """, (book_name, chapter_num))
    results = curr.fetchall()
    conn.close()
    return [row[0] for row in results]

def get_verse_text(book_name, chapter_num, verse_num):
    conn = connect()
    curr = conn.cursor()
    curr.execute("""
    SELECT DISTINCT text FROM verses WHERE book = ? AND chapter = ? AND verse = ? ORDER BY verse
    """, (book_name, chapter_num, verse_num))
    results = curr.fetchall()
    conn.close()
    return [row[0] for row in results][0]

def get_full_book(book_name:str) -> list[dict]:
    conn = connect()
    curr = conn.cursor()
    curr.execute("""
    SELECT chapter, verse, text FROM verses WHERE book = ? ORDER BY chapter, verse
    """, (book_name,))
    rows = curr.fetchall()
    conn.close()
    result = []
    current = None
    for chapter, verse, text in rows:
        if current is None or current['chapter'] != chapter:
            current = {"chapter": chapter, "verses": []}
            result.append(current)
        current['verses'].append({"verse": verse, "text": text})
    return result
