# COMP 163 Code Grader — static site

A single-page grading tool: manual rubric scoring + automatic concept flagging.
No backend, no API key, no server — the Python concept-checker runs **inside the
visitor's browser** via [Pyodide](https://pyodide.org) (a full CPython build compiled
to WebAssembly), so this deploys as plain static files.

## Files

```
netlify_grader/
  index.html            the entire app (HTML + CSS + JS)
  analyzer_source.py    the AST concept-detector, fetched and run in-browser by Pyodide
  netlify.toml           tells Netlify this is a static site, no build step
```

## How it works

- **Rubric** — build criteria (label + max points) once and save them by assignment name.
  Saved rubrics persist in the browser's `localStorage`, so they're there next time you
  open the page on the same device/browser.
- **Scoring** — entirely manual. You read the code, enter points awarded per criterion,
  the total computes itself. This tool doesn't judge correctness for you.
- **Concept flagging** — automatic. On page load, the browser downloads Pyodide (~10MB,
  cached after first visit) and your `analyzer_source.py`. When you click "Check
  concepts," it parses the pasted code's actual syntax tree and reports which concepts
  it uses, then flags anything not yet in your "known concepts" list as of the
  assignment date.
- **Known concepts** — also saved in `localStorage`, so you maintain the list once as
  the semester progresses rather than re-entering it per grading session.

## Deploying to Netlify

**Option A — drag and drop (fastest):**
1. Go to [app.netlify.com/drop](https://app.netlify.com/drop).
2. Drag the whole `netlify_grader` folder onto the page.
3. Netlify gives you a live URL immediately. Done.

**Option B — connect to GitHub (auto-redeploys on push):**
1. Push this folder to a GitHub repo.
2. In Netlify, "Add new site" → "Import an existing project" → pick the repo.
3. Build command: leave blank. Publish directory: `.` (or wherever this folder sits in
   your repo, e.g. `netlify_grader`).
4. Deploy.

## Important notes

- **Data lives in the browser, not the cloud.** Rubrics and concepts are saved via
  `localStorage`, which is per-browser, per-device. Grading on your laptop and your
  desktop means two separate concept/rubric lists unless you re-enter them on both.
  Clearing browser data wipes them too.
- **Nothing about a submission is saved.** Pasted code and entered scores are never
  written anywhere — refreshing the page clears them, by design.
- **First load is slower.** Pyodide is a real Python interpreter running in WebAssembly,
  so the first visit downloads a few megabytes before the "Check concepts" button
  enables. It's cached by the browser after that.
- **Extending the concept list**: edit `CONCEPT_DETECTORS` in `analyzer_source.py` the
  same way you would for the local command-line version — it's the identical logic,
  just running in the browser instead of your terminal.
