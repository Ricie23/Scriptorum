<script setup lang="ts">
import { ref, watch } from "vue";
import KeyWordSearch from "~/views/KeywordSearch.vue";
import BibleNavigation from "~/views/BibleNavigation.vue";
import { useBibleApi } from "~/composables/useBibleApi";

const api = useBibleApi();

const books = ref<string[]>([]);
const selectedBook = ref<string>("John");
const selectedChapter = ref<number | null>(1);
const selectedVerse = ref<number | null>(1);

books.value = await api.fetchBooks();
watch(selectedBook, async (book) => {
  if (book) {
    selectedChapter.value = null;
    selectedVerse.value = null;
  }
});
function handleJump({ book, chapter, verse }: {
  book: string;
  chapter: number;
  verse: number;
}) {
  selectedBook.value = book;
  selectedChapter.value = chapter;
  selectedVerse.value = verse;
}
</script>

<template>
  <div class="p-6 max-w-xl mx-auto">
    <h1 class="text-2xl font-bold mb-4">Scriptorium Navigator</h1>

    <KeyWordSearch
      @jump="handleJump"
    />

    <div class="space-y-4 mt-6">
      <div>
        <label>Book:</label>
        <select v-model="selectedBook">
          <option value="">– select –</option>
          <option v-for="b in books" :key="b" :value="b">{{ b }}</option>
        </select>
      </div>

      <BibleNavigation
        v-model:book="selectedBook"
        v-model:chapter="selectedChapter"
        v-model:verse="selectedVerse"
      />
    </div>
  </div>
</template>
