"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { columnTex, describeVector, Goal, Panel, Readout, RichText, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, nearlyEqual, scale, texNumber, type Vec } from "./math";
import { Arrow, boundsAround, Handle, Label, Marker, Plane, usePlane } from "./plane";
import { EquationLine } from "./systems";

type Columns = [Vec, Vec];

function coloredMatrixTex([first, second]: Columns): string {
  const entry = (value: number, color: string) => `\\textcolor{${color}}{${texNumber(value)}}`;
  const rows = [0, 1].map((row) => `${entry(first[row], palette.yellow)} & ${entry(second[row], palette.blue)}`);
  return `\\begin{bmatrix} ${rows.join(" \\\\ ")} \\end{bmatrix}`;
}

function weightsTex(weights: Vec): string {
  return `\\begin{bmatrix} \\textcolor{${palette.yellow}}{${texNumber(weights[0])}} \\\\ \\textcolor{${palette.blue}}{${texNumber(weights[1])}} \\end{bmatrix}`;
}

/** A x as the weighted sum of the columns of a 2 by 2 matrix, with slider weights and a target to land on. */
export function MatrixVectorExplorer({ columns, target, success }: { columns: Columns; target: Vec; success?: string }) {
  const [x1, setX1] = useState(1);
  const [x2, setX2] = useState(1);
  const scaledFirst = scale(x1, columns[0]);
  const result = add(scaledFirst, scale(x2, columns[1]));
  const { settled: solved, gesture } = useSettled(nearlyEqual(result, target));
  const product = `${coloredMatrixTex(columns)}${weightsTex([x1, x2])} = ${columnTex(result, palette.teal)}`;
  const combination = `${texNumber(x1)}${columnTex(columns[0], palette.yellow)} + ${texNumber(x2)}${columnTex(columns[1], palette.blue)}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Set the weights in <Tex>{"\\mathbf x"}</Tex> so that <Tex>{"A\\mathbf x"}</Tex> lands on the ringed point <Tex>{columnTex(target)}</Tex>.</>}
        success={success ? <RichText>{success}</RichText> : <>You solved <Tex>{`A\\mathbf x = ${columnTex(target)}`}</Tex> with <Tex>{`\\mathbf x = ${columnTex([x1, x2])}`}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([target, ...columns])} label="The columns of A scaled by the weights in x and added tip to tail. Use the two sliders.">
            {!solved ? <Marker at={target} ring /> : null}
            <Arrow to={columns[0]} color="yellow" width={1.5} dashed />
            <Arrow to={columns[1]} color="blue" width={1.5} dashed />
            <Arrow to={scaledFirst} color="yellow" />
            <Arrow from={scaledFirst} to={result} color="blue" />
            <Arrow to={result} color="teal" />
            {solved ? <Marker at={target} color="teal" /> : null}
          </Plane>
        }
        readout={
          <>
            <Slider label="x_1" value={x1} onChange={setX1} min={-3} max={3} step={0.5} color={palette.yellow} />
            <Slider label="x_2" value={x2} onChange={setX2} min={-3} max={3} step={0.5} color={palette.blue} />
            <Readout tex={product} />
            <Readout tex={`= ${combination}`} />
          </>
        }
      />
    </Panel>
  );
}

function signedTerm(coefficient: number, name: string, first: boolean): string {
  if (coefficient === 0) return "";
  const size = Math.abs(coefficient) === 1 ? "" : texNumber(Math.abs(coefficient));
  if (first) return `${coefficient < 0 ? "-" : ""}${size}${name}`;
  return ` ${coefficient < 0 ? "-" : "+"} ${size}${name}`;
}

/** The last entry of [A b] after clearing the second row: p b_2 - q b_1 for a first column (p, q). */
function consistencyTerms([p, q]: Vec): [number, number] {
  return [-q, p];
}

function conditionTex(terms: [number, number]): string {
  const first = signedTerm(terms[0], "b_1", true);
  return first + signedTerm(terms[1], "b_2", first === "");
}

function SpanLine({ direction, lit }: { direction: Vec; lit: boolean }) {
  const { toSvg } = usePlane();
  const reach = 40;
  const [x1, y1] = toSvg(scale(-reach, direction));
  const [x2, y2] = toSvg(scale(reach, direction));
  return (
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke="var(--palette-teal)"
      strokeOpacity={lit ? 0.9 : 0.4}
      strokeWidth={lit ? 4 : 2.5}
      className="transition-[stroke-opacity,stroke-width] duration-300"
    />
  );
}

/** Two parallel columns span only a line; the learner drags b and the reduced augmented matrix reports consistency. */
export function ColumnSpanCheck({ columns, start }: { columns: Columns; start: Vec }) {
  const [b, setB] = useState<Vec>(start);
  const terms = consistencyTerms(columns[0]);
  const lastEntry = terms[0] * b[0] + terms[1] * b[1];
  const onLine = Math.abs(lastEntry) < 1e-9 && !nearlyEqual(b, [0, 0]);
  const { settled: solved, gesture } = useSettled(onLine);
  const [p] = columns[0];
  const lastColor = solved ? palette.teal : palette.text;
  const reduced = `\\begin{bmatrix} ${texNumber(p)} & ${texNumber(columns[1][0])} & ${texNumber(b[0])} \\\\ 0 & 0 & \\textcolor{${lastColor}}{${texNumber(lastEntry)}} \\end{bmatrix}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf b"}</Tex> to a point other than the origin where <Tex>{"A\\mathbf x = \\mathbf b"}</Tex> has a solution.</>}
        success={<>That works. Here <Tex>{`${conditionTex(terms)} = 0`}</Tex>, so the last row reads <Tex>{"0 = 0"}</Tex> and <Tex>{"\\mathbf b"}</Tex> sits on the line the columns span.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([start, ...columns])} label="The line spanned by two parallel columns and a draggable vector b. Drag its tip or use arrow keys.">
            <SpanLine direction={columns[0]} lit={solved} />
            <Arrow to={columns[1]} color="blue" />
            <Arrow to={columns[0]} color="yellow" />
            <Arrow to={b} color={solved ? "teal" : "text"} />
            <Label at={b} color={solved ? "teal" : "text"}>b</Label>
            <Handle at={b} onMove={setB} color={solved ? "teal" : "glow"} label={`Tip of vector b, at ${describeVector(b)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\begin{bmatrix} A & \\mathbf b \\end{bmatrix} \\sim ${reduced}`} />
            <Readout tex={`\\text{last entry} = ${conditionTex(terms)}`} />
          </>
        }
      />
    </Panel>
  );
}

