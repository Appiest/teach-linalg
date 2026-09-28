"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { columnTex, describeVector, Goal, Panel, Readout, RichText, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, nearlyEqual, scale, texNumber, type Vec } from "./math";
import { Arrow, boundsAround, Handle, Label, Marker, Plane, usePlane } from "./plane";

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
