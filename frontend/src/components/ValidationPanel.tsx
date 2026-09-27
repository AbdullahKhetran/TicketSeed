import type { ValidationReport } from "../types";

interface Props {
  validation: ValidationReport;
}

export function ValidationPanel({ validation }: Props) {
  if (validation.issues.length === 0) {
    return (
      <div className="flex items-center gap-2 text-green-700 bg-green-50 border border-green-200 rounded-md px-4 py-2 text-sm">
        <svg className="h-4 w-4 shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path
            fillRule="evenodd"
            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
            clipRule="evenodd"
          />
        </svg>
        All validation checks passed.
      </div>
    );
  }

  const errors = validation.issues.filter((i) => i.severity === "error");
  const warnings = validation.issues.filter((i) => i.severity === "warning");

  return (
    <div className="card overflow-hidden">
      <div
        className={`px-4 py-2 text-sm font-medium border-b border-border ${
          errors.length > 0
            ? "bg-red-50 text-red-700"
            : "bg-yellow-50 text-yellow-800"
        }`}
      >
        {errors.length > 0
          ? `${errors.length} error${errors.length > 1 ? "s" : ""} · ${warnings.length} warning${warnings.length !== 1 ? "s" : ""}`
          : `${warnings.length} warning${warnings.length !== 1 ? "s" : ""}`}
      </div>
      <ul className="divide-y divide-border">
        {validation.issues.map((issue, i) => (
          <li key={i} className="flex gap-3 px-4 py-2 text-sm">
            <span
              className={`mt-0.5 shrink-0 badge ${
                issue.severity === "error"
                  ? "badge-error"
                  : "badge-warning"
              }`}
            >
              {issue.target}
            </span>
            <span className="text-[#1f2328]">{issue.message}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
