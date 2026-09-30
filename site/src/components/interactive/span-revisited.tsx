"use client";

import { createContext, useContext, useId, useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, nearlyEqual, scale, texNumber, type Vec } from "./math";
import { Arrow, Handle, Label, Marker, Plane, usePlane, type Bounds } from "./plane";

type Vec3 = [number, number, number];

const cross3 = (a: Vec3, b: Vec3): Vec3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const dot3 = (a: Vec3, b: Vec3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const combine3 = (s: number, a: Vec3, t: number, b: Vec3): Vec3 => [s * a[0] + t * b[0], s * a[1] + t * b[1], s * a[2] + t * b[2]];
const isZero3 = (v: Vec3) => v.every((entry) => entry === 0);
const parallel = (a: Vec3, b: Vec3) => isZero3(cross3(a, b));

const VIEW = { width: 440, height: 360, unit: 28, azimuth: (150 * Math.PI) / 180, elevation: (30 * Math.PI) / 180 };
const ORIGIN_SVG: [number, number] = [VIEW.width * 0.5, VIEW.height * 0.56];

/** A fixed oblique view: x toward the viewer, y to the right, z up. */
function project([x, y, z]: Vec3): [number, number] {
  const across = -x * Math.sin(VIEW.azimuth) + y * Math.cos(VIEW.azimuth);
  const depth = x * Math.cos(VIEW.azimuth) + y * Math.sin(VIEW.azimuth);
  const up = z * Math.cos(VIEW.elevation) - depth * Math.sin(VIEW.elevation);
  return [ORIGIN_SVG[0] + VIEW.unit * across, ORIGIN_SVG[1] - VIEW.unit * up];
}

const AXES: { end: Vec3; name: string }[] = [
  { end: [5, 0, 0], name: "x" },
  { end: [0, 7, 0], name: "y" },
  { end: [0, 0, 6], name: "z" },
];

function SpaceAxes() {
  return (
    <g aria-hidden>
      {AXES.map(({ end, name }) => {
        const [x1, y1] = project(end.map((value) => -value) as Vec3);
        const [x2, y2] = project(end);
        return (
          <g key={name}>
            <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--palette-axis)" strokeOpacity={0.7} strokeWidth={1.4} />
            <text x={x2 + 6} y={y2 + 4} fill="var(--palette-text-muted)" fontSize={15} fontStyle="italic" fontFamily="KaTeX_Math, serif">{name}</text>
          </g>
        );
      })}
    </g>
  );
}

const SHEET_REACH = 1.6;

/** The parallelogram of s·a + t·b for |s|, |t| ≤ SHEET_REACH, with a few lines of the grid they carve. */
function SpanSheet({ a, b, lit }: { a: Vec3; b: Vec3; lit: boolean }) {
  const r = SHEET_REACH;
  const corners = [combine3(-r, a, -r, b), combine3(r, a, -r, b), combine3(r, a, r, b), combine3(-r, a, r, b)].map(project);
  const steps = [-1, 0, 1];
  const line = (from: Vec3, to: Vec3, key: string) => {
    const [x1, y1] = project(from);
    const [x2, y2] = project(to);
    return <line key={key} x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--palette-teal)" strokeOpacity={0.35} strokeWidth={1} />;
  };
  return (
    <g aria-hidden>
      <polygon
        points={corners.map(([x, y]) => `${x},${y}`).join(" ")}
        fill="var(--palette-teal)"
        fillOpacity={lit ? 0.34 : 0.18}
        className="transition-[fill-opacity] duration-300"
      />
      {steps.map((k) => line(combine3(k, a, -r, b), combine3(k, a, r, b), `a${k}`))}
      {steps.map((k) => line(combine3(-r, a, k, b), combine3(r, a, k, b), `b${k}`))}
    </g>
  );
}

function SpaceArrow({ to, color, from = [0, 0, 0], markerId }: { to: Vec3; color: Hue; from?: Vec3; markerId: string }) {
  const [x1, y1] = project(from);
  const [x2, y2] = project(to);
  if (Math.hypot(x2 - x1, y2 - y1) < 2) return <circle cx={x1} cy={y1} r={4} fill={hue(color)} />;
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={3.5} strokeLinecap="round" markerEnd={`url(#${markerId}-${color})`} />;
}

