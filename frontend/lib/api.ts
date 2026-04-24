import type { CheckResult, StreamEvent } from "./types";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function streamCheck(
  input: string,
  onEvent: (ev: StreamEvent) => void,
  signal?: AbortSignal
): Promise<CheckResult | null> {
  const resp = await fetch(`${BACKEND_URL}/api/check/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ input }),
    signal,
  });

  if (!resp.ok || !resp.body) {
    throw new Error(`Backend ${resp.status}`);
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  let finalResult: CheckResult | null = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });

    let idx;
    while ((idx = buf.indexOf("\n\n")) !== -1) {
      const chunk = buf.slice(0, idx);
      buf = buf.slice(idx + 2);
      const ev = parseSSE(chunk);
      if (ev) {
        onEvent(ev);
        if (ev.name === "result") {
          finalResult = ev.payload as unknown as CheckResult;
        }
      }
    }
  }
  return finalResult;
}

function parseSSE(raw: string): StreamEvent | null {
  let name = "message";
  const dataLines: string[] = [];
  for (const line of raw.split("\n")) {
    if (line.startsWith("event:")) name = line.slice(6).trim();
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
  }
  if (dataLines.length === 0) return null;
  try {
    return { name, payload: JSON.parse(dataLines.join("\n")) };
  } catch {
    return null;
  }
}
