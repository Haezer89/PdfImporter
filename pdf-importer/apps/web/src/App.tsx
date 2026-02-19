import { useEffect, useState } from "react";
import { Link, NavLink, Route, Routes } from "react-router-dom";

import { ImportDetailPage } from "./pages/ImportDetailPage";
import { ImportsPage } from "./pages/ImportsPage";
import { ModelsPage } from "./pages/ModelsPage";

function NavItem({ to, label }: { to: string; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `rounded-lg px-3 py-2 text-sm ${
          isActive
            ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900"
            : "text-slate-700 hover:bg-slate-200 dark:text-slate-300 dark:hover:bg-slate-700"
        }`
      }
    >
      {label}
    </NavLink>
  );
}

export function App() {
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "light" || saved === "dark") return saved;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  });

  useEffect(() => {
    const isDark = theme === "dark";
    document.documentElement.classList.toggle("dark", isDark);
    document.body.classList.toggle("dark", isDark);
    document.documentElement.style.colorScheme = isDark ? "dark" : "light";
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-900 dark:text-slate-100">
      <header className="border-b border-slate-200 bg-white/90 backdrop-blur dark:border-slate-700 dark:bg-slate-800/90">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <Link to="/imports" className="block rounded-md px-1 py-0.5 hover:bg-slate-100 dark:hover:bg-slate-700">
            <h1 className="text-lg font-semibold">pdf-importer</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">OCR + KI Extraktion nach JSON Schema</p>
          </Link>
          <div className="flex items-center gap-2">
            <div className="inline-flex rounded-lg border border-slate-300 p-0.5 dark:border-slate-600">
              <button
                onClick={() => setTheme("light")}
                className={`rounded-md px-2.5 py-1.5 text-xs ${
                  theme === "light"
                    ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900"
                    : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
                }`}
              >
                Light
              </button>
              <button
                onClick={() => setTheme("dark")}
                className={`rounded-md px-2.5 py-1.5 text-xs ${
                  theme === "dark"
                    ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900"
                    : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
                }`}
              >
                Dark
              </button>
            </div>
            <span className="text-xs text-slate-500 dark:text-slate-400">{theme === "dark" ? "Dark aktiv" : "Light aktiv"}</span>
            <nav className="flex gap-2">
              <NavItem to="/imports" label="Imports" />
              <NavItem to="/models" label="Models" />
            </nav>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">
        <Routes>
          <Route path="/imports" element={<ImportsPage />} />
          <Route path="/imports/:id" element={<ImportDetailPage />} />
          <Route path="/models" element={<ModelsPage />} />
          <Route path="*" element={<ImportsPage />} />
        </Routes>
      </main>
    </div>
  );
}
