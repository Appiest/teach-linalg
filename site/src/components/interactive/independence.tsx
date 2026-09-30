"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, nearlyEqual, scale, texNumber, type Vec } from "./math";
import { Arrow, boundsAround, Handle, Label, Marker, Plane, Segment } from "./plane";
import { GraphCurve } from "./subspaces";
import { polynomialTex } from "./vector-spaces";

type Vec3 = [number, number, number];

const ORIGIN: Vec = [0, 0];

/** The running tips 0, c1 v1, c1 v1 + c2 v2, … of a weighted chain of vectors. */
function chainTips(weights: number[], vectors: Vec[]): Vec[] {
  return vectors.reduce<Vec[]>((tips, vector, index) => [...tips, add(tips[index], scale(weights[index], vector))], [ORIGIN]);
}

const CHAIN_HUES: Hue[] = ["yellow", "blue", "pink"];

function Chain({ tips }: { tips: Vec[] }) {
  return (
    <>
      {tips.slice(1).map((tip, index) => (
        <Arrow key={index} from={tips[index]} to={tip} color={CHAIN_HUES[index]} />
      ))}
    </>
  );
}

function signedTerm(weight: number, name: string, first: boolean): string {
  const size = Math.abs(weight) === 1 ? "" : `${texNumber(Math.abs(weight))}\\,`;
  const sign = weight < 0 ? "-" : first ? "" : "+";
  return `${sign} ${size}${name}`;
}

/** Three weight sliders; the learner closes the chain c1 v + c2 w + c3 b back at the origin without using all zeros. */
export function RelationFinder({ v = [3, 2], w = [-1, 2], b = [5, 6] }: { v?: Vec; w?: Vec; b?: Vec }) {
  const [weights, setWeights] = useState([1, 1, 1]);
  const vectors = [v, w, b];
  const tips = chainTips(weights, vectors);
  const end = tips[3];
  const closes = nearlyEqual(end, ORIGIN) && weights.some((weight) => weight !== 0);
  const { settled: solved, gesture } = useSettled(closes);
  const setWeight = (index: number) => (value: number) => setWeights((current) => current.map((old, i) => (i === index ? value : old)));
  const names = [`\\textcolor{${palette.yellow}}{\\mathbf v}`, `\\textcolor{${palette.blue}}{\\mathbf w}`, `\\textcolor{${palette.pink}}{\\mathbf b}`];
  const sum = weights.map((weight, index) => signedTerm(weight, names[index], index === 0)).join(" ");

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Choose weights, not all zero, so that the chain <Tex>{"c_1\\mathbf v + c_2\\mathbf w + c_3\\mathbf b"}</Tex> ends back at the origin.</>}
        success={<>The chain is a closed loop, so the weights on the sliders give a dependence relation and the set is dependent.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([v, w, b, scale(2, v)])} label={`The vectors v, w and b, and the chain of weighted vectors, which currently ends at ${describeVector(end)}`}>
            <Arrow to={v} color="yellow" width={2} dashed />
            <Arrow to={w} color="blue" width={2} dashed />
            <Arrow to={b} color="pink" width={2} dashed />
            <Chain tips={tips} />
            <Marker at={end} color={solved ? "teal" : "glow"} ring={solved} />
            <Label at={v} color="yellow" dx={8} dy={16}>v</Label>
            <Label at={w} color="blue" dx={-18}>w</Label>
            <Label at={b} color="pink">b</Label>
          </Plane>
        }
        readout={
          <>
            <Slider label="c_1" value={weights[0]} onChange={setWeight(0)} min={-3} max={3} step={1} color={palette.yellow} />
            <Slider label="c_2" value={weights[1]} onChange={setWeight(1)} min={-3} max={3} step={1} color={palette.blue} />
            <Slider label="c_3" value={weights[2]} onChange={setWeight(2)} min={-3} max={3} step={1} color={palette.pink} />
            <Readout tex={`${sum} = ${columnTex(end, solved ? palette.teal : palette.glow)}`} />
          </>
        }
      />
    </Panel>
  );
}

/** Weights x with x1 v + x2 w = b, by Cramer's rule. Assumes v and w are independent. */
function solvePair(v: Vec, w: Vec, b: Vec): Vec {
  const determinant = v[0] * w[1] - v[1] * w[0];
  return [(b[0] * w[1] - b[1] * w[0]) / determinant, (v[0] * b[1] - v[1] * b[0]) / determinant];
}

