# H1C — React Advertiser Views Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the React + Vite frontend that consumes the H1B FastAPI service and ships the single-advertiser detail view (and optionally the overview page) using the design language proven in the existing Pepsi/Talon Netlify advertiser-trends sites.

**Architecture:** Vite + React + TypeScript single-page app. React Router for routing, TanStack Query for server state with the H1B API as the source. shadcn/ui primitives + Tailwind for components, themed to match the dark-blue / cyan-accent design language. Plotly.js for charts. The app runs on `localhost:5173`, the FastAPI service on `localhost:8000`. Streamlit on `8504` continues running unchanged for tabs not yet ported.

**Tech Stack:** Vite 5, React 18, TypeScript 5, Tailwind 3, shadcn/ui, React Router 6, TanStack Query 5, Plotly.js 2, TanStack Table 8, Zod, MSW (test only), Vitest, Testing Library, Playwright.

**Spec:** `Claude/Plans/2026-04-29-h1-duckdb-fastapi-react-foundation.md`

**Depends on:** H1B complete (FastAPI service running on `localhost:8000` with advertiser endpoints).

---

## File Structure

| Path | Action | Responsibility |
|---|---|---|
| `frontend/package.json` | Create | Node deps |
| `frontend/vite.config.ts` | Create | Vite config + dev proxy |
| `frontend/tsconfig.json` | Create | TS config |
| `frontend/tailwind.config.ts` | Create | Tailwind theme with design tokens |
| `frontend/postcss.config.js` | Create | PostCSS + Tailwind |
| `frontend/index.html` | Create | App entry HTML |
| `frontend/src/main.tsx` | Create | React + Router + Query providers |
| `frontend/src/App.tsx` | Create | Router shell |
| `frontend/src/styles/globals.css` | Create | Tailwind imports + CSS variables for design tokens |
| `frontend/src/lib/api-client.ts` | Create | typed `fetch` wrapper |
| `frontend/src/lib/query-client.ts` | Create | TanStack Query config |
| `frontend/src/lib/format.ts` | Create | number / date formatters |
| `frontend/src/components/layout/AppShell.tsx` | Create | Outer layout |
| `frontend/src/components/layout/Sidebar.tsx` | Create | Nav sidebar |
| `frontend/src/components/layout/Header.tsx` | Create | Top nav with logo + MI toggle |
| `frontend/src/components/ui/Card.tsx` | Create | Card primitive |
| `frontend/src/components/ui/MetricBlock.tsx` | Create | Single metric display |
| `frontend/src/components/ui/DataLimitationsPanel.tsx` | Create | Caveats panel |
| `frontend/src/components/charts/PlotlyChart.tsx` | Create | Plotly wrapper |
| `frontend/src/components/charts/weekendBands.ts` | Create | Helper to produce weekend shading shapes |
| `frontend/src/components/MobileIndexToggle.tsx` | Create | MI toggle in header |
| `frontend/src/state/mi-toggle-store.ts` | Create | localStorage-backed MI state |
| `frontend/src/routes/index.tsx` | Create | `/` advertiser overview |
| `frontend/src/routes/advertisers/$slug.tsx` | Create | `/advertisers/:slug` detail |
| `frontend/src/features/advertiser-view/AdvertiserHeader.tsx` | Create | Brand metrics header |
| `frontend/src/features/advertiser-view/DailyTimeseriesChart.tsx` | Create | Daily chart with MI overlay |
| `frontend/src/features/advertiser-view/WeeklyTimeseriesChart.tsx` | Create | Weekly chart with brand transitions |
| `frontend/src/features/advertiser-view/CampaignList.tsx` | Create | TanStack Table |
| `frontend/src/features/advertiser-view/hooks/useAdvertiser.ts` | Create | Query hooks |
| `frontend/.env.development` | Create | `VITE_API_BASE_URL=http://localhost:8000` |
| `frontend/.gitignore` | Create | Standard Node / Vite |
| `.gitignore` | Modify | Add `frontend/node_modules`, `frontend/dist` |
| `.env.example` (root) | Modify | Note `FRONTEND_PORT=5173` |

---

## Pre-Flight

### Task 0: Vite scaffold

**Files:**
- Create: `frontend/` directory tree

- [ ] **Step 1: Verify on H1B branch with FastAPI working**

```bash
git status            # on feature/duckdb-migration
git log --oneline -5  # H1B commits visible
startapi &; sleep 2; curl -s localhost:8000/api/advertisers | head -c 200; kill %1
```

Expected: branch correct, API returns valid JSON.

- [ ] **Step 2: Scaffold Vite app**

```bash
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

Expected: `frontend/` directory created with starter Vite + React + TS app. `npm run dev` should start a dev server on port 5173.

- [ ] **Step 3: Add core dependencies**

```bash
cd frontend
npm install react-router-dom @tanstack/react-query @tanstack/react-table plotly.js-dist-min react-plotly.js zod
npm install -D tailwindcss postcss autoprefixer @types/plotly.js @types/react-plotly.js
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom msw @playwright/test
```

- [ ] **Step 4: Initialise Tailwind + shadcn**

```bash
npx tailwindcss init -p
npx shadcn@latest init
```

When shadcn prompts, accept TypeScript / Tailwind defaults. Use `src/components/ui` for shadcn components.

- [ ] **Step 5: Update root .gitignore**

Append to root `.gitignore`:

```
# Frontend
frontend/node_modules/
frontend/dist/
frontend/.env.local
frontend/coverage/
```

- [ ] **Step 6: Commit scaffold**

```bash
cd /Users/ianwyatt/PycharmProjects/Route-Playout-Econometrics_POC
git add frontend/ .gitignore
git commit -m "chore: scaffold Vite + React + TS frontend"
```

---

## Tasks

### Task 1: Tailwind theme + design tokens

**Files:**
- Modify: `frontend/tailwind.config.ts`
- Create: `frontend/src/styles/globals.css`
- Modify: `frontend/src/main.tsx`

Codify the design system from the spec as Tailwind theme + CSS variables.

- [ ] **Step 1: Configure Tailwind**

`frontend/tailwind.config.ts`:

```typescript
import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          base: "#1a1e2e",
          card: "#22273a",
          nav: "#171b28",
        },
        border: {
          DEFAULT: "#2d3348",
        },
        text: {
          primary: "#e0e4ed",
          body: "#c8cdd8",
          muted: "#8891a5",
          dim: "#5a6178",
        },
        accent: {
          cyan: "#4fc3f7",
          orange: "#ffb74d",
        },
        brand: {
          // Used for portfolio sub-brand colour-coding (Pepsi pattern)
          a: "#4fc3f7",
          b: "#81c784",
          c: "#ba68c8",
          d: "#ffb74d",
          e: "#f06292",
        },
      },
      fontSize: {
        h1: ["22px", { fontWeight: "600" }],
        "chart-title": ["15px", { fontWeight: "500" }],
        "chart-subtitle": ["12px", { fontWeight: "400" }],
        body: ["13px", { lineHeight: "1.5" }],
      },
    },
  },
  plugins: [],
} satisfies Config;
```

- [ ] **Step 2: Create globals.css**

`frontend/src/styles/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  color-scheme: dark;
}

