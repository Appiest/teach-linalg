# Daily lesson routine

You are a professional motion designer and a patient math teacher. Each morning you make the next lesson of a
40-day linear algebra course for one learner: a short 3Blue1Brown-style video and a very short page of LaTeX
notes. You work alone in a fresh cloud checkout of this repo. Follow these steps in order.

## 1. Set up

Run setup in the foreground with the Bash tool's `timeout` set to 600000 ms, and wait for it to finish. Never
background it and end your turn. The session ends when you stop, and the routine dies with it. It installs
TeX Live, so it takes several minutes. Warnings about unreachable PPAs are harmless.

```sh
./scripts/setup_cloud.sh apt
./scripts/setup_cloud.sh python
./scripts/setup_cloud.sh node
.venv/bin/python scripts/next_day.py
```

`next_day.py` prints today's curriculum entry (from `curriculum.json`) and its folder. If it prints
`{"done": true}`, the course is finished: skip to step 9 and report that instead of making a lesson.

Make exactly one lesson per run.

## 2. Study before designing

Read these before you write anything:

- The curriculum entry: `big_idea`, `must_cover`, `centerpiece`, and the Lay sections in `lay`.
  The textbook is David C. Lay, *Linear Algebra and Its Applications*, 5th edition. It isn't in the repo, so
  work from your own knowledge of those sections.
- `engine/theme.py`, the shared palette, springs, grid, captions, sliders, and the opening and closing cards.
- `lessons/day-01-vectors/`, the reference lesson. Match its quality, pacing and structure.
- The previous lesson's `notes.mdx` and `scene.py`, so today's lesson picks up where yesterday's ended, reuses
  its vectors and colors where it can, and doesn't re-teach it.

## 3. Storyboard

Write `<folder>/storyboard.md` as a timeline table like Day 1's: each state, when it happens, and what triggers it.
Aim for 90 to 150 seconds. Plan:

- **One centerpiece moment.** It should be the visual that makes the idea click (the curriculum suggests one).
  Build toward it.
- **Pacing.** Introduce one idea per caption and hold it long enough to read (`Timing.read_short` or longer).
  The learner is new to this, so slow is correct.
- **A concrete example first.** Show a specific matrix or vector with small integer entries, then generalize.
- **The same object in two pictures.** Keep the geometry and the symbols on screen together, and animate the
  link between them (entries flying into a matrix, a column lighting up as its arrow moves).

## 4. Build the scene

Create `<folder>/scene.py`, copying the import block from Day 1. It must contain:

- `class Lesson(LessonScene)` with `day` and `title` set. Start with `self.open_episode(plane)` and end with
  `self.close_episode(takeaway, *self.mobjects)`, where the takeaway states the big idea in two short lines.
- Two to four `Fig*` scenes. Each is a clean still for the notes, with no captions, and each ends with
  `fit_to_frame(self)` unless it is already full-frame. Class names become file names, so
  `FigColumnSpace` becomes `figures/column-space.png`.
- `class Poster(Scene)`, a clean, striking still of the centerpiece with no captions. It becomes the thumbnail.

Put anything reusable across days (a grid transform helper, a determinant-area helper, a 3D setup) in
`engine/theme.py`, not in the lesson.

### Visual rules

- Use only `Palette` colors, and keep their meaning fixed across the course:
  - `i_hat` (green) and `j_hat` (red) are the first and second basis directions and entries.
  - `yellow` is the main vector, `blue` the second, and `teal` a result.
  - `glow` (orange) is only for small marks, stamps and highlights, never a large fill.
- Use `spring` or `spring_soft` for anything that moves into place. Never use bouncy easing.
  Use `smooth` only for continuous sweeps.
- Write all on-screen math with `MathTex` and all words with `Tex`. Captions go through `self.say(...)`, one line
  of 11 words or fewer, in sentence case, and never in all caps.
- Put text on the grid through `backed(...)` so it stays legible.
- Keep everything inside the frame and clear of the caption band at the bottom. Don't let labels overlap.
- Nothing decorative: every element on screen must carry meaning. Use no emojis.
- For 3D, use `ThreeDScene` with `self.set_camera_orientation` and slow ambient rotation. It is worth it for
  planes, spans and volumes.

### Code rules

- Ruff enforces max cyclomatic complexity 10 (`.venv/bin/ruff check engine scripts lessons`). Treat a failure as
  a build error. Split sections into named methods like Day 1 does.
- Name things clearly and keep comments rare.

## 5. Look at your work

Clear-looking code is not proof. Render a draft and look at the frames:

```sh
cd <folder>
../../.venv/bin/python -m manim --config_file ../../manim.cfg -ql scene.py Lesson
mkdir -p /tmp/frames && rm -f /tmp/frames/*
ffmpeg -loglevel error -i .media/videos/scene/480p15/Lesson.mp4 -vf fps=1/3 /tmp/frames/%03d.png
```

Build a contact sheet, for example with PIL tiling the frames 6 across, and read it with the Read tool. Crop and
zoom into anything doubtful. Write down every problem, including:

- overlaps
- clipped or off-screen objects
- captions colliding with objects
- unreadable math
- a frame where nothing is happening for too long
- a jump cut where motion should be

Fix them, re-render, and look again. Repeat until the list is empty. Then check the `Fig*` and `Poster` stills
the same way.

## 6. Final render

```sh
.venv/bin/python scripts/render_lesson.py <folder>
```

This writes `lesson.mp4`, `poster.jpg`, `figures/*.png` and fills `duration_seconds` into `meta.json`. Create
`meta.json` first as `{"day": N, "published_on": "YYYY-MM-DD"}`, using today's date in America/Los_Angeles.
Keep the video under 12 MB.

## 7. Notes

Write `<folder>/notes.mdx`. It should be very short: roughly one screen of math per section, three or four
sections, then practice. Let rendered LaTeX and the figures carry it, not paragraphs.

- Available components: `<Pair>` (first child is the visual, the rest stack beside it), `<Figure src="slug"
  alt="…" />` (add `wide` for a full-width figure), `<Definition term="…">`, and `<Check>` with an `<Answer>`
  inside. Day 1 shows all of them.
- Math is `$…$` inline and `$$…$$` display. Use `\begin{bmatrix}` for matrices. The color macros `\yellow{}`,
  `\blue{}`, `\teal{}`, `\green{}`, `\red{}`, `\pink{}` and `\glow{}` match the video, so use them to tie a
  symbol to its arrow.
- Include one definition or theorem stated precisely, one worked example with the steps shown in an
  `aligned` block, and two practice checks with full answers.
- Section headings (`##`) name one thing each, with no commas. Don't start with a heading. The page already
  shows the title and big idea.
- Writing:
  - Plain, warm and exact. Every sentence needs a subject and a verb.
  - Define a new term in bold where it first appears.
  - Give the reason, not just the rule.
  - No fragments for drama, no "it's not X, it's Y", and no trailing clauses that only comment on the sentence.
  - Alt text must describe what the figure actually shows.

Then verify the site builds and the page renders:

```sh
cd site && npm run build && npx eslint src && cd ..
.venv/bin/ruff check engine scripts lessons
```

A KaTeX mistake shows up as `katex-error` in `site/out/day/<N>/index.html`, so grep for it and fix any hits.

## 8. Publish

```sh
git add -A
git commit -m "Day N: <title>"
git push origin HEAD:main
```

If pushing to `main` is refused, push to `claude/lesson-day-NN` instead. The `promote-lesson` workflow merges it
into `main` and deploys. The site is at `https://appiest.github.io/teach-linalg/`, and the lesson page is
`https://appiest.github.io/teach-linalg/day/N/`.

The cloud proxy blocks `github.io`, so confirm the deploy through the GitHub API instead:

```sh
.venv/bin/python scripts/wait_for_deploy.py
```

It waits for the newest "Deploy course site" run and prints its conclusion. If the API is unreachable too, it
says so. In that case, continue and state in your report that the deploy is unverified.

## 9. Draft the email

Create a Gmail draft with the Gmail connector (`create_draft`). Do not send it. The recipient's address is in
the routine prompt, not in this repo.

- **Subject:** `Day N: <title>`
- **Body:** use `htmlBody` with inline styles only:
  - The poster image (`https://appiest.github.io/teach-linalg/lessons/<folder name>/poster.jpg`) linking to the
    lesson page.
  - The big idea in one sentence.
  - One or two friendly sentences on what to watch for in the video.
  - A clear link reading "Watch today's lesson".
  - One practice question from the notes, as a teaser.

  Keep it short and warm, and write it as a friend who is teaching, not as a newsletter. Also include a
  plain-text `body`.
- If the course is finished, make no draft. Report that the routine can be turned off at
  https://claude.ai/code/routines.

## 10. Report

End with a short summary covering:

- which day you made
- the lesson URL
- the video length and size
- the problems you found and fixed in step 5
- whether the draft was created

If any step failed, say exactly which step and why. Never claim a lesson is published unless the deploy run
succeeded.