/** v and w fixed, b dragged anywhere: the loop x1 v + x2 w - b always closes, and the learner hunts for given weights. */
export function LoopAnywhere({ v = [3, 1], w = [1, 2], start = [-2, 3], goal = [1, -1] }: { v?: Vec; w?: Vec; start?: Vec; goal?: Vec }) {
  const [b, setB] = useState<Vec>(start);
  const [x1, x2] = solvePair(v, w, b);
  const target = add(scale(goal[0], v), scale(goal[1], w));
  const { settled: solved, gesture } = useSettled(nearlyEqual(b, target));
  const tips = chainTips([x1, x2, -1], [v, w, b]);
  const named = (weight: number, name: string, color: string, first: boolean) => signedTerm(weight, `\\textcolor{${color}}{${name}}`, first);
  const relation = `${named(x1, "\\mathbf v", palette.yellow, true)} ${named(x2, "\\mathbf w", palette.blue, false)} - \\textcolor{${palette.pink}}{\\mathbf b} = \\mathbf 0`;
  const goalRelation = `${signedTerm(goal[0], "\\mathbf v", true)} ${signedTerm(goal[1], "\\mathbf w", false)} - \\mathbf b = \\mathbf 0`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Wherever you put <Tex>{"\\mathbf b"}</Tex>, some weights close the loop. Drag <Tex>{"\\mathbf b"}</Tex> so the loop reads <Tex>{goalRelation}</Tex>.</>}
        success={<>There it is. Three vectors in <Tex>{"\\mathbb R^2"}</Tex> always close a loop, and this time the weights are <Tex>{`${texNumber(goal[0])}`}</Tex>, <Tex>{`${texNumber(goal[1])}`}</Tex> and <Tex>{"-1"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([v, w, target, start])} label="Fixed vectors v and w, a movable vector b, and the loop of weighted vectors that returns to the origin. Drag the tip of b or use arrow keys.">
            <Chain tips={tips} />
            <Arrow to={v} color="yellow" width={2} dashed />
            <Arrow to={w} color="blue" width={2} dashed />
            {solved ? <Marker at={b} color="teal" ring /> : null}
            <Label at={v} color="yellow" dx={8} dy={16}>v</Label>
            <Label at={w} color="blue" dx={-18}>w</Label>
            <Label at={b} color="pink">b</Label>
            <Handle at={b} onMove={setB} color="pink" label={`Tip of vector b, at ${describeVector(b)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\textcolor{${palette.pink}}{\\mathbf b} = ${columnTex(b, palette.pink)}`} />
            <Readout tex={relation} />
          </>
        }
      />
    </Panel>
  );
}

const AZIMUTH = (32 * Math.PI) / 180;
const ELEVATION = (24 * Math.PI) / 180;
const UNIT = 38;

/** Oblique view of 3D space in SVG units: x1 toward the viewer, x2 to the right, x3 up. */
function project([x, y, z]: Vec3): Vec {
  const across = -x * Math.sin(AZIMUTH) + y * Math.cos(AZIMUTH);
  const depth = x * Math.cos(AZIMUTH) + y * Math.sin(AZIMUTH);
  const up = z * Math.cos(ELEVATION) - depth * Math.sin(ELEVATION);
  return [across * UNIT, -up * UNIT];
}

const add3 = (a: Vec3, b: Vec3): Vec3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const scale3 = (c: number, a: Vec3): Vec3 => [c * a[0], c * a[1], c * a[2]];
const points = (list: Vec3[]) => list.map((point) => project(point).map((value) => value.toFixed(1)).join(",")).join(" ");

function Line3({ from, to, color, width = 1.5, dashed = false, opacity = 1 }: { from: Vec3; to: Vec3; color: string; width?: number; dashed?: boolean; opacity?: number }) {
  const [x1, y1] = project(from);
  const [x2, y2] = project(to);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth={width} strokeOpacity={opacity} strokeDasharray={dashed ? "5 5" : undefined} strokeLinecap="round" />;
}

function Arrow3({ to, color }: { to: Vec3; color: Hue }) {
  const [x2, y2] = project(to);
  if (Math.hypot(x2, y2) < 2) return null;
  return <line x1={0} y1={0} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={3.5} strokeLinecap="round" markerEnd={`url(#lift-head-${color})`} />;
}

