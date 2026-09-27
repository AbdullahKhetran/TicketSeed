/**
 * TicketsView — View 3
 * Shows all tickets for one sprint. Flagged tickets first.
 * Each ticket is expandable. Inline editing. Regenerate button.
 */

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type {
  Ticket,
  TicketList,
  ValidationReport,
  SprintPlan,
  TicketType,
  TicketSize,
  TicketPriority,
} from "../types";
import { ValidationPanel } from "./ValidationPanel";
import { Spinner } from "./Spinner";
import { exportMarkdown, exportJSON } from "../export";

interface Props {
  ticketList: TicketList;
  setTicketList: (tl: TicketList) => void;
  validation: ValidationReport;
  plan: SprintPlan;
  allTicketLists: TicketList[];
  planValidation: ValidationReport;
  onRegenerate: (sprintId: string) => Promise<void>;
  regenerating: boolean;
  regenerateError: string | null;
  onBack: () => void;
}

const SIZES: TicketSize[] = ["XS", "S", "M", "L", "XL"];
const PRIORITIES: TicketPriority[] = ["high", "medium", "low"];
const TYPES: TicketType[] = ["feature", "task", "chore", "spike"];

function TicketCard({
  ticket,
  requirements,
  onUpdate,
}: {
  ticket: Ticket;
  requirements: SprintPlan["requirements"];
  onUpdate: (updated: Ticket) => void;
}) {
  const [expanded, setExpanded] = useState(ticket.needs_clarification);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<Ticket>(ticket);

  const reqMap = Object.fromEntries(requirements.map((r) => [r.id, r]));

  const saveEdit = () => {
    onUpdate(draft);
    setEditing(false);
  };

  const cancelEdit = () => {
    setDraft(ticket);
    setEditing(false);
  };

  return (
    <div
      className={`card overflow-hidden ${
        ticket.needs_clarification
          ? "border-l-4 border-l-yellow-400"
          : ""
      }`}
    >
      {/* Header row */}
      <button
        className="w-full flex items-start gap-3 px-5 py-4 text-left hover:bg-surface transition-colors"
        onClick={() => !editing && setExpanded((o) => !o)}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono text-xs text-muted shrink-0">{ticket.id}</span>
            {ticket.needs_clarification && (
              <span className="badge bg-yellow-100 text-yellow-800 text-xs">⚠ clarification needed</span>
            )}
            <span className={`badge-${ticket.type}`}>{ticket.type}</span>
            <span className={`badge-${ticket.size}`}>{ticket.size}</span>
            <span className={`badge-${ticket.priority}`}>{ticket.priority}</span>
          </div>
          <p className="mt-1 text-sm font-medium text-[#1f2328]">{ticket.title}</p>
          <div className="flex flex-wrap gap-1 mt-1">
            {ticket.areas.map((a) => (
              <span key={a} className="text-xs bg-gray-100 px-1.5 py-0.5 rounded text-muted">
                {a}
              </span>
            ))}
          </div>
        </div>
        <svg
          className={`h-4 w-4 text-muted shrink-0 mt-1 transition-transform ${expanded ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded body */}
      {expanded && (
        <div className="border-t border-border px-5 py-4 flex flex-col gap-4">
          {ticket.needs_clarification && ticket.clarification_note && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-md px-4 py-2 text-sm text-yellow-800">
              <strong>Clarification needed:</strong> {ticket.clarification_note}
            </div>
          )}

          {editing ? (
            /* Edit form */
            <div className="flex flex-col gap-4">
              <div>
                <label className="block text-xs font-medium text-muted mb-1">Title</label>
                <input
                  className="input-field"
                  value={draft.title}
                  onChange={(e) =>
                    setDraft((d) => ({ ...d, title: e.target.value }))
                  }
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-muted mb-1">Type</label>
                  <select
                    className="input-field"
                    value={draft.type}
                    onChange={(e) =>
                      setDraft((d) => ({ ...d, type: e.target.value as TicketType }))
                    }
                  >
                    {TYPES.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted mb-1">Size</label>
                  <select
                    className="input-field"
                    value={draft.size}
                    onChange={(e) =>
                      setDraft((d) => ({ ...d, size: e.target.value as TicketSize }))
                    }
                  >
                    {SIZES.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted mb-1">Priority</label>
                  <select
                    className="input-field"
                    value={draft.priority}
                    onChange={(e) =>
                      setDraft((d) => ({
                        ...d,
                        priority: e.target.value as TicketPriority,
                      }))
                    }
                  >
                    {PRIORITIES.map((p) => (
                      <option key={p} value={p}>{p}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-muted mb-1">Description (Markdown)</label>
                <textarea
                  className="input-field font-mono text-xs resize-y min-h-[120px]"
                  value={draft.description}
                  onChange={(e) =>
                    setDraft((d) => ({ ...d, description: e.target.value }))
                  }
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-muted mb-1">
                  Acceptance Criteria (one per line)
                </label>
                <textarea
                  className="input-field text-sm resize-y min-h-[80px]"
                  value={draft.acceptance_criteria.join("\n")}
                  onChange={(e) =>
                    setDraft((d) => ({
                      ...d,
                      acceptance_criteria: e.target.value
                        .split("\n")
                        .filter(Boolean),
                    }))
                  }
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-muted mb-1">Technical Notes</label>
                <textarea
                  className="input-field text-sm resize-y"
                  rows={3}
                  value={draft.technical_notes}
                  onChange={(e) =>
                    setDraft((d) => ({ ...d, technical_notes: e.target.value }))
                  }
                />
              </div>

              <div className="flex gap-2">
                <button className="btn-primary text-sm py-1.5" onClick={saveEdit}>
                  Save
                </button>
                <button
                  className="btn-secondary text-sm py-1.5"
                  onClick={cancelEdit}
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            /* Read view */
            <div className="flex flex-col gap-4">
              <div>
                <p className="text-xs font-medium text-muted uppercase tracking-wide mb-1">Description</p>
                <div className="prose prose-sm max-w-none text-[#1f2328]">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {ticket.description}
                  </ReactMarkdown>
                </div>
              </div>

              {ticket.acceptance_criteria.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-muted uppercase tracking-wide mb-1">
                    Acceptance Criteria
                  </p>
                  <ul className="list-disc list-inside text-sm text-[#1f2328] space-y-0.5">
                    {ticket.acceptance_criteria.map((ac, i) => (
                      <li key={i}>{ac}</li>
                    ))}
                  </ul>
                </div>
              )}

              {ticket.technical_notes && (
                <div>
                  <p className="text-xs font-medium text-muted uppercase tracking-wide mb-1">
                    Technical Notes
                  </p>
                  <p className="text-sm text-[#1f2328]">{ticket.technical_notes}</p>
                </div>
              )}

              {ticket.depends_on.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-muted uppercase tracking-wide mb-1">
                    Depends On
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {ticket.depends_on.map((d) => (
                      <span key={d} className="font-mono text-xs bg-gray-100 px-2 py-0.5 rounded">
                        {d}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {ticket.requirement_ids.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-muted uppercase tracking-wide mb-1">
                    Linked Requirements
                  </p>
                  <div className="flex flex-col gap-1.5">
                    {ticket.requirement_ids.map((rid) => {
                      const req = reqMap[rid];
                      return req ? (
                        <div key={rid} className="flex items-start gap-2 text-sm">
                          <span className="font-mono text-xs text-muted shrink-0 mt-0.5">{rid}</span>
                          <div>
                            <p>{req.text}</p>
                            <blockquote className="border-l-2 border-accent/40 pl-2 text-muted italic text-xs mt-0.5">
                              {req.source_quote}
                            </blockquote>
                          </div>
                        </div>
                      ) : (
                        <span key={rid} className="text-xs font-mono text-muted">{rid}</span>
                      );
                    })}
                  </div>
                </div>
              )}

              <button
                className="btn-ghost self-start text-xs"
                onClick={() => setEditing(true)}
              >
                Edit ticket
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function TicketsView({
  ticketList,
  setTicketList,
  validation,
  plan,
  allTicketLists,
  planValidation,
  onRegenerate,
  regenerating,
  regenerateError,
  onBack,
}: Props) {
  const sprint = plan.sprints.find((s) => s.id === ticketList.sprint_id);

  // Flagged tickets first, then by id
  const sortedTickets = [...ticketList.tickets].sort((a, b) => {
    if (a.needs_clarification && !b.needs_clarification) return -1;
    if (!a.needs_clarification && b.needs_clarification) return 1;
    return a.id.localeCompare(b.id);
  });

  const updateTicket = (updated: Ticket) => {
    setTicketList({
      ...ticketList,
      tickets: ticketList.tickets.map((t) =>
        t.id === updated.id ? updated : t
      ),
    });
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Top bar */}
      <header className="sticky top-0 z-10 bg-white border-b border-border px-6 py-3 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button onClick={onBack} className="btn-ghost text-sm">
            ← Sprint plan
          </button>
          <span className="text-muted">|</span>
          <span className="font-semibold text-sm">
            {sprint ? `${sprint.id}: ${sprint.name}` : ticketList.sprint_id}
          </span>
          <span className="text-xs text-muted">
            {ticketList.tickets.length} tickets
          </span>
        </div>
        <div className="flex gap-2">
          <button
            className="btn-secondary text-xs py-1.5"
            onClick={() => exportMarkdown(plan, allTicketLists)}
          >
            Export Markdown
          </button>
          <button
            className="btn-secondary text-xs py-1.5"
            onClick={() => exportJSON(plan, allTicketLists, planValidation)}
          >
            Export JSON
          </button>
          {regenerating ? (
            <Spinner label="Regenerating…" />
          ) : (
            <button
              className="btn-secondary text-xs py-1.5"
              onClick={() => onRegenerate(ticketList.sprint_id)}
            >
              Regenerate tickets
            </button>
          )}
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-8 flex flex-col gap-6">
        {/* Sprint goal */}
        {sprint && (
          <div className="card px-5 py-4">
            <p className="text-xs font-medium text-muted uppercase tracking-wide mb-1">Sprint Goal</p>
            <p className="text-sm">{sprint.goal}</p>
          </div>
        )}

        {/* Regenerate error */}
        {regenerateError && (
          <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-4 py-2">
            {regenerateError}
          </div>
        )}

        {/* Validation */}
        <ValidationPanel validation={validation} />

        {/* Tickets */}
        <div className="flex flex-col gap-3">
          {sortedTickets.map((ticket) => (
            <TicketCard
              key={ticket.id}
              ticket={ticket}
              requirements={plan.requirements}
              onUpdate={updateTicket}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