html, body, #root {
  height: 100%;
  margin: 0;
  background: theme(colors.bg.base);
  color: theme(colors.text.body);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 13px;
}

* {
  box-sizing: border-box;
}
```

- [ ] **Step 3: Import in main.tsx**

`frontend/src/main.tsx`:

```typescript
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles/globals.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- [ ] **Step 4: Verify**

```bash
cd frontend && npm run dev
```

Open `http://localhost:5173` — page should render with the dark background. Text on existing default Vite content should be visible against `#1a1e2e`.

- [ ] **Step 5: Commit**

```bash
git add frontend/tailwind.config.ts frontend/src/styles/globals.css frontend/src/main.tsx frontend/postcss.config.js
git commit -m "feat: Tailwind theme tokens for dark advertiser-views design"
```

---

### Task 2: API client + TanStack Query

**Files:**
- Create: `frontend/src/lib/api-client.ts`
- Create: `frontend/src/lib/query-client.ts`
- Create: `frontend/.env.development`
- Modify: `frontend/src/main.tsx`

- [ ] **Step 1: Env file**

`frontend/.env.development`:

```
VITE_API_BASE_URL=http://localhost:8000
```

- [ ] **Step 2: Implement api-client**

`frontend/src/lib/api-client.ts`:

```typescript
// ABOUTME: Typed fetch wrapper around the H1B FastAPI service.
// ABOUTME: All hooks call into this; tests mock at this layer via MSW.

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { Accept: "application/json" },
  });
  const body = res.headers.get("content-type")?.includes("application/json")
    ? await res.json()
    : await res.text();
  if (!res.ok) {
    throw new ApiError(`GET ${path} → ${res.status}`, res.status, body);
  }
  return body as T;
}
```

- [ ] **Step 3: Query client**

`frontend/src/lib/query-client.ts`:

```typescript
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,        // 5 min — matches API cache for volatile data
      gcTime: 30 * 60 * 1000,          // 30 min in cache
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});
```

- [ ] **Step 4: Wire into main.tsx**

```typescript
import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { queryClient } from "./lib/query-client";
import "./styles/globals.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>
);
```

- [ ] **Step 5: Test the API client**

`frontend/src/lib/api-client.test.ts`:

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";
import { apiGet, ApiError } from "./api-client";

describe("apiGet", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("returns parsed JSON on 200", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      headers: new Headers({ "content-type": "application/json" }),
      json: async () => ({ ok: true }),
    }));
    const result = await apiGet<{ ok: boolean }>("/api/health");
    expect(result).toEqual({ ok: true });
  });

  it("throws ApiError on non-2xx", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      headers: new Headers({ "content-type": "application/json" }),
      json: async () => ({ error: "not_found" }),
    }));
    await expect(apiGet("/api/missing")).rejects.toBeInstanceOf(ApiError);
  });
});
```

- [ ] **Step 6: Configure Vitest**

`frontend/vite.config.ts`:

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test/setup.ts"],
  },
});
```

`frontend/src/test/setup.ts`:

```typescript
import "@testing-library/jest-dom";
```

- [ ] **Step 7: Run test, commit**

```bash
cd frontend && npm test -- --run
```

Expected: 2 PASS.

```bash
git add frontend/
git commit -m "feat: api client and TanStack Query setup"
```

---

### Task 3: AppShell, Header, Sidebar layout

**Files:**
- Create: `frontend/src/components/layout/AppShell.tsx`
- Create: `frontend/src/components/layout/Header.tsx`
- Create: `frontend/src/components/layout/Sidebar.tsx`
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: Header**

`frontend/src/components/layout/Header.tsx`:

```typescript
// ABOUTME: Top nav bar with brand text, links, and the global MI toggle.
// ABOUTME: Style matches the existing Pepsi/Talon Netlify advertiser-trends sites.

import { NavLink } from "react-router-dom";
import { MobileIndexToggle } from "@/components/MobileIndexToggle";

export function Header() {
  return (
    <header className="bg-bg-nav border-b border-border px-7 py-3 flex items-center gap-6 flex-wrap">
      <span className="text-text-primary font-semibold text-[14px] flex items-center gap-2">
        Route Playout — Advertiser Trends
      </span>
      <nav className="flex items-center gap-4">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `px-2.5 py-1 rounded text-[13px] transition-colors ${
              isActive ? "text-text-primary bg-[#2d3348]" : "text-text-muted hover:text-text-primary hover:bg-[#2d3348]"
            }`
          }
          end
        >
          Overview
        </NavLink>
        {/* Top advertisers will be added dynamically once data layer is in. */}
      </nav>
      <div className="ml-auto">
        <MobileIndexToggle />
      </div>
    </header>
  );
}
```

- [ ] **Step 2: Sidebar (placeholder, populated in M5/M6 when data is available)**

```typescript
// frontend/src/components/layout/Sidebar.tsx
import { NavLink } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";

interface AdvertiserSummary {
  slug: string;
  brand_name: string;
}

export function Sidebar() {
  const { data: advertisers } = useQuery({
    queryKey: ["advertisers"],
    queryFn: () => apiGet<AdvertiserSummary[]>("/api/advertisers"),
  });

  return (
    <aside className="w-56 bg-bg-nav border-r border-border p-4 overflow-auto">
      <NavLink to="/" className="block mb-3 text-text-primary font-medium text-[13px]">
        All advertisers
      </NavLink>
      <ul className="space-y-1">
        {advertisers?.slice(0, 12).map((a) => (
          <li key={a.slug}>
            <NavLink
              to={`/advertisers/${a.slug}`}
              className={({ isActive }) =>
                `block px-2 py-1 rounded text-[12px] transition-colors ${
                  isActive ? "text-text-primary bg-[#2d3348]" : "text-text-muted hover:text-text-primary"
                }`
              }
            >
              {a.brand_name}
            </NavLink>
          </li>
        ))}
      </ul>
    </aside>
  );
}
```

- [ ] **Step 3: AppShell**