function SpaceSegment({ from, to, color }: { from: Vec3; to: Vec3; color: Hue }) {
  const [x1, y1] = project(from);
  const [x2, y2] = project(to);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={2} strokeDasharray="5 5" />;
}

function SpaceLabel({ at, color, children }: { at: Vec3; color: Hue; children: string }) {
  const [x, y] = project(at);
  return (
    <text x={x + 9} y={y - 8} fill={hue(color)} fontSize={18} fontWeight={700} fontFamily="KaTeX_Main, serif" paintOrder="stroke" stroke="var(--color-surface-sunken)" strokeWidth={4}>
      {children}
    </text>
  );
}

function SpaceMarker({ at, color }: { at: Vec3; color: Hue }) {
  const [x, y] = project(at);
  return (
    <g>
      <circle cx={x} cy={y} r={11} fill="none" stroke={hue(color)} strokeWidth={2} />
      <circle cx={x} cy={y} r={4} fill={hue(color)} />
    </g>
  );
}

const MARKER_HUES: Hue[] = ["yellow", "blue", "pink", "teal"];

function Space({ label, children }: { label: string; children: React.ReactNode }) {
  const prefix = useId().replaceAll(":", "");
  return (
    <svg viewBox={`0 0 ${VIEW.width} ${VIEW.height}`} role="img" aria-label={label} className="block h-auto w-full select-none rounded-media bg-surface-sunken">
      <defs>
        {MARKER_HUES.map((name) => (
          <marker key={name} id={`${prefix}-${name}`} viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" fill={hue(name)} />
          </marker>
        ))}
      </defs>
      <SpaceAxes />
      <MarkerPrefix.Provider value={prefix}>{children}</MarkerPrefix.Provider>
    </svg>
  );
}

const MarkerPrefix = createContext("");

function Arrow3({ to, color, from }: { to: Vec3; color: Hue; from?: Vec3 }) {
  return <SpaceArrow to={to} color={color} from={from} markerId={useContext(MarkerPrefix)} />;
}

/** The point straight above or below `point` (same x and y) on the plane through 0 with this normal. */
function dropToPlane(point: Vec3, normal: Vec3): Vec3 {
  if (normal[2] === 0) return point;
  return [point[0], point[1], -(normal[0] * point[0] + normal[1] * point[1]) / normal[2]];
}

function signPrefix(value: number, first: boolean): string {
  if (first) return value < 0 ? "-" : "";
  return value < 0 ? " - " : " + ";
}

const signed = (value: number, first: boolean) => `${signPrefix(value, first)}${texNumber(Math.abs(value))}`;

/** A weight times a name, such as "2\,u", "- v" or "+ 3\,v", with a weight of 1 left implicit. */
function weightedTerm(weight: number, name: string, first: boolean): string {
  if (Math.abs(weight) === 1) return `${signPrefix(weight, first)}${name}`;
  return `${signed(weight, first)}\\,${name}`;
}

const U: Vec3 = [2, -1, 1];
const V: Vec3 = [1, 2, 1];

