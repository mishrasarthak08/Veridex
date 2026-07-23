const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export async function submitGoal(goal: string) {
  const response = await fetch(`${API_BASE_URL}/agents/goal`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // 'Authorization': `Bearer YOUR_TOKEN` // add auth later if needed
    },
    body: JSON.stringify({ goal }),
  });

  if (!response.ok) {
    throw new Error(`Failed to submit goal: ${response.statusText}`);
  }

  return response.json();
}

export function getTimelineUrl() {
  return `${API_BASE_URL}/agents/timeline`;
}

export async function fetchGraph() {
  const response = await fetch(`${API_BASE_URL}/knowledge/graph`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch graph: ${response.statusText}`);
  }

  return response.json();
}

export async function submitApproval(taskId: string, action: "approve" | "reject", feedback?: string) {
  const res = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}/approval`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, feedback })
  });
  if (!res.ok) throw new Error("Approval failed");
  return res.json();
}

const getToken = () => typeof window !== "undefined" ? localStorage.getItem("token") : null;

const headersWithAuth = () => {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
};

export async function getCurrentUser() {
  const res = await fetch(`http://localhost:8000/api/v1/auth/me`, {
    method: "GET",
    headers: headersWithAuth()
  });
  if (!res.ok) throw new Error("Failed to fetch user");
  const data = await res.json();
  return data.data; // Note: SuccessResponse wraps in data
}

export async function fetchTelemetry() {
  const res = await fetch(`http://localhost:8000/api/v1/telemetry/`, {
    method: "GET",
    headers: headersWithAuth()
  });
  if (!res.ok) throw new Error("Failed to fetch telemetry");
  return res.json();
}

export async function triggerSync(connectorType: string, config: any) {
  const res = await fetch(`http://localhost:8000/api/v1/knowledge/sync`, {
    method: "POST",
    headers: headersWithAuth(),
    body: JSON.stringify({ connector_type: connectorType, config })
  });
  if (!res.ok) throw new Error("Failed to trigger sync");
  return res.json();
}