function Heads() {
  return (
    <defs>
      {(["yellow", "blue", "pink"] as Hue[]).map((name) => (
        <marker key={name} id={`lift-head-${name}`} viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill={hue(name)} />
        </marker>
      ))}
    </defs>
  );
}

function Axes3() {
  const tips: [Vec3, string][] = [[[4.2, 0, 0], "x₁"], [[0, 4.2, 0], "x₂"], [[0, 0, 6.4], "x₃"]];
  return (
    <g aria-hidden>
      {tips.map(([tip, name]) => {
        const [x, y] = project(scale3(1.08, tip));
        return (
          <g key={name}>
            <Line3 from={[0, 0, 0]} to={tip} color="var(--palette-axis)" opacity={0.7} />
            <text x={x} y={y} fill="var(--palette-text-muted)" fontSize={15} fontStyle="italic" fontFamily="KaTeX_Math, serif" textAnchor="middle" dominantBaseline="middle">{name}</text>
          </g>
        );
      })}
    </g>
  );
}

function Box({ edges, flat }: { edges: [Vec3, Vec3, Vec3]; flat: boolean }) {
  const [a, b, c] = edges;
  const corner = (i: number, j: number, k: number) => add3(add3(scale3(i, a), scale3(j, b)), scale3(k, c));
  const faces: Vec3[][] = [
    [corner(0, 0, 0), corner(1, 0, 0), corner(1, 1, 0), corner(0, 1, 0)],
    [corner(0, 0, 1), corner(1, 0, 1), corner(1, 1, 1), corner(0, 1, 1)],
    [corner(0, 0, 0), corner(1, 0, 0), corner(1, 0, 1), corner(0, 0, 1)],
    [corner(0, 1, 0), corner(1, 1, 0), corner(1, 1, 1), corner(0, 1, 1)],
    [corner(0, 0, 0), corner(0, 1, 0), corner(0, 1, 1), corner(0, 0, 1)],
    [corner(1, 0, 0), corner(1, 1, 0), corner(1, 1, 1), corner(1, 0, 1)],
  ];
  const color = flat ? "var(--palette-teal)" : "var(--palette-purple-gray)";
  return (
    <g aria-hidden>
      {faces.map((face, index) => (
        <polygon key={index} points={points(face)} fill={color} fillOpacity={0.08} stroke={color} strokeOpacity={0.5} strokeWidth={1} />
      ))}
    </g>
  );
}

function viewBoxAround(list: Vec3[]): string {
  const projected = list.map(project);
  const xs = projected.map((point) => point[0]);
  const ys = projected.map((point) => point[1]);
  const pad = 28;
  const [left, top] = [Math.min(...xs) - pad, Math.min(...ys) - pad];
  return `${left.toFixed(0)} ${top.toFixed(0)} ${(Math.max(...xs) - left + pad).toFixed(0)} ${(Math.max(...ys) - top + pad).toFixed(0)}`;
}

/** Where the vertical line through (x1, x2) meets the plane spanned by v1 and v2 (assumes their first two entries are independent). */
function planeBelow(v1: Vec3, v2: Vec3, x: number, y: number): Vec3 {
  const [s, t] = solvePair([v1[0], v1[1]], [v2[0], v2[1]], [x, y]);
  return add3(scale3(s, v1), scale3(t, v2));
}