```typescript
// frontend/src/components/layout/AppShell.tsx
import { ReactNode } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <div className="max-w-[1100px] mx-auto px-6 py-8">{children}</div>
        </main>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: App.tsx with routing**

```typescript
// frontend/src/App.tsx
import { Routes, Route } from "react-router-dom";
import { AppShell } from "@/components/layout/AppShell";
import OverviewPage from "@/routes/index";
import AdvertiserDetailPage from "@/routes/advertisers/$slug";

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<OverviewPage />} />
        <Route path="/advertisers/:slug" element={<AdvertiserDetailPage />} />
      </Routes>
    </AppShell>
  );
}
```

- [ ] **Step 5: Stub the route components**

`frontend/src/routes/index.tsx`:
```typescript
export default function OverviewPage() {
  return <h1 className="text-h1 text-text-primary">Advertiser Overview</h1>;
}
```

`frontend/src/routes/advertisers/$slug.tsx`:
```typescript
import { useParams } from "react-router-dom";
export default function AdvertiserDetailPage() {
  const { slug } = useParams();
  return <h1 className="text-h1 text-text-primary">Advertiser: {slug}</h1>;
}
```

- [ ] **Step 6: Path alias**

`frontend/tsconfig.json` — add:
```json
{
  "compilerOptions": {
    "baseUrl": "./",
    "paths": { "@/*": ["src/*"] }
  }
}
```

`frontend/vite.config.ts`:
```typescript
import path from "node:path";
// ...
resolve: { alias: { "@": path.resolve(__dirname, "./src") } },
```

- [ ] **Step 7: Run dev, smoke**

```bash
cd frontend && npm run dev
```

Visit `http://localhost:5173` and `http://localhost:5173/advertisers/lidl`. Layout should render with header, empty sidebar (waiting for API), main area.

- [ ] **Step 8: Commit**

```bash
git add frontend/
git commit -m "feat: AppShell with header, sidebar, and routing skeleton"
```

---

### Task 4: MI toggle + persistent state

**Files:**
- Create: `frontend/src/state/mi-toggle-store.ts`
- Create: `frontend/src/components/MobileIndexToggle.tsx`

The MI toggle persists across pages via localStorage and exposes a hook for components to read state.

- [ ] **Step 1: Implement store**

```typescript
// frontend/src/state/mi-toggle-store.ts
// ABOUTME: localStorage-backed Mobile Index toggle state.
// ABOUTME: Mode is 'off' | 'mean' | 'median' | 'both'. Default 'off'.

import { useEffect, useState } from "react";

export type MIMode = "off" | "mean" | "median" | "both";

const STORAGE_KEY = "route-playout.mi-mode";

function read(): MIMode {
  if (typeof window === "undefined") return "off";
  const v = window.localStorage.getItem(STORAGE_KEY);
  return v === "mean" || v === "median" || v === "both" ? v : "off";
}

const listeners = new Set<(m: MIMode) => void>();

export function setMIMode(mode: MIMode) {
  window.localStorage.setItem(STORAGE_KEY, mode);
  listeners.forEach((l) => l(mode));
}

export function useMIMode(): [MIMode, (m: MIMode) => void] {
  const [mode, setLocal] = useState<MIMode>(read);
  useEffect(() => {
    const listener = (m: MIMode) => setLocal(m);
    listeners.add(listener);
    return () => { listeners.delete(listener); };
  }, []);
  return [mode, setMIMode];
}
```

- [ ] **Step 2: Toggle component**

```typescript
// frontend/src/components/MobileIndexToggle.tsx
import { useMIMode, MIMode } from "@/state/mi-toggle-store";

const MODES: { value: MIMode; label: string }[] = [
  { value: "off", label: "Off" },
  { value: "mean", label: "Mean" },
  { value: "median", label: "Median" },
  { value: "both", label: "Both" },
];

export function MobileIndexToggle() {
  const [mode, setMode] = useMIMode();
  const active = mode !== "off";
  return (
    <label
      className={`flex items-center gap-2 px-3 py-1 rounded border text-[12px] cursor-pointer select-none transition-colors ${
        active
          ? "border-accent-orange bg-accent-orange/10 text-text-primary"
          : "border-border text-text-muted hover:text-text-primary"
      }`}
    >
      <span>📱 Mobile Index</span>
      <select
        value={mode}
        onChange={(e) => setMode(e.target.value as MIMode)}
        className="bg-transparent text-inherit outline-none"
      >
        {MODES.map((m) => (
          <option key={m.value} value={m.value} className="bg-bg-nav">
            {m.label}
          </option>
        ))}
      </select>
    </label>
  );
}
```

- [ ] **Step 3: Test the store**

```typescript
// frontend/src/state/mi-toggle-store.test.ts
import { renderHook, act } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { useMIMode } from "./mi-toggle-store";

describe("useMIMode", () => {
  beforeEach(() => { window.localStorage.clear(); });

  it("defaults to 'off'", () => {
    const { result } = renderHook(() => useMIMode());
    expect(result.current[0]).toBe("off");
  });

  it("persists changes to localStorage", () => {
    const { result } = renderHook(() => useMIMode());
    act(() => result.current[1]("mean"));
    expect(window.localStorage.getItem("route-playout.mi-mode")).toBe("mean");
    expect(result.current[0]).toBe("mean");
  });
});
```

- [ ] **Step 4: Run tests, commit**

```bash
cd frontend && npm test -- --run
git add frontend/src/state frontend/src/components/MobileIndexToggle.tsx frontend/src/state/mi-toggle-store.test.ts
git commit -m "feat: persistent Mobile Index toggle"
```

---

### Task 5: UI primitives — Card, MetricBlock, DataLimitationsPanel

**Files:**
- Create: `frontend/src/components/ui/Card.tsx`
- Create: `frontend/src/components/ui/MetricBlock.tsx`
- Create: `frontend/src/components/ui/DataLimitationsPanel.tsx`

- [ ] **Step 1: Card**

```typescript
// frontend/src/components/ui/Card.tsx
import { ReactNode } from "react";

export function Card({ children, className = "" }: { children: ReactNode; className?: string }) {
  return (
    <div className={`bg-bg-card border border-border rounded-lg px-6 py-5 ${className}`}>
      {children}
    </div>
  );
}

export function CardTitle({ children }: { children: ReactNode }) {
  return <h2 className="text-[14px] font-medium text-text-primary mb-3">{children}</h2>;
}
```

- [ ] **Step 2: MetricBlock**

```typescript
// frontend/src/components/ui/MetricBlock.tsx
import { ReactNode } from "react";

export function MetricBlock({
  label,
  value,
  hint,
}: {
  label: string;
  value: ReactNode;
  hint?: string;
}) {
  return (
    <div className="flex flex-col">
      <span className="text-[11px] text-text-muted uppercase tracking-wide">{label}</span>
      <span className="text-[20px] font-medium text-text-primary mt-1">{value}</span>
      {hint && <span className="text-[11px] text-text-dim mt-0.5">{hint}</span>}
    </div>
  );
}
```

- [ ] **Step 3: DataLimitationsPanel**

