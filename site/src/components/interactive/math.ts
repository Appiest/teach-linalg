export type Vec = [number, number];
export type Matrix2 = [[number, number], [number, number]];

export const add = (a: Vec, b: Vec): Vec => [a[0] + b[0], a[1] + b[1]];
export const scale = (c: number, v: Vec): Vec => [c * v[0], c * v[1]];
export const apply = (m: Matrix2, v: Vec): Vec => [m[0][0] * v[0] + m[0][1] * v[1], m[1][0] * v[0] + m[1][1] * v[1]];
export const det = (m: Matrix2): number => m[0][0] * m[1][1] - m[0][1] * m[1][0];
export const nearlyEqual = (a: Vec, b: Vec, tolerance = 1e-6) =>
  Math.abs(a[0] - b[0]) <= tolerance && Math.abs(a[1] - b[1]) <= tolerance;

export function formatNumber(value: number, digits = 2): string {
  const rounded = Math.round(value * 10 ** digits) / 10 ** digits;
  const text = Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(digits).replace(/0+$/, "");
  return text.replace("-", "−");
}

export function texNumber(value: number, digits = 2): string {
  return formatNumber(value, digits).replace("−", "-");
}
