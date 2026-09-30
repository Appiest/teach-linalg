"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { describeVector, Goal, Panel, Readout, Slider, Tex } from "./controls";
import { hue, type Hue } from "./colors";
import { useSettled } from "./gesture";
import { det, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, Handle, Plane, usePlane, type Bounds } from "./plane";

type Mark = "unmarked" | "pivot" | "free";

const NEXT_MARK: Record<Mark, Mark> = { unmarked: "pivot", pivot: "free", free: "unmarked" };
const MARK_STYLE: Record<Mark, string> = {
  unmarked: "bg-surface-sunken hover:bg-line",
  pivot: "bg-[color-mix(in_oklab,var(--palette-teal)_18%,transparent)] ring-2 ring-[var(--palette-teal)]",
  free: "bg-[color-mix(in_oklab,var(--palette-pink)_18%,transparent)] ring-2 ring-[var(--palette-pink)]",
};
const MARK_TEXT: Record<Mark, string> = { unmarked: "Tap to mark", pivot: "Pivot", free: "Free" };
const MARK_COLOR: Record<Mark, string> = { unmarked: "text-text-muted", pivot: "text-[var(--palette-teal)]", free: "text-[var(--palette-pink)]" };

const columnOf = (rows: number[][], index: number) => rows.map((row) => row[index]);
const columnTex = (entries: number[]) => `\\begin{bmatrix} ${entries.map((value) => texNumber(value)).join(" \\\\ ")} \\end{bmatrix}`;
const count = (marks: Mark[], mark: Mark) => marks.filter((value) => value === mark).length;
const allCorrect = (marks: Mark[], pivots: number[]) => marks.every((mark, index) => mark === (pivots.includes(index) ? "pivot" : "free"));

function MarkLabel({ mark }: { mark: Mark }) {
  return (
    <span className="grid text-meta" aria-hidden>
      {(Object.keys(MARK_TEXT) as Mark[]).map((option) => (
        <span key={option} className={`[grid-area:1/1] ${MARK_COLOR[option]} ${option === mark ? "swap-shown" : "swap-hidden"}`}>
          {MARK_TEXT[option]}
        </span>
      ))}
    </span>
  );
}

function ColumnToggle({ index, entries, mark, onCycle }: { index: number; entries: number[]; mark: Mark; onCycle: () => void }) {
  return (
    <button
      type="button"
      onClick={onCycle}
      aria-label={`Column ${index + 1}, entries ${entries.join(", ")}, marked ${mark}. Tap to change.`}
      className={`grid place-items-center gap-1 rounded-lg px-2 py-2 transition-[background-color,box-shadow] duration-200 ${MARK_STYLE[mark]}`}
    >
      <Tex>{columnTex(entries)}</Tex>
      <MarkLabel mark={mark} />
    </button>
  );
}

/** One cell per column: pivot marks fill teal from the left, free marks fill pink from the right. */
function TallyBar({ marks, lit }: { marks: Mark[]; lit: boolean }) {
  const pivots = count(marks, "pivot");
  const frees = count(marks, "free");
  const cells = marks.map((_, index) => {
    if (index < pivots) return "pivot";
    if (index >= marks.length - frees) return "free";
    return "unmarked";
  });
  const fill: Record<Mark, string> = { pivot: "bg-[var(--palette-teal)]", free: "bg-[var(--palette-pink)]", unmarked: "bg-line" };
  return (
    <div aria-hidden className={`flex gap-1 rounded-lg p-1.5 transition-shadow duration-300 ${lit ? "ring-2 ring-[var(--palette-teal)]" : ""}`}>
      {cells.map((cell, index) => (
        <span key={index} className={`h-6 flex-1 rounded-sm transition-colors duration-300 ${fill[cell as Mark]}`} />
      ))}
    </div>
  );
}

