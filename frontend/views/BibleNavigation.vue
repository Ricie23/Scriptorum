<script setup lang="ts">
import { ref, nextTick, onMounted, watch } from "vue";
import { useBibleApi } from "~/composables/useBibleApi";

const api = useBibleApi();

// reactive state
const books = ref<string[]>([]);
const chapters = ref<number[]>([]);
const verses = ref<number[]>([]);
const text = ref("");
const searchTerm = ref<string>("");
const selectedBook = ref<string>("");
const fullBook = ref<
  { chapter: number; verses: { verse: number; text: string }[] }[]
>([]);
const highlighted = ref<{ chapter: number; verse: number } | null>(null);
const searchResults = ref<
  { book: string; chapter: number; verse: number; text: string }[]
>([]);
const activeChapterIndex = ref<number>(0);
// selected values
const selectedChapter = ref<number | null>(null);
const selectedVerse = ref<number | null>(null);

onMounted(async () => {
  selectedBook.value = "John";
  books.value = await api.fetchBooks();

  await api.fetchChapters("John").then((chaps) => {
    chapters.value = chaps;
  });
  selectedChapter.value = 1;
  await api.fetchVerses("John", 1).then((vers) => {
    verses.value = vers;
  });
  selectedVerse.value = 1;
});

// load books on mount
books.value = await api.fetchBooks();
// when book changes, load chapters and clear downstream
watch(selectedBook, async (book) => {
  clearFullBook();
  clearSearch();
  if (!book) return;
  await viewBook();
  chapters.value = await api.fetchChapters(book);
  selectedChapter.value = null;
  verses.value = [];
  text.value = "";
});

// when chapter changes, load verses
watch(selectedChapter, (chap) => {
  if (chap === null || !fullBook.value.length) return;
  const index = fullBook.value.findIndex((c) => c.chapter === chap);
  if (index !== -1) activeChapterIndex.value = index;
});

// when verse changes, load text
watch([selectedChapter, selectedVerse], ([chap, verse]) => {
  if (chap !== null && verse !== null) {
    highlighted.value = { chapter: chap, verse: verse };
    nextTick(() => {
      const el = document.getElementById(`verse-${chap}-${verse}`);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }
});
async function runSearch() {
  clearFullBook();
  clearNavigation();
  if (!searchTerm.value.trim()) {
    searchResults.value = [];
    return;
  }
  try {
    searchResults.value = await api.keywordSearch(searchTerm.value);
  } catch (err) {
    console.error("Search failed:", err);
    searchResults.value = [];
  }
}
async function viewBook() {
  clearSearch();
  clearNavigation();
  if (!selectedBook.value) return;
  highlighted.value = null;
  fullBook.value = await api.fetchFullBook(selectedBook.value);
  if (selectedChapter.value !== null) {
    const index = fullBook.value.findIndex(
      (c) => c.chapter === selectedChapter.value,
    );
    activeChapterIndex.value = index !== -1 ? index : 0;
  } else {
    activeChapterIndex.value = 0;
  }
}
function goToVerse(chap: number, ver: number) {
  selectedChapter.value = chap;
  selectedVerse.value = ver;
}
function clearSearch() {
  searchTerm.value = "";
  searchResults.value = [];
}
function clearFullBook() {
  fullBook.value = [];
}
function clearNavigation() {
  selectedChapter.value = null;
  selectedVerse.value = null;
  text.value = "";
  chapters.value = [];
  verses.value = [];
}
function nextChapter() {
  if (activeChapterIndex.value < fullBook.value.length - 1) {
    activeChapterIndex.value++;
    selectedChapter.value = fullBook.value[activeChapterIndex.value].chapter;
  }
}

function prevChapter() {
  if (activeChapterIndex.value > 0) {
    activeChapterIndex.value--;
    selectedChapter.value = fullBook.value[activeChapterIndex.value].chapter;
  }
}
async function goToSearchResult(book: string, chapter: number, verse: number) {
  if (selectedBook.value !== book) {
    selectedBook.value = book;
    books.value = await api.fetchBooks(); // optional if books already loaded
  }

  selectedChapter.value = chapter;
  selectedVerse.value = verse;

  // Re-load full book (in case it's a new one)
  fullBook.value = await api.fetchFullBook(book);

  const chapterIndex = fullBook.value.findIndex((c) => c.chapter === chapter);
  if (chapterIndex !== -1) {
    activeChapterIndex.value = chapterIndex;
  }

  // Delay scroll until DOM is updated
  highlighted.value = { chapter, verse };
  await nextTick();

  const el = document.getElementById(`verse-${chapter}-${verse}`);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });

  clearSearch(); // optional: hide results after jumping
}
</script>

