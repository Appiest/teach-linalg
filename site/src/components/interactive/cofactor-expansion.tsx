"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { det, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, boundsAround, Handle, Marker, Plane, usePlane } from "./plane";

type Matrix3 = [[number, number, number], [number, number, number], [number, number, number]];
type Line = { kind: "row" | "column"; index: number };

const INDICES = [0, 1, 2];
const LINES: Line[] = [
  ...INDICES.map((index): Line => ({ kind: "row", index })),
  ...INDICES.map((index): Line => ({ kind: "column", index })),
];

const signOf = (row: number, column: number) => ((row + column) % 2 === 0 ? 1 : -1);
const sameLine = (a: Line, b: Line) => a.kind === b.kind && a.index === b.index;
const lineName = (line: Line) => `${line.kind === "row" ? "Row" : "Column"} ${line.index + 1}`;

/** The (row, column) positions along a line, in order. */
const cellsOf = (line: Line): [number, number][] => INDICES.map((k) => (line.kind === "row" ? [line.index, k] : [k, line.index]));

function minorOf(matrix: Matrix3, row: number, column: number): Matrix2 {
  const rows = INDICES.filter((r) => r !== row);
  const columns = INDICES.filter((c) => c !== column);
  return rows.map((r) => columns.map((c) => matrix[r][c])) as Matrix2;
}

function det3(matrix: Matrix3): number {
  return INDICES.reduce((total, column) => total + signOf(0, column) * matrix[0][column] * det(minorOf(matrix, 0, column)), 0);
}

const minorsNeeded = (matrix: Matrix3, line: Line) => cellsOf(line).filter(([r, c]) => matrix[r][c] !== 0).length;

function termTex(matrix: Matrix3, row: number, column: number): string {
  const entry = matrix[row][column];
  const sign = `\\textcolor{${palette.glow}}{${signOf(row, column) > 0 ? "+" : "-"}}`;
  if (entry === 0) return `\\textcolor{${palette.text_muted}}{${sign}\\,0}`;
  const shown = entry < 0 ? `(${texNumber(entry)})` : texNumber(entry);
  const [[a, b], [c, d]] = minorOf(matrix, row, column);
  const minor = `\\begin{vmatrix} ${texNumber(a)} & ${texNumber(b)} \\\\ ${texNumber(c)} & ${texNumber(d)} \\end{vmatrix}`;
  return `${sign}\\textcolor{${palette.yellow}}{${shown}}\\textcolor{${palette.blue}}{${minor}}`;
}

function expansionTex(matrix: Matrix3, line: Line): string {
  const terms = cellsOf(line).map(([r, c]) => termTex(matrix, r, c)).join(" ");
  return `\\det A = ${terms} = \\textcolor{${palette.teal}}{${texNumber(det3(matrix))}}`;
}

function cellClass(inLine: boolean, solved: boolean): string {
  if (!inLine) return "text-text-muted";
  return solved ? "bg-[color-mix(in_oklab,var(--palette-teal)_18%,transparent)] text-text" : "bg-[color-mix(in_oklab,var(--palette-yellow)_16%,transparent)] text-text";
}

function MatrixCells({ matrix, line, solved }: { matrix: Matrix3; line: Line; solved: boolean }) {
  const inLine = (row: number, column: number) => cellsOf(line).some(([r, c]) => r === row && c === column);
  return (
    <div aria-hidden className="mx-auto grid w-fit grid-cols-3 gap-1.5 rounded-lg bg-surface-sunken p-3">
      {matrix.map((values, row) =>
        values.map((value, column) => (
          <div key={`${row}-${column}`} className={`relative grid size-14 place-items-center rounded-md text-lg tabular-nums transition-colors duration-300 ${cellClass(inLine(row, column), solved)}`}>
            <span className="absolute left-1.5 top-0.5 text-sm text-[var(--palette-glow)]">{signOf(row, column) > 0 ? "+" : "−"}</span>
            <Tex>{texNumber(value)}</Tex>
          </div>
        )),
      )}
    </div>
  );
}

function LineButton({ line, selected, onSelect }: { line: Line; selected: boolean; onSelect: () => void }) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onSelect}
      className={`whitespace-nowrap rounded-lg px-3 py-2 text-meta font-semibold transition-colors duration-200 ${
        selected ? "bg-text text-surface" : "bg-surface-sunken text-text hover:bg-line"
      }`}
    >
      {lineName(line)}
    </button>
  );
}