/** Mark each column of an echelon form as a pivot column or a free column, and watch rank and nullity add up to n. */
export function RankTally({ rows, pivots }: { rows: number[][]; pivots: number[] }) {
  const columns = rows[0].length;
  const [marks, setMarks] = useState<Mark[]>(() => Array.from({ length: columns }, () => "unmarked" as Mark));
  const { settled: solved, gesture } = useSettled(allCorrect(marks, pivots));
  const cycle = (index: number) => setMarks((current) => current.map((mark, i) => (i === index ? NEXT_MARK[mark] : mark)));
  const rank = count(marks, "pivot");
  const nullity = count(marks, "free");

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>This matrix is already in echelon form. Tap each column once to mark it pivot, twice to mark it free.</>}
        success={<>Right: <Tex>{`\\operatorname{rank}A = ${pivots.length}`}</Tex> and <Tex>{`\\operatorname{nullity}A = ${columns - pivots.length}`}</Tex>, which add up to the <Tex>{`${columns}`}</Tex> columns.</>}
      />
      <div className="space-y-4">
        <div role="group" aria-label="Columns of the echelon form" className="grid grid-cols-3 gap-2 sm:grid-cols-[repeat(var(--columns),minmax(0,1fr))]" style={{ "--columns": columns } as React.CSSProperties}>
          {marks.map((mark, index) => (
            <ColumnToggle key={index} index={index} entries={columnOf(rows, index)} mark={mark} onCycle={() => cycle(index)} />
          ))}
        </div>
        <TallyBar marks={marks} lit={solved} />
        <Readout
          tex={`\\textcolor{${palette.teal}}{\\operatorname{rank} = ${rank}} \\quad \\textcolor{${palette.pink}}{\\operatorname{nullity} = ${nullity}} \\quad n = ${columns}`}
        />
      </div>
    </Panel>
  );
}

const CELL = 34;
const GAP = 4;

function pivotCell(column: number, rows: number) {
  return column < rows ? column : null;
}

function StaircaseGrid({ rows, columns, rank }: { rows: number; columns: number; rank: number }) {
  const overflow = Math.max(0, rank - rows);
  const width = columns * (CELL + GAP) + GAP;
  const reserveOverflowRow = columns > rows;
  const height = (rows + (reserveOverflowRow ? 1 : 0)) * (CELL + GAP) + GAP + (reserveOverflowRow ? 8 : 0);
  const cellX = (column: number) => GAP + column * (CELL + GAP);
  const cellY = (row: number) => GAP + row * (CELL + GAP);
  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label={`A ${rows} by ${columns} grid with ${Math.min(rank, rows)} pivots on the staircase${overflow > 0 ? `, and ${overflow} pivot${overflow > 1 ? "s" : ""} with no row left to sit in` : ""}.`}
      className="mx-auto block h-auto w-full max-w-md select-none"
    >
      {Array.from({ length: columns }, (_, column) => (
        <g key={column}>
          {Array.from({ length: rows }, (_, row) => {
            const pivotColumn = column < rank;
            const isPivot = pivotColumn && pivotCell(column, rows) === row;
            return (
              <rect
                key={row}
                x={cellX(column)}
                y={cellY(row)}
                width={CELL}
                height={CELL}
                fill={pivotColumn ? "var(--palette-teal)" : "var(--palette-pink)"}
                fillOpacity={isPivot ? 0.9 : 0.22}
                stroke={isPivot ? "var(--palette-glow)" : "none"}
                strokeWidth={2.5}
                className="transition-[fill,fill-opacity] duration-300"
              />
            );
          })}
          {column < rank && column >= rows ? <MissingRow x={cellX(column)} y={cellY(rows) + 8} /> : null}
        </g>
      ))}
    </svg>
  );
}

function MissingRow({ x, y }: { x: number; y: number }) {
  return (
    <g>
      <rect x={x} y={y} width={CELL} height={CELL} fill="none" stroke="var(--palette-glow)" strokeWidth={2} strokeDasharray="4 3" />
      <path d={`M${x + 9},${y + 9} L${x + CELL - 9},${y + CELL - 9} M${x + CELL - 9},${y + 9} L${x + 9},${y + CELL - 9}`} stroke="var(--palette-glow)" strokeWidth={2.5} />
    </g>
  );
}