<template>
  <div class="p-6 max-w-xl mx-auto">
    <h1 class="text-2xl font-bold mb-4">Scriptorium Navigator</h1>
    <div class="space-y-4">
      <div>
        <label for="search">🔍 Keyword Search:</label>
        <div class="flex space-x-2">
          <input
            id="search"
            v-model="searchTerm"
            @keyup.enter="runSearch"
            placeholder="e.g. light"
            class="border px-2 py-1 flex-1"
          />
          <button
            class="px-4 py-1 bg-blue-600 text-white rounded"
            @click="runSearch"
          >
            Search
          </button>
        </div>
      </div>
      <div>
        <label>Book:</label>
        <select v-model="selectedBook">
          <option value="">– select –</option>
          <option v-for="b in books" :key="b" :value="b">{{ b }}</option>
        </select>
      </div>

      <div v-if="chapters.length">
        <label>Chapter:</label>
        <select v-model="selectedChapter">
          <option value="">– select –</option>
          <option v-for="c in chapters" :key="c" :value="c">{{ c }}</option>
        </select>
      </div>

      <div v-if="verses.length">
        <label>Verse:</label>
        <select v-model="selectedVerse">
          <option value="">– select –</option>
          <option v-for="v in verses" :key="v" :value="v">{{ v }}</option>
        </select>
      </div>
    </div>
    <div v-if="fullBook.length" class="mt-6 space-y-4">
      <div class="flex items-center justify-between">
        <button
          @click="prevChapter"
          :disabled="activeChapterIndex === 0"
          class="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
        >
          ← Previous
        </button>
        <h2 class="text-xl font-semibold">
          Chapter {{ fullBook[activeChapterIndex].chapter }}
        </h2>
        <button
          @click="nextChapter"
          :disabled="activeChapterIndex === fullBook.length - 1"
          class="px-3 py-1 bg-gray-200 rounded disabled:opacity-50"
        >
          Next →
        </button>
      </div>

      <div class="space-y-2">
        <div
          v-for="v in fullBook[activeChapterIndex].verses"
          :key="v.verse"
          :id="`verse-${fullBook[activeChapterIndex].chapter}-${v.verse}`"
          :class="[
            'p-1',
            selectedVerse === v.verse ? 'bg-yellow-100 font-semibold' : '',
          ]"
        >
          <span class="text-gray-500 mr-2">{{ v.verse }}</span>
          <span>{{ v.text }}</span>
        </div>
      </div>
    </div>
    <div v-if="text" class="mt-6 p-4 border rounded bg-gray-50">
      <p class="whitespace-pre-wrap">{{ text }}</p>
    </div>
    <div v-if="searchResults.length" class="mt-4">
      <h2 class="text-xl font-semibold mb-2">Results</h2>
      <ul class="list-disc pl-5 space-y-2">
        <li
          v-for="r in searchResults"
          :key="`${r.book}-${r.chapter}-${r.verse}`"
          class="border-b pb-1 cursor-pointer hover:bg-gray-100"
          @click="goToSearchResult(r.book, r.chapter, r.verse)"
        >
          <strong>{{ r.book }} {{ r.chapter }}:{{ r.verse }}</strong>
          — {{ r.text }}
        </li>
      </ul>
    </div>

    <div v-else-if="searchTerm" class="mt-4 italic text-gray-500">
      No matches for “{{ searchTerm }}”.
    </div>
  </div>
</template>
