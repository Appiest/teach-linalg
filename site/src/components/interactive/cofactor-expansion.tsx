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
      <div className="grid items-start gap-5 md:grid-cols-[auto_1fr]">
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

type Position = [number, number];

const cofactorOf = (matrix: Matrix3, row: number, column: number) => signOf(row, column) * det(minorOf(matrix, row, column));
const samePosition = (a: Position, b: Position) => a[0] === b[0] && a[1] === b[1];

function positionWithCofactor(matrix: Matrix3, target: number): Position {
  const cells = INDICES.flatMap((row) => INDICES.map((column): Position => [row, column]));
  return cells.find(([row, column]) => cofactorOf(matrix, row, column) === target) ?? [0, 0];
}

function vmatrixTex([[a, b], [c, d]]: Matrix2): string {
  return `\\begin{vmatrix} ${texNumber(a)} & ${texNumber(b)} \\\\ ${texNumber(c)} & ${texNumber(d)} \\end{vmatrix}`;
}

function cofactorTex(matrix: Matrix3, [row, column]: Position): string {
  const minor = det(minorOf(matrix, row, column));
  const sign = `\\textcolor{${palette.glow}}{${signOf(row, column) > 0 ? "+" : "-"}}`;
  const shownMinor = `(${texNumber(minor)})`;
  const minorTex = `\\textcolor{${palette.blue}}{${vmatrixTex(minorOf(matrix, row, column))}}`;
  return `C_{${row + 1}${column + 1}} = ${sign}${minorTex} = ${sign}${shownMinor} = ${texNumber(cofactorOf(matrix, row, column))}`;
}

function huntCellClass(picked: boolean, crossed: boolean, solved: boolean): string {
  if (picked && solved) return "ring-2 ring-[var(--palette-teal)] bg-[color-mix(in_oklab,var(--palette-teal)_18%,transparent)]";
  if (picked) return "ring-2 ring-[var(--palette-yellow)] bg-[color-mix(in_oklab,var(--palette-yellow)_14%,transparent)]";
  if (crossed) return "text-text-muted opacity-40 line-through";
  return "bg-[color-mix(in_oklab,var(--palette-blue)_16%,transparent)] hover:bg-[color-mix(in_oklab,var(--palette-blue)_26%,transparent)]";
}

function HuntCell({ value, position, picked, crossed, solved, onPick }: {
  value: number; position: Position; picked: boolean; crossed: boolean; solved: boolean; onPick: () => void;
}) {
  const [row, column] = position;
  return (
    <button
      type="button"
      aria-pressed={picked}
      aria-label={`Row ${row + 1}, column ${column + 1}, entry ${texNumber(value)}`}
      onClick={onPick}
      className={`relative grid size-14 place-items-center rounded-md text-lg tabular-nums transition-colors duration-200 ${huntCellClass(picked, crossed, solved)}`}
    >
      <span className="absolute left-1.5 top-0.5 text-sm text-[var(--palette-glow)]">{signOf(row, column) > 0 ? "+" : "−"}</span>
      <Tex>{texNumber(value)}</Tex>
    </button>
  );
}

/** Pick an entry to delete its row and column, and find the position whose signed minor matches the target cofactor. */
export function CofactorHunt({ matrix, target }: { matrix: Matrix3; target: number }) {
  const [picked, setPicked] = useState<Position>([0, 0]);
  const answer = positionWithCofactor(matrix, target);
  const { settled: solved, gesture } = useSettled(samePosition(picked, answer));
  const crossed = ([row, column]: Position) => row === picked[0] || column === picked[1];
  const answerMinor = det(minorOf(matrix, answer[0], answer[1]));
  const answerSign = signOf(answer[0], answer[1]) > 0 ? "+" : "-";

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Pick an entry to delete its row and column. Find the position whose cofactor is <Tex>{`C_{ij} = ${texNumber(target)}`}</Tex>.</>}
        success={<>Position <Tex>{`(${answer[0] + 1}, ${answer[1] + 1})`}</Tex> works. Its minor is <Tex>{texNumber(answerMinor)}</Tex>, and the <Tex>{answerSign}</Tex> sign from the checkerboard makes the cofactor <Tex>{texNumber(target)}</Tex>.</>}
      />
      <div className="grid items-center gap-5 md:grid-cols-[auto_1fr]">
        <div role="group" aria-label="Entries of A. Pick one to delete its row and column." className="mx-auto grid w-fit grid-cols-3 gap-1.5 rounded-lg bg-surface-sunken p-3">
          {matrix.map((values, row) =>
            values.map((value, column) => {
              const position: Position = [row, column];
              const isPicked = samePosition(position, picked);
              return (
                <HuntCell
                  key={`${row}-${column}`}
                  value={value}
                  position={position}
                  picked={isPicked}
                  crossed={!isPicked && crossed(position)}
                  solved={solved}
                  onPick={() => setPicked(position)}
                />
              );
            }),
          )}
        </div>
        <div className="min-w-0">
          <Readout tex={cofactorTex(matrix, picked)} />
        </div>
      </div>
    </Panel>
  );
}

