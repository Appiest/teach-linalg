"use client";

import { Check } from "@phosphor-icons/react";
import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { Goal, Panel, Readout, RichText, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { formatNumber, texNumber, type Vec } from "./math";
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

type Matrix = number[][];
type Operation = "replace" | "swap" | "scale";

const tidy = (value: number) => {
  const rounded = Math.round(value);
  return Math.abs(value - rounded) < EPSILON ? rounded + 0 : value;
};

const leadingIndex = (row: number[]) => row.findIndex((entry) => !isZero(entry));

function rowIsReduced(rows: Matrix, leads: number[], index: number): boolean {
  const lead = leads[index];
  if (lead === -1) return leads.slice(index + 1).every((later) => later === -1);
  const above = index > 0 ? leads[index - 1] : -Infinity;
  if (above === -1 || above >= lead) return false;
  if (!isZero(rows[index][lead] - 1)) return false;
  return rows.every((row, other) => other === index || isZero(row[lead]));
}

export function isReducedEchelon(rows: Matrix): boolean {
  const leads = rows.map(leadingIndex);
  return rows.every((_, index) => rowIsReduced(rows, leads, index));
}

type Move = { operation: Operation; target: number; source: number; factor: number };

function moveIsValid(rows: Matrix, { operation, target, source, factor }: Move): boolean {
  if (operation === "scale") return leadingIndex(rows[target]) !== -1 && !isZero(rows[target][leadingIndex(rows[target])] - 1);
  if (target === source) return false;
  return operation === "swap" || !isZero(factor);
}

function applyMove(rows: Matrix, { operation, target, source, factor }: Move): Matrix {
  if (operation === "swap") return rows.map((row, index) => rows[index === target ? source : index === source ? target : index]);
  const lead = rows[target][leadingIndex(rows[target])];
  const updated = operation === "scale"
    ? rows[target].map((entry) => tidy(entry / lead))
    : rows[target].map((entry, column) => tidy(entry + factor * rows[source][column]));
  return rows.map((row, index) => (index === target ? updated : row));
}

function scaleTex(rows: Matrix, target: number): string {
  const lead = leadingIndex(rows[target]);
  if (lead === -1) return `R_${target + 1} \\text{ is all zeros}`;
  return `R_${target + 1} \\leftarrow \\tfrac{1}{${texNumber(rows[target][lead])}}\\,R_${target + 1}`;
}

function moveTex(rows: Matrix, move: Move): string {
  const { operation, target, source, factor } = move;
  if (operation === "swap") return `R_${target + 1} \\leftrightarrow R_${source + 1}`;
  if (operation === "scale") return scaleTex(rows, target);
  const sign = factor < 0 ? "-" : "+";
  const size = Math.abs(factor) === 1 ? "" : texNumber(Math.abs(factor));
  return `R_${target + 1} \\leftarrow R_${target + 1} ${sign} ${size}R_${source + 1}`;
}

function matrixTex(rows: Matrix): string {
  const columns = rows[0].length;
  const spec = `${"r".repeat(columns - 1)}|r`;
  const body = rows
    .map((row) => {
      const lead = leadingIndex(row);
      return row.map((entry, column) => (column === lead ? `\\textcolor{${palette.glow}}{${texNumber(entry)}}` : texNumber(entry))).join(" & ");
    })
    .join(" \\\\ ");
  const labels = rows.map((_, index) => `R_${index + 1}`).join(" \\\\ ");
  return `\\begin{matrix} ${labels} \\end{matrix} \\left[\\begin{array}{${spec}} ${body} \\end{array}\\right]`;
}

const segment = "min-h-9 rounded-lg px-3 py-1.5 text-meta font-semibold transition-colors";
const segmentOn = `${segment} bg-text text-surface`;
const segmentOff = `${segment} bg-surface-sunken text-text-muted hover:text-text`;

function Segmented<T extends string | number>({ label, options, value, onChange }: {
  label: string; options: { value: T; text: string }[]; value: T; onChange: (value: T) => void;
}) {
  return (
    <div className="space-y-1.5">
      <span className="block text-meta text-text-muted">{label}</span>
      <div role="group" aria-label={label} className="flex flex-wrap gap-1.5">
        {options.map((option) => (
          <button key={option.text} type="button" aria-pressed={option.value === value} className={option.value === value ? segmentOn : segmentOff} onClick={() => onChange(option.value)}>
            {option.text}
          </button>
        ))}
      </div>
    </div>
  );
}

const OPERATIONS: { value: Operation; text: string }[] = [
  { value: "replace", text: "Replace" },
  { value: "swap", text: "Swap" },
  { value: "scale", text: "Scale" },
];

function MoveControls({ move, rowCount, onChange }: { move: Move; rowCount: number; onChange: (move: Move) => void }) {
  const rowOptions = Array.from({ length: rowCount }, (_, index) => ({ value: index, text: `Row ${index + 1}` }));
  const usesSource = move.operation !== "scale";
  return (
    <div className="space-y-3">
      <Segmented label="Operation" options={OPERATIONS} value={move.operation} onChange={(operation) => onChange({ ...move, operation })} />
      <Segmented label="Row that changes" options={rowOptions} value={move.target} onChange={(target) => onChange({ ...move, target })} />
      <div inert={!usesSource} className={usesSource ? "" : "opacity-35"}>
        <Segmented label="Row it uses" options={rowOptions} value={move.source} onChange={(source) => onChange({ ...move, source })} />
      </div>
      <div inert={move.operation !== "replace"} className={move.operation === "replace" ? "" : "opacity-35"}>
        <Slider label="c" value={move.factor} onChange={(factor) => onChange({ ...move, factor })} min={-3} max={3} step={1} color={palette.blue} />
      </div>
    </div>
  );
}

const primary = "rounded-lg bg-text px-4 py-2 text-meta font-semibold text-surface transition-opacity hover:opacity-90 disabled:opacity-35";
const secondary = "rounded-lg px-3 py-2 text-meta font-semibold text-text-muted transition-colors hover:text-text disabled:opacity-35";

/** A row-reduction workbench: pick a row operation, apply it, and keep going until the matrix is in reduced echelon form. */
export function RowReducer({ matrix, solution }: { matrix: Matrix; solution: number[] }) {
  const [rows, setRows] = useState<Matrix>(matrix);
  const [history, setHistory] = useState<Matrix[]>([]);
  const [move, setMove] = useState<Move>({ operation: "swap", target: 0, source: 1, factor: -1 });
  const { settled: solved, gesture } = useSettled(isReducedEchelon(rows));
  const valid = moveIsValid(rows, move);
  const apply = () => {
    setHistory([...history, rows]);
    setRows(applyMove(rows, move));
  };
  const undo = () => {
    setRows(history[history.length - 1] ?? matrix);
    setHistory(history.slice(0, -1));
  };
  const answer = solution.map((value, index) => `x_${index + 1} = ${texNumber(value)}`).join(",\\ ");
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Use row operations to reach reduced echelon form. The orange entries are the leading entries of each row.</>}
        success={<>That is the reduced echelon form, and the last column reads <Tex>{answer}</Tex>.</>}
      />
      <Workbench
        plane={
          <div className="grid min-h-48 place-items-center rounded-media bg-surface-sunken px-4 py-6 [&_.katex]:text-[1.35em]">
            <Tex display>{matrixTex(rows)}</Tex>
          </div>
        }
        readout={
          <>
            <MoveControls move={move} rowCount={rows.length} onChange={setMove} />
            <Readout tex={moveTex(rows, move)} />
            <div className="flex flex-wrap items-center gap-2">
              <button type="button" className={primary} disabled={!valid} onClick={apply}>
                Apply
              </button>
              <button type="button" className={secondary} disabled={history.length === 0} onClick={undo}>
                Undo
              </button>
              <button type="button" className={secondary} disabled={history.length === 0} onClick={() => { setRows(matrix); setHistory([]); }}>
                Start over
              </button>
              <span className="ml-auto text-meta tabular-nums text-text-muted">{history.length} moves</span>
            </div>
          </>
        }
      />
    </Panel>
  );
}

