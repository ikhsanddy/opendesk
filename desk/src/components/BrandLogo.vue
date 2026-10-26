<template>
  <img
    v-if="config.brandLogo"
    :src="config.brandLogo"
    alt="Brand Logo"
    class="h-8 w-8 shrink-0 object-cover"
  />
  <ODLogo v-else class="h-8 w-8 shrink-0 rounded-4" />
</template>

<script setup lang="ts">
import ODLogo from "@/assets/logos/ODLogo.vue";

import { useConfigStore } from "@/stores/config";
const config = useConfigStore();
</script>

<style scoped></style>