/** Push the rank of an m × n matrix up until the staircase of pivots runs out of rows. */
export function PivotBudget({ rows, columns }: { rows: number; columns: number }) {
  const [rank, setRank] = useState(1);
  const best = Math.min(rows, columns);
  const { settled: solved, gesture } = useSettled(rank === best);
  const possible = rank <= best;
  const nullity = columns - rank;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide the rank <Tex>{"r"}</Tex> as high as a <Tex>{`${rows}\\times ${columns}`}</Tex> matrix allows. That gives its smallest possible nullity.</>}
        success={<>Each pivot needs its own row, so <Tex>{`\\operatorname{rank}A \\le ${rows}`}</Tex> and <Tex>{`\\operatorname{nullity}A \\ge ${columns} - ${rows} = ${columns - best}`}</Tex>.</>}
      />
      <div className="grid items-start gap-5 md:grid-cols-[1.35fr_1fr]">
        <div className="min-w-0 rounded-media bg-surface-sunken p-3">
          <StaircaseGrid rows={rows} columns={columns} rank={rank} />
        </div>
        <div className="min-w-0 space-y-4">
          <Slider label="r" value={rank} onChange={setRank} min={0} max={columns} step={1} color={palette.teal} />
          <Readout
            tex={
              possible
                ? `\\textcolor{${palette.teal}}{${rank}} + \\textcolor{${palette.pink}}{${nullity}} = ${columns}`
                : `\\textcolor{${palette.glow}}{${rank} \\text{ pivots} > ${rows} \\text{ rows}}`
            }
          />
        </div>
      </div>
    </Panel>
  );
}

function FullLine({ direction, color, width = 3, dashed = false }: { direction: Vec; color: Hue; width?: number; dashed?: boolean }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg([-30 * direction[0], -30 * direction[1]]);
  const [x2, y2] = toSvg([30 * direction[0], 30 * direction[1]]);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={width} strokeDasharray={dashed ? "7 6" : undefined} strokeLinecap="round" />;
}

function PlaneWash({ lit }: { lit: boolean }) {
  const { bounds, toSvg } = usePlane();
  const [x, y] = toSvg([bounds.xMin, bounds.yMax]);
  const [x2, y2] = toSvg([bounds.xMax, bounds.yMin]);
  return <rect x={x} y={y} width={x2 - x} height={y2 - y} fill="var(--palette-teal)" fillOpacity={lit ? 0.14 : 0} className="transition-[fill-opacity] duration-300" />;
}

const matrix2Tex = (m: Matrix2) => `\\begin{bmatrix} ${texNumber(m[0][0])} & ${texNumber(m[0][1])} \\\\ ${texNumber(m[1][0])} & ${texNumber(m[1][1])} \\end{bmatrix}`;
const COLLAPSE_BOUNDS: Bounds = { xMin: -4, xMax: 6, yMin: -3, yMax: 8 };

/** Slide one entry of a 2x2 matrix; at the singular value the outputs collapse from the whole plane to a line and a null line appears. */
export function CollapseSlider({ start = 1 }: { start?: number }) {
  const [k, setK] = useState(start);
  const matrix: Matrix2 = [[1, 2], [2, k]];
  const singular = det(matrix) === 0;
  const { settled: solved, gesture } = useSettled(singular);
  const rank = singular ? 1 : 2;
  const first: Vec = [matrix[0][0], matrix[1][0]];
  const second: Vec = [matrix[0][1], matrix[1][1]];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The teal wash is <Tex>{"\\operatorname{Col}A"}</Tex>. Slide <Tex>{"k"}</Tex> until the outputs collapse from the whole plane onto one line.</>}
        success={<>At <Tex>{"k = 4"}</Tex> the columns line up, so the rank drops to <Tex>{"1"}</Tex>. The pink line of crushed inputs appears at the same moment, and <Tex>{"1 + 1 = 2"}</Tex>.</>}
      />
      <div className="grid items-start gap-5 md:grid-cols-[1.35fr_1fr]">
        <Plane bounds={COLLAPSE_BOUNDS} label={`Column space of A with k = ${k}: ${singular ? "a line, with the null space drawn as a pink line" : "the whole plane"}`}>
          <PlaneWash lit={!singular} />
          {singular ? <FullLine direction={first} color="teal" width={5} /> : null}
          {singular ? <FullLine direction={[-matrix[0][1], matrix[0][0]]} color="pink" dashed /> : null}
          <Arrow to={first} color="green" />
          <Arrow to={second} color="red" />
        </Plane>
        <div className="min-w-0 space-y-4">
          <Slider label="k" value={k} onChange={setK} min={1} max={6} step={1} color={palette.j_hat} />
          <Readout tex={`A = ${matrix2Tex(matrix)}`} />
          <Readout tex={`\\textcolor{${palette.teal}}{\\operatorname{rank} = ${rank}} \\quad \\textcolor{${palette.pink}}{\\operatorname{nullity} = ${2 - rank}}`} />
        </div>
      </div>
    </Panel>
  );
}

