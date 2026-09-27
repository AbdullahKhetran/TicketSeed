/**
 * SprintPlanView — View 2
 * Project summary, ordered sprint cards (with "Generate tickets"),
 * collapsible requirements, client questions side panel, validation.
 */

import { useState } from "react";
import type { SprintPlan, ValidationReport, TicketList, Requirement, Sprint } from "../types";
import { ValidationPanel } from "./ValidationPanel";
import { Spinner } from "./Spinner";
import { exportJSON, exportMarkdown } from "../export";

interface Props {
  plan: SprintPlan;
  setPlan: (plan: SprintPlan) => void;
  validation: ValidationReport;
  ticketLists: TicketList[];
  onGenerateTickets: (sprintId: string) => Promise<void>;
  ticketLoading: string | null; // sprint id currently loading, or null
  ticketError: Record<string, string>;
  onViewTickets: (sprintId: string) => void;
  onReset: () => void;
}

function RequirementsSection({
  requirements,
}: {
  requirements: Requirement[];
}) {
  const [open, setOpen] = useState(false);
  return (
    <section className="card">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-5 py-4 text-left"
      >
        <span className="font-medium text-sm">
          Requirements ({requirements.length})
        </span>
        <svg
          className={`h-4 w-4 text-muted transition-transform ${open ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          strokeWidth={2}
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && (
        <ul className="divide-y divide-border border-t border-border">
          {requirements.map((r) => (
            <li key={r.id} className="px-5 py-3 text-sm">
              <div className="flex items-start gap-3">
                <span className="font-mono text-xs text-muted shrink-0 mt-0.5">{r.id}</span>
                <div className="flex flex-col gap-1">
                  <p className="text-[#1f2328]">{r.text}</p>
                  <blockquote className="border-l-2 border-accent/40 pl-3 text-muted italic text-xs">
                    {r.source_quote}
                  </blockquote>
                  <span className={`badge-${r.kind} self-start`}>{r.kind}</span>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function SprintCard({
  sprint,
  requirements,
  onGenerateTickets,
  loading,
  error,
  hasTickets,
  onViewTickets,
  onEdit,
}: {
  sprint: Sprint;
  requirements: Requirement[];
  onGenerateTickets: (id: string) => void;
  loading: boolean;
  error: string | null;
  hasTickets: boolean;
  onViewTickets: (id: string) => void;
  onEdit: (updated: Sprint) => void;
}) {
  const [editName, setEditName] = useState(false);
  const [editGoal, setEditGoal] = useState(false);
  const [name, setName] = useState(sprint.name);
  const [goal, setGoal] = useState(sprint.goal);
  const reqMap = Object.fromEntries(requirements.map((r) => [r.id, r]));

  const save = () => {
    onEdit({ ...sprint, name, goal });
    setEditName(false);
    setEditGoal(false);
  };

  return (
    <div className="card overflow-hidden">
      {/* Header */}
      <div className="bg-surface border-b border-border px-5 py-3 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 min-w-0">
          <span className="font-mono text-xs text-muted shrink-0">{sprint.id}</span>
          {editName ? (
            <input
              className="input-field py-1 text-sm font-semibold"
              value={name}
              onChange={(e) => setName(e.target.value)}
              onBlur={save}
              onKeyDown={(e) => e.key === "Enter" && save()}
              autoFocus
            />
          ) : (
            <button
              onClick={() => setEditName(true)}
              className="font-semibold text-sm text-[#1f2328] hover:text-accent truncate text-left"
              title="Click to edit sprint name"
            >
              {sprint.name}
            </button>
          )}
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {sprint.depends_on.length > 0 && (
            <span className="text-xs text-muted">
              after {sprint.depends_on.join(", ")}
            </span>
          )}
          <span className="text-xs font-mono bg-gray-100 px-2 py-0.5 rounded text-muted">
            order {sprint.order}
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="px-5 py-4 flex flex-col gap-4">
        {/* Goal */}
        <div>
          <p className="text-xs font-medium text-muted uppercase tracking-wide mb-1">Goal</p>
          {editGoal ? (
            <textarea
              className="input-field text-sm resize-none"
              rows={2}
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              onBlur={save}
              autoFocus
            />
          ) : (
            <p
              className="text-sm text-[#1f2328] cursor-pointer hover:text-accent"
              onClick={() => setEditGoal(true)}
              title="Click to edit goal"
            >
              {sprint.goal}
            </p>
          )}
        </div>

        {/* Requirements covered */}
        {sprint.requirement_ids.length > 0 && (
          <div>
            <p className="text-xs font-medium text-muted uppercase tracking-wide mb-2">Requirements</p>
            <div className="flex flex-col gap-1.5">
              {sprint.requirement_ids.map((rid) => {
                const req = reqMap[rid];
                return req ? (
                  <div key={rid} className="flex items-start gap-2 text-sm">
                    <span className="font-mono text-xs text-muted shrink-0 mt-0.5">{rid}</span>
                    <span className="text-[#1f2328]">{req.text}</span>
                  </div>
                ) : (
                  <span key={rid} className="text-xs text-muted">{rid}</span>
                );
              })}
            </div>
          </div>
        )}

        {/* Deliverables */}
        {sprint.deliverables.length > 0 && (
          <div>
            <p className="text-xs font-medium text-muted uppercase tracking-wide mb-1">Deliverables</p>
            <ul className="list-disc list-inside text-sm text-[#1f2328] space-y-0.5">
              {sprint.deliverables.map((d, i) => (
                <li key={i}>{d}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Rationale */}
        <details className="text-sm">
          <summary className="cursor-pointer text-muted text-xs select-none">Rationale</summary>
          <p className="mt-1 text-[#1f2328] text-sm">{sprint.rationale}</p>
        </details>

        {/* Error */}
        {error && (
          <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded px-3 py-1.5">
            {error}
          </p>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-1">
          {loading ? (
            <Spinner label={`Generating tickets for ${sprint.id}…`} className="text-sm" />
          ) : hasTickets ? (
            <>
              <button
                className="btn-primary text-sm py-1.5"
                onClick={() => onViewTickets(sprint.id)}
              >
                View tickets →
              </button>
              <button
                className="btn-secondary text-sm py-1.5"
                onClick={() => onGenerateTickets(sprint.id)}
              >
                Regenerate
              </button>
            </>
          ) : (
            <button
              className="btn-primary text-sm py-1.5"
              onClick={() => onGenerateTickets(sprint.id)}
            >
              Generate tickets
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function ClientQuestionsPanel({
  questions,
  requirements,
}: {
  questions: SprintPlan["client_questions"];
  requirements: Requirement[];
}) {
  const [copied, setCopied] = useState(false);
  const reqMap = Object.fromEntries(requirements.map((r) => [r.id, r]));

  const handleCopyAll = () => {
    const text = questions
      .map(
        (q, i) =>
          `${i + 1}. ${q.question}\n   (Why it matters: ${q.why_it_matters})`
      )
      .join("\n\n");
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  if (questions.length === 0) return null;

  return (
    <div className="card">
      <div className="flex items-center justify-between px-5 py-3 border-b border-border">
        <h3 className="font-medium text-sm">Client Questions ({questions.length})</h3>
        <button className="btn-ghost text-xs" onClick={handleCopyAll}>
          {copied ? "Copied!" : "Copy all"}
        </button>
      </div>
      <ul className="divide-y divide-border">
        {questions.map((q) => (
          <li key={q.id} className="px-5 py-4">
            <div className="flex gap-3">
              <span className="font-mono text-xs text-muted shrink-0 mt-0.5">{q.id}</span>
              <div className="flex flex-col gap-1.5">
                <p className="text-sm font-medium text-[#1f2328]">{q.question}</p>
                <p className="text-xs text-muted">{q.why_it_matters}</p>
                {q.requirement_ids.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {q.requirement_ids.map((rid) => (
                      <span
                        key={rid}
                        className="text-xs bg-gray-100 px-1.5 py-0.5 rounded font-mono"
                        title={reqMap[rid]?.text}
                      >
                        {rid}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function SprintPlanView({
  plan,
  setPlan,
  validation,
  ticketLists,
  onGenerateTickets,
  ticketLoading,
  ticketError,
  onViewTickets,
  onReset,
}: Props) {
  const updateSprint = (updated: Sprint) => {
    setPlan({
      ...plan,
      sprints: plan.sprints.map((s) => (s.id === updated.id ? updated : s)),
    });
  };

  const sortedSprints = [...plan.sprints].sort((a, b) => a.order - b.order);

  return (
    <div className="min-h-screen bg-white">
      {/* Top bar */}
      <header className="sticky top-0 z-10 bg-white border-b border-border px-6 py-3 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button onClick={onReset} className="btn-ghost text-sm">
            ← New PRD
          </button>
          <span className="text-muted">|</span>
          <h1 className="font-semibold text-sm text-[#1f2328]">{plan.project.name}</h1>
        </div>
        <div className="flex gap-2">
          <button
            className="btn-secondary text-xs py-1.5"
            onClick={() => exportMarkdown(plan, ticketLists)}
          >
            Export Markdown
          </button>
          <button
            className="btn-secondary text-xs py-1.5"
            onClick={() => exportJSON(plan, ticketLists, validation)}
          >
            Export JSON
          </button>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main column */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          {/* Project summary */}
          <section className="card px-5 py-4">
            <h2 className="font-semibold text-base mb-1">{plan.project.name}</h2>
            <p className="text-sm text-[#1f2328] mb-3">{plan.project.summary}</p>
            {plan.project.assumptions.length > 0 && (
              <details className="text-sm">
                <summary className="cursor-pointer text-xs text-muted select-none">
                  {plan.project.assumptions.length} assumptions
                </summary>
                <ul className="mt-2 list-disc list-inside space-y-0.5 text-sm text-[#1f2328]">
                  {plan.project.assumptions.map((a, i) => (
                    <li key={i}>{a}</li>
                  ))}
                </ul>
              </details>
            )}
          </section>

          {/* Validation */}
          <ValidationPanel validation={validation} />

          {/* Requirements */}
          <RequirementsSection requirements={plan.requirements} />

          {/* Sprint cards */}
          <div className="flex flex-col gap-4">
            <h2 className="font-semibold text-sm text-muted uppercase tracking-wide">
              {sortedSprints.length} Sprint{sortedSprints.length !== 1 ? "s" : ""}
            </h2>
            {sortedSprints.map((sprint) => (
              <SprintCard
                key={sprint.id}
                sprint={sprint}
                requirements={plan.requirements}
                onGenerateTickets={onGenerateTickets}
                loading={ticketLoading === sprint.id}
                error={ticketError[sprint.id] ?? null}
                hasTickets={ticketLists.some((t) => t.sprint_id === sprint.id)}
                onViewTickets={onViewTickets}
                onEdit={updateSprint}
              />
            ))}
          </div>
        </div>

        {/* Sidebar */}
        <div className="flex flex-col gap-6">
          <ClientQuestionsPanel
            questions={plan.client_questions}
            requirements={plan.requirements}
          />
        </div>
      </div>
    </div>
  );
}
