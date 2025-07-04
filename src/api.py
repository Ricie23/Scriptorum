# backend.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db import get_books, get_chapters, get_verses, get_verse_text, search_verses, get_full_book

# 1) Create FastAPI instance named "app" at module level
app = FastAPI()

# 2) Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 3) Define endpoints
@app.get("/books")
def list_books():
    return get_books()

@app.get("/chapters")
def list_chapters(book: str):
    return get_chapters(book)

@app.get("/verses")
def list_verses(book: str, chapter: int):
    return get_verses(book, chapter)

@app.get("/verse")
def read_verse(book: str, chapter: int, verse: int):
    return {"text": get_verse_text(book, chapter, verse)}

@app.get("/books/{book_name}/all")
def read_full_book(book_name: str):
    chapters = get_full_book(book_name)
    if not chapters:
        raise HTTPException(404, f"No such book: {book_name}")
    return chapters

@app.get("/search")
def search(keyword: str):
    # ⚠️ This must be your full-text search helper,
    #     not get_books() or get_chapters()!
    items = search_verses(keyword)

    results = []
    for row in items:
        # row should be either
        #   (book, chapter, verse, text)
        # or (id, book, chapter, verse, text)
        if len(row) == 4:
            book, chapter, verse, text = row
        elif len(row) == 5:
            _, book, chapter, verse, text = row
        else:
            # debug unexpected shapes
            print("⚠ unexpected row shape:", row)
            continue

        results.append({
            "book":    book,
            "chapter": int(chapter),
            "verse":   int(verse),
            "text":    text,
        })

    return results
