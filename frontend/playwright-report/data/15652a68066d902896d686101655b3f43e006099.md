# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: resilience.spec.ts >> Chaos Engineering Control Panel allows injecting chaos
- Location: tests/e2e/resilience.spec.ts:3:5

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('heading', { name: /Chaos Engineering Control Panel/i })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByRole('heading', { name: /Chaos Engineering Control Panel/i })

```

```yaml
- alert
- heading "Veridex" [level=1]
- heading "Welcome Back" [level=2]
- text: Email
- textbox "you@example.com"
- text: Password
- textbox "••••••••"
- button "Sign In"
- text: or login with
- button "GitHub":
  - img
  - text: GitHub
- button "Google":
  - img
  - text: Google
- paragraph:
  - text: Don't have an account?
  - link "Sign up":
    - /url: /register
- region "Notifications alt+T"
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test('Chaos Engineering Control Panel allows injecting chaos', async ({ page }) => {
  4  |   // Mock the API response
  5  |   await page.route('**/api/v1/resilience/chaos', async route => {
  6  |     const json = { status: "chaos_injected", mode: "503_error" };
  7  |     await route.fulfill({ json });
  8  |   });
  9  | 
  10 |   await page.goto('/resilience');
  11 | 
  12 |   // Verify header
> 13 |   await expect(page.getByRole('heading', { name: /Chaos Engineering Control Panel/i })).toBeVisible();
     |                                                                                         ^ Error: expect(locator).toBeVisible() failed
  14 | 
  15 |   // Click the simulate 503 outage button
  16 |   const simulateBtn = page.getByRole('button', { name: /Simulate 503 Outage/i });
  17 |   await expect(simulateBtn).toBeVisible();
  18 |   await simulateBtn.click({ force: true });
  19 | 
  20 |   // Verify toast appears (assuming toast renders text)
  21 |   await expect(page.getByText('Chaos injected: 503_error')).toBeVisible();
  22 | });
  23 | 
```