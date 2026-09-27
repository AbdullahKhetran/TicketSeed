/**
 * Export helpers: Markdown and JSON downloads.
 */

import type { SprintPlan, TicketList, ValidationReport } from "./types";

function download(filename: string, content: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function exportJSON(
  plan: SprintPlan,
  ticketLists: TicketList[],
  planValidation: ValidationReport
) {
  const data = { plan, tickets: ticketLists, validation: planValidation };
  download(
    "ticketseed-export.json",
    JSON.stringify(data, null, 2),
    "application/json"
  );
}

export function exportMarkdown(
  plan: SprintPlan,
  ticketLists: TicketList[]
) {
  const lines: string[] = [];

  // Project summary
  lines.push(`# ${plan.project.name}`);
  lines.push("");
  lines.push(plan.project.summary);
  lines.push("");

  if (plan.project.assumptions.length > 0) {
    lines.push("## Assumptions");
    plan.project.assumptions.forEach((a) => lines.push(`- ${a}`));
    lines.push("");
  }

  // Requirements
  lines.push("## Requirements");
  plan.requirements.forEach((r) => {
    lines.push(`### ${r.id} — ${r.text}`);
    lines.push(`**Kind:** ${r.kind}`);
    lines.push(`> ${r.source_quote}`);
    lines.push("");
  });

  // Sprints
  lines.push("## Sprint Plan");
  plan.sprints.forEach((s) => {
    lines.push(`### ${s.id}: ${s.name}`);
    lines.push(`**Goal:** ${s.goal}`);
    lines.push(`**Requirements:** ${s.requirement_ids.join(", ")}`);
    if (s.depends_on.length > 0)
      lines.push(`**Depends on:** ${s.depends_on.join(", ")}`);
    if (s.deliverables.length > 0) {
      lines.push("**Deliverables:**");
      s.deliverables.forEach((d) => lines.push(`- ${d}`));
    }
    lines.push("");
    lines.push(`*Rationale: ${s.rationale}*`);
    lines.push("");

    // Tickets for this sprint
    const tl = ticketLists.find((t) => t.sprint_id === s.id);
    if (tl && tl.tickets.length > 0) {
      lines.push(`#### Tickets for ${s.id}`);
      tl.tickets.forEach((t) => {
        lines.push(`##### ${t.id}: ${t.title}`);
        lines.push(`**Type:** ${t.type} | **Size:** ${t.size} | **Priority:** ${t.priority}`);
        if (t.needs_clarification && t.clarification_note) {
          lines.push(`> ⚠️ Needs clarification: ${t.clarification_note}`);
        }
        lines.push("");
        lines.push(t.description);
        lines.push("");
        if (t.acceptance_criteria.length > 0) {
          lines.push("**Acceptance criteria:**");
          t.acceptance_criteria.forEach((ac) => lines.push(`- ${ac}`));
          lines.push("");
        }
        if (t.technical_notes) {
          lines.push(`**Technical notes:** ${t.technical_notes}`);
          lines.push("");
        }
      });
    }
  });

  // Client questions
  if (plan.client_questions.length > 0) {
    lines.push("## Client Questions");
    plan.client_questions.forEach((q) => {
      lines.push(`### ${q.id}: ${q.question}`);
      lines.push(`*Why it matters: ${q.why_it_matters}*`);
      lines.push(`Related requirements: ${q.requirement_ids.join(", ")}`);
      lines.push("");
    });
  }

  download(
    "ticketseed-export.md",
    lines.join("\n"),
    "text/markdown"
  );
}
