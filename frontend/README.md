# MCI Platform — Frontend

A premium enterprise SaaS frontend for the Marine Competency Index (MCI)
platform, built with Next.js, React 19, TypeScript, and Tailwind CSS v4.
Visual identity generated entirely from the official lighthouse logo.

---

## What's real vs. what's scaffolded

This frontend was built against the **actual `mci-platform` FastAPI backend**
(the companion repo from this same project), which currently implements MCI
scoring, Job Readiness, and Skill Gap Analysis only. To be honest about
what you're getting:

| Page | Status |
|---|---|
| Login | ✅ UI complete, demo-mode (see "Backend Gaps" below) |
| Dashboard | ✅ **Fully wired to the real backend** — live KPIs, charts, recent candidates |
| Candidates | ✅ **Fully wired** — real table, create/list via the actual API |
| Candidate Profile | ✅ **Fully wired** — real MCI score display |
| MCI Score | ✅ **Fully wired** — real factor entry, scoring, readiness, skill gap |
| Companies, Assessments, Question Bank, Assessment Sessions, Certificates, Reports, Analytics, Notifications | ⚠️ Professional "Backend Pending" empty states — **not fake data**, genuine UI shells with the exact API contracts they'll need once built |
| Settings | ✅ Theme switching fully functional; account/security sections pending backend |
| Profile | ✅ UI complete; live data pending `GET /api/auth/me` |

Every "Backend Pending" page explicitly lists the API endpoints it needs —
use these as the spec when building those backend modules next.

Verified before delivery: `npm run build` completes with **0 TypeScript
errors**, `npm run lint` is **0 errors / 0 warnings that matter** (one
informational React Compiler note about TanStack Table is expected and
harmless), and the wired pages were tested against a real running instance
of the backend with real data round-tripping end-to-end.

---

## Backend Gaps (read before wiring auth)

The provided spec assumed JWT authentication and a much larger API surface
(Candidates/Companies/Assessments/Question Bank/Certificates/Reports) than
the current backend implements. Specifically **not yet on the backend**:

- `POST /api/auth/login`, `GET /api/auth/me`, JWT issuance/validation
- Companies, Assessments, Question Bank, Sessions, Certificates, Reports, Analytics, Notifications endpoints

The frontend is already wired so that adding these requires **zero
frontend architecture changes** — `src/lib/api/client.ts` already attaches
a JWT from `localStorage` to every request if one is present, and the
Login page's `onSubmit` has the exact code commented in, ready to
uncomment once `/api/auth/login` exists.

---

## Design system

Colors were extracted programmatically (pixel sampling) from the provided
logo:

| Token | Hex | Source |
|---|---|---|
| `brand-900` (dark background) | `#071B3D` | Logo's deep navy background |
| `brand-300` (primary accent) | `#6AABE9` | Lighthouse beam / "PLATFORM" text |
| Full 11-step scale | `brand-50` → `brand-950` | Interpolated between the two |

Light and dark themes are both first-class (see `src/app/globals.css`),
toggled via `next-themes`, and every page was designed to look intentional
in both.

---

## Run locally

```bash
npm install
cp .env.local.example .env.local   # point NEXT_PUBLIC_API_URL at your backend
npm run dev
```

Open http://localhost:3000 — you'll be redirected to `/dashboard`.

```bash
npm run build   # production build
npm run lint
npm run start   # serve the production build
```

---

## Connecting to the backend

Set `NEXT_PUBLIC_API_URL` (in `.env.local` for local dev, or as an
environment variable on your hosting platform) to the backend's public
URL — e.g. your Render service URL:

```
NEXT_PUBLIC_API_URL=https://mci-platform-backend.onrender.com
```

No other configuration is needed — `src/lib/api/client.ts` is the single
place the base URL is read from.

---

## Deploying

This is a standard Next.js app — deploy it to **Vercel** (zero-config,
recommended), **Render** (Web Service, build command `npm run build`,
start command `npm run start`), or any Node host. Push to GitHub and
connect the repo; set `NEXT_PUBLIC_API_URL` in the platform's environment
variables dashboard.

---

## Project structure

```
src/
├── app/
│   ├── layout.tsx                 root layout (theme, query, toaster providers)
│   ├── page.tsx                   redirects to /dashboard
│   ├── login/page.tsx             auth page
│   ├── not-found.tsx              404 page
│   └── (dashboard)/               route group sharing the sidebar+topbar shell
│       ├── layout.tsx
│       ├── loading.tsx            skeleton loading state
│       ├── error.tsx              error boundary
│       ├── dashboard/page.tsx     ✅ real KPIs + charts
│       ├── candidates/            ✅ real table, [id] detail page, add-candidate dialog
│       ├── mci-score/             ✅ real factor entry, scoring, readiness, skill-gap tabs
│       └── {companies,assessments,question-bank,sessions,certificates,
│           reports,analytics,notifications,settings,profile}/page.tsx
├── components/
│   ├── ui/                        hand-built shadcn/ui-pattern primitives (Radix + CVA)
│   ├── layout/                    Sidebar, Topbar, DashboardShell, nav-config, sidebar-context
│   ├── shared/                    PageHeader, DataTable, BackendPendingState
│   └── providers/                 ThemeProvider, QueryProvider
├── lib/api/                       client.ts (axios) + candidates.ts, mci.ts, positions.ts
├── hooks/                         React Query hooks per domain
└── types/mci.ts                   TypeScript types matching the backend's Pydantic schemas
```

Why hand-built UI primitives instead of the `shadcn` CLI? The CLI needs to
fetch component source from `ui.shadcn.com` at generation time, which
wasn't reachable from the sandboxed build environment this was created
in. The components follow shadcn's exact conventions (Radix primitives +
`class-variance-authority` + `tailwind-merge`), so running the real CLI
later (`npx shadcn add <component>`) will slot in cleanly if you ever want
to pull additional components.

## Recommended next steps

1. Build the missing backend endpoints listed in each "Backend Pending"
   page (start with `/api/auth/*` since Settings/Profile/every protected
   route benefits from it immediately).
2. Replace the Login page's demo-mode block with the real `apiClient.post("/api/auth/login", ...)` call (already stubbed, see the code comment).
3. Add a route guard (middleware or a client-side check on `mci_token`) once auth is live — intentionally omitted for now since there's nothing to guard against yet.
