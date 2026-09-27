import fs from "node:fs";
import path from "node:path";

const siteRoot = path.resolve(import.meta.dirname, "..");
const repoRoot = path.resolve(siteRoot, "..");
const lessonsSource = path.join(repoRoot, "lessons");
const lessonsTarget = path.join(siteRoot, "public", "lessons");
const publishedFiles = ["lesson.mp4", "poster.jpg"];

function syncLesson(folder) {
  const source = path.join(lessonsSource, folder);
  const target = path.join(lessonsTarget, folder);
  fs.mkdirSync(target, { recursive: true });
  for (const file of publishedFiles) {
    const from = path.join(source, file);
    if (fs.existsSync(from)) fs.copyFileSync(from, path.join(target, file));
  }
  const figures = path.join(source, "figures");
  if (fs.existsSync(figures)) fs.cpSync(figures, path.join(target, "figures"), { recursive: true });
}

function writePaletteCss() {
  const palette = JSON.parse(fs.readFileSync(path.join(repoRoot, "engine", "palette.json"), "utf8"));
  const lines = Object.entries(palette).map(([name, hex]) => `  --palette-${name.replaceAll("_", "-")}: ${hex};`);
  const css = `/* Generated from engine/palette.json by scripts/sync-media.mjs */\n:root {\n${lines.join("\n")}\n}\n`;
  fs.writeFileSync(path.join(siteRoot, "src", "app", "palette.generated.css"), css);
  const ts = `// Generated from engine/palette.json by scripts/sync-media.mjs\nexport const palette = ${JSON.stringify(palette, null, 2)} as const;\n`;
  fs.writeFileSync(path.join(siteRoot, "src", "lib", "palette.generated.ts"), ts);
}

fs.rmSync(lessonsTarget, { recursive: true, force: true });
for (const folder of fs.readdirSync(lessonsSource)) {
  if (fs.existsSync(path.join(lessonsSource, folder, "lesson.mp4"))) syncLesson(folder);
}
writePaletteCss();
