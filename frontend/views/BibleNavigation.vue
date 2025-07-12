<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from "vue";
import { useBibleApi } from "~/composables/useBibleApi";

const api = useBibleApi();

const selectedBook = defineModel<string>("book");
const selectedChapter = defineModel<number | null>("chapter");
const selectedVerse = defineModel<number | null>("verse");

const chapters = ref<number[]>([]);
const verses = ref<number[]>([]);
const fullBook = ref<{ chapter: number; verses: { verse: number; text: string }[] }[]>([]);
const activeChapterIndex = ref(0);
const highlighted = ref<{ chapter: number; verse: number } | null>(null);

onMounted(async () => {
  if (selectedBook.value) {
    await loadBook(selectedBook.value);
  }
});

watch(selectedBook, async (book) => {
  if (book) await loadBook(book);
});

watch(selectedChapter, (chap) => {
  const index = fullBook.value.findIndex((c) => c.chapter === chap);
  if (index !== -1) activeChapterIndex.value = index;
});

watch([selectedChapter, selectedVerse], ([chap, verse]) => {
  if (chap !== null && verse !== null) {
    highlighted.value = { chapter: chap, verse };
    nextTick(() => {
      const el = document.getElementById(`verse-${chap}-${verse}`);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
    });
  }
});

async function loadBook(book: string) {
  chapters.value = await api.fetchChapters(book);
  fullBook.value = await api.fetchFullBook(book);
  if (selectedChapter.value !== null) {
    const i = fullBook.value.findIndex((c) => c.chapter === selectedChapter.value);
    activeChapterIndex.value = i !== -1 ? i : 0;
  } else {
    activeChapterIndex.value = 0;
    selectedChapter.value = fullBook.value[0]?.chapter || null;
  }
  verses.value = await api.fetchVerses(book, selectedChapter.value!);
}

function prevChapter() {
  if (activeChapterIndex.value > 0) {
    activeChapterIndex.value--;
    selectedChapter.value = fullBook.value[activeChapterIndex.value].chapter;
  }
}

function nextChapter() {
  if (activeChapterIndex.value < fullBook.value.length - 1) {
    activeChapterIndex.value++;
    selectedChapter.value = fullBook.value[activeChapterIndex.value].chapter;
  }
}
</script>

<template>
  <div v-if="fullBook.length" class="mt-6 space-y-4">
    <div class="flex items-center justify-between">
      <button @click="prevChapter" :disabled="activeChapterIndex === 0" class="px-3 py-1 bg-gray-200 rounded disabled:opacity-50">
        ← Previous
      </button>
      <h2 class="text-xl font-semibold">
        Chapter {{ fullBook[activeChapterIndex].chapter }}
      </h2>
      <button @click="nextChapter" :disabled="activeChapterIndex === fullBook.length - 1" class="px-3 py-1 bg-gray-200 rounded disabled:opacity-50">
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
          selectedVerse === v.verse ? 'bg-yellow-100 font-semibold' : ''
        ]"
      >
        <span class="text-gray-500 mr-2">{{ v.verse }}</span>
        <span>{{ v.text }}</span>
      </div>
    </div>
  </div>
</template>
