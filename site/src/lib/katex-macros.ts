import fs from "node:fs";
import path from "node:path";

const palettePath = path.resolve(process.cwd(), "..", "engine", "palette.json");

const macroColors = {
  yellow: "yellow",
  blue: "blue",
  teal: "teal",
  pink: "pink",
  green: "i_hat",
  red: "j_hat",
  glow: "glow",
} as const;

export function katexMacros(): Record<string, string> {
  const palette = JSON.parse(fs.readFileSync(palettePath, "utf8")) as Record<string, string>;
  return Object.fromEntries(
    Object.entries(macroColors).map(([macro, key]) => [`\\${macro}`, `\\textcolor{#${palette[key]}}{#1}`]),
  );
}
