export type Hue = "yellow" | "blue" | "teal" | "pink" | "green" | "red" | "glow" | "text";

const variables: Record<Hue, string> = {
  yellow: "var(--palette-yellow)",
  blue: "var(--palette-blue)",
  teal: "var(--palette-teal)",
  pink: "var(--palette-pink)",
  green: "var(--palette-i-hat)",
  red: "var(--palette-j-hat)",
  glow: "var(--palette-glow)",
  text: "var(--palette-text)",
};

export const hue = (name: Hue) => variables[name];
