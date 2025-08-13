import axios from "axios";

// Use env when provided; default to /api (works in Docker/Nginx)
const baseURL =
  (import.meta as any).env?.VITE_API_BASE?.trim() ||
  "/api";

export const API = axios.create({
  baseURL,
  timeout: 90_000, // 90s
});

// ---- Types ----
export type ProjectType = "Mechanical" | "Electrical" | "Civil" | "Software" | "Other";

export interface GenerateReq {
  projectName: string;
  projectType: "Mechanical" | "Electrical" | "Civil" | "Software" | "Other";
  description: string;
  tone: "formal" | "concise";
  level: "high" | "detailed";
}



export async function generateRequirements(payload: GenerateReq) {
  const { data } = await API.post("/generate", payload);
  return data; // { project_name, summary, categories, requirements, generated_at }
}

export async function exportRequirements(format: "pdf" | "docx" | "md", payload: any) {
  return API.post(`/export?format=${format}`, payload, { responseType: "blob" });
}