/** Three sliders build a third vector w beside Day 2's u and v. The readout's echelon form is worked out for this u and v. */
export function ThirdVectorHunt({ start = [0, 0, 2] }: { start?: Vec3 }) {
  const u = U;
  const v = V;
  const [w, setW] = useState<Vec3>(start);
  const normal = cross3(u, v);
  const offset = dot3(normal, w);
  const inPlane = offset === 0;
  const redundant = inPlane && !isZero3(w) && !parallel(w, u) && !parallel(w, v);
  const { settled: solved, gesture } = useSettled(redundant);
  const setEntry = (index: number) => (value: number) => setW((old) => old.map((entry, i) => (i === index ? value : entry)) as Vec3);
  const lastColor = inPlane ? palette.teal : palette.glow;
  const echelon = `\\begin{bmatrix} 2 & 1 & ${texNumber(w[0])} \\\\ 0 & 5 & ${texNumber(w[0] + 2 * w[1])} \\\\ 0 & 0 & \\textcolor{${lastColor}}{${texNumber(2 * offset)}} \\end{bmatrix}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Build a third vector <Tex>{"\\mathbf w"}</Tex> that leaves the span a plane. Skip <Tex>{"\\mathbf 0"}</Tex> and plain multiples of <Tex>{"\\mathbf u"}</Tex> or <Tex>{"\\mathbf v"}</Tex>.</>}
        success={<>That <Tex>{"\\mathbf w"}</Tex> is redundant. It is a combination of <Tex>{"\\mathbf u"}</Tex> and <Tex>{"\\mathbf v"}</Tex>, so adding it to the set leaves the span the same plane.</>}
      />
      <Workbench
        plane={
          <Space label={`The plane spanned by u and v, and the pink vector w at (${w.join(", ")}). ${inPlane ? "w lies in the plane." : "w is off the plane."}`}>
            <SpanSheet a={u} b={v} lit={solved} />
            {inPlane ? null : <SpaceSegment from={w} to={dropToPlane(w, normal)} color="glow" />}
            <Arrow3 to={u} color="yellow" />
            <Arrow3 to={v} color="blue" />
            <Arrow3 to={w} color="pink" />
            <SpaceLabel at={u} color="yellow">u</SpaceLabel>
            <SpaceLabel at={v} color="blue">v</SpaceLabel>
            <SpaceLabel at={w} color="pink">w</SpaceLabel>
            {solved ? <SpaceMarker at={w} color="teal" /> : null}
          </Space>
        }
        readout={
          <>
            <Slider label="w_1" value={w[0]} onChange={setEntry(0)} min={-4} max={4} step={1} color={palette.pink} />
            <Slider label="w_2" value={w[1]} onChange={setEntry(1)} min={-4} max={4} step={1} color={palette.pink} />
            <Slider label="w_3" value={w[2]} onChange={setEntry(2)} min={-4} max={4} step={1} color={palette.pink} />
            <Readout tex={`\\begin{bmatrix} \\mathbf u & \\mathbf v & \\mathbf w \\end{bmatrix} \\sim ${echelon}`} />
          </>
        }
      />
    </Panel>
  );
}

type Rows = number[][];

function eliminateBelow(rows: Rows, pivotRow: number, column: number): Rows {
  return rows.map((row, index) => {
    if (index <= pivotRow) return row;
    const factor = row[column] / rows[pivotRow][column];
    return row.map((entry, j) => entry - factor * rows[pivotRow][j]);
  });
}

function swapUpNonzero(rows: Rows, pivotRow: number, column: number): Rows | null {
  const found = rows.findIndex((row, index) => index >= pivotRow && Math.abs(row[column]) > 1e-9);
  if (found < 0) return null;
  const next = rows.map((row) => [...row]);
  [next[pivotRow], next[found]] = [next[found], next[pivotRow]];
  return next;
}

/** Row replacement and swaps only, so the echelon form keeps whole numbers where it can. Returns the pivot cells too. */
function echelon(rows: Rows): { rows: Rows; pivots: [number, number][] } {
  let current = rows.map((row) => [...row]);
  const pivots: [number, number][] = [];
  for (let column = 0; column < current[0].length && pivots.length < current.length; column += 1) {
    const swapped = swapUpNonzero(current, pivots.length, column);
    if (!swapped) continue;
    current = eliminateBelow(swapped, pivots.length, column);
    pivots.push([pivots.length, column]);
  }
  return { rows: current.map((row) => row.map((entry) => (Math.abs(entry) < 1e-9 ? 0 : entry))), pivots };
}

function matrixTex(rows: Rows, pivots: [number, number][]): string {
  const isPivot = (r: number, c: number) => pivots.some(([pr, pc]) => pr === r && pc === c);
  const cell = (entry: number, r: number, c: number) =>
    isPivot(r, c) ? `\\fcolorbox{${palette.glow}}{transparent}{$${texNumber(entry)}$}` : texNumber(entry);
  const rowHeight = `\\vphantom{\\fcolorbox{${palette.glow}}{transparent}{$0$}}`;
  return `\\begin{bmatrix} ${rows.map((row, r) => row.map((entry, c) => cell(entry, r, c)).join(" & ") + rowHeight).join(" \\\\ ")} \\end{bmatrix}`;
}

const transpose = (columns: Vec3[]): Rows => [0, 1, 2].map((r) => columns.map((column) => column[r]));

/** A slider sets the last entry h of a third column. The goal is the one h that costs the matrix its third pivot. */
export function PivotHunt({ a1 = [1, 2, 0], a2 = [0, 1, 1], a3 = [2, 1], start = 1 }: { a1?: Vec3; a2?: Vec3; a3?: [number, number]; start?: number }) {
  const [h, setH] = useState(start);
  const third: Vec3 = [a3[0], a3[1], h];
  const reduced = echelon(transpose([a1, a2, third]));
  const pivotCount = reduced.pivots.length;
  const { settled: solved, gesture } = useSettled(pivotCount < 3);
  const normal = cross3(a1, a2);
  const pierce = dropToPlane(third, normal);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide <Tex>h</Tex> until the matrix loses a pivot, so its columns no longer span <Tex>{"\\mathbb R^3"}</Tex>.</>}
        success={<>Right, <Tex>{`h = ${texNumber(-(a3[0] * normal[0] + a3[1] * normal[1]) / normal[2])}`}</Tex>. Row three is all zeros and <Tex>{"\\mathbf a_3"}</Tex> drops into the plane of <Tex>{"\\mathbf a_1"}</Tex> and <Tex>{"\\mathbf a_2"}</Tex>, so the span is only that plane.</>}
      />
      <Workbench
        plane={
          <Space label={`The plane spanned by a1 and a2, and a3 at (${third.join(", ")}) on a dashed vertical line. ${solved ? "a3 lies in the plane." : "a3 is off the plane."}`}>
            <SpanSheet a={a1} b={a2} lit={solved} />
            <SpaceSegment from={[a3[0], a3[1], -4]} to={[a3[0], a3[1], 4]} color="text" />
            <Arrow3 to={a1} color="yellow" />
            <Arrow3 to={a2} color="blue" />
            <Arrow3 to={third} color="pink" />
            <SpaceLabel at={a1} color="yellow">a₁</SpaceLabel>
            <SpaceLabel at={a2} color="blue">a₂</SpaceLabel>
            <SpaceLabel at={third} color="pink">a₃</SpaceLabel>
            <SpaceMarker at={pierce} color={solved ? "teal" : "text"} />
          </Space>
        }
        readout={
          <>
            <Slider label="h" value={h} onChange={setH} min={-4} max={4} step={1} color={palette.pink} />
            <Readout tex={`${columnTex(a1, palette.yellow)}\\; ${columnTex(a2, palette.blue)}\\; ${columnTex(third, palette.pink)}`} />
            <Readout tex={`\\sim ${matrixTex(reduced.rows, reduced.pivots)}`} />
            <Readout tex={`\\text{rows with a pivot: } ${pivotCount} \\text{ of } 3`} />
          </>
        }
      />
    </Panel>
  );
}

type Coefficients = [number, number, number];

const GRAPH = { tMin: -1.5, tMax: 1.5, yMin: -6, yMax: 10, width: 420, height: 340 };

const toGraph = (t: number, y: number): [number, number] => [
  ((t - GRAPH.tMin) / (GRAPH.tMax - GRAPH.tMin)) * GRAPH.width,
  ((GRAPH.yMax - y) / (GRAPH.yMax - GRAPH.yMin)) * GRAPH.height,
];

const evaluate = (c: Coefficients, t: number) => c[0] + c[1] * t + c[2] * t * t;

function curvePath(coeffs: Coefficients): string {
  const steps = 90;
  return Array.from({ length: steps + 1 }, (_, i) => {
    const t = GRAPH.tMin + ((GRAPH.tMax - GRAPH.tMin) * i) / steps;
    const [x, y] = toGraph(t, evaluate(coeffs, t));
    return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
}

function GraphGrid() {
  const ys = [-4, -2, 0, 2, 4, 6, 8];
  const ts = [-1, 0, 1];
  const gridLine = (axis: boolean) => ({
    stroke: axis ? "var(--palette-axis)" : "var(--palette-grid)",
    strokeOpacity: axis ? 0.9 : 0.4,
    strokeWidth: axis ? 1.6 : 1,
  });
  return (
    <g aria-hidden>
      {ys.map((y) => {
        const [, py] = toGraph(0, y);
        return <line key={`y${y}`} x1={0} x2={GRAPH.width} y1={py} y2={py} {...gridLine(y === 0)} />;
      })}
      {ts.map((t) => {
        const [px] = toGraph(t, 0);
        return <line key={`t${t}`} x1={px} x2={px} y1={0} y2={GRAPH.height} {...gridLine(t === 0)} />;
      })}
      <text x={GRAPH.width - 14} y={toGraph(0, 0)[1] - 8} fill="var(--palette-text-muted)" fontSize={15} fontStyle="italic" fontFamily="KaTeX_Math, serif">t</text>
    </g>
  );
}

const POWERS = ["", "t", "t^2"];

function polynomialTex(coeffs: Coefficients): string {
  const terms = coeffs.flatMap((value, power) => (value === 0 ? [] : [{ value, power }]));
  if (terms.length === 0) return "0";
  return terms
    .map(({ value, power }, index) => {
      const size = Math.abs(value);
      const body = power > 0 && size === 1 ? POWERS[power] : `${texNumber(size)}${POWERS[power]}`;
      return `${signPrefix(value, index === 0)}${body}`;
    })
    .join("");
}

const BASIS_COLORS = [palette.yellow, palette.blue, palette.pink];
const BASIS_HUES: Hue[] = ["yellow", "blue", "pink"];

/** Three weights on a spanning set of P2, with a dashed target curve to rebuild. */
export function PolynomialRecipe({ basis, target }: { basis: [Coefficients, Coefficients, Coefficients]; target: Coefficients }) {
  const [weights, setWeights] = useState<Coefficients>([1, 1, 1]);
  const result = basis.reduce<Coefficients>(
    (sum, p, i) => [sum[0] + weights[i] * p[0], sum[1] + weights[i] * p[1], sum[2] + weights[i] * p[2]],
    [0, 0, 0],
  );
  const matches = result.every((value, index) => value === target[index]);
  const { settled: solved, gesture } = useSettled(matches);
  const clipId = `${useId().replaceAll(":", "")}-clip`;
  const setWeight = (index: number) => (value: number) => setWeights((old) => old.map((entry, i) => (i === index ? value : entry)) as Coefficients);
  const recipe = weights.map((c, i) => weightedTerm(c, `\\textcolor{${BASIS_COLORS[i]}}{\\mathbf p_${i + 1}}`, i === 0)).join("");

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Use the recipe <Tex>{"c_1\\mathbf p_1 + c_2\\mathbf p_2 + c_3\\mathbf p_3"}</Tex> to rebuild the dashed target <Tex>{polynomialTex(target)}</Tex>.</>}
        success={<>That&rsquo;s the recipe. The coefficient columns match entry by entry, so these weights rebuild <Tex>{polynomialTex(target)}</Tex> exactly.</>}
      />
      <Workbench
        plane={
          <svg viewBox={`0 0 ${GRAPH.width} ${GRAPH.height}`} role="img" aria-label={`Graphs of p1, p2, p3, the dashed target and the teal combination, currently ${polynomialTex(result)}`} className="block h-auto w-full select-none rounded-media bg-surface-sunken">
            <defs>
              <clipPath id={clipId}>
                <rect width={GRAPH.width} height={GRAPH.height} />
              </clipPath>
            </defs>
            <GraphGrid />
            <g clipPath={`url(#${clipId})`}>
              {basis.map((p, i) => (
                <path key={i} d={curvePath(p)} fill="none" stroke={hue(BASIS_HUES[i])} strokeWidth={2} strokeOpacity={0.8} />
              ))}
              <path d={curvePath(target)} fill="none" stroke={hue(solved ? "teal" : "text")} strokeWidth={2.5} strokeDasharray="7 7" />
              <path d={curvePath(result)} fill="none" stroke={hue("teal")} strokeWidth={solved ? 5 : 3.5} strokeLinecap="round" />
            </g>
          </svg>
        }
        readout={
          <>
            {[0, 1, 2].map((i) => (
              <Slider key={i} label={`c_${i + 1}`} value={weights[i]} onChange={setWeight(i)} min={-3} max={3} step={1} color={BASIS_COLORS[i]} />
            ))}
            <Readout tex={`\\begin{aligned} ${basis.map((p, i) => `\\textcolor{${BASIS_COLORS[i]}}{\\mathbf p_${i + 1}} &= \\textcolor{${BASIS_COLORS[i]}}{${polynomialTex(p)}}`).join(" \\\\ ")} \\end{aligned}`} />
            <Readout tex={`\\begin{aligned} &${recipe} \\\\ &= \\textcolor{${palette.teal}}{${polynomialTex(result)}} \\end{aligned}`} />
          </>
        }
      />
    </Panel>
  );
}

