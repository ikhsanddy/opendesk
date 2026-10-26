// TODO: drop after #3846/#3847 merge; import from shared directly.
import { __ } from "@opendesk/shared/translation";

export { __, translationPlugin } from "@opendesk/shared/translation";

declare module "@vue/runtime-core" {
  interface ComponentCustomProperties {
    __: typeof __;
  }
}
