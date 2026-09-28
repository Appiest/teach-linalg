"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { Goal, Panel, Readout, RichText, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { texNumber, type Vec } from "./math";
import { Label, Marker, Plane, usePlane, type Bounds } from "./plane";

export type Row = [number, number, number];

const EPSILON = 1e-9;
const isZero = (value: number) => Math.abs(value) < EPSILON;

export const addRows = (row: Row, other: Row, factor: number): Row => [
  row[0] + factor * other[0],
  row[1] + factor * other[1],
  row[2] + factor * other[2],
];

function slabRange(base: number, direction: number, low: number, high: number): [number, number] | null {
  if (isZero(direction)) return base >= low && base <= high ? [-Infinity, Infinity] : null;
  const ends = [(low - base) / direction, (high - base) / direction].sort((a, b) => a - b);
  return [ends[0], ends[1]];
}

/** Endpoints of a·x + b·y = c inside the bounds, or null when the line misses them. */
export function clipLine([a, b, c]: Row, bounds: Bounds): [Vec, Vec] | null {
  const norm = a * a + b * b;
  if (norm < EPSILON) return null;
  const base: Vec = [(a * c) / norm, (b * c) / norm];
  const direction: Vec = [-b / Math.sqrt(norm), a / Math.sqrt(norm)];
  const xs = slabRange(base[0], direction[0], bounds.xMin, bounds.xMax);
  const ys = slabRange(base[1], direction[1], bounds.yMin, bounds.yMax);
  if (!xs || !ys) return null;
  const low = Math.max(xs[0], ys[0]);
  const high = Math.min(xs[1], ys[1]);
  if (low >= high) return null;
  const at = (t: number): Vec => [base[0] + t * direction[0], base[1] + t * direction[1]];
  return [at(low), at(high)];
}

export function EquationLine({ row, color, width = 3 }: { row: Row; color: Hue; width?: number }) {
  const { bounds, toSvg } = usePlane();
  const ends = clipLine(row, bounds);
  if (!ends) return null;
  const [x1, y1] = toSvg(ends[0]);
  const [x2, y2] = toSvg(ends[1]);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={width} strokeLinecap="round" />;
}

export function augmentedTex(rows: Row[], colors: string[]): string {
  const body = rows
    .map((row, index) => row.map((entry) => `\\textcolor{${colors[index]}}{${texNumber(entry)}}`).join(" & "))
    .join(" \\\\ ");
  return `\\left[\\begin{array}{rr|r} ${body} \\end{array}\\right]`;
}

function termTex(coefficient: number, variable: string, leading: boolean): string {
  if (isZero(coefficient)) return "";
  const magnitude = Math.abs(Math.abs(coefficient) - 1) < EPSILON ? "" : texNumber(Math.abs(coefficient));
  const sign = coefficient < 0 ? "-" : leading ? "" : "+";
  return `${sign} ${magnitude}${variable}`;
}

function equationTex(row: Row, color: string): string {
  const first = termTex(row[0], "x_1", true);
  const second = termTex(row[1], "x_2", first === "");
  const left = `${first} ${second}`.trim() || "0";
  return `\\textcolor{${color}}{${left} = ${texNumber(row[2])}}`;
}

const ROW_COLORS = [palette.yellow, palette.blue];
const PIVOT_BOUNDS: Bounds = { xMin: -3, xMax: 7, yMin: -2, yMax: 5 };

function OperationSlider({ tex, label, value, onChange, color }: { tex: string; label: string; value: number; onChange: (value: number) => void; color: string }) {
  return (
    <div className="space-y-1.5">
      <div className="text-meta text-text-muted">
        <Tex>{tex}</Tex>
      </div>
      <Slider label={label} value={value} onChange={onChange} min={-3} max={3} step={0.5} color={color} />
    </div>
  );
}

export function RowReduceExplorer({ rows = [[1, -2, -1], [-1, 3, 3]], solution = [3, 2] }: { rows?: [Row, Row]; solution?: Vec }) {
  const [a, setA] = useState(0);
  const [b, setB] = useState(0);
  const second = addRows(rows[1], rows[0], a);
  const first = addRows(rows[0], second, b);
  const { settled: solved, gesture } = useSettled(isZero(second[0]) && isZero(first[1]));
  const lineWidth = solved ? 4.5 : 3;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Clear the <Tex>{"x_1"}</Tex> entry of row 2, then the <Tex>{"x_2"}</Tex> entry of row 1, so each row mentions a single unknown.</>}
        success={<>Now the matrix reads <Tex>{`x_1 = ${texNumber(solution[0])}`}</Tex> and <Tex>{`x_2 = ${texNumber(solution[1])}`}</Tex>. The lines turned the whole time, but they never stopped crossing at the same point.</>}
      />
      <Workbench
        plane={
          <Plane bounds={PIVOT_BOUNDS} label="Two lines, one per row of the augmented matrix. They cross at the solution.">
            <EquationLine row={first} color="yellow" width={lineWidth} />
            <EquationLine row={second} color="blue" width={lineWidth} />
            <Marker at={solution} color="teal" ring={!solved} />
            {solved ? <Label at={solution} color="teal">{`(${solution[0]}, ${solution[1]})`}</Label> : null}
          </Plane>
        }
        readout={
          <>
            <OperationSlider tex={"R_2 \\leftarrow R_2 + a\\,R_1"} label="a" value={a} onChange={setA} color={palette.blue} />
            <OperationSlider tex={"R_1 \\leftarrow R_1 + b\\,R_2"} label="b" value={b} onChange={setB} color={palette.yellow} />
            <Readout tex={augmentedTex([first, second], ROW_COLORS)} />
            <Readout tex={`\\begin{aligned} ${equationTex(first, palette.yellow)} \\\\ ${equationTex(second, palette.blue)} \\end{aligned}`} />
          </>
        }
      />
    </Panel>
  );
}

