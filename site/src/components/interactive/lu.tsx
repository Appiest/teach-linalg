"use client";

import { CheckCircle, Circle } from "@phosphor-icons/react";
import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { columnTex, Goal, Panel, Readout, RichText, Slider, Tex } from "./controls";
import { useSettled } from "./gesture";
import { formatNumber, texNumber } from "./math";

type Row3 = [number, number, number];
type Matrix3 = [Row3, Row3, Row3];

const EPSILON = 1e-9;
const isZero = (value: number) => Math.abs(value) < EPSILON;
const subtract = (row: Row3, other: Row3, factor: number): Row3 => [
  row[0] - factor * other[0],
  row[1] - factor * other[1],
  row[2] - factor * other[2],
];
const dot = (row: Row3, values: Row3) => row[0] * values[0] + row[1] * values[1] + row[2] * values[2];

const colored = (value: number, color: string) => `\\textcolor{${color}}{${texNumber(value)}}`;

function matrixTex(rows: Row3[], colorOf: (row: number, col: number) => string): string {
  const body = rows.map((row, r) => row.map((entry, c) => colored(entry, colorOf(r, c))).join(" & ")).join(" \\\\ ");
  return `\\begin{bmatrix} ${body} \\end{bmatrix}`;
}

type Multipliers = [number, number, number];

function eliminate(a: Matrix3, [l21, l31, l32]: Multipliers): Matrix3 {
  const second = subtract(a[1], a[0], l21);
  const third = subtract(subtract(a[2], a[0], l31), second, l32);
  return [a[0], second, third];
}

const BELOW: [number, number][] = [[1, 0], [2, 0], [2, 1]];

function isUpper(u: Matrix3): boolean {
  return BELOW.every(([r, c]) => isZero(u[r][c]));
}

function lowerTex([l21, l31, l32]: Multipliers): string {
  const rows: Row3[] = [[1, 0, 0], [l21, 1, 0], [l31, l32, 1]];
  return matrixTex(rows, (r, c) => (r > c ? palette.pink : r === c ? palette.text : palette.text_muted));
}

function upperColor(settled: Matrix3) {
  return (r: number, c: number) => {
    if (r <= c) return palette.text;
    return isZero(settled[r][c]) ? palette.teal : palette.glow;
  };
}

const multiplierKey = (values: Multipliers) => values.join(",");
const parseKey = (key: string) => key.split(",").map(Number) as Multipliers;

/** Elimination with slider multipliers: L fills with the multipliers while the working matrix becomes U. */
export function LUBuilder({ matrix }: { matrix: Matrix3 }) {
  const [multipliers, setMultipliers] = useState<Multipliers>([0, 0, 0]);
  const { settled: settledKey, gesture } = useSettled(multiplierKey(multipliers));
  const settledU = eliminate(matrix, parseKey(settledKey));
  const solved = isUpper(settledU);
  const current = eliminate(matrix, multipliers);
  const setAt = (index: number) => (value: number) =>
    setMultipliers((old) => old.map((entry, i) => (i === index ? value : entry)) as Multipliers);
  const sliders = [
    { tex: "R_2 \\leftarrow R_2 - \\ell_{21} R_1", label: "\\ell_{21}" },
    { tex: "R_3 \\leftarrow R_3 - \\ell_{31} R_1", label: "\\ell_{31}" },
    { tex: "R_3 \\leftarrow R_3 - \\ell_{32} R_2", label: "\\ell_{32}" },
  ];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Choose the three multipliers so every entry below the diagonal of <Tex>{"U"}</Tex> becomes 0. Clear column 1 first, then column 2.</>}
        success={<>That is an LU factorization. Each multiplier is the entry you cleared divided by the pivot above it, and multiplying <Tex>{"LU"}</Tex> gives back <Tex>{"A"}</Tex>.</>}
      />
      <div className="space-y-5">
        <div className="grid gap-4 md:grid-cols-3">
          {sliders.map((slider, index) => (
            <div key={slider.label} className="space-y-1.5">
              <div className="text-meta text-text-muted">
                <Tex>{slider.tex}</Tex>
              </div>
              <Slider label={slider.label} value={multipliers[index]} onChange={setAt(index)} min={-4} max={4} step={0.5} color={palette.pink} />
            </div>
          ))}
        </div>
        <div className="grid min-w-0 gap-3 sm:grid-cols-3">
          <Readout tex={`A = ${matrixTex(matrix, () => palette.text)}`} />
          <Readout tex={`L = ${lowerTex(multipliers)}`} />
          <Readout tex={`U = ${matrixTex(current, upperColor(settledU))}`} />
        </div>
      </div>
    </Panel>
  );
}

type Kind = "lower" | "upper";

const ORDER: Record<Kind, number[]> = { lower: [0, 1, 2], upper: [2, 1, 0] };

function rowEquationTex(row: Row3, values: Row3, color: string): string {
  const terms = row
    .map((coefficient, index) => (isZero(coefficient) ? "" : `${texNumber(coefficient)}(\\textcolor{${color}}{${texNumber(values[index])}})`))
    .filter(Boolean)
    .join(" + ")
    .replaceAll("+ -", "- ");
  return `${terms} = ${texNumber(dot(row, values))}`;
}

