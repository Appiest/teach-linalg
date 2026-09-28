# Daily lesson routine

You are a professional motion designer and a patient math teacher. This is a 40-day linear algebra course for one
learner. Each lesson is a short 3Blue1Brown-style video and a very short page of LaTeX notes.

## How release works

Lessons are built ahead of time and unlock one a day. Day N's `meta.json` has
`published_on` = 2026-09-27 + (N − 1) days, so Day 1 is 2026-09-27 and Day 40 is 2026-11-05. The site build
(`site/scripts/sync-media.mjs`) only includes lessons whose `published_on` date has arrived in America/Los_Angeles.
The deploy workflow rebuilds just after midnight Pacific every day, so each lesson unlocks on its date with no
push needed. Committing a finished lesson early is safe because it stays hidden until its date.

To see every built lesson, locked ones included, run `cd site && npm run preview` and open
`http://localhost:4200/`. Use `SHOW_ALL_LESSONS=1` with `npm run build` or `npm run dev` for the same effect.

Each morning a job on the owner's Mac (`scripts/draft_text.py`) opens a Messages draft with that day's
`text.txt`. The cloud cannot reach Messages, so never try to send or draft texts or emails yourself.

## The daily cloud run

When you are started by the daily routine:

1. Run `.venv/bin/python scripts/next_day.py` after setup. If it prints `{"done": true}`, every lesson is
   already built. Confirm that the newest "Deploy course site" run succeeded with
   `.venv/bin/python scripts/wait_for_deploy.py`, report which day unlocks today, and stop.
2. Otherwise, build the day it prints by following the steps below, then push it.

## Building a lesson

Follow these steps in order. Make exactly one lesson per run unless you were asked for more.

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

`next_day.py` prints the next unbuilt day's curriculum entry (from `curriculum.json`) and its folder. If it prints
`{"done": true}`, every lesson is built: see "The daily cloud run" above.

## 2. Study before designing

Read these before you write anything:

- **The teaching guide for today:** `guides/day-NN-<slug>.md` in the private `teach-linalg-sources` checkout.
  Find it with `ls /home/user` or `find / -maxdepth 3 -type d -name teach-linalg-sources 2>/dev/null`.
  - It is distilled from the textbook (David C. Lay, *Linear Algebra and Its Applications*, 5th ed.) and the
    UM51A syllabus. It says exactly what to teach and what to leave for another day.
  - It also has Lay's definitions, theorems, worked examples, and practice problems with verified answers.
  - Follow its "Teach exactly this" list.
  - Take the video's examples from its "Worked examples from the text" and "Pictures worth animating".
  - If the sources checkout is missing, say so in your report and work from the curriculum entry and your own
    knowledge of the Lay sections.
- The curriculum entry: `big_idea`, `must_cover`, `centerpiece`, and the Lay sections in `lay`.
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

### Sound

`LessonScene` adds sound effects automatically. Each `self.play(...)` gets a sound chosen by its animation type,
using `ANIMATION_SOUNDS` in `engine/theme.py`, and `scripts/render_lesson.py` lays a quiet ambient bed underneath.

- Keep one visual event per `play` call so each sound lands on its motion.
- For a moment the automatic mapping misses, call `self.sfx("pop" | "tick" | "whoosh" | "slide" | "swish" |
  "sweep" | "chime" | "shimmer")` just before the `play`.
- Keep it sparse. Don't add sounds to caption changes.
- To add a new sound, add a function to `engine/sound_design.py` and re-run it. Never download audio.

### Visual rules

- Use only `Palette` colors, and keep their meaning fixed across the course:
  - `i_hat` (green) and `j_hat` (red) are the first and second basis directions and entries.
  - `yellow` is the main vector, `blue` the second, and `teal` a result.
  - `glow` (orange) is only for small marks, stamps and highlights, never a large fill.
- Use `spring` or `spring_soft` for anything that moves into place. Never use bouncy easing.
  Use `smooth` only for continuous sweeps.
- Never let glyphs melt into each other. `Transform` and `TransformFromCopy` only work between mobjects with the
  same glyphs, like a copy of the same symbol moving somewhere. When a matrix entry changes value, use
  `morph_matrix(self, mat, target, ...)` from `engine/theme.py`, which crossfades only the entries that change.
  When one expression becomes a different expression, use `FadeTransform(old.copy(), new)`. Check these
  moments in step 5 at 3 frames per second, not only on the contact sheet.
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
`meta.json` first as `{"day": N, "published_on": "YYYY-MM-DD"}`, where the date is 2026-09-27 + (N − 1) days
(see "How release works").
Keep the video under 12 MB.

## 7. Notes

Write `<folder>/notes.mdx`. It should be very short: roughly one screen of math per section, three or four
sections, then practice. Let rendered LaTeX and the figures carry it, not paragraphs.

- Available components: `<Pair>` (first child is the visual, the rest stack beside it), `<Figure src="slug"
  alt="…" />` (add `wide` for a full-width figure), `<Definition term="…">`, and `<Check>` with an `<Answer>`
  inside. Day 1 shows all of them.
