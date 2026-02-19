import { useEffect, useState } from "react";

import { api, type ModelDefinition } from "../api/client";

const defaultSchema = {
  type: "object",
  properties: {
    invoice_number: { type: "string", minLength: 1 },
    total: { type: "number", minimum: 0 },
  },
  required: ["invoice_number", "total"],
  additionalProperties: false,
};

export function ModelsPage() {
  const [models, setModels] = useState<ModelDefinition[]>([]);
  const [name, setName] = useState("Invoice Model");
  const [schema, setSchema] = useState(JSON.stringify(defaultSchema, null, 2));
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [saving, setSaving] = useState(false);

  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [editSchema, setEditSchema] = useState("");
  const [rowBusyId, setRowBusyId] = useState<number | null>(null);

  const load = async () => {
    const data = await api.listModels();
    setModels(data);
  };

  useEffect(() => {
    load().catch((e) => setError(e.message));
  }, []);

  const save = async () => {
    try {
      setSaving(true);
      setError("");
      setSuccess("");
      const parsed = JSON.parse(schema);
      await api.createModel(name, parsed);
      setSuccess("Modell gespeichert.");
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Fehler");
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (m: ModelDefinition) => {
    setEditingId(m.id);
    setEditName(m.name);
    setEditSchema(JSON.stringify(m.json_schema, null, 2));
    setError("");
    setSuccess("");
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditName("");
    setEditSchema("");
  };

  const saveEdit = async (id: number) => {
    try {
      setRowBusyId(id);
      setError("");
      setSuccess("");
      const parsed = JSON.parse(editSchema);
      await api.updateModel(id, editName, parsed);
      setSuccess(`Modell #${id} aktualisiert.`);
      cancelEdit();
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Aktualisierung fehlgeschlagen.");
    } finally {
      setRowBusyId(null);
    }
  };

  const removeModel = async (id: number) => {
    if (!window.confirm(`Modell #${id} wirklich loeschen?`)) return;
    try {
      setRowBusyId(id);
      setError("");
      setSuccess("");
      await api.deleteModel(id);
      setSuccess(`Modell #${id} geloescht.`);
      if (editingId === id) cancelEdit();
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Loeschen fehlgeschlagen.");
    } finally {
      setRowBusyId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <h2 className="text-xl font-semibold">Neues Modell</h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Schema als gueltiges JSON eingeben und speichern.</p>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="mt-3 w-full rounded-lg border border-slate-300 bg-white p-2 dark:border-slate-600 dark:bg-slate-900"
          placeholder="Modellname"
        />
        <textarea
          value={schema}
          onChange={(e) => setSchema(e.target.value)}
          rows={12}
          className="mt-3 w-full rounded-lg border border-slate-300 bg-white p-2 font-mono text-sm dark:border-slate-600 dark:bg-slate-900"
        />
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            onClick={save}
            disabled={saving}
            className="rounded-lg bg-slate-900 px-4 py-2 text-white disabled:cursor-not-allowed disabled:opacity-50 dark:bg-slate-100 dark:text-slate-900"
          >
            {saving ? "Speichere..." : "Modell speichern"}
          </button>
          <button
            onClick={() => setSchema(JSON.stringify(defaultSchema, null, 2))}
            className="rounded-lg border border-slate-300 px-4 py-2 text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
          >
            Vorlage laden
          </button>
          <button
            onClick={() => {
              try {
                setSchema(JSON.stringify(JSON.parse(schema), null, 2));
                setError("");
              } catch {
                setError("JSON ist nicht valide und konnte nicht formatiert werden.");
              }
            }}
            className="rounded-lg border border-slate-300 px-4 py-2 text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
          >
            JSON formatieren
          </button>
        </div>
        {success && <p className="mt-2 text-sm text-emerald-700">{success}</p>}
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <h2 className="text-xl font-semibold">Modelle</h2>
        {models.length === 0 && <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">Noch keine Modelle vorhanden.</p>}
        <ul className="mt-3 space-y-3 text-sm">
          {models.map((m) => {
            const isEditing = editingId === m.id;
            const isBusy = rowBusyId === m.id;

            return (
              <li key={m.id} className="rounded border border-slate-200 p-3 dark:border-slate-700">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <div className="font-medium">Modell #{m.id}</div>
                    <div className="text-xs text-slate-500 dark:text-slate-400">{new Date(m.created_at).toLocaleString()}</div>
                  </div>
                  <div className="flex gap-2">
                    {!isEditing && (
                      <button
                        onClick={() => startEdit(m)}
                        className="rounded-lg border border-slate-300 px-3 py-1.5 text-xs hover:bg-slate-50 dark:border-slate-600 dark:hover:bg-slate-700"
                      >
                        Bearbeiten
                      </button>
                    )}
                    <button
                      onClick={() => removeModel(m.id)}
                      disabled={isBusy}
                      className="rounded-lg border border-rose-300 px-3 py-1.5 text-xs text-rose-700 hover:bg-rose-50 disabled:opacity-50 dark:border-rose-700 dark:text-rose-300 dark:hover:bg-rose-900/30"
                    >
                      Loeschen
                    </button>
                  </div>
                </div>

                {isEditing ? (
                  <div className="mt-3 space-y-2">
                    <input
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      className="w-full rounded-lg border border-slate-300 bg-white p-2 dark:border-slate-600 dark:bg-slate-900"
                      placeholder="Modellname"
                    />
                    <textarea
                      value={editSchema}
                      onChange={(e) => setEditSchema(e.target.value)}
                      rows={10}
                      className="w-full rounded-lg border border-slate-300 bg-white p-2 font-mono text-sm dark:border-slate-600 dark:bg-slate-900"
                    />
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => saveEdit(m.id)}
                        disabled={isBusy}
                        className="rounded-lg bg-slate-900 px-3 py-2 text-xs text-white disabled:opacity-50 dark:bg-slate-100 dark:text-slate-900"
                      >
                        {isBusy ? "Speichere..." : "Aenderungen speichern"}
                      </button>
                      <button
                        onClick={cancelEdit}
                        className="rounded-lg border border-slate-300 px-3 py-2 text-xs hover:bg-slate-50 dark:border-slate-600 dark:hover:bg-slate-700"
                      >
                        Abbrechen
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="mt-2 font-medium">{m.name}</div>
                    <pre className="mt-2 overflow-auto rounded bg-slate-50 p-2 dark:bg-slate-900">{JSON.stringify(m.json_schema, null, 2)}</pre>
                  </>
                )}
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