/** Expand a 3 by 3 determinant along any row or column and find the line that needs the fewest 2 by 2 minors. */
export function CofactorLinePicker({ matrix }: { matrix: Matrix3 }) {
  const [line, setLine] = useState<Line>(LINES[0]);
  const fewest = Math.min(...LINES.map((candidate) => minorsNeeded(matrix, candidate)));
  const needed = minorsNeeded(matrix, line);
  const { settled: solved, gesture } = useSettled(needed === fewest);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Every row and column gives the same determinant. Pick the line that needs the fewest <Tex>{"2 \\times 2"}</Tex> determinants.</>}
        success={<>{lineName(line)} needs only {fewest === 1 ? "one" : fewest} <Tex>{"2 \\times 2"}</Tex> determinant, because its zero entries wipe out their whole terms.</>}
      />
      <div className="grid items-center gap-5 md:grid-cols-[auto_1fr]">
        <MatrixCells matrix={matrix} line={line} solved={solved} />
        <div className="min-w-0 space-y-4">
          <div role="group" aria-label="Line to expand along" className="flex flex-wrap gap-2">
            {LINES.map((candidate) => (
              <LineButton key={lineName(candidate)} line={candidate} selected={sameLine(candidate, line)} onSelect={() => setLine(candidate)} />
            ))}
          </div>
          <p className="text-meta text-text-muted">
            <Tex>{"2 \\times 2"}</Tex> determinants to compute: <span className="font-semibold tabular-nums text-text">{needed}</span>
          </p>
        </div>
      </div>
      <div className="mt-5">
        <Readout tex={expansionTex(matrix, line)} />
      </div>
    </Panel>
  );
}

function Parallelogram({ matrix, color, opacity = 0.3, outline = false }: { matrix: Matrix2; color: string; opacity?: number; outline?: boolean }) {
  const { toSvg } = usePlane();
  const first: Vec = [matrix[0][0], matrix[1][0]];
  const second: Vec = [matrix[0][1], matrix[1][1]];
  const corners: Vec[] = [[0, 0], first, [first[0] + second[0], first[1] + second[1]], second];
  const points = corners.map((corner) => toSvg(corner).join(",")).join(" ");
  return (
    <polygon
      points={points}
      fill={outline ? "none" : color}
      fillOpacity={opacity}
      stroke={outline ? color : "none"}
      strokeWidth={2}
      strokeDasharray={outline ? "6 5" : undefined}
      className="transition-[fill] duration-300"
    />
  );
}

function ColumnArrows({ matrix }: { matrix: Matrix2 }) {
  return (
    <>
      <Arrow to={[matrix[0][0], matrix[1][0]]} color="green" />
      <Arrow to={[matrix[0][1], matrix[1][1]]} color="red" />
    </>
  );
}

function coloredMatrixTex(matrix: Matrix2): string {
  const entry = (value: number, column: number) => `\\textcolor{${column === 0 ? palette.i_hat : palette.j_hat}}{${texNumber(value)}}`;
  return `\\begin{bmatrix} ${entry(matrix[0][0], 0)} & ${entry(matrix[0][1], 1)} \\\\ ${entry(matrix[1][0], 0)} & ${entry(matrix[1][1], 1)} \\end{bmatrix}`;
}

const REPLACEMENT_REACH = 3;
const clamp = (value: number, low: number, high: number) => Math.min(high, Math.max(low, value));

function replaced(matrix: Matrix2, k: number): Matrix2 {
  return [matrix[0], [matrix[1][0] + k * matrix[0][0], matrix[1][1] + k * matrix[0][1]]];
}

function replacementTex(k: number): string {
  if (k === 0) return "R_2 \\leftarrow R_2 + 0R_1";
  const size = Math.abs(k) === 1 ? "" : texNumber(Math.abs(k));
  return `R_2 \\leftarrow R_2 ${k < 0 ? "-" : "+"} ${size}R_1`;
}