const CLEAR_REACH = 4;

function clearedMatrix(matrix: Matrix3, multiples: [number, number]): Matrix3 {
  const [top, second, third] = matrix;
  const addTop = (row: number[], c: number) => row.map((value, k) => value + c * top[k]) as [number, number, number];
  return [top, addTop(second, multiples[0]), addTop(third, multiples[1])];
}

function replacementStepTex(row: number, c: number): string {
  if (c === 0) return `R_${row} \\leftarrow R_${row}`;
  const size = Math.abs(c) === 1 ? "" : texNumber(Math.abs(c));
  return `R_${row} \\leftarrow R_${row} ${c < 0 ? "-" : "+"} ${size}R_1`;
}

function columnOneExpansionTex(matrix: Matrix3): string {
  const terms = INDICES.map((row) => termTex(matrix, row, 0)).join(" ");
  return `\\det = ${terms} = \\textcolor{${palette.teal}}{${texNumber(det3(matrix))}}`;
}

function clearCellTone(matrix: Matrix3, row: number, column: number, solved: boolean): string {
  const teal = "bg-[color-mix(in_oklab,var(--palette-teal)_18%,transparent)] text-text";
  if (column !== 0) return "text-text-muted";
  if (solved || (row > 0 && matrix[row][0] === 0)) return teal;
  return "bg-[color-mix(in_oklab,var(--palette-yellow)_16%,transparent)] text-text";
}

function ClearCells({ matrix, solved }: { matrix: Matrix3; solved: boolean }) {
  return (
    <div aria-hidden className="mx-auto grid w-fit grid-cols-3 gap-1.5 rounded-lg bg-surface-sunken p-3">
      {matrix.map((values, row) =>
        values.map((value, column) => (
          <div key={`${row}-${column}`} className={`grid h-12 w-14 place-items-center rounded-md text-lg tabular-nums transition-colors duration-300 ${clearCellTone(matrix, row, column, solved)}`}>
            <Tex>{texNumber(value)}</Tex>
          </div>
        )),
      )}
    </div>
  );
}

/** Two row replacements clear column 1 below its top entry. The determinant stays put while its expansion shrinks to one term. */
export function ColumnClearExpand({ matrix }: { matrix: Matrix3 }) {
  const [c2, setC2] = useState(0);
  const [c3, setC3] = useState(0);
  const current = clearedMatrix(matrix, [c2, c3]);
  const { settled: solved, gesture } = useSettled(current[1][0] === 0 && current[2][0] === 0);
  const pivot = matrix[0][0];
  const finalMinor = det(minorOf(clearedMatrix(matrix, [-matrix[1][0] / pivot, -matrix[2][0] / pivot]), 0, 0));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Add multiples of row 1 to rows 2 and 3 until column 1 reads <Tex>{`${texNumber(pivot)}, 0, 0`}</Tex> from top to bottom. Watch the determinant as you go.</>}
        success={<>Column 1 has one nonzero entry, so expanding down it takes one <Tex>{"2 \\times 2"}</Tex> determinant: <Tex>{`${texNumber(pivot)} \\cdot (${texNumber(finalMinor)}) = ${texNumber(det3(matrix))}`}</Tex>. The replacements never changed the answer.</>}
      />
      <div className="grid items-start gap-5 md:grid-cols-[auto_1fr]">
        <ClearCells matrix={current} solved={solved} />
        <div className="min-w-0 space-y-4">
          <Slider label="c_2" value={c2} onChange={setC2} min={-CLEAR_REACH} max={CLEAR_REACH} step={1} color={palette.yellow} />
          <Slider label="c_3" value={c3} onChange={setC3} min={-CLEAR_REACH} max={CLEAR_REACH} step={1} color={palette.blue} />
          <Readout tex={`${replacementStepTex(2, c2)} \\qquad ${replacementStepTex(3, c3)}`} />
        </div>
      </div>
      <div className="mt-5">
        <Readout tex={columnOneExpansionTex(current)} />
      </div>
    </Panel>
  );
}