```typescript
// frontend/src/components/ui/DataLimitationsPanel.tsx
import { Card, CardTitle } from "./Card";

export interface DataLimitation {
  code: string;
  title: string;
  detail: string;
}

export function DataLimitationsPanel({ items }: { items: DataLimitation[] }) {
  if (!items?.length) return null;
  return (
    <Card>
      <CardTitle>Data Limitations & Caveats</CardTitle>
      <ol className="list-decimal pl-5 space-y-2">
        {items.map((item) => (
          <li key={item.code} className="text-[12px] text-text-body leading-relaxed">
            <strong className="text-text-primary font-medium">{item.title}.</strong>{" "}
            {item.detail}
          </li>
        ))}
      </ol>
    </Card>
  );
}
```

- [ ] **Step 4: Smoke test**

```typescript
// frontend/src/components/ui/Card.test.tsx
import { render, screen } from "@testing-library/react";
import { Card, CardTitle } from "./Card";

test("Card renders children", () => {
  render(<Card><CardTitle>Hello</CardTitle></Card>);
  expect(screen.getByText("Hello")).toBeInTheDocument();
});
```

```typescript
// frontend/src/components/ui/DataLimitationsPanel.test.tsx
import { render, screen } from "@testing-library/react";
import { DataLimitationsPanel } from "./DataLimitationsPanel";

test("renders limitation items", () => {
  render(<DataLimitationsPanel items={[
    { code: "x", title: "Brand attribution", detail: "Some campaigns lack labels." }
  ]} />);
  expect(screen.getByText(/Brand attribution/i)).toBeInTheDocument();
  expect(screen.getByText(/Some campaigns lack labels/)).toBeInTheDocument();
});
```

- [ ] **Step 5: Run tests, commit**

```bash
cd frontend && npm test -- --run
git add frontend/src/components/ui/
git commit -m "feat: Card, MetricBlock, DataLimitationsPanel primitives"
```

---

### Task 6: Plotly chart wrapper + helpers

**Files:**
- Create: `frontend/src/components/charts/PlotlyChart.tsx`
- Create: `frontend/src/components/charts/weekendBands.ts`
- Create: `frontend/src/components/charts/avgLine.ts`
- Create: `frontend/src/components/charts/plotlyDarkTheme.ts`

The charts library: a wrapper plus reusable layout helpers so every chart in the app inherits weekend-shading + avg-line + dark-theme defaults.

- [ ] **Step 1: Dark theme defaults**

```typescript
// frontend/src/components/charts/plotlyDarkTheme.ts
import type { Layout, Config } from "plotly.js";

export const darkLayout: Partial<Layout> = {
  paper_bgcolor: "#22273a",
  plot_bgcolor: "#22273a",
  font: { color: "#c8cdd8", family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", size: 12 },
  xaxis: {
    gridcolor: "#2d3348",
    zerolinecolor: "#2d3348",
    tickcolor: "#5a6178",
    color: "#8891a5",
  },
  yaxis: {
    gridcolor: "#2d3348",
    zerolinecolor: "#2d3348",
    tickcolor: "#5a6178",
    color: "#8891a5",
  },
  margin: { l: 50, r: 20, t: 20, b: 50 },
  hovermode: "x unified",
  legend: {
    orientation: "h",
    y: -0.18,
    x: 0,
    font: { color: "#c8cdd8" },
  },
};

export const plotlyConfig: Partial<Config> = {
  displaylogo: false,
  responsive: true,
  modeBarButtonsToRemove: ["lasso2d", "select2d", "autoScale2d"],
};
```

- [ ] **Step 2: Weekend-bands helper**

```typescript
// frontend/src/components/charts/weekendBands.ts
import type { Shape } from "plotly.js";

export function weekendBands(dates: Date[]): Partial<Shape>[] {
  const shapes: Partial<Shape>[] = [];
  if (!dates.length) return shapes;
  const min = dates[0];
  const max = dates[dates.length - 1];
  const cursor = new Date(min);
  while (cursor <= max) {
    const dow = cursor.getDay();
    if (dow === 6) {
      // Saturday — band runs to end of Sunday
      const end = new Date(cursor);
      end.setDate(end.getDate() + 2);
      shapes.push({
        type: "rect",
        xref: "x",
        yref: "paper",
        x0: cursor.toISOString(),
        x1: end.toISOString(),
        y0: 0,
        y1: 1,
        fillcolor: "rgba(45, 51, 72, 0.4)",
        line: { width: 0 },
        layer: "below",
      });
    }
    cursor.setDate(cursor.getDate() + 1);
  }
  return shapes;
}
```

- [ ] **Step 3: Avg-line helper**

```typescript
// frontend/src/components/charts/avgLine.ts
import type { Shape } from "plotly.js";

export function avgLine(values: number[], xRange: [Date, Date]): Partial<Shape> | null {
  if (!values.length) return null;
  const avg = values.reduce((a, b) => a + b, 0) / values.length;
  return {
    type: "line",
    xref: "x",
    yref: "y",
    x0: xRange[0].toISOString(),
    x1: xRange[1].toISOString(),
    y0: avg,
    y1: avg,
    line: { color: "#8891a5", width: 1, dash: "dash" },
    layer: "above",
  };
}
```

- [ ] **Step 4: Chart wrapper**

```typescript
// frontend/src/components/charts/PlotlyChart.tsx
import Plot from "react-plotly.js";
import type { Data, Layout } from "plotly.js";
import { darkLayout, plotlyConfig } from "./plotlyDarkTheme";

export function PlotlyChart({
  data,
  layout = {},
  height = 420,
}: {
  data: Data[];
  layout?: Partial<Layout>;
  height?: number;
}) {
  const merged: Partial<Layout> = {
    ...darkLayout,
    ...layout,
    height,
    xaxis: { ...darkLayout.xaxis, ...layout.xaxis },
    yaxis: { ...darkLayout.yaxis, ...layout.yaxis },
  };
  return (
    <Plot
      data={data}
      layout={merged}
      config={plotlyConfig}
      style={{ width: "100%", height: `${height}px` }}
      useResizeHandler
    />
  );
}
```

- [ ] **Step 5: Test helpers**

```typescript
// frontend/src/components/charts/weekendBands.test.ts
import { describe, it, expect } from "vitest";
import { weekendBands } from "./weekendBands";

describe("weekendBands", () => {
  it("returns empty for empty input", () => {
    expect(weekendBands([])).toEqual([]);
  });

  it("produces one shape per weekend in range", () => {
    // Mon Aug 4 2025 → Sun Aug 17 2025 = 2 weekends
    const dates = [];
    for (let d = new Date("2025-08-04"); d <= new Date("2025-08-17"); d.setDate(d.getDate() + 1)) {
      dates.push(new Date(d));
    }
    expect(weekendBands(dates).length).toBe(2);
  });
});
```

- [ ] **Step 6: Run tests, commit**

```bash
cd frontend && npm test -- --run
git add frontend/src/components/charts/
git commit -m "feat: Plotly wrapper with weekend bands and avg line helpers"
```

---

### Task 7: Advertiser data hooks

**Files:**
- Create: `frontend/src/features/advertiser-view/hooks/useAdvertiser.ts`
- Create: `frontend/src/features/advertiser-view/types.ts`

