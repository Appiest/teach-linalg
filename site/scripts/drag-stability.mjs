import { chromium } from "playwright";
// Usage: node scripts/drag-stability.mjs <firstDay> <lastDay> [viewportWidth] [baseUrl]
// Drags every slider and handle with the mouse held and fails if any control, plane or goal box moves or resizes.
const [from, to, width = "1280", base = "http://localhost:4300"] = process.argv.slice(2);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: Number(width), height: 900 } });
const snapshot = (i) => page.evaluate((i) => {
  const panel = document.querySelectorAll("div.not-prose")[i];
  const top = panel.getBoundingClientRect().top;
  const rel = (el) => Math.round((el.getBoundingClientRect().top - top) * 10) / 10;
  const goal = panel.querySelector("[aria-live]");
  return {
    height: Math.round(panel.getBoundingClientRect().height * 10) / 10,
    goal: goal ? Math.round(goal.getBoundingClientRect().height) : 0,
    ys: [...panel.querySelectorAll('input[type="range"], svg[role=group]')].map(rel),
  };
}, i);
const moved = (a, b) => Math.max(Math.abs(a.goal - b.goal), ...a.ys.map((y, i) => Math.abs(y - b.ys[i])), 0);
let problems = 0;
for (let d = Number(from); d <= Number(to); d++) {
  await page.goto(`${base}/day/${d}/`, { waitUntil: "networkidle" });
  const panels = page.locator("div.not-prose");
  for (let p = 0; p < await panels.count(); p++) {
    const panel = panels.nth(p);
    const controls = panel.locator('input[type="range"], g[role="slider"] circle:last-of-type');
    const n = await controls.count();
    if (!n) continue;
    for (let c = 0; c < n; c++) {
      await panel.scrollIntoViewIfNeeded();
      const control = controls.nth(c);
      const box = await control.boundingBox();
      if (!box) continue;
      const isRange = (await control.evaluate((el) => el.tagName)) === "INPUT";
      let start, path;
      if (isRange) {
        const frac = await control.evaluate((el) => (el.value - el.min) / (el.max - el.min));
        start = [box.x + 8 + frac * (box.width - 16), box.y + box.height / 2];
        path = [...Array(12)].map((_, k) => [box.x + (box.width * k) / 11, start[1]]).concat([...Array(12)].map((_, k) => [box.x + box.width - (box.width * k) / 11, start[1]]));
      } else {
        start = [box.x + box.width / 2, box.y + box.height / 2];
        path = [[-60, 0], [-60, -60], [0, -60], [60, -60], [60, 0], [60, 60], [0, 60], [-60, 60], [0, 0]].map(([dx, dy]) => [start[0] + dx, start[1] + dy]);
      }
      const base = await snapshot(p);
      await page.mouse.move(...start);
      await page.mouse.down();
      let worst = 0;
      for (const point of path) {
        await page.mouse.move(...point, { steps: 3 });
        worst = Math.max(worst, moved(base, await snapshot(p)));
      }
      await page.mouse.up();
      if (worst > 1.5) { problems++; console.log(`day ${d} panel ${p} ${isRange ? "slider" : "handle"} ${c}: moved ${worst}px while dragging (width ${width})`); }
    }
  }
}
console.log(`done ${from}-${to} @${width}: ${problems} problems`);
await browser.close();
process.exit(problems ? 1 : 0);
