"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { useSettled } from "./gesture";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { hue, type Hue } from "./colors";
import { add, scale, texNumber, type Vec } from "./math";
import { Arrow, boundsAround, Handle, Label, Marker, Plane, Segment, usePlane } from "./plane";

const cross = (a: Vec, b: Vec) => a[0] * b[1] - a[1] * b[0];
const isZero = (v: Vec) => v[0] === 0 && v[1] === 0;

function Line({ through, direction, color, width, opacity }: { through: Vec; direction: Vec; color: Hue; width: number; opacity: number }) {
  const { toSvg, bounds } = usePlane();
  const span = bounds.xMax - bounds.xMin + bounds.yMax - bounds.yMin + Math.hypot(...through);
  const reach = span / Math.max(Math.hypot(...direction), 1e-9);
  const [x1, y1] = toSvg(add(through, scale(-reach, direction)));
  const [x2, y2] = toSvg(add(through, scale(reach, direction)));
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={width} strokeOpacity={opacity} strokeLinecap="round" />;
}

const MAX_LINES_PER_FAMILY = 200;

/** The whole-number weights k whose line k·offset + t·direction crosses the visible plane. */
function weightsCovering(offset: Vec, direction: Vec, corners: Vec[]): number[] {
  const denominator = cross(direction, offset);
  if (denominator === 0) return [0];
  const reached = corners.map((corner) => cross(direction, corner) / denominator);
  const low = Math.max(Math.floor(Math.min(...reached)), -MAX_LINES_PER_FAMILY / 2);
  const high = Math.min(Math.ceil(Math.max(...reached)), MAX_LINES_PER_FAMILY / 2);
  return Array.from({ length: high - low + 1 }, (_, i) => low + i);
}

/** Lines of a·v + t·w and t·v + b·w for whole-number weights, enough of them to reach every corner of the plane. */
function SkewedGrid({ v, w }: { v: Vec; w: Vec }) {
  const { bounds } = usePlane();
  const corners: Vec[] = [[bounds.xMin, bounds.yMin], [bounds.xMin, bounds.yMax], [bounds.xMax, bounds.yMin], [bounds.xMax, bounds.yMax]];
  return (
    <g aria-hidden>
      {isZero(w) ? null : weightsCovering(v, w, corners).map((k) => <Line key={`v${k}`} through={scale(k, v)} direction={w} color="teal" width={1.2} opacity={0.45} />)}
      {isZero(v) ? null : weightsCovering(w, v, corners).map((k) => <Line key={`w${k}`} through={scale(k, w)} direction={v} color="teal" width={1.2} opacity={0.45} />)}
    </g>
  );
}

function spanName(v: Vec, w: Vec): string {
  if (isZero(v) && isZero(w)) return "\\{\\vec 0\\}";
  return cross(v, w) === 0 ? "\\text{a line}" : "\\mathbb{R}^2";
}

export function SpanPainter({ v: startV = [3, 2], w: startW = [-1, 2] }: { v?: Vec; w?: Vec }) {
  const [v, setV] = useState<Vec>(startV);
  const [w, setW] = useState<Vec>(startW);
  const collapsed = !isZero(v) && cross(v, w) === 0;
  const { settled: solved, gesture } = useSettled(collapsed);
  const determinant = cross(v, w);
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The teal lines show where <Tex>{"a\\vec v + b\\vec w"}</Tex> can land. Move <Tex>{"\\vec w"}</Tex> until the span shrinks to a single line.</>}
        success={<>Now <Tex>{"\\vec w"}</Tex> is a multiple of <Tex>{"\\vec v"}</Tex>, so every combination is a multiple of <Tex>{"\\vec v"}</Tex> and lands on the one teal line.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([startV, startW])} label="Plane with vectors v and w and the lines their combinations cover. Drag either tip.">
            <SkewedGrid v={v} w={w} />
            {solved ? <Line through={[0, 0]} direction={v} color="teal" width={4} opacity={1} /> : null}
            <Arrow to={w} color="blue" />
            <Arrow to={v} color="yellow" />
            <Label at={v} color="yellow">v</Label>
            <Label at={w} color="blue" dx={-18}>w</Label>
            <Handle at={w} onMove={setW} color="blue" label={`Tip of vector w, at ${describeVector(w)}`} />
            <Handle at={v} onMove={setV} color="yellow" label={`Tip of vector v, at ${describeVector(v)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\begin{aligned} &\\operatorname{Span}\\{${columnTex(v, palette.yellow)}, ${columnTex(w, palette.blue)}\\} \\\\ &= ${spanName(v, w)} \\end{aligned}`} />
            <Readout tex={`v_1 w_2 - v_2 w_1 = ${texNumber(determinant)}`} />
          </>
        }
      />
    </Panel>
  );
}