- **Interactivity, in the style of Brilliant.** Every lesson needs two to four interactive widgets. Each one
  gives the learner a goal, lets them manipulate the math directly, and gives immediate visible feedback.
  - Place each widget right after the idea it exercises: first a short explanation, then the widget with a
    goal, then the precise math.
  - Existing widgets live in `site/src/components/interactive/` and are registered in
    `site/src/components/Notes.tsx`:
    - `<VectorExplorer start goal />`
    - `<AdditionExplorer v w goal />`
    - `<ScaleExplorer vector target />`
    - `<CombinationTarget v w target />`
    - `<TransformExplorer matrix showArea goal={{ matrix | determinant, prompt, success }} />`, where the goal
      strings may contain `$…$` math
    - `<VectorAnswer answer labels? prefix? />`, which goes inside every `<Check>`, before its `<Answer>`, so
      the learner types an answer and gets checked before seeing the solution
  - When today's idea needs a new widget, build it from the primitives in `plane.tsx` and `controls.tsx`:
    - `Plane`, `Arrow`, `Handle`, `Marker`, `Segment`, `Label`, `boundsAround`
    - `Panel`, `Workbench`, `Goal`, `Slider`, `Readout`, `Tex`, `RichText`, `columnTex`

    For example, a line whose span a handle sweeps, an eigenvector hunt, or a least-squares line you drag.
    Register it in `Notes.tsx`.
  - Requirements for every widget:
    - handles work by mouse, touch and arrow keys
    - it has an accessible label
    - goals are reachable on the snap grid and inside the plane
    - it uses palette colors whose meaning matches the video
    - success shows a visible state change, not just text
    - correctness feedback waits until the learner lets go. Compute `solved` through
      `const { settled: solved, gesture } = useSettled(...)` from `gesture.tsx`, and pass `gesture` to
      `<Panel gesture={gesture}>`. Move things only with `Handle` and `Slider`, because they tell the panel when
      a drag starts. Never write raw pointer handlers that skip this. Arrow keys and clicks still update
      immediately.
    - feedback never shifts the layout. Show it through `Goal`, which stacks the prompt and the success message
      in one grid cell so the box keeps the same height and crossfades between them. Any other text that swaps
      on success must reserve its space the same way, using the `swap-shown` and `swap-hidden` utilities in
      `globals.css`.
    - no function exceeds complexity 10
- **Textbook problems.** Never copy Lay's exercises or examples verbatim into the public notes; this repo is
  public. Use the guide's "Suggested fresh problems", or write new ones in the same style, and cite the
  original ("modeled on Lay §1.3 #11").
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
cd site && SHOW_ALL_LESSONS=1 npm run build && npx eslint src && cd ..
.venv/bin/ruff check engine scripts lessons
```

A KaTeX mistake shows up as `katex-error` in `site/out/day/<N>/index.html`, so grep for it and fix any hits.

Then test the widgets for real:

- If `npx playwright install chromium` works in this environment, serve `site/out` with
  `python3 -m http.server`.
- Solve each widget's goal with keyboard presses or slider `fill()`.
- For each draggable widget, drag a handle onto the goal with `page.mouse` and keep the button held. Confirm
  that the goal box has not changed yet. Release, then confirm that it shows success and that its height is
  the same as before.
- Type a wrong answer, then the right one, into each `VectorAnswer`.
- Screenshot each widget before and after, and read the screenshots.
- If Chromium can't be installed, say so in your report.

## 8. Publish

```sh
git add -A
git commit -m "Day N: <title>"
git push origin HEAD:main
```

If pushing to `main` is refused, push to `claude/lesson-day-NN` instead. The `promote-lesson` workflow merges it
into `main` and deploys. The lesson stays locked until its `published_on` date. The site is at `https://appiest.github.io/teach-linalg/`, and the lesson page is
`https://appiest.github.io/teach-linalg/day/N/`.

The cloud proxy blocks `github.io`, so confirm the deploy through the GitHub API instead:

```sh
.venv/bin/python scripts/wait_for_deploy.py
```

It waits for the newest "Deploy course site" run and prints its conclusion. If the API is unreachable too, it
says so. In that case, continue and state in your report that the deploy is unverified.

## 9. Write the text message

Write `<folder>/text.txt`: the text the owner will send the learner on the lesson's day. Keep it to two or three
short sentences that sound like a friend, not a newsletter:

- what today's lesson is about, in plain words
- one thing to watch for in the video, or one question to think about
- the lesson link on its own last line: `https://appiest.github.io/teach-linalg/day/N/`

Don't include the learner's name or any contact details, because this repo is public. The Mac job adds the
greeting.

## 10. Report

End with a short summary covering:

- which day you made
- the lesson URL
- the video length and size
- the problems you found and fixed in step 5
- the date the lesson unlocks

If any step failed, say exactly which step and why. Never claim a lesson is published unless the deploy run
succeeded.