const ENTRY_COLORS = [palette.i_hat, palette.j_hat];

function rowRuleTex(row: Vec, x: Vec, target: number, color: string): string {
  const value = row[0] * x[0] + row[1] * x[1];
  const holds = Math.abs(value - target) < 1e-9;
  const mark = holds ? `\\textcolor{${palette.teal}}{\\checkmark}` : "\\phantom{\\checkmark}";
  const products = `\\textcolor{${color}}{${texNumber(row[0])}}(${texNumber(x[0])}) + (\\textcolor{${color}}{${texNumber(row[1])}})(${texNumber(x[1])})`;
  return `${products} &= ${texNumber(value)} & ${mark}`;
}

/** The row picture of A x = b: each row of A sets one entry of A x, and the solution x sits where the two row lines cross. */
export function RowPictureSolver({ rows, b, solution }: { rows: [Vec, Vec]; b: Vec; solution: Vec }) {
  const [x, setX] = useState<Vec>([0, 0]);
  const values = rows.map((row) => row[0] * x[0] + row[1] * x[1]);
  const { settled: solved, gesture } = useSettled(values.every((value, i) => Math.abs(value - b[i]) < 1e-9));
  const lines = rows.map((row, i) => [row[0], row[1], b[i]] as [number, number, number]);
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf x"}</Tex> so that both rows of <Tex>{`A\\mathbf x`}</Tex> match <Tex>{`\\mathbf b = ${columnTex(b)}`}</Tex>. Each colored line shows where one row matches.</>}
        success={<>Both rows hold at <Tex>{`\\mathbf x = ${columnTex(solution)}`}</Tex>. The column picture found the same weights, because the row rule and the column rule compute the same product.</>}
      />
      <Workbench
        plane={
          <Plane bounds={{ xMin: -3, xMax: 5, yMin: -4, yMax: 4 }} label="The plane of inputs x, with one line for each row of A x = b. Drag x or use arrow keys.">
            <EquationLine row={lines[0]} color="green" />
            <EquationLine row={lines[1]} color="red" />
            {solved ? <Marker at={x} color="teal" ring /> : null}
            <Arrow to={x} color="yellow" />
            <Label at={x} color="yellow" dx={12} dy={-12}>x</Label>
            <Handle at={x} onMove={setX} color="yellow" label={`Tip of vector x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\begin{aligned} ${rows.map((row, i) => rowRuleTex(row, x, b[i], ENTRY_COLORS[i])).join(" \\\\ ")} \\end{aligned}`} />
            <Readout tex={`A\\mathbf x = \\begin{bmatrix} \\textcolor{${ENTRY_COLORS[0]}}{${texNumber(values[0])}} \\\\ \\textcolor{${ENTRY_COLORS[1]}}{${texNumber(values[1])}} \\end{bmatrix}`} />
          </>
        }
      />
    </Panel>
  );
}