/** v1 and v2 span a tilted plane; the slider sets the last entry of v3, and the box they build flattens when v3 lands in the plane. */
export function LiftToPlane({ v1 = [1, 0, 1], v2 = [0, 1, 2], v3 = [1, 2], min = -2, max = 8 }: { v1?: Vec3; v2?: Vec3; v3?: Vec; min?: number; max?: number }) {
  const [h, setH] = useState(min);
  const third: Vec3 = [v3[0], v3[1], h];
  const below = planeBelow(v1, v2, v3[0], v3[1]);
  const gap = h - below[2];
  const { settled: solved, gesture } = useSettled(Math.abs(gap) < 1e-9);
  const [s, t] = solvePair([v1[0], v1[1]], [v2[0], v2[1]], v3);
  const corner = (a: number, b: number) => add3(scale3(a, v1), scale3(b, v2));
  const patch = [corner(-0.4, -0.4), corner(s + 0.4, -0.4), corner(s + 0.4, t + 0.4), corner(-0.4, t + 0.4)];
  const extent: Vec3[] = [...patch, [v3[0], v3[1], min], [v3[0], v3[1], max], [0, 0, 6.6], [4.4, 0, 0], [0, 4.4, 0], add3(add3(v1, v2), [v3[0], v3[1], max])];
  const matrixTex = `\\begin{bmatrix} ${v1[0]} & ${v2[0]} & ${v3[0]} \\\\ ${v1[1]} & ${v2[1]} & ${v3[1]} \\\\ ${v1[2]} & ${v2[2]} & h \\end{bmatrix}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The teal patch is <Tex>{"\\operatorname{Span}\\{\\mathbf v_1, \\mathbf v_2\\}"}</Tex>. Find the <Tex>h</Tex> that makes <Tex>{"\\{\\mathbf v_1, \\mathbf v_2, \\mathbf v_3\\}"}</Tex> linearly dependent.</>}
        success={<>At <Tex>{`h = ${texNumber(h)}`}</Tex> the arrow <Tex>{"\\mathbf v_3"}</Tex> lies in the plane, the box is flat, and the third column has no pivot.</>}
      />
      <Workbench
        plane={
          <svg viewBox={viewBoxAround(extent)} role="img" aria-label={`Three vectors in space. v3 has last entry ${h}, and it is ${solved ? "in" : "off"} the plane of v1 and v2.`} className="block h-auto w-full select-none rounded-media bg-surface-sunken">
            <Heads />
            <Axes3 />
            <polygon points={points(patch)} fill="var(--palette-teal)" fillOpacity={solved ? 0.3 : 0.16} stroke="var(--palette-teal)" strokeOpacity={0.6} strokeWidth={1.2} />
            <Box edges={[v1, v2, third]} flat={solved} />
            {solved ? null : <Line3 from={third} to={below} color={hue("pink")} dashed width={2} />}
            <Arrow3 to={v1} color="yellow" />
            <Arrow3 to={v2} color="blue" />
            <Arrow3 to={third} color="pink" />
          </svg>
        }
        readout={
          <>
            <Slider label="h" value={h} onChange={setH} min={min} max={max} step={1} color={palette.pink} />
            <Readout tex={`[\\,\\textcolor{${palette.yellow}}{\\mathbf v_1}\\ \\textcolor{${palette.blue}}{\\mathbf v_2}\\ \\textcolor{${palette.pink}}{\\mathbf v_3}\\,] = ${matrixTex}`} />
            <Readout tex={`\\sim \\begin{bmatrix} 1 & 0 & ${texNumber(s)} \\\\ 0 & 1 & ${texNumber(t)} \\\\ 0 & 0 & \\textcolor{${solved ? palette.teal : palette.glow}}{${texNumber(gap)}} \\end{bmatrix}`} />
          </>
        }
      />
    </Panel>
  );
}

const PAIR_BOUNDS = { xMin: -5, xMax: 5, yMin: -4, yMax: 4 };

function LineThrough({ direction, lit }: { direction: Vec; lit: boolean }) {
  return (
    <g opacity={lit ? 0.8 : 0.35} aria-hidden>
      <Segment from={scale(-20, direction)} to={scale(20, direction)} color={lit ? "teal" : "text"} dashed={!lit} />
    </g>
  );
}

function pairRelationTex(v: Vec, w: Vec): string {
  const cross = v[0] * w[1] - v[1] * w[0];
  if (cross !== 0) return "c_1\\mathbf v + c_2\\mathbf w = \\mathbf 0 \\text{ only for } c_1 = c_2 = 0";
  const ratio = v[0] !== 0 ? w[0] / v[0] : w[1] / v[1];
  return `${signedTerm(ratio, `\\textcolor{${palette.yellow}}{\\mathbf v}`, true)} - \\textcolor{${palette.blue}}{\\mathbf w} = \\mathbf 0`;
}

/** Two vectors are dependent exactly when they lie on one line through the origin. The learner drags w onto the line of v. */
export function CollinearHunt({ v, start }: { v: Vec; start: Vec }) {
  const [w, setW] = useState<Vec>(start);
  const onLine = v[0] * w[1] - v[1] * w[0] === 0;
  const isZero = w[0] === 0 && w[1] === 0;
  const { settled: solved, gesture } = useSettled(onLine && !isZero);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf w"}</Tex> so that <Tex>{"\\{\\mathbf v, \\mathbf w\\}"}</Tex> is dependent, without parking it at <Tex>{"\\mathbf 0"}</Tex>. Watch the relation below change.</>}
        success={<>Dependent. Now <Tex>{"\\mathbf w"}</Tex> is a multiple of <Tex>{"\\mathbf v"}</Tex>, the two arrows share one line through the origin, and a relation with nonzero weights appears.</>}
      />
      <Workbench
        plane={
          <Plane bounds={PAIR_BOUNDS} label={`Vector v is fixed and vector w is at ${describeVector(w)}. ${onLine ? "They lie on one line." : "They point in different directions."} Drag w or use the arrow keys.`}>
            <LineThrough direction={v} lit={onLine} />
            <Arrow to={v} color="yellow" />
            <Arrow to={w} color="blue" />
            {solved ? <Marker at={w} color="teal" ring /> : null}
            <Label at={v} color="yellow" dy={22}>v</Label>
            <Label at={w} color="blue">w</Label>
            <Handle at={w} onMove={setW} color="blue" label={`Tip of vector w, at ${describeVector(w)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\textcolor{${palette.yellow}}{\\mathbf v} = ${columnTex(v, palette.yellow)}, \\quad \\textcolor{${palette.blue}}{\\mathbf w} = ${columnTex(w, palette.blue)}`} />
            <Readout tex={pairRelationTex(v, w)} />
          </>
        }
      />
    </Panel>
  );
}

type Coefficients = [number, number, number];

const FUNCTION_BOUNDS = { xMin: -3, xMax: 3, yMin: -4, yMax: 5 };
const CURVE_HUES: Hue[] = ["yellow", "blue", "pink"];
const CURVE_COLORS = [palette.yellow, palette.blue, palette.pink];

function weightedCoefficients(weights: number[], polys: Coefficients[]): Coefficients {
  return [0, 1, 2].map((power) => polys.reduce((total, poly, index) => total + weights[index] * poly[power], 0)) as Coefficients;
}

/**
 * Three polynomials drawn as graphs. The learner picks weights, not all zero, that flatten the combined graph onto
 * the t-axis, which is the zero vector of the function space.
 */
export function ZeroFunctionHunt({ polys }: { polys: [Coefficients, Coefficients, Coefficients] }) {
  const [weights, setWeights] = useState([1, 1, 1]);
  const combined = weightedCoefficients(weights, polys);
  const flat = combined.every((value) => Math.abs(value) < 1e-9) && weights.some((weight) => weight !== 0);
  const { settled: solved, gesture } = useSettled(flat);
  const setWeight = (index: number) => (value: number) => setWeights((current) => current.map((old, i) => (i === index ? value : old)));
  const names = polys.map((poly, index) => `\\textcolor{${CURVE_COLORS[index]}}{(${polynomialTex(poly)})}`);
  const sum = weights.map((weight, index) => signedTerm(weight, names[index], index === 0)).join(" ");

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Choose weights, not all zero, that flatten the orange graph of <Tex>{"c_1\\mathbf p_1 + c_2\\mathbf p_2 + c_3\\mathbf p_3"}</Tex> onto the <Tex>t</Tex>-axis at every <Tex>t</Tex>.</>}
        success={<>The combination is the zero polynomial, equal to <Tex>0</Tex> for every <Tex>t</Tex>. That is a dependence relation, so the three polynomials are dependent.</>}
      />
      <Workbench
        plane={
          <Plane bounds={FUNCTION_BOUNDS} label="Graphs of three polynomials, dashed, and their weighted sum as a solid curve. The goal is a sum that lies flat on the t-axis.">
            {polys.map((poly, index) => (
              <GraphCurve key={index} coeffs={poly} color={CURVE_HUES[index]} dashed width={2} />
            ))}
            <GraphCurve coeffs={combined} color={solved ? "teal" : "glow"} width={4} />
          </Plane>
        }
        readout={
          <>
            {[0, 1, 2].map((index) => (
              <Slider key={index} label={`c_${index + 1}`} value={weights[index]} onChange={setWeight(index)} min={-3} max={3} step={1} color={CURVE_COLORS[index]} />
            ))}
            <Readout tex={sum} />
            <Readout tex={`= \\textcolor{${solved ? palette.teal : palette.glow}}{${polynomialTex(combined)}}`} />
          </>
        }
      />
    </Panel>
  );
}
