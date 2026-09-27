/**
 * App.tsx — root component, owns all session state.
 *
 * View routing (no router library needed — just 3 views):
 *   "input"  → InputView
 *   "plan"   → SprintPlanView
 *   "tickets"→ TicketsView (one sprint at a time)
 */

import { useState } from "react";
import type { SprintPlan, ValidationReport, TicketList } from "./types";
import { generateSprintPlan, generateTickets } from "./api";
import { InputView } from "./components/InputView";
import { SprintPlanView } from "./components/SprintPlanView";
import { TicketsView } from "./components/TicketsView";

type View = "input" | "plan" | "tickets";

export default function App() {
  const [view, setView] = useState<View>("input");

  // Session state
  const [prd, setPrd] = useState("");
  const [plan, setPlan] = useState<SprintPlan | null>(null);
  const [planValidation, setPlanValidation] = useState<ValidationReport>({
    ok: true,
    issues: [],
  });

  // Tickets per sprint: sprint_id → TicketList
  const [ticketListMap, setTicketListMap] = useState<Record<string, TicketList>>({});
  const [ticketValidationMap, setTicketValidationMap] = useState<
    Record<string, ValidationReport>
  >({});

  // Active sprint being viewed
  const [activeSprintId, setActiveSprintId] = useState<string | null>(null);

  // Loading / error state
  const [planLoading, setPlanLoading] = useState(false);
  const [planError, setPlanError] = useState<string | null>(null);
  const [ticketLoadingId, setTicketLoadingId] = useState<string | null>(null);
  const [ticketErrors, setTicketErrors] = useState<Record<string, string>>({});
  const [regenerating, setRegenerating] = useState(false);
  const [regenerateError, setRegenerateError] = useState<string | null>(null);

  // ─── Handlers ────────────────────────────────────────────────────────────

  const handleGenerate = async (prdMarkdown: string) => {
    setPrd(prdMarkdown);
    setPlanLoading(true);
    setPlanError(null);
    try {
      const res = await generateSprintPlan(prdMarkdown);
      setPlan(res.plan);
      setPlanValidation(res.validation);
      setTicketListMap({});
      setTicketValidationMap({});
      setView("plan");
    } catch (err) {
      setPlanError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setPlanLoading(false);
    }
  };

  const handleGenerateTickets = async (sprintId: string) => {
    if (!plan) return;
    setTicketLoadingId(sprintId);
    setTicketErrors((prev) => {
      const next = { ...prev };
      delete next[sprintId];
      return next;
    });
    try {
      const res = await generateTickets(prd, plan, sprintId);
      setTicketListMap((prev) => ({
        ...prev,
        [sprintId]: res.tickets,
      }));
      setTicketValidationMap((prev) => ({
        ...prev,
        [sprintId]: res.validation,
      }));
    } catch (err) {
      setTicketErrors((prev) => ({
        ...prev,
        [sprintId]: err instanceof Error ? err.message : "Unknown error",
      }));
    } finally {
      setTicketLoadingId(null);
    }
  };

  const handleViewTickets = (sprintId: string) => {
    setActiveSprintId(sprintId);
    setRegenerateError(null);
    setView("tickets");
  };

  const handleRegenerate = async (sprintId: string) => {
    if (!plan) return;
    setRegenerating(true);
    setRegenerateError(null);
    try {
      const res = await generateTickets(prd, plan, sprintId);
      setTicketListMap((prev) => ({
        ...prev,
        [sprintId]: res.tickets,
      }));
      setTicketValidationMap((prev) => ({
        ...prev,
        [sprintId]: res.validation,
      }));
    } catch (err) {
      setRegenerateError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setRegenerating(false);
    }
  };

  const handleReset = () => {
    setPlan(null);
    setPlanError(null);
    setTicketListMap({});
    setTicketValidationMap({});
    setActiveSprintId(null);
    setView("input");
  };

  const handleBackToPlan = () => {
    setActiveSprintId(null);
    setView("plan");
  };

  // ─── Render ──────────────────────────────────────────────────────────────

  if (view === "plan" && plan) {
    return (
      <SprintPlanView
        plan={plan}
        setPlan={setPlan}
        validation={planValidation}
        ticketLists={Object.values(ticketListMap)}
        onGenerateTickets={handleGenerateTickets}
        ticketLoading={ticketLoadingId}
        ticketError={ticketErrors}
        onViewTickets={handleViewTickets}
        onReset={handleReset}
      />
    );
  }

  if (view === "tickets" && plan && activeSprintId) {
    const ticketList = ticketListMap[activeSprintId];
    const ticketValidation = ticketValidationMap[activeSprintId] ?? {
      ok: true,
      issues: [],
    };

    if (!ticketList) {
      // Shouldn't happen, but fall back to plan
      setView("plan");
      return null;
    }

    return (
      <TicketsView
        ticketList={ticketList}
        setTicketList={(tl) =>
          setTicketListMap((prev) => ({ ...prev, [activeSprintId]: tl }))
        }
        validation={ticketValidation}
        plan={plan}
        allTicketLists={Object.values(ticketListMap)}
        planValidation={planValidation}
        onRegenerate={handleRegenerate}
        regenerating={regenerating}
        regenerateError={regenerateError}
        onBack={handleBackToPlan}
      />
    );
  }

  // Default: input view
  return (
    <InputView
      onGenerate={handleGenerate}
      loading={planLoading}
      error={planError}
    />
  );
}
