import { test, expect } from '@playwright/test';

test('Chaos Engineering Control Panel allows injecting chaos', async ({ page }) => {
  // Mock the API response
  await page.route('**/api/v1/resilience/chaos', async route => {
    const json = { status: "chaos_injected", mode: "503_error" };
    await route.fulfill({ json });
  });

  // Mock authentication to prevent redirect to login
  await page.route('**/api/v1/auth/me', async route => {
    await route.fulfill({ json: { id: "test", email: "test@example.com", first_name: "Test", last_name: "User" } });
  });

  await page.addInitScript(() => {
    // Create a fake JWT that doesn't expire
    const payload = btoa(JSON.stringify({ exp: Date.now() / 1000 + 3600, sub: 'test-user' }));
    localStorage.setItem('token', `header.${payload}.signature`);
  });

  await page.goto('/resilience');

  // Verify header
  await expect(page.getByRole('heading', { name: /Chaos Engineering Control Panel/i })).toBeVisible();

  // Click the simulate 503 outage button
  const simulateBtn = page.getByRole('button', { name: /Simulate 503 Outage/i });
  await expect(simulateBtn).toBeVisible();
  await simulateBtn.click({ force: true });

  // Verify toast appears (assuming toast renders text)
  await expect(page.getByText('Chaos injected: 503_error')).toBeVisible();
});