export function EntryHunt({ v = [2, 1], w = [-4, -2], x = 4, answer = 2, min = -3, max = 4 }: {
  v?: Vec; w?: Vec; x?: number; answer?: number; min?: number; max?: number;
}) {
  const [h, setH] = useState(min);
  const b: Vec = [x, h];
  const { settled: solved, gesture } = useSettled(h === answer);
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Every <Tex>{`\\vec b = \\begin{bmatrix} ${texNumber(x)} \\\\ h \\end{bmatrix}`}</Tex> sits on the dashed line. Find the <Tex>h</Tex> that puts <Tex>{"\\vec b"}</Tex> in <Tex>{"\\operatorname{Span}\\{\\vec v, \\vec w\\}"}</Tex>.</>}
        success={<>Right, <Tex>{`h = ${texNumber(answer)}`}</Tex>. The dashed line crosses the span in exactly one place, so only one <Tex>h</Tex> works.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([v, w, [x, min], [x, max]])} label={`Span of v and w, and the vector b equal to (${x}, h)`}>
            <Line through={[0, 0]} direction={v} color="teal" width={3} opacity={0.8} />
            <Segment from={[x, min - 1]} to={[x, max + 1]} color="text" />
            <Arrow to={w} color="blue" />
            <Arrow to={v} color="yellow" />
            <Arrow to={b} color="pink" />
            <Label at={v} color="yellow" dx={-6} dy={-14}>v</Label>
            <Label at={w} color="blue" dx={-18} dy={18}>w</Label>
            <Label at={b} color="pink">b</Label>
            {solved ? <Marker at={b} color="teal" /> : null}
          </Plane>
        }
        readout={
          <>
            <Slider label="h" value={h} onChange={setH} min={min} max={max} step={1} color={palette.pink} />
            <Readout tex={`x_1${columnTex(v, palette.yellow)} + x_2${columnTex(w, palette.blue)} = ${columnTex(b, palette.pink)}`} />
          </>
        }
      />
    </Panel>
  );
}

const sameChoices = (a: boolean[], b: boolean[]) => a.every((value, index) => value === b[index]);

function PickablePoint({ at, picked, onToggle, label }: { at: Vec; picked: boolean; onToggle: () => void; label: string }) {
  const { toSvg } = usePlane();
  const [x, y] = toSvg(at);
  const onKeyDown = (event: React.KeyboardEvent) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    event.preventDefault();
    onToggle();
  };
  return (
    <g role="checkbox" tabIndex={0} aria-checked={picked} aria-label={label} className="group cursor-pointer outline-none" onClick={onToggle} onKeyDown={onKeyDown}>
      <circle cx={x} cy={y} r={20} fill="transparent" />
      <circle cx={x} cy={y} r={16} fill="none" stroke="var(--palette-yellow)" strokeWidth={2.5} className="opacity-0 group-focus-visible:opacity-100" />
      {picked ? (
        <>
          <circle cx={x} cy={y} r={11} fill={hue("glow")} />
          <path d={`M${x - 5},${y} l3.5,3.5 l6.5,-7`} fill="none" stroke="var(--color-surface-sunken)" strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
        </>
      ) : (
        <circle cx={x} cy={y} r={7} fill="var(--color-surface-sunken)" stroke={hue("text")} strokeOpacity={0.7} strokeWidth={2} />
      )}
    </g>
  );
}

