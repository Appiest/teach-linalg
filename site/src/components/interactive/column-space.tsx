"use client";

import { Check } from "@phosphor-icons/react";
import { useId, useState } from "react";
import { palette } from "@/lib/palette.generated";
import { describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { hue, type Hue } from "./colors";
import { useSettled } from "./gesture";
import { add, scale, texNumber, type Vec } from "./math";
import { Arrow, Handle, Label, Marker, Plane, Segment } from "./plane";

type Vec3 = [number, number, number];

const VIEW = { width: 320, height: 280, unit: 34, azimuth: (60 * Math.PI) / 180, elevation: (20 * Math.PI) / 180 };
const ORIGIN_SVG: Vec = [VIEW.width / 2, VIEW.height / 2 + 8];
const FLOOR_REACH = 3;
const SHEET_STEPS = [-2, -1, 0, 1, 2];
const INPUT_BOUNDS = { xMin: -3, xMax: 3, yMin: -3, yMax: 3 };

const add3 = (a: Vec3, b: Vec3): Vec3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const scale3 = (c: number, v: Vec3): Vec3 => [c * v[0], c * v[1], c * v[2]];
const combine = (s: number, u: Vec3, t: number, v: Vec3): Vec3 => add3(scale3(s, u), scale3(t, v));
const same3 = (a: Vec3, b: Vec3) => a.every((value, index) => Math.abs(value - b[index]) < 1e-9);

/** The same fixed oblique view the video uses: x toward the viewer, y to the right, z up. */
function project([x, y, z]: Vec3): Vec {
  const { azimuth, elevation, unit } = VIEW;
  const across = -x * Math.sin(azimuth) + y * Math.cos(azimuth);
  const depth = x * Math.cos(azimuth) + y * Math.sin(azimuth);
  const up = z * Math.cos(elevation) - depth * Math.sin(elevation);
  return [ORIGIN_SVG[0] + unit * across, ORIGIN_SVG[1] - unit * up];
}

const tripleTex = (v: Vec3) => `(${v.map((value) => texNumber(value)).join(", ")})`;
const columnTex3 = (v: Vec3, color?: string) => {
  const body = `\\begin{bmatrix} ${v.map((value) => texNumber(value)).join(" \\\\ ")} \\end{bmatrix}`;
  return color ? `\\textcolor{${color}}{${body}}` : body;
};

function Line3({ from, to, stroke, width = 1, opacity = 1 }: { from: Vec3; to: Vec3; stroke: string; width?: number; opacity?: number }) {
  const [x1, y1] = project(from);
  const [x2, y2] = project(to);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={stroke} strokeWidth={width} strokeOpacity={opacity} />;
}

function FloorAndAxes() {
  const ticks = Array.from({ length: 2 * FLOOR_REACH + 1 }, (_, index) => index - FLOOR_REACH);
  return (
    <g aria-hidden>
      {ticks.map((k) => (
        <g key={k}>
          <Line3 from={[k, -FLOOR_REACH, 0]} to={[k, FLOOR_REACH, 0]} stroke="var(--palette-grid-faint)" />
          <Line3 from={[-FLOOR_REACH, k, 0]} to={[FLOOR_REACH, k, 0]} stroke="var(--palette-grid-faint)" />
        </g>
      ))}
      <Line3 from={[-FLOOR_REACH, 0, 0]} to={[FLOOR_REACH + 0.4, 0, 0]} stroke="var(--palette-axis)" width={1.4} />
      <Line3 from={[0, -FLOOR_REACH, 0]} to={[0, FLOOR_REACH + 0.4, 0]} stroke="var(--palette-axis)" width={1.4} />
      <Line3 from={[0, 0, -2.5]} to={[0, 0, 3]} stroke="var(--palette-axis)" width={1.4} />
    </g>
  );
}

/** The patch s*u + t*v for s, t in [-2, 2], with its grid lines, drawn as a translucent teal sheet. */
function Sheet({ u, v, lit }: { u: Vec3; v: Vec3; lit: boolean }) {
  const corners = [[-2, -2], [2, -2], [2, 2], [-2, 2]].map(([s, t]) => project(combine(s, u, t, v)).join(",")).join(" ");
  return (
    <g aria-hidden>
      <polygon points={corners} fill="var(--palette-teal)" fillOpacity={lit ? 0.28 : 0.16} className="transition-[fill-opacity] duration-300" />
      {SHEET_STEPS.map((k) => (
        <g key={k}>
          <Line3 from={combine(k, u, -2, v)} to={combine(k, u, 2, v)} stroke="var(--palette-teal)" opacity={0.55} />
          <Line3 from={combine(-2, u, k, v)} to={combine(2, u, k, v)} stroke="var(--palette-teal)" opacity={0.55} />
        </g>
      ))}
    </g>
  );
}

function Arrow3({ to, color, markerPrefix, width = 3 }: { to: Vec3; color: Hue; markerPrefix: string; width?: number }) {
  const [x1, y1] = project([0, 0, 0]);
  const [x2, y2] = project(to);
  if (Math.hypot(x2 - x1, y2 - y1) < 2) return null;
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={width} strokeLinecap="round" markerEnd={`url(#${markerPrefix}-${color})`} />;
}

function SpaceView({ label, colors, children }: { label: string; colors: Hue[]; children: (markerPrefix: string) => React.ReactNode }) {
  const markerPrefix = useId().replaceAll(":", "");
  return (
    <svg viewBox={`0 0 ${VIEW.width} ${VIEW.height}`} role="img" aria-label={label} className="block h-auto w-full select-none rounded-media bg-surface-sunken">
      <defs>
        {colors.map((name) => (
          <marker key={name} id={`${markerPrefix}-${name}`} viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill={hue(name)} />
          </marker>
        ))}
      </defs>
      <FloorAndAxes />
      {children(markerPrefix)}
    </svg>
  );
}

function Ring3({ at, solved }: { at: Vec3; solved: boolean }) {
  const [x, y] = project(at);
  return (
    <g>
      <circle cx={x} cy={y} r={11} fill="none" stroke={solved ? "var(--palette-teal)" : "var(--palette-glow)"} strokeWidth={2} strokeDasharray={solved ? undefined : "4 4"} />
      <circle cx={x} cy={y} r={4} fill={solved ? "var(--palette-teal)" : "var(--palette-glow)"} />
    </g>
  );
}

/** Drag the input x in the plane and watch Ax move across the tilted plane Col A in space. */
export function OutputReach({ columns, target }: { columns: [Vec3, Vec3]; target: Vec3 }) {
  const [x, setX] = useState<Vec>([1, 1]);
  const output = combine(x[0], columns[0], x[1], columns[1]);
  const { settled: solved, gesture } = useSettled(same3(output, target));
  const matrixTex = `\\begin{bmatrix} ${[0, 1, 2].map((row) => `\\textcolor{${palette.i_hat}}{${columns[0][row]}} & \\textcolor{${palette.j_hat}}{${columns[1][row]}}`).join(" \\\\ ")} \\end{bmatrix}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf x"}</Tex> so that <Tex>{"A\\mathbf x"}</Tex> lands on the ringed point <Tex>{tripleTex(target)}</Tex> in space.</>}
        success={<>The input <Tex>{`(${texNumber(x[0])}, ${texNumber(x[1])})`}</Tex> lands there, so <Tex>{tripleTex(target)}</Tex> is in <Tex>{"\\operatorname{Col}A"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={INPUT_BOUNDS} label="The input plane with a draggable vector x. Drag its tip or use arrow keys.">
            <Arrow to={[1, 0]} color="green" width={2.5} />
            <Arrow to={[0, 1]} color="red" width={2.5} />
            <Arrow to={x} color="yellow" />
            <Label at={x} color="yellow">x</Label>
            <Handle at={x} onMove={setX} color="yellow" label={`Tip of the input x, at (${x[0]}, ${x[1]})`} />
          </Plane>
        }
        readout={
          <>
            <SpaceView label={`Three-dimensional view of the plane Col A with the output Ax at (${output.join(", ")})`} colors={["green", "red", "teal"]}>
              {(prefix) => (
                <>
                  <Sheet u={columns[0]} v={columns[1]} lit={solved} />
                  <Arrow3 to={columns[0]} color="green" markerPrefix={prefix} />
                  <Arrow3 to={columns[1]} color="red" markerPrefix={prefix} />
                  <Ring3 at={target} solved={solved} />
                  <Arrow3 to={output} color="teal" markerPrefix={prefix} width={3.5} />
                </>
              )}
            </SpaceView>
            <Readout tex={`${matrixTex}\\begin{bmatrix} ${texNumber(x[0])} \\\\ ${texNumber(x[1])} \\end{bmatrix} = ${columnTex3(output, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}

type Matrix34 = [number[], number[], number[]];

const columnOf = (matrix: Matrix34, index: number): Vec3 => [matrix[0][index], matrix[1][index], matrix[2][index]];
const sameSet = (picked: number[], wanted: number[]) => picked.length === wanted.length && wanted.every((index) => picked.includes(index));

function matrixTex(matrix: Matrix34, highlight: number[] = []) {
  const entry = (value: number, column: number) => (highlight.includes(column) ? `\\textcolor{${palette.glow}}{${texNumber(value)}}` : texNumber(value));
  return `\\begin{bmatrix} ${matrix.map((row) => row.map(entry).join(" & ")).join(" \\\\ ")} \\end{bmatrix}`;
}

function ColumnButton({ index, column, picked, onToggle }: { index: number; column: Vec3; picked: boolean; onToggle: () => void }) {
  return (
    <button
      type="button"
      aria-pressed={picked}
      aria-label={`Column ${index + 1} of A, ${column.join(", ")}`}
      onClick={onToggle}
      className={`relative grid place-items-center rounded-lg px-3 py-2 transition-[background-color,box-shadow] duration-200 ${
        picked ? "bg-line ring-2 ring-[var(--palette-text)]" : "bg-surface-sunken hover:bg-line"
      }`}
    >
      <Tex>{columnTex3(column)}</Tex>
      <span className="mt-1 text-meta text-text-muted">
        <Tex>{`\\mathbf a_${index + 1}`}</Tex>
      </span>
      <span className={`absolute right-1.5 top-1.5 ${picked ? "swap-shown" : "swap-hidden"}`} aria-hidden>
        <Check weight="bold" className="size-3.5 text-text" />
      </span>
    </button>
  );
}

/** Pick the columns of A that form a basis for Col A, using the reduced echelon form as the guide. */
export function PivotPicker({ matrix, reduced, pivots }: { matrix: Matrix34; reduced: Matrix34; pivots: number[] }) {
  const [picked, setPicked] = useState<number[]>([]);
  const { settled: solved, gesture } = useSettled(sameSet(picked, pivots));
  const toggle = (index: number) => setPicked((current) => (current.includes(index) ? current.filter((value) => value !== index) : [...current, index].sort()));
  const names = pivots.map((index) => `\\mathbf a_${index + 1}`).join(", ");

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Tap the columns of <Tex>{"A"}</Tex> that form a basis for <Tex>{"\\operatorname{Col}A"}</Tex>. The reduced form shows where the pivots are.</>}
        success={<>That is the basis <Tex>{`\\{${names}\\}`}</Tex>. Each other column is a combination of these, with the same weights you can read off the reduced form.</>}
      />
      <div className="grid items-start gap-5 md:grid-cols-[1.35fr_1fr]">
        <div role="group" aria-label="Columns of A" className="grid grid-cols-4 gap-2">
          {matrix[0].map((_, index) => (
            <ColumnButton key={index} index={index} column={columnOf(matrix, index)} picked={picked.includes(index)} onToggle={() => toggle(index)} />
          ))}
        </div>
        <Readout tex={`A \\sim ${matrixTex(reduced, solved ? pivots : [])}`} />
      </div>
    </Panel>
  );
}

/** Slide row 2 of B by adding c times row 1; the row arrow moves but never leaves the row space. */
export function RowSlide({ rows }: { rows: [Vec3, Vec3] }) {
  const [c, setC] = useState(0);
  const moved = add3(rows[1], scale3(c, rows[0]));
  const { settled: solved, gesture } = useSettled(Math.abs(moved[0]) < 1e-9);
  const rowTex = (row: Vec3, color: string) => row.map((value) => `\\textcolor{${color}}{${texNumber(value)}}`).join(" & ");
  const bTex = `\\begin{bmatrix} ${rowTex(rows[0], palette.i_hat)} \\\\ ${rowTex(moved, palette.j_hat)} \\end{bmatrix}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Choose <Tex>{"c"}</Tex> in <Tex>{"R_2 \\leftarrow R_2 + cR_1"}</Tex> so that row 2 starts with a zero.</>}
        success={<>Now <Tex>{"B"}</Tex> is in echelon form, and its nonzero rows <Tex>{`${tripleTex(rows[0])}`}</Tex> and <Tex>{tripleTex(moved)}</Tex> are a basis for <Tex>{"\\operatorname{Row}B"}</Tex>.</>}
      />
      <Workbench
        plane={
          <SpaceView label={`The row space of B as a plane in space, with row 1 in green and row 2 in red at (${moved.join(", ")})`} colors={["green", "red"]}>
            {(prefix) => (
              <>
                <Sheet u={rows[0]} v={add3(rows[1], scale3(-rows[1][0] / rows[0][0], rows[0]))} lit={solved} />
                <Arrow3 to={rows[0]} color="green" markerPrefix={prefix} />
                <Arrow3 to={moved} color="red" markerPrefix={prefix} />
              </>
            )}
          </SpaceView>
        }
        readout={
          <>
            <Slider label="c" value={c} onChange={setC} min={-3} max={3} step={0.5} color={palette.j_hat} />
            <Readout tex={`B = ${bTex}`} />
          </>
        }
      />
    </Panel>
  );
}

const LINE_BOUNDS = { xMin: -5, xMax: 5, yMin: -5, yMax: 5 };
const isZero = (value: number) => Math.abs(value) < 1e-9;
const columnTex2 = (v: Vec, color: string) => `\\textcolor{${color}}{\\begin{bmatrix} ${texNumber(v[0])} \\\\ ${texNumber(v[1])} \\end{bmatrix}}`;

/** Drag b and watch the last row of the reduced augmented matrix; it reads 0 = 0 exactly when b is on the line Col A. */
export function ConsistencyLine({ columns }: { columns: [Vec, Vec] }) {
  const [b, setB] = useState<Vec>([3, 1]);
  const [first, second] = columns;
  const leftover = b[1] - (first[1] / first[0]) * b[0];
  const { settled: solved, gesture } = useSettled(isZero(leftover) && !(b[0] === 0 && b[1] === 0));
  const leftoverColor = isZero(leftover) ? palette.teal : palette.glow;
  const augmented = `\\left[\\begin{array}{cc|c} ${first[0]} & ${second[0]} & ${texNumber(b[0])} \\\\ 0 & 0 & \\textcolor{${leftoverColor}}{${texNumber(leftover)}} \\end{array}\\right]`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf b"}</Tex> anywhere except the origin so that the last row of the reduced augmented matrix says <Tex>{"0 = 0"}</Tex>.</>}
        success={<>Now the system is consistent, so <Tex>{"\\mathbf b"}</Tex> is an output of <Tex>{"A"}</Tex>. Every output lies on the teal line, which is <Tex>{"\\operatorname{Col}A"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={LINE_BOUNDS} label="Plane with the two columns of A along one line and a draggable vector b">
            <g opacity={solved ? 0.95 : 0.45} className="transition-opacity duration-300">
              <Segment from={scale(-5, first)} to={scale(5, first)} color="teal" dashed={false} />
            </g>
            <Arrow to={first} color="green" />
            <Arrow to={second} color="red" />
            <Arrow to={b} color="yellow" />
            <Label at={b} color="yellow">b</Label>
            <Handle at={b} onMove={setB} color="yellow" label={`Tip of b, at ${describeVector(b)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\mathbf b = ${columnTex2(b, palette.yellow)}`} />
            <Readout tex={`[\\,A \\ \\ \\mathbf b\\,] \\sim ${augmented}`} />
          </>
        }
      />
    </Panel>
  );
}

const TWIN_BOUNDS = { xMin: -2, xMax: 5, yMin: -2, yMax: 5 };

function TwinPlane({ columns, weights, name, lit }: { columns: [Vec, Vec, Vec]; weights: Vec; name: string; lit: boolean }) {
  const [first, second, third] = columns;
  const partial = scale(weights[0], first);
  const result = add(partial, scale(weights[1], second));
  return (
    <figure className="min-w-0">
      <Plane bounds={TWIN_BOUNDS} label={`Columns of ${name}, with the combination of the first two at ${describeVector(result)} and the third column at ${describeVector(third)}`}>
        <Arrow to={first} color="green" width={2.5} />
        <Arrow to={second} color="red" width={2.5} />
        <Arrow to={third} color="pink" width={2.5} />
        <Segment from={[0, 0]} to={partial} color="green" />
        <Segment from={partial} to={result} color="red" />
        <Marker at={third} color={lit ? "teal" : "glow"} ring={!lit} />
        <Arrow to={result} color="teal" />
      </Plane>
      <figcaption className="mt-2 text-center text-meta text-text-muted">
        <Tex>{name}</Tex>
      </figcaption>
    </figure>
  );
}

/** One pair of weights drives a combination in A and in its reduced form B at once; the same weights reach column 3 in both. */
export function RelationTwins({ matrix, reduced, answer }: { matrix: [Vec, Vec, Vec]; reduced: [Vec, Vec, Vec]; answer: Vec }) {
  const [c1, setC1] = useState(0);
  const [c2, setC2] = useState(0);
  const inA = add(scale(c1, matrix[0]), scale(c2, matrix[1]));
  const reached = isZero(inA[0] - matrix[2][0]) && isZero(inA[1] - matrix[2][1]);
  const { settled: solved, gesture } = useSettled(reached);
  const relation = (name: string) => `${texNumber(c1)}\\,\\mathbf ${name}_1 + ${texNumber(c2)}\\,\\mathbf ${name}_2`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Choose weights so the teal arrow in the left picture lands on the pink third column of <Tex>{"A"}</Tex>. Keep an eye on the right picture as you go.</>}
        success={<>The weights <Tex>{`c_1 = ${answer[0]}`}</Tex> and <Tex>{`c_2 = ${answer[1]}`}</Tex> build the third column in both pictures, because row operations keep every relation among the columns.</>}
      />
      <div className="grid gap-4 sm:grid-cols-2">
        <TwinPlane columns={matrix} weights={[c1, c2]} name="A" lit={solved} />
        <TwinPlane columns={reduced} weights={[c1, c2]} name="B" lit={solved} />
      </div>
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <div className="space-y-3">
          <Slider label="c_1" value={c1} onChange={setC1} min={-3} max={3} step={1} color={palette.i_hat} />
          <Slider label="c_2" value={c2} onChange={setC2} min={-3} max={3} step={1} color={palette.j_hat} />
        </div>
        <div className="space-y-3">
          <Readout tex={relation("a")} />
          <Readout tex={relation("b")} />
        </div>
      </div>
    </Panel>
  );
}