function RowStatus({ holds, tex, target }: { holds: boolean; tex: string; target: number }) {
  return (
    <li
      className={`flex items-center gap-3 rounded-lg px-4 py-2 transition-colors duration-300 ${
        holds ? "bg-[color-mix(in_oklab,var(--palette-teal)_16%,transparent)]" : "bg-surface-sunken"
      }`}
    >
      {holds ? (
        <CheckCircle weight="fill" className="size-5 shrink-0 text-[var(--palette-teal)]" aria-label="This row holds" />
      ) : (
        <Circle className="size-5 shrink-0 text-text-muted" aria-label="This row does not hold yet" />
      )}
      <span className="min-w-0 flex-1 overflow-x-auto">
        <Tex>{tex}</Tex>
      </span>
      <span className="shrink-0 text-meta text-text-muted">
        needs <Tex>{texNumber(target)}</Tex>
      </span>
    </li>
  );
}

const valuesKey = (values: Row3) => values.join(",");

/** Forward or back substitution: the learner picks each unknown and watches which rows of the triangular system hold. */
export function SubstitutionSolver({ matrix, rhs, kind, name, hue }: { matrix: Matrix3; rhs: Row3; kind: Kind; name: string; hue: "yellow" | "blue" }) {
  const [values, setValues] = useState<Row3>([0, 0, 0]);
  const { settled: settledKey, gesture } = useSettled(valuesKey(values));
  const settled = settledKey.split(",").map(Number) as Row3;
  const holds = matrix.map((row, index) => isZero(dot(row, settled) - rhs[index]));
  const solved = holds.every(Boolean);
  const color = palette[hue];
  const setAt = (index: number) => (value: number) => setValues((old) => old.map((entry, i) => (i === index ? value : entry)) as Row3);
  const system = `${matrixTex(matrix, () => palette.text)} \\begin{bmatrix} ${[1, 2, 3].map((i) => `\\textcolor{${color}}{${name}_${i}}`).join(" \\\\ ")} \\end{bmatrix} = ${columnTex(rhs, palette.teal)}`;
  const start = kind === "lower" ? "top" : "bottom";
  const solution = `\\textcolor{${color}}{\\mathbf ${name}} = (${values.map((v) => texNumber(v)).join(", ")})`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Set <Tex>{`${name}_1, ${name}_2, ${name}_3`}</Tex> so every row holds. Start at the {start} row, where only one unknown appears.</>}
        success={<>Solved with <Tex>{solution}</Tex>. Each row brought in one new unknown, so the {start} row was the only place to begin.</>}
      />
      <div className="space-y-5">
        <div className="grid items-center gap-5 md:grid-cols-2">
          <Readout tex={system} />
          <div className="space-y-4">
            {ORDER[kind].map((index) => (
              <Slider key={index} label={`${name}_${index + 1}`} value={values[index]} onChange={setAt(index)} min={-6} max={6} step={1} color={color} />
            ))}
          </div>
        </div>
        <ol className="min-w-0 space-y-2" aria-label="Each row of the system with the current values plugged in">
          {matrix.map((row, index) => (
            <RowStatus key={index} holds={holds[index]} tex={rowEquationTex(row, values, color)} target={rhs[index]} />
          ))}
        </ol>
      </div>
    </Panel>
  );
}

const FACTOR_COST = 2 / 3;
const SOLVE_COST = 0.002;
const INVERSE_COST = 2;

function costs(k: number) {
  return [
    { name: "Row reduce each time", value: FACTOR_COST * k, color: palette.purple_gray },
    { name: "Invert A once", value: INVERSE_COST + SOLVE_COST * k, color: palette.text_muted },
    { name: "LU once", value: FACTOR_COST + SOLVE_COST * k, color: palette.teal },
  ];
}

const ratioAt = (k: number) => (FACTOR_COST * k) / (FACTOR_COST + SOLVE_COST * k);

/** Flop counts for n = 1000 as the number of right-hand sides grows. */
export function CostCompare({ target = 50 }: { target?: number }) {
  const [k, setK] = useState(1);
  const { settled, gesture } = useSettled(k);
  const answer = Array.from({ length: 150 }, (_, i) => i + 1).find((count) => ratioAt(count) >= target) ?? 150;
  const solved = settled === answer;
  const bars = costs(k);
  const largest = Math.max(...bars.map((bar) => bar.value));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<RichText>{`Find the fewest right-hand sides $k$ for which LU does at least ${target} times less work than row reducing each time. Here $n = 1000$.`}</RichText>}
        success={<RichText>{`At $k = ${answer}$, LU is ${formatNumber(ratioAt(answer), 1)} times cheaper. One fewer right-hand side gives only ${formatNumber(ratioAt(answer - 1), 1)}.`}</RichText>}
      />
      <div className="space-y-5">
        <Slider label="k" value={k} onChange={setK} min={1} max={120} step={1} color={palette.teal} />
        <ul className="space-y-3">
          {bars.map((bar) => (
            <li key={bar.name} className="grid grid-cols-[1fr_auto] items-center gap-x-3 gap-y-1.5 text-meta sm:grid-cols-[minmax(0,10rem)_1fr_7rem]">
              <span className="text-text-muted">{bar.name}</span>
              <span className="order-last col-span-2 h-3 rounded-full bg-surface-sunken sm:order-none sm:col-span-1">
                <span
                  className="block h-3 rounded-full"
                  style={{ width: `max(4px, ${(100 * bar.value) / largest}%)`, backgroundColor: bar.color }}
                />
              </span>
              <span className="text-right tabular-nums">{formatNumber(bar.value, 2)} billion</span>
            </li>
          ))}
        </ul>
        <Readout tex={`\\frac{\\text{row reduce each time}}{\\text{LU once}} = ${formatNumber(ratioAt(k), 1)}`} />
      </div>
    </Panel>
  );
}
