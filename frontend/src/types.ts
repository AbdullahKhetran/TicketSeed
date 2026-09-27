/**
 * TypeScript types mirroring backend/app/models.py exactly.
 * If models.py changes, update this file immediately and notify the team.
 */

// ---------------------------------------------------------------------------
// Shared enums
// ---------------------------------------------------------------------------

export type RequirementKind = "functional" | "non_functional";
export type TicketType = "feature" | "task" | "chore" | "spike";
export type TicketArea = "frontend" | "backend" | "database" | "devops" | "design" | "qa";
export type TicketSize = "XS" | "S" | "M" | "L" | "XL";
export type TicketPriority = "high" | "medium" | "low";
export type IssueSeverity = "warning" | "error";

// ---------------------------------------------------------------------------
// Capability 1 — Sprint plan
// ---------------------------------------------------------------------------

export interface Project {
  name: string;
  summary: string;
  assumptions: string[];
}

export interface Requirement {
  id: string; // R1, R2, …
  text: string;
  source_quote: string;
  kind: RequirementKind;
}

export interface Sprint {
  id: string; // S1, S2, …
  order: number;
  name: string;
  goal: string;
  requirement_ids: string[];
  deliverables: string[];
  depends_on: string[];
  rationale: string;
}

export interface ClientQuestion {
  id: string; // Q1, Q2, …
  question: string;
  why_it_matters: string;
  requirement_ids: string[];
}

export interface SprintPlan {
  project: Project;
  requirements: Requirement[];
  sprints: Sprint[];
  client_questions: ClientQuestion[];
}

// ---------------------------------------------------------------------------
// Capability 2 — Ticket list
// ---------------------------------------------------------------------------

export interface Ticket {
  id: string; // S2-T1, …
  title: string;
  type: TicketType;
  description: string;
  acceptance_criteria: string[];
  technical_notes: string;
  areas: TicketArea[];
  size: TicketSize;
  priority: TicketPriority;
  depends_on: string[];
  requirement_ids: string[];
  needs_clarification: boolean;
  clarification_note: string | null;
}

export interface TicketList {
  sprint_id: string;
  tickets: Ticket[];
}

// ---------------------------------------------------------------------------
// Shared validation report
// ---------------------------------------------------------------------------

export interface ValidationIssue {
  severity: IssueSeverity;
  target: string;
  message: string;
}

export interface ValidationReport {
  ok: boolean;
  issues: ValidationIssue[];
}

// ---------------------------------------------------------------------------
// API request / response envelopes
// ---------------------------------------------------------------------------

export interface SprintsRequest {
  prd_markdown: string;
}

export interface SprintsResponse {
  plan: SprintPlan;
  validation: ValidationReport;
}

export interface TicketsRequest {
  prd_markdown: string;
  plan: SprintPlan;
  sprint_id: string;
}

export interface TicketsResponse {
  tickets: TicketList;
  validation: ValidationReport;
}