- [ ] **Step 1: Types**

```typescript
// frontend/src/features/advertiser-view/types.ts
export interface AdvertiserSummary {
  slug: string;
  brand_name: string;
  campaign_count: number;
  weeks_active: number;
  peak_week_impacts: number;
  peak_week_label?: string;
  mean_week_impacts: number;
  shape_descriptor: string;
}

export interface AdvertiserDetail {
  slug: string;
  brand_name: string;
  campaign_count: number;
  weeks_active: number;
  period_start?: string;
  period_end?: string;
  total_impacts: number;
  sub_brands: string[];
}

export interface AdvertiserCampaign {
  campaign_id: string;
  period_start?: string;
  period_end?: string;
  days_active: number;
  total_impacts: number;
  reach?: number;
  frequency?: number;
  primary_media_owner?: string;
}

export interface DailyPoint {
  date: string;
  total_impacts: number;
  indexed_impacts?: number;
  median_indexed_impacts?: number;
  is_partial: boolean;
}

export interface WeeklyPoint {
  week_label: string;
  iso_week: number;
  total_impacts: number;
  indexed_impacts?: number;
  median_indexed_impacts?: number;
  active_brand?: string;
  frame_count: number;
  campaign_count: number;
  is_partial: boolean;
}

export interface DataLimitation {
  code: string;
  title: string;
  detail: string;
}
```

- [ ] **Step 2: Hooks**

```typescript
// frontend/src/features/advertiser-view/hooks/useAdvertiser.ts
import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api-client";
import type {
  AdvertiserSummary,
  AdvertiserDetail,
  AdvertiserCampaign,
  DailyPoint,
  WeeklyPoint,
  DataLimitation,
} from "../types";
import { MIMode } from "@/state/mi-toggle-store";

export function useAdvertisers() {
  return useQuery({
    queryKey: ["advertisers"],
    queryFn: () => apiGet<AdvertiserSummary[]>("/api/advertisers"),
  });
}

export function useAdvertiser(slug: string) {
  return useQuery({
    queryKey: ["advertiser", slug],
    queryFn: () => apiGet<AdvertiserDetail>(`/api/advertisers/${slug}`),
    enabled: !!slug,
  });
}

export function useAdvertiserCampaigns(slug: string) {
  return useQuery({
    queryKey: ["advertiser", slug, "campaigns"],
    queryFn: () => apiGet<AdvertiserCampaign[]>(`/api/advertisers/${slug}/campaigns`),
    enabled: !!slug,
  });
}

export function useAdvertiserDaily(slug: string, mi: MIMode) {
  return useQuery({
    queryKey: ["advertiser", slug, "daily", mi],
    queryFn: () =>
      apiGet<DailyPoint[]>(`/api/advertisers/${slug}/timeseries/daily?mi=${mi}`),
    enabled: !!slug,
  });
}

export function useAdvertiserWeekly(slug: string, mi: MIMode) {
  return useQuery({
    queryKey: ["advertiser", slug, "weekly", mi],
    queryFn: () =>
      apiGet<WeeklyPoint[]>(`/api/advertisers/${slug}/timeseries/weekly?mi=${mi}`),
    enabled: !!slug,
  });
}

export function useAdvertiserDataLimitations(slug: string) {
  return useQuery({
    queryKey: ["advertiser", slug, "data-limitations"],
    queryFn: () =>
      apiGet<{ items: DataLimitation[] }>(`/api/advertisers/${slug}/data-limitations`),
    enabled: !!slug,
    select: (d) => d.items,
  });
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/advertiser-view/
git commit -m "feat: advertiser data hooks via TanStack Query"
```

---

### Task 8: Advertiser overview page (`/`) — OPTIONAL CUT POINT

If H1 needs to slim, skip this task and Task 8.x. The detail page (Task 9–13) is the minimum viable H1.

**Files:**
- Modify: `frontend/src/routes/index.tsx`
- Create: `frontend/src/features/advertiser-view/AdvertiserSummaryTable.tsx`
- Create: `frontend/src/features/advertiser-view/AdvertiserCardGrid.tsx`

- [ ] **Step 1: Summary table**

```typescript
// frontend/src/features/advertiser-view/AdvertiserSummaryTable.tsx
import { Link } from "react-router-dom";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  ColumnDef,
  flexRender,
} from "@tanstack/react-table";
import { useState } from "react";
import type { AdvertiserSummary } from "./types";

const cols: ColumnDef<AdvertiserSummary>[] = [
  {
    accessorKey: "brand_name",
    header: "Advertiser",
    cell: (c) => (
      <Link
        to={`/advertisers/${c.row.original.slug}`}
        className="text-accent-cyan hover:underline"
      >
        {c.getValue<string>()}
      </Link>
    ),
  },
  { accessorKey: "campaign_count", header: "Campaigns" },
  { accessorKey: "weeks_active", header: "Weeks" },
  {
    accessorKey: "peak_week_impacts",
    header: "Peak (000s)",
    cell: (c) => `${Math.round(c.getValue<number>() / 1000)}k`,
  },
  {
    accessorKey: "mean_week_impacts",
    header: "Mean (000s)",
    cell: (c) => `${Math.round(c.getValue<number>() / 1000)}k`,
  },
  { accessorKey: "peak_week_label", header: "Peak Week" },
  { accessorKey: "shape_descriptor", header: "Shape" },
];

export function AdvertiserSummaryTable({ data }: { data: AdvertiserSummary[] }) {
  const [sorting, setSorting] = useState([]);
  const table = useReactTable({
    data,
    columns: cols,
    state: { sorting },
    onSortingChange: setSorting as any,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <table className="w-full text-[12px] border-collapse">
      <thead>
        {table.getHeaderGroups().map((hg) => (
          <tr key={hg.id}>
            {hg.headers.map((h) => (
              <th
                key={h.id}
                className="text-left text-text-muted font-medium px-2 py-1.5 border-b border-border cursor-pointer"
                onClick={h.column.getToggleSortingHandler()}
              >
                {flexRender(h.column.columnDef.header, h.getContext())}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody>
        {table.getRowModel().rows.map((row) => (
          <tr key={row.id} className="hover:bg-[rgba(79,195,247,0.04)]">
            {row.getVisibleCells().map((cell) => (
              <td
                key={cell.id}
                className="text-text-body px-2 py-2 border-b border-border/50"
              >
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

- [ ] **Step 2: Card grid**

```typescript
// frontend/src/features/advertiser-view/AdvertiserCardGrid.tsx
import { Link } from "react-router-dom";
import type { AdvertiserSummary } from "./types";