type Grid = number[][];

const tidyEntry = (value: number) => (Math.abs(value - Math.round(value)) < 1e-9 ? Math.round(value) + 0 : value);

function clearBelow(rows: Grid, pivotRow: number, column: number): Grid {
  return rows.map((row, i) => {
    if (i <= pivotRow) return row;
    const factor = row[column] / rows[pivotRow][column];
    return row.map((entry, j) => tidyEntry(entry - factor * rows[pivotRow][j]));
  });
}

/** The forward phase of row reduction, returning an echelon form and its pivot positions. */
function forwardPhase(matrix: Grid): { rows: Grid; pivots: string[] } {
  let rows = matrix.map((row) => [...row]);
  const pivots: string[] = [];
  for (let column = 0; column < rows[0].length && pivots.length < rows.length; column += 1) {
    const top = pivots.length;
    const found = rows.findIndex((row, i) => i >= top && Math.abs(row[column]) > 1e-9);
    if (found === -1) continue;
    rows = rows.map((row, i) => (i === top ? rows[found] : i === found ? rows[top] : row));
    rows = clearBelow(rows, top, column);
    pivots.push(`${top},${column}`);
  }
  return { rows, pivots };
}

function gridTex(rows: Grid, color: (row: number, column: number) => string | null): string {
  const body = rows.map((row, r) => row.map((entry, c) => {
    const tint = color(r, c);
    return tint ? `\\textcolor{${tint}}{${texNumber(entry)}}` : texNumber(entry);
  }).join(" & ")).join(" \\\\ ");
  return `\\begin{bmatrix} ${body} \\end{bmatrix}`;
}

/** One entry of a 3 by 3 matrix is a slider. The echelon form updates live, and the goal is the value that leaves a row without a pivot. */
export function SpanBreaker({ matrix, entry, min, max, start, answer }: { matrix: Grid; entry: [number, number]; min: number; max: number; start: number; answer: number }) {
  const [k, setK] = useState(start);
  const current = matrix.map((row, r) => row.map((value, c) => (r === entry[0] && c === entry[1] ? k : value)));
  const { rows, pivots } = forwardPhase(current);
  const { settled: solved, gesture } = useSettled(pivots.length < matrix.length);
  const pivotSet = new Set(pivots);
  const echelon = gridTex(rows, (r, c) => (pivotSet.has(`${r},${c}`) ? palette.glow : null));
  const original = gridTex(current, (r, c) => (r === entry[0] && c === entry[1] ? palette.blue : null));
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide <Tex>k</Tex> until some row of the echelon form has no pivot. The orange entries are the pivots.</>}
        success={<>At <Tex>{`k = ${texNumber(answer)}`}</Tex> the last row of the echelon form is all zeros. The columns of <Tex>A</Tex> then span only a plane, so <Tex>{"A\\mathbf x = \\mathbf b"}</Tex> has no solution for some <Tex>{"\\mathbf b"}</Tex>.</>}
      />
      <div className="space-y-4">
        <Slider label="k" value={k} onChange={setK} min={min} max={max} step={1} color={palette.blue} />
        <div className="grid items-center gap-4 rounded-media bg-surface-sunken px-4 py-5 sm:grid-cols-2 [&_.katex]:text-[1.2em]">
          <div className="text-center"><Tex display>{`A = ${original}`}</Tex></div>
          <div className="text-center"><Tex display>{`\\sim ${echelon}`}</Tex></div>
        </div>
        <Readout tex={`\\text{rows with a pivot: } ${pivots.length} \\text{ of } ${matrix.length}`} />
      </div>
    </Panel>
  );
}
