import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  timeout: 180_000,
  expect: {
    timeout: 90_000,   // controls toBeVisible() / toBeEnabled() etc.
  },
  use: {
    baseURL: 'http://localhost:5173',
    actionTimeout: 90_000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  // Both servers start in parallel. If already running, they are reused.
  // Requires .env at the project root with OPENAI_API_KEY and DATABASE_URL.
  webServer: [
    {
      command: 'uv run --env-file .env python scripts/run_server.py',
      url: 'http://localhost:8000/docs',
      cwd: '../',
      reuseExistingServer: true,
      timeout: 30_000,
    },
    {
      command: 'npm run dev',
      url: 'http://localhost:5173',
      reuseExistingServer: true,
    },
  ],
})