export function AdvertiserCardGrid({ items }: { items: AdvertiserSummary[] }) {
  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(320px,1fr))] gap-4">
      {items.map((a) => (
        <Link
          key={a.slug}
          to={`/advertisers/${a.slug}`}
          className="bg-bg-card border border-border rounded-lg px-6 py-5 transition-all hover:border-accent-cyan hover:-translate-y-0.5"
        >
          <h3 className="text-[15px] font-medium text-text-primary mb-1">{a.brand_name}</h3>
          <div className="text-[12px] text-text-muted mb-2">
            {a.campaign_count} campaigns · {a.weeks_active} weeks ·{" "}
            <span className="text-accent-cyan font-medium">
              Peak {Math.round(a.peak_week_impacts / 1000)}k {a.peak_week_label}
            </span>
          </div>
          <div className="text-[12px] text-text-body leading-relaxed">{a.shape_descriptor}</div>
        </Link>
      ))}
    </div>
  );
}
```

- [ ] **Step 3: Wire into route**

```typescript
// frontend/src/routes/index.tsx
import { useAdvertisers } from "@/features/advertiser-view/hooks/useAdvertiser";
import { AdvertiserSummaryTable } from "@/features/advertiser-view/AdvertiserSummaryTable";
import { AdvertiserCardGrid } from "@/features/advertiser-view/AdvertiserCardGrid";
import { Card, CardTitle } from "@/components/ui/Card";

export default function OverviewPage() {
  const { data, isLoading, error } = useAdvertisers();

  if (isLoading) return <p className="text-text-muted">Loading…</p>;
  if (error) return <p className="text-accent-orange">Error: {(error as Error).message}</p>;
  if (!data) return null;

  return (
    <>
      <h1 className="text-h1 text-text-primary mb-1">Advertiser Trends</h1>
      <p className="text-[13px] text-text-muted mb-8">2025 playout snapshot · All Adults</p>

      <Card className="mb-6">
        <CardTitle>Advertiser Summary</CardTitle>
        <AdvertiserSummaryTable data={data} />
      </Card>

      <h2 className="text-[14px] font-medium text-text-primary mb-3 mt-8">Individual Charts</h2>
      <AdvertiserCardGrid items={data} />
    </>
  );
}
```

- [ ] **Step 4: Run dev, smoke**

```bash
cd frontend && npm run dev
# In another terminal: startapi
```

Visit `http://localhost:5173`. Expected: header + sidebar + summary table + card grid populated from API.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/routes/index.tsx frontend/src/features/advertiser-view/
git commit -m "feat: advertiser overview page (M5)"
```

---

### Task 9: Advertiser detail header

**Files:**
- Create: `frontend/src/features/advertiser-view/AdvertiserHeader.tsx`

- [ ] **Step 1: Implement**

```typescript
// frontend/src/features/advertiser-view/AdvertiserHeader.tsx
import { MetricBlock } from "@/components/ui/MetricBlock";
import type { AdvertiserDetail } from "./types";

