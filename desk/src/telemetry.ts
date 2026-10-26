import { useTelemetry } from "@framework/ui";
const APP = "opendesk";

interface CaptureOptions {
  data: {
    [key: string]: string | number | boolean | object;
  };
}

export function capture(event: string, options: CaptureOptions = { data: {} }) {
  const { capture: _capture } = useTelemetry();
  _capture(event, options.data);
}
