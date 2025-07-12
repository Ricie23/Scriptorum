<script setup lang="ts">
import { ref } from "vue";
import { useBibleApi } from "~/composables/useBibleApi";

const emit = defineEmits(["jump"]);
const searchTerm = ref("");
const api = useBibleApi();
const results = ref<
  { book: string; chapter: number; verse: number; text: string }[]
>([]);
async function runSearch() {
  results.value = [];
  if (!searchTerm.value.trim()) return;
  try {
    results.value = await api.keywordSearch(searchTerm.value);
  } catch (err) {
    console.error("Search failed:", err);
  }
}
</script>

<template>
  <div class="space-y-4">
    <div>
      <label for="search"> Keyword Search:</label>
      <div class="flex space-x-2">
        <input
          id="search"
          v-model="searchTerm"
          placeholder="e.g. light"
          class="border px-2 py-1 flex-1"
          @keyup.enter="runSearch"
        />
        <button
          class="px-4 py-1 bg-blue-600 text-white rounded"
          @click="runSearch"
        >
          Search
        </button>
      </div>
    </div>

    <div v-if="results.length" class="mt-4">
      <h2 class="text-xl font-semibold mb-2">Results</h2>
      <ul class="list-disc pl-5 space-y-2">
        <li
          v-for="r in results"
          :key="`${r.book}-${r.chapter}-${r.verse}`"
          class="border-b pb-1 cursor-pointer hover:bg-gray-100"
          @click="emit('jump', r)"
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