export function AdvertiserHeader({ data }: { data: AdvertiserDetail }) {
  const period =
    data.period_start && data.period_end
      ? `${data.period_start} – ${data.period_end}`
      : "—";
  return (
    <header className="mb-6">
      <h1 className="text-h1 text-text-primary mb-1">{data.brand_name}</h1>
      <div className="text-[13px] text-text-muted mb-5">
        {period} · {data.campaign_count} campaigns · {data.weeks_active} weeks · All Adults
      </div>
      <div className="grid grid-cols-4 gap-4">
        <MetricBlock label="Total impacts" value={`${(data.total_impacts / 1_000_000).toFixed(1)}M`} hint="000s" />
        <MetricBlock label="Campaigns" value={data.campaign_count} />
        <MetricBlock label="Weeks active" value={data.weeks_active} />
        <MetricBlock label="Sub-brands" value={data.sub_brands?.length ?? 0} />
      </div>
    </header>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/features/advertiser-view/AdvertiserHeader.tsx
git commit -m "feat: AdvertiserHeader with metric blocks"
```

---

### Task 10: Daily timeseries chart

**Files:**
- Create: `frontend/src/features/advertiser-view/DailyTimeseriesChart.tsx`

- [ ] **Step 1: Implement**

```typescript
// frontend/src/features/advertiser-view/DailyTimeseriesChart.tsx
import type { Data } from "plotly.js";
import { PlotlyChart } from "@/components/charts/PlotlyChart";
import { weekendBands } from "@/components/charts/weekendBands";
import { avgLine } from "@/components/charts/avgLine";
import { Card, CardTitle } from "@/components/ui/Card";
import type { DailyPoint } from "./types";
import { MIMode } from "@/state/mi-toggle-store";

export function DailyTimeseriesChart({
  data,
  miMode,
  brandColour = "#4fc3f7",
}: {
  data: DailyPoint[];
  miMode: MIMode;
  brandColour?: string;
}) {
  if (!data.length) {
    return (
      <Card>
        <CardTitle>Daily Audience Shape</CardTitle>
        <p className="text-text-muted text-[13px]">No data.</p>
      </Card>
    );
  }

  const dates = data.map((d) => new Date(d.date));
  const totals = data.map((d) => d.total_impacts);

  const traces: Data[] = [
    {
      type: "scatter",
      mode: "lines",
      x: dates,
      y: totals,
      name: "Impacts (000s)",
      line: { color: brandColour, width: 2 },
      fill: "tozeroy",
      fillcolor: `${brandColour}33`,
      hovertemplate: "%{x|%a %d %b}<br>Impacts: %{y:,.0f}k<extra></extra>",
    },
  ];

  if (miMode === "mean" || miMode === "both") {
    traces.push({
      type: "scatter",
      mode: "lines",
      x: dates,
      y: data.map((d) => d.indexed_impacts ?? null),
      name: "Mobile Mean",
      line: { color: "#ffb74d", width: 2, dash: "dash" },
      hovertemplate: "%{x|%a %d %b}<br>Mobile Mean: %{y:,.0f}k<extra></extra>",
    });
  }
  if (miMode === "median" || miMode === "both") {
    traces.push({
      type: "scatter",
      mode: "lines",
      x: dates,
      y: data.map((d) => d.median_indexed_impacts ?? null),
      name: "Mobile Median",
      line: { color: "#ba68c8", width: 2, dash: "dot" },
      hovertemplate: "%{x|%a %d %b}<br>Mobile Median: %{y:,.0f}k<extra></extra>",
    });
  }

  const shapes = [
    ...weekendBands(dates),
    ...(avgLine(totals, [dates[0], dates[dates.length - 1]]) ? [avgLine(totals, [dates[0], dates[dates.length - 1]])!] : []),
  ];

  return (
    <Card>
      <CardTitle>Daily Audience Shape</CardTitle>
      <PlotlyChart
        data={traces}
        layout={{ shapes, yaxis: { title: { text: "Impacts (000s)" } } }}
      />
    </Card>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/features/advertiser-view/DailyTimeseriesChart.tsx
git commit -m "feat: DailyTimeseriesChart with weekend bands, avg line, MI overlays"
```

---

### Task 11: Weekly timeseries chart with brand transitions

**Files:**
- Create: `frontend/src/features/advertiser-view/WeeklyTimeseriesChart.tsx`

Each week's bar coloured by `active_brand`. Maps brand names to the `brand-a` / `brand-b` / `brand-c` palette via a deterministic hash.

- [ ] **Step 1: Brand colour helper**

```typescript
// frontend/src/features/advertiser-view/brandColour.ts
const PALETTE = ["#4fc3f7", "#81c784", "#ba68c8", "#ffb74d", "#f06292"];

export function brandColour(name?: string): string {
  if (!name) return "#546e7a";
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) & 0xffffffff;
  return PALETTE[Math.abs(hash) % PALETTE.length];
}
```

- [ ] **Step 2: Implement chart**

```typescript
// frontend/src/features/advertiser-view/WeeklyTimeseriesChart.tsx
import type { Data } from "plotly.js";
import { PlotlyChart } from "@/components/charts/PlotlyChart";
import { Card, CardTitle } from "@/components/ui/Card";
import type { WeeklyPoint } from "./types";
import { brandColour } from "./brandColour";
import { MIMode } from "@/state/mi-toggle-store";

export function WeeklyTimeseriesChart({
  data,
  miMode,
}: {
  data: WeeklyPoint[];
  miMode: MIMode;
}) {
  if (!data.length) return <Card><CardTitle>Weekly Shape</CardTitle><p>No data.</p></Card>;

  const labels = data.map((d) => d.week_label);
  const colours = data.map((d) => (d.is_partial ? "#5a6178" : brandColour(d.active_brand)));

  const traces: Data[] = [
    {
      type: "bar",
      x: labels,
      y: data.map((d) => d.total_impacts),
      marker: { color: colours },
      name: "Impacts (000s)",
      hovertemplate: "%{x}<br>Impacts: %{y:,.0f}k<extra></extra>",
    },
  ];

  if (miMode === "mean" || miMode === "both") {
    traces.push({
      type: "scatter",
      mode: "lines+markers",
      x: labels,
      y: data.map((d) => d.indexed_impacts ?? null),
      name: "Mobile Mean",
      line: { color: "#ffb74d", width: 2, dash: "dash" },
      marker: { size: 6 },
    });
  }
  if (miMode === "median" || miMode === "both") {
    traces.push({
      type: "scatter",
      mode: "lines+markers",
      x: labels,
      y: data.map((d) => d.median_indexed_impacts ?? null),
      name: "Mobile Median",
      line: { color: "#ba68c8", width: 2, dash: "dot" },
      marker: { size: 6 },
    });
  }

  // Build legend swatches for unique active brands
  const uniqueBrands = Array.from(new Set(data.map((d) => d.active_brand).filter(Boolean) as string[]));

  return (
    <Card>
      <CardTitle>Weekly Campaign Shape</CardTitle>
      {uniqueBrands.length > 1 && (
        <div className="flex gap-4 mb-3 text-[11px]">
          {uniqueBrands.map((brand) => (
            <span key={brand} className="flex items-center gap-1.5">
              <span
                className="inline-block w-3 h-1 rounded-sm"
                style={{ background: brandColour(brand) }}
              />
              <span className="text-text-muted">{brand}</span>
            </span>
          ))}
        </div>
      )}
      <PlotlyChart data={traces} layout={{ yaxis: { title: { text: "Impacts (000s)" } } }} />
    </Card>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/features/advertiser-view/WeeklyTimeseriesChart.tsx frontend/src/features/advertiser-view/brandColour.ts
git commit -m "feat: WeeklyTimeseriesChart with brand transition colour coding"
```

---

### Task 12: Campaign list table

**Files:**
- Create: `frontend/src/features/advertiser-view/CampaignList.tsx`

Click row → deep-link to existing Streamlit campaign detail. Streamlit URL pattern: the user clicks a campaign in Streamlit's browser; H1 doesn't have a clean URL for "open campaign N", so the simplest bridge is opening Streamlit and instructing the user to search for the campaign. **Improvement candidate (post-H1):** add a query-param-driven autoload to Streamlit (e.g. `?campaign_id=N` triggers selection on app start).

For H1, the row click opens Streamlit at the root: `http://localhost:8504/?prefill=<id>` and we add a small Streamlit-side change in M7 to read the query param.

- [ ] **Step 1: Implement table**

```typescript
// frontend/src/features/advertiser-view/CampaignList.tsx
import { Card, CardTitle } from "@/components/ui/Card";
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  ColumnDef,
  flexRender,
} from "@tanstack/react-table";
import { useState } from "react";
import type { AdvertiserCampaign } from "./types";

const STREAMLIT_BASE = import.meta.env.VITE_STREAMLIT_URL ?? "http://localhost:8504";

const cols: ColumnDef<AdvertiserCampaign>[] = [
  { accessorKey: "campaign_id", header: "Campaign" },
  {
    accessorKey: "period_start",
    header: "From",
    cell: (c) => c.getValue<string>() ?? "—",
  },
  {
    accessorKey: "period_end",
    header: "To",
    cell: (c) => c.getValue<string>() ?? "—",
  },
  { accessorKey: "days_active", header: "Days" },
  {
    accessorKey: "total_impacts",
    header: "Impacts (000s)",
    cell: (c) => `${Math.round(c.getValue<number>() / 1000).toLocaleString()}`,
  },
  { accessorKey: "primary_media_owner", header: "Media owner" },
];

export function CampaignList({ campaigns }: { campaigns: AdvertiserCampaign[] }) {
  const [sorting, setSorting] = useState([]);
  const table = useReactTable({
    data: campaigns,
    columns: cols,
    state: { sorting },
    onSortingChange: setSorting as any,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <Card>
      <CardTitle>Campaigns</CardTitle>
      <table className="w-full text-[12px] border-collapse">
        <thead>
          {table.getHeaderGroups().map((hg) => (
            <tr key={hg.id}>
              {hg.headers.map((h) => (
                <th
                  key={h.id}
                  className="text-left text-text-muted font-medium px-2 py-1.5 border-b border-border cursor-pointer"
                  onClick={h.column.getToggleSortingHandler()}
                >
                  {flexRender(h.column.columnDef.header, h.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr
              key={row.id}
              className="cursor-pointer hover:bg-[rgba(79,195,247,0.04)]"
              onClick={() =>
                window.open(
                  `${STREAMLIT_BASE}/?campaign_id=${row.original.campaign_id}`,
                  "_blank",
                )
              }
            >
              {row.getVisibleCells().map((cell) => (
                <td
                  key={cell.id}
                  className="text-text-body px-2 py-2 border-b border-border/50"
                >
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/features/advertiser-view/CampaignList.tsx
git commit -m "feat: CampaignList with Streamlit deep-link"
```

---

### Task 13: Wire detail page

**Files:**
- Modify: `frontend/src/routes/advertisers/$slug.tsx`

- [ ] **Step 1: Implement page**

```typescript
// frontend/src/routes/advertisers/$slug.tsx
import { useParams } from "react-router-dom";
import {
  useAdvertiser,
  useAdvertiserCampaigns,
  useAdvertiserDaily,
  useAdvertiserWeekly,
  useAdvertiserDataLimitations,
} from "@/features/advertiser-view/hooks/useAdvertiser";
import { AdvertiserHeader } from "@/features/advertiser-view/AdvertiserHeader";
import { DailyTimeseriesChart } from "@/features/advertiser-view/DailyTimeseriesChart";
import { WeeklyTimeseriesChart } from "@/features/advertiser-view/WeeklyTimeseriesChart";
import { CampaignList } from "@/features/advertiser-view/CampaignList";
import { DataLimitationsPanel } from "@/components/ui/DataLimitationsPanel";
import { useMIMode } from "@/state/mi-toggle-store";

export default function AdvertiserDetailPage() {
  const { slug = "" } = useParams();
  const [miMode] = useMIMode();
  const detail = useAdvertiser(slug);
  const campaigns = useAdvertiserCampaigns(slug);
  const daily = useAdvertiserDaily(slug, miMode);
  const weekly = useAdvertiserWeekly(slug, miMode);
  const limitations = useAdvertiserDataLimitations(slug);

  if (detail.isLoading) return <p className="text-text-muted">Loading…</p>;
  if (detail.error) return <p className="text-accent-orange">Error: {(detail.error as Error).message}</p>;
  if (!detail.data) return null;

  return (
    <div className="space-y-5">
      <AdvertiserHeader data={detail.data} />

      {daily.data && <DailyTimeseriesChart data={daily.data} miMode={miMode} />}
      {weekly.data && <WeeklyTimeseriesChart data={weekly.data} miMode={miMode} />}
      {campaigns.data && <CampaignList campaigns={campaigns.data} />}
      {limitations.data && <DataLimitationsPanel items={limitations.data} />}
    </div>
  );
}
```

- [ ] **Step 2: Smoke**

```bash
# Terminal 1: startapi
# Terminal 2: cd frontend && npm run dev
# Browser: http://localhost:5173/advertisers/lidl
```

Expected: full advertiser detail page renders — header, daily chart with MI toggle effect, weekly chart with brand colour coding, campaign list, data limitations panel.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/routes/advertisers/$slug.tsx
git commit -m "feat: wire single-advertiser detail page"
```

---

### Task 14: E2E happy path with Playwright

**Files:**
- Create: `frontend/playwright.config.ts`
- Create: `frontend/tests/e2e/advertiser-flow.spec.ts`

- [ ] **Step 1: Playwright config**

```typescript
// frontend/playwright.config.ts
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  use: { baseURL: "http://localhost:5173" },
  webServer: {
    command: "npm run dev",
    url: "http://localhost:5173",
    reuseExistingServer: !process.env.CI,
  },
});
```

- [ ] **Step 2: E2E test**

```typescript
// frontend/tests/e2e/advertiser-flow.spec.ts
import { test, expect } from "@playwright/test";

test("advertiser overview → detail → MI toggle", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /advertiser/i })).toBeVisible();

  // Click first card
  const firstCard = page.locator("a[href^='/advertisers/']").first();
  await firstCard.click();
  await expect(page).toHaveURL(/\/advertisers\//);

  // Daily chart should render
  await expect(page.getByText(/Daily Audience Shape/i)).toBeVisible();

  // Toggle MI
  const select = page.locator("select");
  await select.selectOption("mean");
  // Allow a tick for re-fetch
  await page.waitForTimeout(500);
  await expect(page.getByText(/Mobile Mean/i)).toBeVisible();
});
```

- [ ] **Step 3: Run (with FastAPI running)**

```bash
# Terminal 1: startapi
# Terminal 2: cd frontend && npx playwright test
```

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add frontend/playwright.config.ts frontend/tests/e2e/
git commit -m "test: Playwright E2E happy path for advertiser flow"
```

