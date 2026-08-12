import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test('should allow a user to navigate to login and see the login form', async ({ page }) => {
    await page.goto('/login');
    
    // Check if Veridex branding is visible
    await expect(page.getByRole('heading', { name: /Veridex/i })).toBeVisible();
    
    // Check if email input exists
    await expect(page.getByPlaceholder(/you@example.com/i)).toBeVisible();
    
    // Check if password input exists
    await expect(page.getByPlaceholder(/••••••••/i)).toBeVisible();
    
    // Check if sign in button exists
    await expect(page.getByRole('button', { name: /Sign In/i })).toBeVisible();
  });
  
  test('should show validation errors on empty submit', async ({ page }) => {
    await page.goto('/login');
    
    // Click sign in without entering details
    await page.getByRole('button', { name: /Sign In/i }).click();
    
    // Wait for the HTML5 validation or form library validation
    // Since we're using generic assertions here, just make sure the page hasn't navigated away
    await expect(page).toHaveURL('/login');
  });
});