/** Dots to sort into "in the span" or not, for a w that is a multiple of v, so the span is one line. */
export function LineSpanPicker({ v, w, points }: { v: Vec; w: Vec; points: Vec[] }) {
  const [picked, setPicked] = useState<boolean[]>(points.map(() => false));
  const inSpan = points.map((point) => cross(v, point) === 0);
  const { settled: solved, gesture } = useSettled(sameChoices(picked, inSpan));
  const ratio = (w[0] * v[0] + w[1] * v[1]) / (v[0] * v[0] + v[1] * v[1]);
  const toggle = (index: number) => setPicked((current) => current.map((value, i) => (i === index ? !value : value)));
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Tap every dot that is in <Tex>{"\\operatorname{Span}\\{\\vec v, \\vec w\\}"}</Tex> and leave the others alone.</>}
        success={<>That&rsquo;s the whole set. Every combination is a multiple of <Tex>{"\\vec v"}</Tex>, so the span is the teal line, and the origin is on it.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([...points, v, w])} label="Plane with vectors v and w and several dots to sort. Tab to a dot and press Enter to pick it.">
            {solved ? <Line through={[0, 0]} direction={v} color="teal" width={4} opacity={0.9} /> : null}
            <Arrow to={w} color="blue" />
            <Arrow to={v} color="yellow" />
            <Label at={v} color="yellow" dx={-4} dy={-16}>v</Label>
            <Label at={w} color="blue" dx={-18} dy={22}>w</Label>
            {points.map((point, index) => (
              <PickablePoint
                key={index}
                at={point}
                picked={picked[index]}
                onToggle={() => toggle(index)}
                label={`Dot at ${describeVector(point)}`}
              />
            ))}
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\vec w = ${texNumber(ratio)}\\,\\vec v`} />
            <Readout tex={`a\\vec v + b\\vec w = (a ${ratio < 0 ? "-" : "+"} ${texNumber(Math.abs(ratio))}b)\\,\\vec v`} />
          </>
        }
      />
    </Panel>
  );
}

type Row = { u: number; v: number; rhs: number };

const rowHolds = (row: Row, point: Vec) => Math.abs(row.u * point[0] + row.v * point[1] - row.rhs) < 1e-9;

function leadingTerm(coefficient: number, variable: string): string {
  if (coefficient === 1) return variable;
  if (coefficient === -1) return `-${variable}`;
  return `${texNumber(coefficient)}${variable}`;
}

function trailingTerm(coefficient: number, variable: string): string {
  const size = Math.abs(coefficient);
  return `${coefficient < 0 ? "-" : "+"} ${size === 1 ? "" : texNumber(size)}${variable}`;
}

function rowTex(row: Row, color: string, holds: boolean): string {
  const mark = holds ? `\\textcolor{${palette.teal}}{\\checkmark}` : "\\phantom{\\checkmark}";
  return `\\textcolor{${color}}{${leadingTerm(row.u, "x_1")} ${trailingTerm(row.v, "x_2")}} &= ${texNumber(row.rhs)} && ${mark}`;
}

function RowLine({ row, color }: { row: Row; color: Hue }) {
  const lengthSquared = row.u * row.u + row.v * row.v;
  const through = scale(row.rhs / lengthSquared, [row.u, row.v]);
  return <Line through={through} direction={[-row.v, row.u]} color={color} width={3} opacity={0.85} />;
}

const ROW_HUES: Hue[] = ["yellow", "blue", "pink"];
const ROW_COLORS = [palette.yellow, palette.blue, palette.pink];

/** The weight plane for x₁u + x₂v = b in R³. Each row of the system is a line of weights, and b is in the span when all three lines meet. */
export function RowLinesMeet({ u, v, b, answer, solution, min = -2, max = 6 }: {
  u: number[]; v: number[]; b: [number, number]; answer: number; solution: Vec; min?: number; max?: number;
}) {
  const [h, setH] = useState(min);
  const [weights, setWeights] = useState<Vec>([0, 0]);
  const rows: Row[] = [0, 1, 2].map((i) => ({ u: u[i], v: v[i], rhs: i < 2 ? b[i] : h }));
  const holds = rows.map((row) => rowHolds(row, weights));
  const { settled: solved, gesture } = useSettled(holds.every(Boolean));
  const system = rows.map((row, i) => rowTex(row, ROW_COLORS[i], holds[i])).join(" \\\\ ");
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Each row of the system is a line of weights. Slide <Tex>h</Tex> until all three lines meet, then drag the teal weight point onto the meeting point.</>}
        success={<>All three rows hold at <Tex>{`x_1 = ${texNumber(solution[0])},\\ x_2 = ${texNumber(solution[1])}`}</Tex> when <Tex>{`h = ${texNumber(answer)}`}</Tex>. For any other <Tex>h</Tex> the pink line misses that crossing.</>}
      />
      <Workbench
        plane={
          <Plane bounds={{ xMin: -3, xMax: 5, yMin: -2, yMax: 5 }} label="Weight plane with axes x1 and x2 and one line per row of the system. Drag the weight point or use arrow keys.">
            {rows.map((row, i) => (
              <RowLine key={i} row={row} color={ROW_HUES[i]} />
            ))}
            <Label at={[4.4, 0]} color="text" dx={-4} dy={-8}>x₁</Label>
            <Label at={[0, 4.4]} color="text" dx={8} dy={4}>x₂</Label>
            {solved ? <Marker at={weights} color="teal" ring /> : null}
            <Handle at={weights} onMove={setWeights} color="teal" label={`Weights x1 and x2, at ${describeVector(weights)}`} />
          </Plane>
        }
        readout={
          <>
            <Slider label="h" value={h} onChange={setH} min={min} max={max} step={1} color={palette.pink} />
            <Readout tex={`\\begin{aligned} ${system} \\end{aligned}`} />
            <Readout tex={`(x_1, x_2) = (${texNumber(weights[0])}, ${texNumber(weights[1])})`} />
          </>
        }
      />
    </Panel>
  );
}
