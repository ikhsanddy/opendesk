<template>
  <div class="flex gap-5 w-full">
    <FormControl
      type="combobox"
      label="Default ticket status"
      :options="openStatuses"
      class="flex-1"
      v-model="slaData.default_ticket_status"
    />
    <FormControl
      type="combobox"
      label="Ticket reopen status"
      :options="openStatuses"
      class="flex-1"
      v-model="slaData.reopen_ticket_status"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ComputedRef } from "vue";
import { slaData } from "@/stores/sla";
import { useTicketStatusStore } from "@/stores/ticketStatus";
import { ODTicketStatus } from "@/types/doctypes";

const { statuses } = useTicketStatusStore();

const openStatuses: ComputedRef<ODTicketStatus[]> = computed(() => {
  return (
    statuses?.data
      ?.filter((s: ODTicketStatus) => s.category === "Open")
      ?.map((s: ODTicketStatus) => {
        return {
          label: s.label_agent,
          value: s.label_agent,
        };
      }) || []
  );
});
</script>