/** Drag the green column's tip to add a multiple of row 1 to row 2: the parallelogram shears and its area never changes. */
export function ReplacementShear({ matrix = [[1, -1], [1, 2]] }: { matrix?: Matrix2 }) {
  const [k, setK] = useState(0);
  const current = replaced(matrix, k);
  const { settled: solved, gesture } = useSettled(current[1][0] === 0);
  const extremes = [-REPLACEMENT_REACH, REPLACEMENT_REACH].map((reach) => replaced(matrix, reach));
  const bounds = boundsAround(extremes.flatMap((m): Vec[] => [[m[0][0], m[1][0]], [m[0][1], m[1][1]], [m[0][0] + m[0][1], m[1][0] + m[1][1]]]));
  const moveTip = (point: Vec) => setK(clamp(Math.round((point[1] - matrix[1][0]) / matrix[0][0]), -REPLACEMENT_REACH, REPLACEMENT_REACH));
  const tip: Vec = [current[0][0], current[1][0]];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the green tip up or down to add a multiple of row 1 to row 2. Make the bottom-left entry <Tex>{"0"}</Tex>, then read the determinant off the diagonal.</>}
        success={<>The matrix is triangular, so <Tex>{`\\det = ${texNumber(current[0][0])} \\cdot ${texNumber(current[1][1])} = ${texNumber(det(current))}`}</Tex>. That is the same area you started with, because a row replacement only shears.</>}
      />
      <Workbench
        plane={
          <Plane bounds={bounds} label={`The parallelogram of the columns of the matrix, with the green column at (${tip[0]}, ${tip[1]}). Its area is ${det(current)}.`}>
            <Parallelogram matrix={matrix} color="var(--palette-text-muted)" opacity={0.7} outline />
            <Parallelogram matrix={current} color={solved ? "var(--palette-teal)" : "var(--palette-yellow)"} />
            <Marker at={[matrix[0][0], 0]} color={solved ? "teal" : "glow"} ring={!solved} />
            <ColumnArrows matrix={current} />
            <Handle at={tip} onMove={moveTip} color="green" label={`Tip of the green column, which moves up and down only. Row 2 gets ${k} times row 1 added`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={replacementTex(k)} />
            <Readout tex={`${coloredMatrixTex(current)} \\qquad \\det = ${texNumber(det(current))}`} />
          </>
        }
      />
    </Panel>
  );
}

const scaled = (k: number, matrix: Matrix2): Matrix2 => [
  [k * matrix[0][0], k * matrix[0][1]],
  [k * matrix[1][0], k * matrix[1][1]],
];

/** Slide k and watch det(kA) grow like k squared, because both rows of a 2 by 2 matrix get scaled. */
export function MultipleAreaScale({ matrix = [[1, -1], [1, 1]], factor = 4 }: { matrix?: Matrix2; factor?: number }) {
  const [k, setK] = useState(1);
  const current = scaled(k, matrix);
  const base = det(matrix);
  const { settled: solved, gesture } = useSettled(Math.abs(det(current) - factor * base) < 1e-9);
  const bounds = boundsAround([scaled(2.5, matrix), scaled(-2.5, matrix)].flatMap((m): Vec[] => [[m[0][0] + m[0][1], m[1][0] + m[1][1]], [m[0][0], m[1][0]], [m[0][1], m[1][1]]]));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Choose <Tex>{"k"}</Tex> so that <Tex>{`\\det(kA)`}</Tex> is <Tex>{texNumber(factor)}</Tex> times <Tex>{"\\det A"}</Tex>.</>}
        success={<>With <Tex>{`k = ${texNumber(k)}`}</Tex>, each of the two rows is scaled by <Tex>{texNumber(k)}</Tex>, so the area grows by <Tex>{`${k < 0 ? `(${texNumber(k)})` : texNumber(k)}^2 = ${texNumber(k * k)}`}</Tex>, not by <Tex>{texNumber(k)}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={bounds} label={`The parallelogram of A, dashed, and of k times A, filled, with k = ${k}.`}>
            <Parallelogram matrix={matrix} color="var(--palette-text-muted)" opacity={0.7} outline />
            <Parallelogram matrix={current} color={solved ? "var(--palette-teal)" : "var(--palette-yellow)"} />
            <ColumnArrows matrix={current} />
          </Plane>
        }
        readout={
          <>
            <Slider label="k" value={k} onChange={setK} min={-2.5} max={2.5} step={0.5} color={palette.yellow} />
            <Readout tex={`kA = ${coloredMatrixTex(current)}`} />
            <Readout tex={`\\det(kA) = ${texNumber(det(current))} = ${texNumber(k * k)} \\cdot \\underbrace{${texNumber(base)}}_{\\det A}`} />
          </>
        }
      />
    </Panel>
  );
}
