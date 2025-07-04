
import argparse
from db import search_verses

def main():
    parser = argparse.ArgumentParser(description="Search the Bible")
    parser.add_argument("--search", type=str, help="Keyword to search for")
    args = parser.parse_args()

    if args.search:
        results = search_verses(args.search)
        if not results:
            print("No results found.")
        for book, chapter, verse, text in results:
            print(f"{book} {chapter}:{verse} — {text}")
    else:
        print("Please provide a search keyword with --search")

if __name__ == "__main__":
    main()
