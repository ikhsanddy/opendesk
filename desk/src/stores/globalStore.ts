import { defineStore } from "pinia";
import { getCurrentInstance } from "vue";

export const globalStore = defineStore("od-global", () => {
  const app = getCurrentInstance();
  const { $dialog, $socket } = app.appContext.config.globalProperties;

  return {
    $dialog,
    $socket,
  };
});
