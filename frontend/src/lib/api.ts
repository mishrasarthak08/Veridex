import { OpenAPI, AgentsService, ChatService, KnowledgeService, AuthService, TelemetryService, EvaluationsService, ResilienceService } from "../client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
OpenAPI.BASE = API_URL;

const getToken = () => typeof window !== "undefined" ? localStorage.getItem("token") : null;

OpenAPI.TOKEN = async () => {
  const token = getToken();
  return token || "";
};

export async function submitGoal(goal: string, threadId: string = "default") {
  // Save message to chat history
  const response = await ChatService.addChatMessageApiV1ChatMessagePost({
    thread_id: threadId,
    role: 'user',
    content: goal,
    traces: []
  });

  // Submit to orchestrator
  await AgentsService.submitGoalApiV1AgentsGoalPost({ goal });
  
  return response;
}

export function getTimelineUrl() {
  return `${OpenAPI.BASE}/api/v1/agents/timeline`;
}

export async function fetchChatHistory(threadId: string) {
  return await ChatService.getChatHistoryApiV1ChatHistoryThreadIdGet(threadId);
}

export async function fetchChatThreads() {
  const res = await fetch(`${OpenAPI.BASE}/api/v1/chat/threads`, {
    method: "GET",
    headers: { ...(getToken() ? { "Authorization": `Bearer ${getToken()}` } : {}) },
  });
  if (!res.ok) throw new Error("Failed to fetch chat threads");
  return res.json();
}

export async function saveChatMessage(threadId: string, role: string, content: string, traces: any[] = []) {
  return await ChatService.addChatMessageApiV1ChatMessagePost({
    thread_id: threadId,
    role: role,
    content: content,
    traces: traces
  });
}

export async function fetchGraph() {
  return await KnowledgeService.getGraphDataApiV1KnowledgeGraphGet();
}

export async function submitApproval(taskId: string, action: "approve" | "reject", feedback?: string) {
  // Using explicit fetch for non-openapi mapped routes, or mapping if available.
  // Wait, /tasks/{taskId}/approval might not be mapped since it was custom.
  // Let's use the explicit fetch since it might not be in the openapi schema correctly.
  const res = await fetch(`${OpenAPI.BASE}/api/v1/tasks/${taskId}/approval`, {
    method: "POST",
    headers: { 
      "Content-Type": "application/json",
      ...(getToken() ? { "Authorization": `Bearer ${getToken()}` } : {})
    },
    body: JSON.stringify({ action, feedback })
  });
  if (!res.ok) throw new Error("Approval failed");
  return res.json();
}

export async function getCurrentUser() {
  const res = await AuthService.readUsersMeApiV1AuthMeGet();
  return res.data;
}

export async function fetchTelemetry() {
  return await TelemetryService.getTelemetryLogsApiV1TelemetryGet();
}

export async function triggerSync(connectorType: string, config: any) {
  return await KnowledgeService.triggerSyncApiV1KnowledgeSyncPost({
    connector_type: connectorType,
    config: config
  });
}

export async function runEvaluations() {
  // fallback to fetch if method doesn't exist
  const res = await fetch(`${OpenAPI.BASE}/api/v1/evaluations/run`, {
    method: "POST",
    headers: { ...(getToken() ? { "Authorization": `Bearer ${getToken()}` } : {}) },
  });
  if (!res.ok) throw new Error("Evaluation run failed");
  return res.json();
}

export async function runChaosTest() {
  const res = await fetch(`${OpenAPI.BASE}/api/v1/resilience/chaos`, {
    method: "POST",
    headers: { ...(getToken() ? { "Authorization": `Bearer ${getToken()}` } : {}) },
  });
  if (!res.ok) throw new Error("Chaos run failed");
  return res.json();
}

export async function fetchEvaluations() {
  const res = await fetch(`${OpenAPI.BASE}/api/v1/evaluations/`, {
    method: "GET",
    headers: { ...(getToken() ? { "Authorization": `Bearer ${getToken()}` } : {}) },
  });
  if (!res.ok) throw new Error("Failed to fetch evaluations");
  return res.json();
}
