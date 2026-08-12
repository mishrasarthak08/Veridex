import { AgentsService, ChatService, KnowledgeService, AuthService, TelemetryService, EvaluationsService, ResilienceService } from "./api-client";
import { OpenAPI } from "./api-client";

import axios from "axios";

export const API_URL = process.env.NEXT_PUBLIC_API_URL?.replace('/api/v1', '') || "http://localhost:8000";
OpenAPI.BASE = API_URL;

export const getToken = () => typeof window !== "undefined" ? localStorage.getItem("token") : null;

// Initialize token on load
const token = getToken();
if (token) {
  OpenAPI.TOKEN = token;
}
// Global Axios Interceptor for Zero-Friction Networking
let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        })
          .then(token => {
            originalRequest.headers['Authorization'] = 'Bearer ' + token;
            return axios(originalRequest);
          })
          .catch(err => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // The refresh endpoint uses HttpOnly cookies to securely refresh
        const res = await axios.post(`${API_URL}/api/v1/auth/refresh`, {}, { withCredentials: true });
        const newToken = res.data.access_token;
        if (typeof window !== "undefined") {
          localStorage.setItem("token", newToken);
        }
        OpenAPI.TOKEN = newToken;
        originalRequest.headers['Authorization'] = 'Bearer ' + newToken;
        processQueue(null, newToken);
        return axios(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        if (typeof window !== "undefined") {
          localStorage.removeItem("token");
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

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
  return `${OpenAPI.BASE}/agents/timeline`;
}

export async function fetchChatHistory(threadId: string) {
  return await ChatService.getChatHistoryApiV1ChatHistoryThreadIdGet(threadId);
}

export async function fetchChatThreads() {
  const res = await ChatService.getChatThreadsApiV1ChatThreadsGet();
  return res;
}

export async function saveChatMessage(threadId: string, role: string, content: string, traces: any[] = []) {
  return await ChatService.addChatMessageApiV1ChatMessagePost({
    thread_id: threadId,
    role: role as any,
    content: content,
    traces: traces
  });
}

export async function fetchGraph() {
  return await KnowledgeService.getGraphDataApiV1KnowledgeGraphGet();
}

export async function submitApproval(taskId: string, action: "approve" | "reject", feedback?: string) {
  const res = await AgentsService.submitApprovalApiV1AgentsApprovePost({
      task_id: taskId,
      decision: action
  });
  return res;
}

export async function getCurrentUser() {
  const res = await AuthService.readUsersMeApiV1AuthMeGet();
  return res;
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
  const res = await EvaluationsService.triggerEvaluationApiV1EvaluationsRunPost();
  return res;
}

export async function runChaosTest() {
  const res = await ResilienceService.startChaosApiV1ResilienceChaosPost({ mode: "latency", duration_ms: 5000, probability: 1.0 });
  return res;
}

export async function fetchEvaluations() {
  return await EvaluationsService.listEvaluationsApiV1EvaluationsGet();
}