function pivotLabel(row: number, column: number, value: number): string {
  return `Row ${row + 1}, column ${column + 1}, entry ${formatNumber(value)}`;
}

function EntryButton({ value, picked, label, onToggle }: { value: number; picked: boolean; label: string; onToggle: () => void }) {
  const look = picked
    ? "bg-[color-mix(in_oklab,var(--palette-glow)_20%,transparent)] ring-2 ring-[var(--palette-glow)] text-text"
    : "bg-surface-sunken text-text hover:bg-line";
  return (
    <button type="button" aria-pressed={picked} aria-label={label} onClick={onToggle} className={`relative h-11 rounded-lg text-body tabular-nums transition-colors ${look}`}>
      {formatNumber(value)}
      {picked ? <Check weight="bold" aria-hidden className="absolute top-1 right-1 size-3 text-[var(--palette-glow)]" /> : null}
    </button>
  );
}

function ColumnName({ column, isPivot, solved }: { column: number; isPivot: boolean; solved: boolean }) {
  const color = !solved ? "text-text-muted" : isPivot ? "text-[var(--palette-teal)]" : "text-[var(--palette-glow)]";
  return (
    <div className={`text-center transition-colors ${color}`}>
      <Tex>{`x_{${column + 1}}`}</Tex>
    </div>
  );
}

