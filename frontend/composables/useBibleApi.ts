export function useBibleApi() {
  const { public: cfg } = useRuntimeConfig();
  const base = cfg.apiBase;

  return {
    async fetchBooks() {
      return await $fetch<string[]>(`${base}/books`);
    },
    async fetchChapters(book: string) {
      return await $fetch<number[]>(`${base}/chapters`, { params: { book } });
    },
    async fetchVerses(book: string, chapter: number) {
      return await $fetch<number[]>(`${base}/verses`, {
        params: { book, chapter },
      });
    },
    async fetchText(book: string, chapter: number, verse: number) {
      const res = await $fetch<{ text: string }>(`${base}/verse`, {
        params: { book, chapter, verse },
      });
      return res.text;
    },
    async keywordSearch(keyword: string) {
      const raw = await $fetch(`${base}/search`, { params: { keyword } });
      // if backend is correct, raw is already an array:
      return raw.map((r: any) => ({
        book: r.book,
        chapter: r.chapter,
        verse: r.verse,
        text: r.text,
      }));
    },
    async fetchFullBook(book: string) {
      return await $fetch<{ chapter:number; verses:{verse:number; text:string}[] }[]>(
        `${base}/books/${encodeURIComponent(book)}/all`
      )
    }
  };
}
