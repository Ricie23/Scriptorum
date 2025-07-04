<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { useBibleApi } from "~/composables/useBibleApi";

const api = useBibleApi();

// reactive state
const books = ref<string[]>([]);
const chapters = ref<number[]>([]);
const verses = ref<number[]>([]);
const text = ref("");
const searchTerm = ref<string>("");
const fullBook = ref<
  { chapter: number; verses: { verse: number; text: string }[] }[]
>([]);
const searchResults = ref<
  { book: string; chapter: number; verse: number; text: string }[]
>([]);

// selected values
const selectedBook = ref<string>("");
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
  chapters.value = await api.fetchChapters(book);
  selectedChapter.value = null;
  verses.value = [];
  text.value = "";
});

// when chapter changes, load verses
watch(selectedChapter, async (chap) => {
  if (chap === null || !selectedBook.value) return;
  console.log(selectedBook.value, chap);
  verses.value = await api.fetchVerses(selectedBook.value, chap);
  console.log("Verses loaded:", verses.value);
  selectedVerse.value = null;
  text.value = "";
});

// when verse changes, load text
watch(selectedVerse, async (v) => {
  if (v === null || !selectedBook.value || selectedChapter.value === null)
    return;
  text.value = await api.fetchText(
    selectedBook.value,
    selectedChapter.value,
    v,
  );
});
async function runSearch() {
  clearFullBook();
  clearNavigation()
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
  fullBook.value = await api.fetchFullBook(selectedBook.value);
}
function goToVerse(chap: number, ver: number) {
  selectedChapter.value = chap;
  selectedVerse.value = ver;
  // update your single-verse text view
  api.fetchText(selectedBook.value, chap, ver).then((t) => (text.value = t));

  // scroll the element into view
  nextTick(() => {
    const el = document.getElementById(`verse-${chap}-${ver}`);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
  });
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
        <button
          class="px-4 py-1 bg-green-600 text-white rounded"
          @click="viewBook"
          :disabled="!selectedBook"
        >
          View Full {{ selectedBook || "Book" }}
        </button>
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
    <div v-if="fullBook.length" class="mt-6 space-y-8">
      <div
        v-for="chapObj in fullBook"
        :key="chapObj.chapter"
        class="border p-4 rounded"
      >
        <h2 class="text-xl font-semibold mb-2">
          Chapter {{ chapObj.chapter }}
        </h2>
        <div class="space-y-2">
          <div
            v-for="vObj in chapObj.verses"
            :key="vObj.verse"
            class="flex items-start space-x-2"
          >
            <button
              :id="`verse-${chapObj.chapter}-${vObj.verse}`"
              class="font-bold text-blue-600"
              @click="goToVerse(chapObj.chapter, vObj.verse)"
            >
              {{ vObj.verse }}
            </button>
            <p class="flex-1">{{ vObj.text }}</p>
          </div>
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
          class="border-b pb-1"
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