---

### Task 15: M7 — Streamlit prefill query param + final integration

**Files:**
- Modify: `src/ui/app.py`
- Modify: `.env.example`

- [ ] **Step 1: Streamlit prefill from `?campaign_id=N`**

In `src/ui/app.py` near `initialize_session_state`:

```python
def initialize_session_state():
    if "campaign_data" not in st.session_state:
        st.session_state.campaign_data = None
    if "selected_campaign_id" not in st.session_state:
        st.session_state.selected_campaign_id = None
    if "show_analysis" not in st.session_state:
        st.session_state.show_analysis = False
    # Allow deep-link prefill from React advertiser-view CampaignList
    qp = st.query_params
    prefill = qp.get("campaign_id")
    if prefill and st.session_state.selected_campaign_id != prefill:
        st.session_state.selected_campaign_id = prefill
        # Optional: auto-trigger campaign load. Mark for next rerun to trigger analyze.
        st.session_state.show_analysis = True
```

- [ ] **Step 2: Add `VITE_STREAMLIT_URL` to env**

`frontend/.env.development`:
```
VITE_API_BASE_URL=http://localhost:8000
VITE_STREAMLIT_URL=http://localhost:8504
```

- [ ] **Step 3: End-to-end smoke (manual)**

```bash
# Terminal 1: startstream
# Terminal 2: startapi
# Terminal 3: cd frontend && npm run dev
```

- Visit `http://localhost:5173`
- Click an advertiser card
- Verify the daily/weekly charts populate, MI toggle works
- Click a campaign row in the campaign list
- Verify Streamlit opens with the campaign preselected (analysis loads)

- [ ] **Step 4: Update root `.env.example`**

```
# Frontend
FRONTEND_PORT=5173
```

- [ ] **Step 5: Final commit + push**

```bash
git add src/ui/app.py .env.example frontend/.env.development
git commit -m "feat: Streamlit prefill via ?campaign_id= for cross-app deep-linking"
git push origin feature/duckdb-migration
```

---

## Done Criteria

- [ ] `npm test -- --run` passes (unit tests)
- [ ] `npx playwright test` passes (E2E happy path)
- [ ] Streamlit, FastAPI, and React all run simultaneously with no port conflict
- [ ] Visiting `/advertisers/lidl` (or another known slug) renders header + daily chart + weekly chart + campaign list + data limitations
- [ ] MI toggle changes both daily and weekly charts and persists across page navigation
- [ ] Brand transition colour coding visible on weekly chart for portfolios with multiple sub-brands
- [ ] Clicking a campaign row deep-links to Streamlit which auto-loads that campaign
- [ ] Visual fidelity matches the existing Pepsi/Talon Netlify reference

H1C ship signal. H1 complete. The React app is the demoable surface for stakeholder buy-in; Streamlit remains the back-stop until H2 ports the rest.
