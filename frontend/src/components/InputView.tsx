/**
 * InputView — View 1
 * Drag-and-drop / paste area for the PRD markdown, rendered preview,
 * and the "Generate sprint plan" button.
 */

import { useCallback, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Spinner } from "./Spinner";

interface Props {
  onGenerate: (prd: string) => Promise<void>;
  loading: boolean;
  error: string | null;
}

const MAX_CHARS = 30_000;

export function InputView({ onGenerate, loading, error }: Props) {
  const [prd, setPrd] = useState("");
  const [dragging, setDragging] = useState(false);
  const [tab, setTab] = useState<"edit" | "preview">("edit");
  const fileRef = useRef<HTMLInputElement>(null);

  const readFile = (file: File) => {
    if (!file.name.endsWith(".md") && file.type !== "text/markdown") {
      alert("Please upload a .md file.");
      return;
    }
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      setPrd(text.slice(0, MAX_CHARS));
    };
    reader.readAsText(file);
  };

  const onDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setDragging(false);
      const file = e.dataTransfer.files[0];
      if (file) readFile(file);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const handleSubmit = () => {
    const trimmed = prd.trim();
    if (!trimmed) return;
    onGenerate(trimmed);
  };

  const charCount = prd.length;
  const overLimit = charCount > MAX_CHARS;

  return (
    <div className="max-w-3xl mx-auto px-4 py-12 flex flex-col gap-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-[#1f2328]">TicketSeed</h1>
        <p className="text-muted text-sm mt-1">
          Paste or drop a client PRD to generate a sprint plan and developer-ready tickets.
        </p>
      </div>

      {/* Drop zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => fileRef.current?.click()}
        className={`border-2 border-dashed rounded-lg px-6 py-8 text-center cursor-pointer transition-colors select-none ${
          dragging
            ? "border-accent bg-blue-50"
            : "border-border hover:border-accent/60 hover:bg-surface"
        }`}
      >
        <input
          ref={fileRef}
          type="file"
          accept=".md"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) readFile(file);
            e.target.value = "";
          }}
        />
        <svg
          className="mx-auto mb-2 h-8 w-8 text-muted"
          fill="none"
          stroke="currentColor"
          strokeWidth={1.5}
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
          />
        </svg>
        <p className="text-sm text-muted">
          Drop a <code className="font-mono bg-gray-100 px-1 rounded">.md</code> file here, or click to browse
        </p>
      </div>

      {/* Tabs: Edit / Preview */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-1 border-b border-border pb-0">
          {(["edit", "preview"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-1.5 text-sm font-medium rounded-t transition-colors capitalize ${
                tab === t
                  ? "border border-border border-b-white bg-white text-[#1f2328] -mb-px"
                  : "text-muted hover:text-[#1f2328]"
              }`}
            >
              {t}
            </button>
          ))}
          <span className={`ml-auto text-xs ${overLimit ? "text-red-500 font-medium" : "text-muted"}`}>
            {charCount.toLocaleString()} / {MAX_CHARS.toLocaleString()} chars
          </span>
        </div>

        {tab === "edit" ? (
          <textarea
            className="input-field resize-y min-h-[280px] font-mono text-xs leading-relaxed"
            placeholder="Paste your PRD markdown here…"
            value={prd}
            onChange={(e) => setPrd(e.target.value.slice(0, MAX_CHARS))}
          />
        ) : (
          <div className="border border-border rounded-md p-4 min-h-[280px] prose prose-sm max-w-none overflow-auto">
            {prd.trim() ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{prd}</ReactMarkdown>
            ) : (
              <p className="text-muted italic text-sm">Nothing to preview yet.</p>
            )}
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-4 py-2">
          {error}
        </div>
      )}

      {/* Actions */}
      {loading ? (
        <Spinner label="Analysing PRD and generating sprint plan… this may take 20–40 seconds." />
      ) : (
        <button
          className="btn-primary self-start"
          onClick={handleSubmit}
          disabled={!prd.trim() || overLimit}
        >
          Generate sprint plan →
        </button>
      )}
    </div>
  );
}
