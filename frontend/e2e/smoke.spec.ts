import { test, expect } from '@playwright/test'

const JD_TEXT = `
We are looking for a Senior Python Engineer to join our AI team.
Requirements:
- 5+ years of Python experience
- Experience with LLMs and LangChain
- Strong background in REST API design
- Experience with cloud platforms (AWS/GCP)
- Good communication skills for cross-team collaboration
`

const RESUME_TEXT = `
John Doe
Senior Software Engineer

Experience:
- 6 years of Python development
- Built RAG pipelines using LangChain and OpenAI
- Designed REST APIs serving 1M+ requests/day on AWS
- Led cross-functional team of 5 engineers

Skills: Python, FastAPI, LangChain, AWS, PostgreSQL
`

const RESUME_FILE = {
  name: 'john_doe.txt',
  mimeType: 'text/plain',
  buffer: Buffer.from(RESUME_TEXT),
}

test('smoke: full flow with real LLM', async ({ page }) => {
  await page.goto('/')

  // ── Initial state ───────────────────────────────────────────────────────
  await expect(page.getByText('No criteria yet')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Fill JD' })).toBeVisible()

  // ── JD flow ─────────────────────────────────────────────────────────────
  await page.getByRole('button', { name: 'Fill JD' }).click()
  await page.getByPlaceholder('Paste job description here').fill(JD_TEXT)
  await page.getByRole('button', { name: 'Analyze' }).click()

  await expect(page.getByText('Review Criteria')).toBeVisible()
  await page.getByPlaceholder(/Type 'approve'/).fill('approve')
  await page.getByRole('button', { name: 'Submit' }).click()

  await expect(page.getByText('Scoring Criteria')).toBeVisible()

  // ── Resume upload ────────────────────────────────────────────────────────
  await expect(page.getByRole('button', { name: 'Upload Resumes' })).toBeVisible()

  const fileChooserPromise = page.waitForEvent('filechooser')
  await page.getByRole('button', { name: 'Upload Resumes' }).click()
  const fileChooser = await fileChooserPromise
  await fileChooser.setFiles(RESUME_FILE)

  await expect(page.getByText('Resumes')).toBeVisible()
  await expect(page.getByText('john_doe.txt')).toBeVisible()

  // ── Feedback ─────────────────────────────────────────────────────────────
  await expect(page.getByPlaceholder(/Enter feedback/)).toBeVisible()
  await page.getByPlaceholder(/Enter feedback/).fill('Prioritize candidates with LangChain experience')
  await page.getByRole('button', { name: 'Send' }).click()

  // feedbackText is cleared on send; textarea re-enables when streaming is done
  await expect(page.getByPlaceholder(/Enter feedback/)).toBeEnabled()
})

test('smoke: session restore after JD approval', async ({ page }) => {
  await page.goto('/')

  // ── JD flow ─────────────────────────────────────────────────────────────
  await page.getByRole('button', { name: 'Fill JD' }).click()
  await page.getByPlaceholder('Paste job description here').fill(JD_TEXT)
  await page.getByRole('button', { name: 'Analyze' }).click()

  await expect(page.getByText('Review Criteria')).toBeVisible()
  await page.getByPlaceholder(/Type 'approve'/).fill('approve')
  await page.getByRole('button', { name: 'Submit' }).click()

  await expect(page.getByText('Scoring Criteria')).toBeVisible()

  // ── Reload and verify session is restored from backend ──────────────────
  await page.reload()

  await expect(page.getByText('Scoring Criteria')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Upload Resumes' })).toBeVisible()
})
