# E2E Tests with Playwright

This directory contains end-to-end tests using Playwright.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Install browsers:
```bash
npx playwright install
```

## Running Tests

- List tests: `npx playwright test --list`
- Run all tests: `npx playwright test`
- Run with UI: `npx playwright test --ui`
- Run in headed mode: `npx playwright test --headed`
- Run specific browser: `npx playwright test --project=chromium`

## Test Structure

- `basic.spec.js` - Basic functionality tests
- Tests run against multiple browsers and mobile devices
- Web server starts automatically on port 3000

## Configuration

See `playwright.config.js` for full configuration including:
- Browser projects (Chrome, Firefox, Safari, Mobile)
- Test timeouts and retries
- Screenshot and video capture on failure
- HTML and JSON reporting
