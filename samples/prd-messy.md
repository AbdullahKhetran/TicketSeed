# Product Requirements Document — ShelfMate

**Prepared by:** Marcus Holt, Founder  
**Date:** June 2026  
**Version:** 1.4 (latest)

> Demo sample: shortened for Groq free-tier ~8k token limits. See `docs/QUICKSTART.md`.

---

## What we want

ShelfMate is for readers: scan a barcode to add a book, track read/unread, share shelves with friends, get recommendations. Social (follow friends, see what they're reading) matters most — but the barcode scanner is also critical for launch.

People want progress by page (e.g. 47 of 312), not just finished/not. Auto-update while reading would be nice but we're unsure how. Ebooks may need % instead of pages — users should choose. Kindle sync: leave out for now; maybe mention "coming soon."

---

## Books and shelves

States: Want to Read, Currently Reading, Finished, Did Not Finish. Maybe "Lent to a friend" later — not confirmed.

Add books by: phone barcode scan, title/author search, or manual ISBN. Lookup should fill cover, title, author, description, page count via Google Books or Open Library (team decides which is free/better). Missing covers get a nice placeholder, not a grey box.

Progress: page number with a progress bar for Currently Reading; cannot exceed total pages. Optional page vs % mode for ebooks.

---

## Social, notifications, discovery

Follow users; activity feed (adds, status changes, reviews) reverse-chronological. Search users by username or email. Stretch: "interesting" feed of popular books among follows.

Reviews: 1–5 stars + text for finished books; public by default; private reviews TBD (per review vs account).

Notify (in-app for web; design for future push): new follower, friend adds book, friend finishes a book you're reading, review liked.

Discovery: Trending this week (adds in last 7 days), Popular in your network, "Because you read X" on the home screen. No ML team — external API or simple algorithm TBD; must feel smart for investors.

Search: books (title/author/ISBN), users, reviews in one box; most queries under 500ms.

---

## UX and tech

Clean/minimal, Goodreads-but-better. Tabs: feed, shelf, discovery; profile top corner. Mobile-first web app that also works on desktop. Dark mode follows system setting by default.

Pages under 2s; book lookup under 1s (users in bookshops). No ads; premium later. Data private by default; shelf public/private TBD vs separate shelf vs activity visibility. Full shelf + history export as JSON or CSV. Email/password accounts; Google login optional; no anonymous browsing.

---

## Not building yet

Native apps, Kindle sync, browser extension, premium tier, book clubs.

Launch in ~3 months: 2 backend, 1 frontend, designer Figma not ready, no QA. Core loop must work: add book → track progress → share with friend → see activity.

---

## Open questions

- Google Books vs Open Library?
- Review privacy: per review or account?
- Followers always see full shelf, or two visibility settings?
- Recommendations algorithm/API?
- "Lent to a friend" in launch scope?
