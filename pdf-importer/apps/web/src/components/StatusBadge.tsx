type Props = {
  status: string;
};

const statusMap: Record<string, string> = {
  done: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300",
  failed: "bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300",
  processing: "bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-300",
};

export function StatusBadge({ status }: Props) {
  const cls = statusMap[status] ?? "bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-200";
  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${cls}`}>
      {status}
    </span>
  );
}
