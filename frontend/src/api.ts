/**
 * API client — all calls go to relative /api paths.
 * Works locally via Vite proxy and on Vercel without any CORS config.
 */

import type {
  SprintsRequest,
  SprintsResponse,
  TicketsRequest,
  TicketsResponse,
} from "./types";

async function post<TReq, TRes>(path: string, body: TReq): Promise<TRes> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    let message = `HTTP ${res.status}`;
    try {
      const data = await res.json();
      message = data.detail || data.message || message;
    } catch {
      // ignore JSON parse failure
    }
    throw new Error(message);
  }

  return res.json() as Promise<TRes>;
}

export async function generateSprintPlan(
  prd_markdown: string
): Promise<SprintsResponse> {
  return post<SprintsRequest, SprintsResponse>("/api/plan/sprints", {
    prd_markdown,
  });
}

export async function generateTickets(
  prd_markdown: string,
  plan: SprintsResponse["plan"],
  sprint_id: string
): Promise<TicketsResponse> {
  return post<TicketsRequest, TicketsResponse>("/api/plan/tickets", {
    prd_markdown,
    plan,
    sprint_id,
  });
}