const FLAT_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -5, yMax: 5 };
const LINE_REACH = 20;

function SpanLine({ direction, lit }: { direction: Vec; lit: boolean }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg(scale(-LINE_REACH, direction));
  const [x2, y2] = toSvg(scale(LINE_REACH, direction));
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--palette-purple-gray)" strokeWidth={lit ? 7 : 4} strokeOpacity={lit ? 0.75 : 0.45} strokeLinecap="round" aria-hidden />;
}

function WholePlaneTint() {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg([FLAT_BOUNDS.xMin, FLAT_BOUNDS.yMax]);
  const [x2, y2] = toSvg([FLAT_BOUNDS.xMax, FLAT_BOUNDS.yMin]);
  return <rect x={x1} y={y1} width={x2 - x1} height={y2 - y1} fill="var(--palette-purple-gray)" fillOpacity={0.16} aria-hidden />;
}

const cross2 = (a: Vec, b: Vec) => a[0] * b[1] - a[1] * b[0];

const entryTex = (value: number, color: string) => `\\textcolor{${color}}{${texNumber(value)}}`;

/**
 * Two parallel columns in R^2 span only a line. The learner drags b and watches the last entry of the
 * reduced augmented matrix, which is zero exactly when b is reachable.
 */
export function ConsistencyHunt({ a1, a2, start }: { a1: Vec; a2: Vec; start: Vec }) {
  const [b, setB] = useState<Vec>(start);
  const multiplier = a1[1] / a1[0];
  const leftover = b[1] - multiplier * b[0];
  const reachable = Math.abs(leftover) < 1e-9 && (b[0] !== 0 || b[1] !== 0);
  const { settled: solved, gesture } = useSettled(reachable);
  const leftoverColor = Math.abs(leftover) < 1e-9 ? palette.teal : palette.glow;
  const augmented = `\\left[\\begin{array}{cc|c} ${entryTex(a1[0], palette.yellow)} & ${entryTex(a2[0], palette.blue)} & ${entryTex(b[0], palette.teal)} \\\\ ${entryTex(a1[1], palette.yellow)} & ${entryTex(a2[1], palette.blue)} & ${entryTex(b[1], palette.teal)} \\end{array}\\right]`;
  const reduced = `\\sim \\left[\\begin{array}{cc|c} ${texNumber(a1[0])} & ${texNumber(a2[0])} & ${texNumber(b[0])} \\\\ 0 & 0 & ${entryTex(leftover, leftoverColor)} \\end{array}\\right]`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf b"}</Tex> to a point other than <Tex>{"\\mathbf 0"}</Tex> where <Tex>{"x_1\\mathbf a_1 + x_2\\mathbf a_2 = \\mathbf b"}</Tex> has a solution. Watch the orange entry in the last row.</>}
        success={<>That <Tex>{"\\mathbf b"}</Tex> is reachable. The last row reads <Tex>{"0 = 0"}</Tex> only when <Tex>{"\\mathbf b"}</Tex> lies on the line through <Tex>{"\\mathbf a_1"}</Tex>, so that line is the whole span.</>}
      />
      <Workbench
        plane={
          <Plane bounds={FLAT_BOUNDS} label={`The columns a1 and a2 lie on one line. The target b is at ${describeVector(b)}. Drag b or use the arrow keys.`}>
            <SpanLine direction={a1} lit={solved} />
            <Arrow to={a2} color="blue" />
            <Arrow to={a1} color="yellow" />
            <Arrow to={b} color="teal" width={2.5} />
            {solved ? <Marker at={b} color="teal" ring /> : null}
            <Label at={a1} color="yellow">a₁</Label>
            <Label at={a2} color="blue">a₂</Label>
            <Label at={b} color="teal" dx={14} dy={22}>b</Label>
            <Handle at={b} onMove={setB} color="teal" label={`Tip of target b, at ${describeVector(b)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={augmented} />
            <Readout tex={reduced} />
            <p className="text-meta text-text-muted">
              The second row is <Tex>{`R_2 ${multiplier < 0 ? "+" : "-"} ${texNumber(Math.abs(multiplier))}R_1`}</Tex>. It clears both columns of <Tex>A</Tex> because <Tex>{"\\mathbf a_2"}</Tex> is a multiple of <Tex>{"\\mathbf a_1"}</Tex>.
            </p>
          </>
        }
      />
    </Panel>
  );
}

/**
 * v1 is fixed and v2 starts as a multiple of it, so the span is a line and the ringed target is out of reach.
 * The learner drags v2 off the line to grow the span to the whole plane, then finds weights.
 */
export function GrowTheSpan({ v1, start, target }: { v1: Vec; start: Vec; target: Vec }) {
  const [v2, setV2] = useState<Vec>(start);
  const [c1, setC1] = useState(1);
  const [c2, setC2] = useState(1);
  const first = scale(c1, v1);
  const result = add(first, scale(c2, v2));
  const flat = cross2(v1, v2) === 0;
  const { settled: solved, gesture } = useSettled(nearlyEqual(result, target));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Make <Tex>{"c_1\\mathbf v_1 + c_2\\mathbf v_2"}</Tex> land on the ringed point. While <Tex>{"\\mathbf v_2"}</Tex> lies on the line of <Tex>{"\\mathbf v_1"}</Tex> no weights can do it, so first drag <Tex>{"\\mathbf v_2"}</Tex> somewhere new.</>}
        success={<>Reached. Moving <Tex>{"\\mathbf v_2"}</Tex> off the line grew the span from a line to the whole plane, and the new span contains the target.</>}
      />
      <Workbench
        plane={
          <Plane bounds={FLAT_BOUNDS} label={`Vector v1 is fixed. Vector v2 is at ${describeVector(v2)}, and the span is ${flat ? "a line" : "the whole plane"}. Drag v2 or use the arrow keys.`}>
            {flat ? <SpanLine direction={v1} lit={false} /> : <WholePlaneTint />}
            <Marker at={target} color={solved ? "teal" : "glow"} ring />
            <Arrow to={first} color="yellow" width={2} dashed />
            <Arrow from={first} to={result} color="blue" width={2} dashed />
            <Arrow to={result} color="teal" />
            <Arrow to={v1} color="yellow" />
            <Arrow to={v2} color="blue" />
            <Label at={v1} color="yellow" dy={22}>v₁</Label>
            <Label at={v2} color="blue">v₂</Label>
            <Handle at={v2} onMove={setV2} color="blue" label={`Tip of vector v2, at ${describeVector(v2)}`} />
          </Plane>
        }
        readout={
          <>
            <Slider label="c_1" value={c1} onChange={setC1} min={-4} max={4} step={0.5} color={palette.yellow} />
            <Slider label="c_2" value={c2} onChange={setC2} min={-4} max={4} step={0.5} color={palette.blue} />
            <Readout tex={`${texNumber(c1)}${columnTex(v1, palette.yellow)} + ${texNumber(c2)}${columnTex(v2, palette.blue)} = ${columnTex(result, palette.teal)}`} />
            <div className="grid rounded-lg bg-surface-sunken px-4 py-3 text-meta">
              <span className={`[grid-area:1/1] ${flat ? "swap-shown" : "swap-hidden"}`} aria-hidden={!flat}>
                The span is the line through <Tex>{"\\mathbf v_1"}</Tex>.
              </span>
              <span className={`[grid-area:1/1] ${flat ? "swap-hidden" : "swap-shown"}`} aria-hidden={flat}>
                The span is the whole plane.
              </span>
            </div>
          </>
        }
      />
    </Panel>
  );
}
