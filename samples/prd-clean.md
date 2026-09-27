# Product Requirements Document — Invoicio

**Prepared by:** Priya Nair, Head of Product  
**Date:** May 2026  
**Version:** 2.0 — approved for development

> Demo sample: shortened for Groq free-tier ~8k token limits. See `docs/QUICKSTART.md`.

---

## 1. Overview

Invoicio is a web app for freelancers and small agencies (1–10 members) to create, send, and track invoices. It replaces spreadsheet/PDF workflows and reduces late payments via automated reminders.

**Business goal:** 500 active monthly users within 6 months; 60-day retention above 50%.

---

## 2. User roles

- **Member:** create/send invoices, manage clients, view own financial data.
- **Admin:** all Member permissions plus invite members, team dashboard, workspace settings.

The first user creates the workspace and becomes Admin. Admins invite Members by email.

---

## 3. Core features

### Clients
Each client stores: company name (required), contact name/email (required), billing address (required), VAT (optional), currency (default USD), payment terms in days (default 30). Clients are workspace-scoped.

### Invoices
Invoices include: auto number `INV-{YYYY}-{sequence}`, issue date (default today), due date (issue + payment terms, editable), line items (description, qty, unit price, tax %), optional flat or % discount, notes. Totals calculated server-side.

### Lifecycle
`Draft → Sent → Viewed → Paid` (or `Overdue` / `Void`). Draft is editable; Sent emails PDF + payment link and becomes read-only; Viewed when client opens link; Overdue via daily job when past due and unpaid; Paid set manually (Stripe is Phase 2); Void requires a reason and drops from totals.

### PDF & reminders
On send, backend generates a branded PDF (logo, accent colour) and stores it (not regenerated each view). Reminders: 3 days before due, on due date, 7 days after — if still unpaid; disableable per invoice.

### Dashboard & settings
Admins: invoiced/paid/outstanding (month + all time), aging buckets, top 5 clients. Members see own invoices only. Admins configure name, logo (≤2 MB PNG/JPG), accent colour, default currency/terms, invoice prefix.

### Auth
Email/password with verification and password reset. Sessions expire after 7 days inactivity. Google OAuth out of scope.

---

## 4. Non-functional

- Pages load ≤2s on broadband; usable at ≥375px width.
- HTTPS in transit; passwords bcrypt-hashed.
- PDF endpoint ≤5s for ≤50 line items; support ~100 concurrent users at launch.

---

## 5. Out of scope

Stripe payments, recurring invoices, expenses, multi-currency per invoice, native apps, QuickBooks/Xero, time tracking.

---

## 6. Acceptance (high-level)

1. Register → workspace → client → send invoice → download PDF in under 5 minutes.
2. Sent invoices become Overdue within 24h of due date passing.
3. Client gets email + valid PDF within 60s of Send.
4. Admin invite → Member accepts and logs in.
5. Dashboard totals match underlying invoices.
6. Admins can export invoices/clients as CSV.
