"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { Goal, Panel, Readout, Slider, Tex } from "./controls";
import { useSettled } from "./gesture";
import { texNumber } from "./math";

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
