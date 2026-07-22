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

export async function submitApproval(taskId: string, decision: 'approve' | 'reject' | 'revise') {
  const response = await fetch(`${API_BASE_URL}/agents/approve`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ task_id: taskId, decision }),
  });

  if (!response.ok) {
    throw new Error(`Failed to submit approval: ${response.statusText}`);
  }

  return response.json();
}