type Outcome = "none" | "one" | "many";

const OUTCOME_TEXT: Record<Outcome, string> = {
  none: "The last row says $0 = $ a nonzero number, so there is no solution.",
  one: "Every row has a pivot, so there is exactly one solution.",
  many: "The last row is all zeros, so $x_2$ is free and there are infinitely many solutions.",
};

function outcomeOf(echelonRow: Row): Outcome {
  if (!isZero(echelonRow[1])) return "one";
  return isZero(echelonRow[2]) ? "many" : "none";
}

function intersection(first: Row, second: Row): Vec | null {
  const det = first[0] * second[1] - first[1] * second[0];
  if (isZero(det)) return null;
  return [(first[2] * second[1] - first[1] * second[2]) / det, (first[0] * second[2] - first[2] * second[0]) / det];
}

const SUCCESS_TEXT: Record<Outcome, string> = {
  none: "That works. The lines are parallel, and the echelon form has a row that says $0 =$ a nonzero number.",
  one: "That works. Row 2 keeps a pivot, so the lines cross exactly once.",
  many: "That works. Both equations describe the same line, and the echelon row $[\\,0\\ \\ 0 \\mid 0\\,]$ says only $0 = 0$.",
};

const COUNT_BOUNDS: Bounds = { xMin: -5, xMax: 8, yMin: -4, yMax: 4 };

function SolutionSet({ outcome, first, second }: { outcome: Outcome; first: Row; second: Row }) {
  if (outcome === "many") return <EquationLine row={first} color="teal" width={7} />;
  const point = outcome === "one" ? intersection(first, second) : null;
  return point ? <Marker at={point} color="teal" /> : null;
}

function OutcomeLine({ outcome }: { outcome: Outcome }) {
  return (
    <div className="grid rounded-lg bg-surface-sunken px-4 py-3 text-meta">
      {(Object.keys(OUTCOME_TEXT) as Outcome[]).map((key) => (
        <p key={key} aria-hidden={key !== outcome} className={`[grid-area:1/1] ${key === outcome ? "swap-shown" : "swap-hidden"}`}>
          <RichText>{OUTCOME_TEXT[key]}</RichText>
        </p>
      ))}
    </div>
  );
}

export function SolutionCountExplorer({ first = [1, -2, 3], goal = "many" }: { first?: Row; goal?: Outcome }) {
  const [h, setH] = useState(1);
  const [k, setK] = useState(2);
  const second: Row = [3, h, k];
  const echelonRow = addRows(second, first, -second[0] / first[0]);
  const outcome = outcomeOf(echelonRow);
  const { settled: solved, gesture } = useSettled(outcome === goal);
  const goalText: Record<Outcome, string> = {
    none: "Choose $h$ and $k$ so the system has no solution.",
    one: "Choose $h$ and $k$ so the system has exactly one solution.",
    many: "Choose $h$ and $k$ so the system has infinitely many solutions.",
  };

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<RichText>{goalText[goal]}</RichText>}
        success={<RichText>{SUCCESS_TEXT[goal]}</RichText>}
      />
      <Workbench
        plane={
          <Plane bounds={COUNT_BOUNDS} label="The yellow line is fixed. The blue line changes with h and k.">
            <EquationLine row={first} color="yellow" />
            <EquationLine row={second} color="blue" />
            <SolutionSet outcome={outcome} first={first} second={second} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\begin{aligned} ${equationTex(first, palette.yellow)} \\\\ \\textcolor{${palette.blue}}{3x_1 + h\\,x_2 = k} \\end{aligned}`} />
            <Slider label="h" value={h} onChange={setH} min={-8} max={4} step={1} color={palette.blue} />
            <Slider label="k" value={k} onChange={setK} min={0} max={12} step={1} color={palette.blue} />
            <Readout tex={`\\sim ${augmentedTex([first, echelonRow], ROW_COLORS)}`} />
            <OutcomeLine outcome={outcome} />
          </>
        }
      />
    </Panel>
  );
}
