import { useState } from "react";
import { useForm, type SubmitHandler } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { generateRequirements, exportRequirements } from "./lib/api";
import { saveAs } from "file-saver";

// Zod schema: make tone/level REQUIRED (no .default())
const schema = z.object({
  projectName: z.string().min(2, "Enter a valid name."),
  projectType: z.enum(["Mechanical", "Electrical", "Civil", "Software", "Other"]),
  description: z.string().min(10, "Min 10 characters."),
  tone: z.enum(["formal", "concise"]),
  level: z.enum(["high", "detailed"]),
});

type FormData = z.infer<typeof schema>;

export default function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      projectName: "",
      projectType: "Mechanical",
      description: "",
      tone: "formal",        // supply defaults here
      level: "detailed",     // and here
    },
  });

  const onSubmit: SubmitHandler<FormData> = async (vals) => {
    setLoading(true);
    setResult(null);
    try {
      const data = await generateRequirements(vals);
      setResult(data);
    } catch (e) {
      console.error(e);
      alert("Failed to generate. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: "pdf" | "docx" | "md") => {
    if (!result) return;
    try {
      const r = await exportRequirements(format, result);
      const type =
        format === "pdf"
          ? "application/pdf"
          : format === "docx"
          ? "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          : "text/markdown;charset=utf-8";
      saveAs(new Blob([r.data], { type }), `${result.project_name}.${format}`);
    } catch (e) {
      console.error(e);
      alert("Export failed. Check the backend /api/export endpoint.");
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <header className="bg-[var(--indigo)] text-white">
        <div className="mx-auto max-w-6xl px-6 py-10">
          <span className="text-[var(--green)] font-semibold">Mai</span>
          <h1 className="text-4xl md:text-5xl font-bold mt-3">
            AI-Assisted Technical Requirement Generator
          </h1>
          <p className="mt-3 opacity-90 max-w-2xl">
            Create comprehensive technical requirements for your engineering projects with AI.
          </p>
        </div>
      </header>

      {/* Body */}
      <main className="mx-auto max-w-6xl grid md:grid-cols-2 gap-8 px-6 py-10">
        {/* Form Card */}
        <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-2xl font-semibold mb-4">Project Details</h2>

          <label className="block text-sm mb-1">Project name</label>
          <input className="w-full rounded-xl border p-3 mb-2" {...register("projectName")} />
          {errors.projectName && <p className="text-red-600 text-sm mb-2">{errors.projectName.message}</p>}

          <label className="block text-sm mb-1">Project type</label>
          <select className="w-full rounded-xl border p-3 mb-2" {...register("projectType")}>
            {["Mechanical", "Electrical", "Civil", "Software", "Other"].map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>

          <label className="block text-sm mb-1">Project description</label>
          <textarea rows={6} className="w-full rounded-xl border p-3 mb-2" {...register("description")} />
          {errors.description && <p className="text-red-600 text-sm mb-2">{errors.description.message}</p>}

          <div className="grid grid-cols-2 gap-3 mb-4">
            <div>
              <label className="block text-sm mb-1">Tone</label>
              <select className="w-full rounded-xl border p-3" {...register("tone")}>
                <option value="formal">formal</option>
                <option value="concise">concise</option>
              </select>
            </div>
            <div>
              <label className="block text-sm mb-1">Detail level</label>
              <select className="w-full rounded-xl border p-3" {...register("level")}>
                <option value="detailed">detailed</option>
                <option value="high">high</option>
              </select>
            </div>
          </div>

          <button
            className="w-full rounded-xl py-3 font-semibold text-[var(--indigo)] bg-[var(--blue)]/90 hover:bg-[var(--blue)] transition"
            disabled={loading}
          >
            {loading ? "Generating..." : "Generate Requirements"}
          </button>
        </form>

        {/* Results Card */}
        <section className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-2xl font-semibold mb-4">Generated Requirements</h2>
          {!result && <p className="opacity-70">Results will appear here after you generate.</p>}

          {result && (
            <>
              {/* Export buttons */}
              <div className="flex flex-wrap gap-3 mb-4">
                <button
                  type="button"
                  className="rounded-lg px-3 py-2 text-sm bg-[var(--blue)]/90 hover:bg-[var(--blue)]"
                  onClick={() => handleExport("pdf")}
                >
                  Export PDF
                </button>
                <button
                  type="button"
                  className="rounded-lg px-3 py-2 text-sm bg-[var(--blue)]/90 hover:bg-[var(--blue)]"
                  onClick={() => handleExport("docx")}
                >
                  Export DOCX
                </button>
                <button
                  type="button"
                  className="rounded-lg px-3 py-2 text-sm bg-[var(--blue)]/90 hover:bg-[var(--blue)]"
                  onClick={() => handleExport("md")}
                >
                  Export Markdown
                </button>
              </div>

              <div className="text-sm opacity-80 mb-4">{result.summary}</div>
              {result.categories?.map((c: string) => (
                <div key={c} className="mb-6">
                  <h3 className="font-semibold text-lg">{c}</h3>
                  <ul className="mt-2 space-y-3">
                    {result.requirements
                      .filter((r: any) => r.category === c)
                      .map((r: any, idx: number) => (
                        <li key={idx} className="border rounded-xl p-3">
                          <div className="text-sm">
                            <span className="px-2 py-0.5 rounded bg-[var(--green)]/60 mr-2">{r.priority}</span>
                            {r.text}
                          </div>
                          {r.acceptance_criteria?.length > 0 && (
                            <ul className="list-disc ml-6 mt-2 text-sm opacity-90">
                              {r.acceptance_criteria.map((a: string, i: number) => (
                                <li key={i}>{a}</li>
                              ))}
                            </ul>
                          )}
                          {r.rationale && (
                            <p className="text-xs mt-2 opacity-80">
                              <em>Rationale:</em> {r.rationale}
                            </p>
                          )}
                          {r.standard_refs?.length > 0 && (
                            <p className="text-xs mt-1 opacity-80">
                              <em>Standards:</em> {r.standard_refs.join(", ")}
                            </p>
                          )}
                        </li>
                      ))}
                  </ul>
                </div>
              ))}
            </>
          )}
        </section>
      </main>
    </div>
  );
}
