import axios from "axios";

export const API = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  // was 20000; Gemini can take longer on first call / bigger outputs
  timeout: 90000, // 90s
});


// ---- Types ----
export type ProjectType = "Mechanical" | "Electrical" | "Civil" | "Software" | "Other";

export interface GenerateReq {
  projectName: string;
  projectType: ProjectType;
  description: string;
  tone?: "formal" | "concise";
  level?: "high" | "detailed";
}

export async function generateRequirements(payload: GenerateReq) {
  const { data } = await API.post("/generate", payload);
  return data; // { project_name, summary, categories, requirements, generated_at }
}