/** Tap the pivot positions of an augmented matrix that is already in echelon form. */
export function PivotSpotter({ matrix }: { matrix: Matrix }) {
  const leads = matrix.map(leadingIndex);
  const [picked, setPicked] = useState<boolean[][]>(matrix.map((row) => row.map(() => false)));
  const allRight = matrix.every((row, r) => row.every((_, c) => picked[r][c] === (leads[r] === c)));
  const { settled: solved, gesture } = useSettled(allRight);
  const columns = matrix[0].length;
  const pivotColumns = new Set(leads.filter((lead) => lead >= 0));
  const variables = Array.from({ length: columns - 1 }, (_, column) => column);
  const listTex = (chosen: number[]) => chosen.map((column) => `x_{${column + 1}}`).join(", ");
  const toggle = (r: number, c: number) => setPicked((current) => current.map((row, i) => row.map((value, j) => (i === r && j === c ? !value : value))));
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Tap every pivot position in this echelon form, and nothing else.</>}
        success={<>Those are the pivots. Their columns make <Tex>{listTex(variables.filter((c) => pivotColumns.has(c)))}</Tex> basic, shown in teal, and the columns without a pivot make <Tex>{listTex(variables.filter((c) => !pivotColumns.has(c)))}</Tex> free, shown in orange.</>}
      />
      <div className="mx-auto grid max-w-xl gap-2" style={{ gridTemplateColumns: `repeat(${columns - 1}, minmax(0, 1fr)) 2px minmax(0, 1fr)` }}>
        {matrix.map((row, r) =>
          row.map((value, c) => (
            <div key={`${r}-${c}`} className="grid" style={{ gridRow: r + 1, gridColumn: c === columns - 1 ? c + 2 : c + 1 }}>
              <EntryButton value={value} picked={picked[r][c]} label={pivotLabel(r, c, value)} onToggle={() => toggle(r, c)} />
            </div>
          )),
        )}
        <div aria-hidden className="bg-text-muted" style={{ gridColumn: columns, gridRow: `1 / span ${matrix.length}` }} />
        {variables.map((column) => (
          <div key={column} style={{ gridRow: matrix.length + 1, gridColumn: column + 1 }}>
            <ColumnName column={column} isPivot={pivotColumns.has(column)} solved={solved} />
          </div>
        ))}
      </div>
    </Panel>
  );
}