const TWIN_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -5, yMax: 5 };

function rankOf(matrix: Matrix2): number {
  if (det(matrix) !== 0) return 2;
  return matrix.flat().some((entry) => entry !== 0) ? 1 : 0;
}

function SpanOf({ vectors, rank }: { vectors: [Vec, Vec]; rank: number }) {
  if (rank === 2) return <PlaneWash lit />;
  const direction = vectors.find((v) => v[0] !== 0 || v[1] !== 0);
  return rank === 1 && direction ? <FullLine direction={direction} color="teal" width={4} /> : null;
}

/** Drag row 2 of a 2x2 matrix; the moment the rows become dependent, the columns do too. */
export function RowColumnDrop({ firstRow = [2, 1], start = [1, 3] }: { firstRow?: Vec; start?: Vec }) {
  const [secondRow, setSecondRow] = useState<Vec>(start);
  const matrix: Matrix2 = [firstRow, secondRow];
  const rank = rankOf(matrix);
  const nonzero = secondRow[0] !== 0 || secondRow[1] !== 0;
  const { settled: solved, gesture } = useSettled(rank === 1 && nonzero);
  const columns: [Vec, Vec] = [[firstRow[0], secondRow[0]], [firstRow[1], secondRow[1]]];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag row 2 to a nonzero spot where the two rows span only a line. Watch the columns on the right.</>}
        success={<>The rows fell onto one line, and the columns fell onto a different line at the same moment. Row rank and column rank both dropped to <Tex>{"1"}</Tex>.</>}
      />
      <div className="grid gap-4 sm:grid-cols-2">
        <figure className="min-w-0">
          <Plane bounds={TWIN_BOUNDS} label={`Rows of A: row 1 at ${describeVector(firstRow)} and row 2 at ${describeVector(secondRow)}`}>
            <SpanOf vectors={[firstRow, secondRow]} rank={rank} />
            <Arrow to={firstRow} color="yellow" />
            <Arrow to={secondRow} color="blue" />
            <Handle at={secondRow} onMove={setSecondRow} color="blue" label={`Row 2 of A, at ${describeVector(secondRow)}`} />
          </Plane>
          <figcaption className="mt-2 text-center text-meta text-text-muted">Rows</figcaption>
        </figure>
        <figure className="min-w-0">
          <Plane bounds={TWIN_BOUNDS} label={`Columns of A: ${describeVector(columns[0])} and ${describeVector(columns[1])}`}>
            <SpanOf vectors={columns} rank={rank} />
            <Arrow to={columns[0]} color="green" />
            <Arrow to={columns[1]} color="red" />
          </Plane>
          <figcaption className="mt-2 text-center text-meta text-text-muted">Columns</figcaption>
        </figure>
      </div>
      <div className="mt-4">
        <Readout tex={`A = \\begin{bmatrix} \\textcolor{${palette.yellow}}{${firstRow[0]}} & \\textcolor{${palette.yellow}}{${firstRow[1]}} \\\\ \\textcolor{${palette.blue}}{${secondRow[0]}} & \\textcolor{${palette.blue}}{${secondRow[1]}} \\end{bmatrix}, \\quad \\dim\\operatorname{Row}A = \\dim\\operatorname{Col}A = ${rank}`} />
      </div>
    </Panel>
  );
}
