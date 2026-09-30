"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, formatNumber, nearlyEqual, scale, texNumber, type Vec } from "./math";
import { Arrow, boundsAround, Handle, Label, Marker, Plane, Segment, usePlane, type Bounds } from "./plane";

const dot = (a: Vec, b: Vec) => a[0] * b[0] + a[1] * b[1];
const minus = (a: Vec, b: Vec): Vec => [a[0] - b[0], a[1] - b[1]];
const length = (a: Vec) => Math.hypot(a[0], a[1]);
const colored = (color: string, tex: string) => `\\textcolor{${color}}{${tex}}`;

/** Where a line through the origin crosses the plane's window, so it can be drawn edge to edge. */
function FullLine({ direction, color }: { direction: Vec; color: Hue }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg(scale(-40, direction));
  const [x2, y2] = toSvg(scale(40, direction));
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={2.5} strokeOpacity={0.7} />;
}

/** A small square corner at `corner` between two directions, in plane units. */
function RightAngle({ corner, first, second, size = 0.35 }: { corner: Vec; first: Vec; second: Vec; size?: number }) {
  const { toSvg } = usePlane();
  const along = (direction: Vec) => scale(size / length(direction), direction);
  const a = add(corner, along(first));
  const b = add(a, along(second));
  const c = add(corner, along(second));
  const path = [a, b, c].map((point) => toSvg(point).map((value) => value.toFixed(1)).join(",")).join(" ");
  return <polyline points={path} fill="none" stroke={hue("glow")} strokeWidth={2.5} />;
}

/** The whole multiple of u nearest to a dragged point, stepping one notch when a key press alone would round back. */
function nextWeight(point: Vec, current: number, u: Vec, limits: [number, number]): number {
  let weight = Math.round(dot(point, u) / dot(u, u));
  if (weight === current) {
    const push = dot(minus(point, scale(current, u)), u);
    weight = current + (push > 1e-9 ? 1 : push < -1e-9 ? -1 : 0);
  }
  return Math.min(limits[1], Math.max(limits[0], weight));
}

/** Slide a point along the line through u until it is as close as possible to the tip of y. */
export function LineFootHunt({ y = [2, 6], u = [2, 1], start = -1, limits = [-2, 3] }: { y?: Vec; u?: Vec; start?: number; limits?: [number, number] }) {
  const [weight, setWeight] = useState(start);
  const { settled, gesture } = useSettled(weight);
  const best = dot(y, u) / dot(u, u);
  const solved = Math.abs(settled - best) < 1e-9;
  const point = scale(weight, u);
  const gap = minus(y, point);
  const leftover = dot(gap, u);
  const bounds = boundsAround([y, scale(limits[0], u), scale(limits[1], u)]);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide the teal point along <Tex>L</Tex> to the spot closest to the tip of <Tex>{colored(palette.yellow, "\\mathbf y")}</Tex>. Watch the dot product under the plane.</>}
        success={<>That spot is <Tex>{colored(palette.teal, "\\hat{\\mathbf y}")}</Tex>. The gap <Tex>{colored(palette.pink, "\\mathbf y - \\hat{\\mathbf y}")}</Tex> now meets <Tex>L</Tex> at a right angle, so its dot product with <Tex>{colored(palette.i_hat, "\\mathbf u")}</Tex> is zero.</>}
      />
      <Workbench
        plane={
          <Plane bounds={bounds} label={`The line L through u, the vector y, and a point ${formatNumber(weight)} u on L at ${describeVector(point)}. Drag the point or use the arrow keys.`}>
            <FullLine direction={u} color="teal" />
            {solved ? <RightAngle corner={point} first={gap} second={scale(-1, u)} /> : null}
            <Segment from={point} to={y} color={solved ? "pink" : "text"} dashed={!solved} />
            <Arrow to={u} color="green" />
            <Arrow to={y} color="yellow" />
            <Label at={y} color="yellow" dx={-22}>y</Label>
            <Label at={u} color="green" dx={8} dy={18}>u</Label>
            <Handle at={point} onMove={(next) => setWeight(nextWeight(next, weight, u, limits))} color="teal" label={`Point on L, at ${formatNumber(weight)} times u`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`${colored(palette.teal, "\\mathbf v")} = ${texNumber(weight)}\\,${colored(palette.i_hat, "\\mathbf u")} = ${columnTex(point, palette.teal)}`} />
            <Readout tex={`\\|\\mathbf y - \\mathbf v\\| = ${texNumber(length(gap))}`} />
            <Readout tex={`(\\mathbf y - \\mathbf v)\\cdot ${colored(palette.i_hat, "\\mathbf u")} = ${colored(Math.abs(leftover) < 1e-9 ? palette.teal : palette.glow, texNumber(leftover))}`} />
          </>
        }
      />
    </Panel>
  );
}

const SHADOW_BASE: Bounds = { xMin: -3, xMax: 3, yMin: -3, yMax: 3 };

function shadowOn(y: Vec, u: Vec): Vec {
  const size = dot(u, u);
  return size === 0 ? [0, 0] : scale(dot(y, u) / size, u);
}

/** u1 is fixed and u2 is dragged; the shadows of y on each are added tip to tail, and they reach y only when u1 and u2 are perpendicular. */
export function ShadowSumBasis({ y = [3, 4], u1 = [2, 1], start = [1, 2] }: { y?: Vec; u1?: Vec; start?: Vec }) {
  const [u2, setU2] = useState<Vec>(start);
  const { settled, gesture } = useSettled(`${u2[0]},${u2[1]}`);
  const settledU2 = settled.split(",").map(Number) as Vec;
  const solved = nearlyEqual(add(shadowOn(y, u1), shadowOn(y, settledU2)), y);
  const first = shadowOn(y, u1);
  const second = shadowOn(y, u2);
  const total = add(first, second);
  const viewBounds = boundsAround([y, u1, start, first, add(first, shadowOn(y, start))], SHADOW_BASE);
  const weightTex = (u: Vec) => (dot(u, u) === 0 ? "0" : texNumber(dot(y, u) / dot(u, u)));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Here <Tex>W</Tex> is the whole plane, so the projection of <Tex>{colored(palette.yellow, "\\mathbf y")}</Tex> should be <Tex>{colored(palette.yellow, "\\mathbf y")}</Tex> itself. Drag <Tex>{colored(palette.j_hat, "\\mathbf u_2")}</Tex> until the two shadows add up to <Tex>{colored(palette.yellow, "\\mathbf y")}</Tex>.</>}
        success={<>The shadows add up to <Tex>{colored(palette.yellow, "\\mathbf y")}</Tex> because <Tex>{`${colored(palette.i_hat, "\\mathbf u_1")}\\cdot${colored(palette.j_hat, "\\mathbf u_2")} = 0`}</Tex>. Any other direction for <Tex>{colored(palette.j_hat, "\\mathbf u_2")}</Tex> misses, so the formula needs an orthogonal basis.</>}
      />
      <Workbench
        plane={
          <Plane bounds={viewBounds} label={`y, the fixed basis vector u1, a movable u2 at ${describeVector(u2)}, and the sum of the shadows of y at ${describeVector(total)}. Drag u2 or use the arrow keys.`}>
            <Marker at={y} color="glow" ring />
            <Arrow to={y} color="yellow" width={2.5} />
            <Arrow to={u1} color="green" width={2} dashed />
            <Arrow to={u2} color="red" width={2} dashed />
            <Arrow to={first} color="green" />
            <Arrow from={first} to={total} color="red" />
            <Arrow to={total} color={solved ? "teal" : "text"} width={2.5} />
            <Label at={y} color="yellow" dx={-22}>y</Label>
            <Label at={u2} color="red">u₂</Label>
            <Handle at={u2} onMove={setU2} color="red" label={`Tip of basis vector u2, at ${describeVector(u2)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`${colored(palette.i_hat, "\\mathbf u_1")}\\cdot${colored(palette.j_hat, "\\mathbf u_2")} = ${texNumber(dot(u1, u2))}`} />
            <Readout tex={`${weightTex(u1)}\\,${colored(palette.i_hat, "\\mathbf u_1")} + ${weightTex(u2)}\\,${colored(palette.j_hat, "\\mathbf u_2")} = ${columnTex(total, solved ? palette.teal : undefined)}`} />
          </>
        }
      />
    </Panel>
  );
}

type Vec3 = [number, number, number];

const AZIMUTH = (30 * Math.PI) / 180;
const ELEVATION = (25 * Math.PI) / 180;
const UNIT = 44;

function project([x, y, z]: Vec3): Vec {
  const across = -x * Math.sin(AZIMUTH) + y * Math.cos(AZIMUTH);
  const depth = x * Math.cos(AZIMUTH) + y * Math.sin(AZIMUTH);
  const up = z * Math.cos(ELEVATION) - depth * Math.sin(ELEVATION);
  return [across * UNIT, -up * UNIT];
}

const combine3 = (a: number, u: Vec3, b: number, v: Vec3): Vec3 => [a * u[0] + b * v[0], a * u[1] + b * v[1], a * u[2] + b * v[2]];
const minus3 = (a: Vec3, b: Vec3): Vec3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const dot3 = (a: Vec3, b: Vec3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const svgPoints = (list: Vec3[]) => list.map((point) => project(point).map((value) => value.toFixed(1)).join(",")).join(" ");
const column3 = (v: Vec3, color: string) => colored(color, `\\begin{bmatrix} ${v.map((entry) => texNumber(entry)).join(" \\\\ ")} \\end{bmatrix}`);

function SpaceLine({ from, to, color, width = 2, dashed = false, opacity = 1 }: { from: Vec3; to: Vec3; color: string; width?: number; dashed?: boolean; opacity?: number }) {
  const [x1, y1] = project(from);
  const [x2, y2] = project(to);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth={width} strokeOpacity={opacity} strokeDasharray={dashed ? "5 5" : undefined} strokeLinecap="round" />;
}

function SpaceArrow({ from = [0, 0, 0], to, color }: { from?: Vec3; to: Vec3; color: Hue }) {
  return (
    <g>
      <SpaceLine from={from} to={to} color={hue(color)} width={3.5} />
      <circle cx={project(to)[0]} cy={project(to)[1]} r={4} fill={hue(color)} />
    </g>
  );
}

function SpaceAxes() {
  const tips: [Vec3, string][] = [[[3.2, 0, 0], "x₁"], [[0, 4.2, 0], "x₂"], [[0, 0, 3.6], "x₃"]];
  return (
    <g aria-hidden>
      {tips.map(([tip, name]) => {
        const [x, y] = project([tip[0] * 1.1, tip[1] * 1.1, tip[2] * 1.1]);
        return (
          <g key={name}>
            <SpaceLine from={[0, 0, 0]} to={tip} color="var(--palette-axis)" opacity={0.6} width={1.5} />
            <text x={x} y={y} fill="var(--palette-text-muted)" fontSize={15} fontStyle="italic" fontFamily="KaTeX_Math, serif" textAnchor="middle" dominantBaseline="middle">{name}</text>
          </g>
        );
      })}
    </g>
  );
}

function SpaceRightAngle({ corner, first, second, size = 0.35 }: { corner: Vec3; first: Vec3; second: Vec3; size?: number }) {
  const along = (v: Vec3) => {
    const norm = Math.sqrt(dot3(v, v));
    return combine3(size / norm, v, 0, v);
  };
  const a = combine3(1, corner, 1, along(first));
  const b = combine3(1, a, 1, along(second));
  const c = combine3(1, corner, 1, along(second));
  return <polyline points={svgPoints([a, b, c])} fill="none" stroke={hue("glow")} strokeWidth={2.5} />;
}

function viewBoxFor(list: Vec3[]): string {
  const projected = list.map(project);
  const xs = projected.map((point) => point[0]);
  const ys = projected.map((point) => point[1]);
  const pad = 30;
  const [left, top] = [Math.min(...xs) - pad, Math.min(...ys) - pad];
  return `${left.toFixed(0)} ${top.toFixed(0)} ${(Math.max(...xs) - left + pad).toFixed(0)} ${(Math.max(...ys) - top + pad).toFixed(0)}`;
}

function SpaceTag({ at, color, dx, dy, children }: { at: Vec3; color: Hue; dx: number; dy: number; children: string }) {
  const [x, y] = project(at);
  return (
    <text x={x + dx} y={y + dy} fill={hue(color)} fontSize={17} fontWeight={700} fontFamily="KaTeX_Main, serif" paintOrder="stroke" stroke="var(--color-surface-sunken)" strokeWidth={4}>
      {children}
    </text>
  );
}

function PlaneSearchView({ patch, y, v, foot, solved }: { patch: Vec3[]; y: Vec3; v: Vec3; foot: Vec3; solved: boolean }) {
  const [vx, vy] = project(v);
  const distance = Math.sqrt(dot3(minus3(y, v), minus3(y, v)));
  return (
    <svg viewBox={viewBoxFor([...patch, y, [0, 0, 3.9], [0, 4.6, 0], [3.5, 0, 0]])} role="img" aria-label={`A tilted plane W, the vector y, and a point v in W at (${v.map((entry) => formatNumber(entry)).join(", ")}). The distance from y to v is ${formatNumber(distance)}.`} className="block h-auto w-full select-none rounded-media bg-surface-sunken">
      <SpaceAxes />
      <polygon points={svgPoints(patch)} fill="var(--palette-teal)" fillOpacity={0.16} stroke="var(--palette-teal)" strokeOpacity={0.6} strokeWidth={1.2} />
      <SpaceLine from={y} to={v} color={hue(solved ? "pink" : "blue")} width={solved ? 3.5 : 2.5} />
      {solved ? <SpaceRightAngle corner={foot} first={minus3(y, foot)} second={minus3([0, 0, 0], foot)} /> : null}
      <SpaceArrow to={y} color="yellow" />
      <circle cx={vx} cy={vy} r={6} fill={hue(solved ? "teal" : "blue")} />
      <SpaceTag at={y} color="yellow" dx={-18} dy={-8}>y</SpaceTag>
      <SpaceTag at={v} color={solved ? "teal" : "blue"} dx={10} dy={18}>{solved ? "ŷ" : "v"}</SpaceTag>
    </svg>
  );
}

/** Two weight sliders move v around the plane W; the distance to y bottoms out when v reaches the foot of the perpendicular. */
export function NearestPlanePoint({ u1 = [1, 1, 0], u2 = [-1, 1, 1], y = [2, 2, 3], ranges = [[-1, 3], [-1, 2]] }: { u1?: Vec3; u2?: Vec3; y?: Vec3; ranges?: [[number, number], [number, number]] }) {
  const [a, setA] = useState(0);
  const [b, setB] = useState(0);
  const { settled, gesture } = useSettled(`${a},${b}`);
  const [settledA, settledB] = settled.split(",").map(Number);
  const bestA = dot3(y, u1) / dot3(u1, u1);
  const bestB = dot3(y, u2) / dot3(u2, u2);
  const solved = Math.abs(settledA - bestA) < 1e-9 && Math.abs(settledB - bestB) < 1e-9;
  const v = combine3(a, u1, b, u2);
  const foot = combine3(bestA, u1, bestB, u2);
  const far = dot3(minus3(y, v), minus3(y, v));
  const error = dot3(minus3(y, foot), minus3(y, foot));
  const near = dot3(minus3(foot, v), minus3(foot, v));
  const patch = [combine3(ranges[0][0] - 0.3, u1, ranges[1][0] - 0.3, u2), combine3(ranges[0][1] + 0.3, u1, ranges[1][0] - 0.3, u2), combine3(ranges[0][1] + 0.3, u1, ranges[1][1] + 0.3, u2), combine3(ranges[0][0] - 0.3, u1, ranges[1][1] + 0.3, u2)];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The blue point <Tex>{colored(palette.blue, "\\mathbf v")}</Tex> lives in the teal plane <Tex>W</Tex>. Move it with the weights until it is as close to <Tex>{colored(palette.yellow, "\\mathbf y")}</Tex> as it can get.</>}
        success={<>You reached <Tex>{colored(palette.teal, "\\hat{\\mathbf y}")}</Tex>. The gap is now the pink <Tex>{colored(palette.pink, "\\mathbf z")}</Tex>, which stands at a right angle to <Tex>W</Tex>, and the last term of the Pythagoras line has dropped to zero.</>}
      />
      <Workbench
        plane={
          <PlaneSearchView patch={patch} y={y} v={v} foot={foot} solved={solved} />
        }
        readout={
          <>
            <Slider label="a" value={a} onChange={setA} min={ranges[0][0]} max={ranges[0][1]} step={0.5} color={palette.i_hat} />
            <Slider label="b" value={b} onChange={setB} min={ranges[1][0]} max={ranges[1][1]} step={0.5} color={palette.j_hat} />
            <Readout tex={`${colored(palette.blue, "\\mathbf v")} = a${colored(palette.i_hat, "\\mathbf u_1")} + b${colored(palette.j_hat, "\\mathbf u_2")} = ${column3(v, palette.blue)}`} />
            <Readout tex={`${colored(palette.blue, "\\|\\mathbf y - \\mathbf v\\|^2")} = ${colored(palette.pink, texNumber(error))} + ${colored(near < 1e-9 ? palette.teal : palette.glow, texNumber(near))} = ${texNumber(far)}`} />
          </>
        }
      />
    </Panel>
  );
}

const weightFraction = (y: Vec, u: Vec) => (dot(u, u) === 0 ? "0" : `\\tfrac{${texNumber(dot(y, u))}}{${texNumber(dot(u, u))}}`);

/** Drag the direction u; the shadow of y stays put as long as u stays on the same line. */
export function LineOnlyShadow({ y = [1, 5], start = [1, 1], target = [3, 3] }: { y?: Vec; start?: Vec; target?: Vec }) {
  const [u, setU] = useState<Vec>(start);
  const shadow = shadowOn(y, u);
  const { settled: solved, gesture } = useSettled(nearlyEqual(shadow, target) && !nearlyEqual(u, start));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{colored(palette.i_hat, "\\mathbf u")}</Tex> somewhere new so that the shadow <Tex>{colored(palette.teal, "\\hat{\\mathbf y}")}</Tex> still lands on the ring at <Tex>{`(${target[0]}, ${target[1]})`}</Tex>.</>}
        success={<>Any nonzero multiple of <Tex>{`(${start[0]}, ${start[1]})`}</Tex> gives the same shadow. Stretching <Tex>{colored(palette.i_hat, "\\mathbf u")}</Tex> by <Tex>k</Tex> multiplies the top of the fraction by <Tex>k</Tex> and the bottom by <Tex>{"k^2"}</Tex>, and <Tex>{colored(palette.i_hat, "\\mathbf u")}</Tex> itself carries the missing factor of <Tex>k</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={{ xMin: -5, xMax: 6, yMin: -4, yMax: 6 }} label={`The vector y, a movable direction u at ${describeVector(u)}, the line through u, and the shadow of y at ${describeVector(shadow)}. Drag u or use the arrow keys.`}>
            <FullLine direction={u} color={solved ? "teal" : "text"} />
            <Marker at={target} color="glow" ring />
            <Segment from={shadow} to={y} color="pink" />
            <Arrow to={y} color="yellow" />
            <Arrow to={shadow} color="teal" />
            <Arrow to={u} color="green" />
            <Label at={y} color="yellow" dx={-22}>y</Label>
            <Label at={u} color="green" dx={10} dy={20}>u</Label>
            <Handle at={u} onMove={setU} color="green" label={`Tip of direction u, at ${describeVector(u)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\frac{\\mathbf y\\cdot${colored(palette.i_hat, "\\mathbf u")}}{${colored(palette.i_hat, "\\mathbf u")}\\cdot${colored(palette.i_hat, "\\mathbf u")}} = ${weightFraction(y, u)}`} />
            <Readout tex={`${colored(palette.teal, "\\hat{\\mathbf y}")} = ${weightFraction(y, u)}${columnTex(u, palette.i_hat)} = ${columnTex(shadow, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}

function projectionMatrixTex(u: Vec): string {
  const [a, b] = u;
  return `\\tfrac{1}{${dot(u, u)}}\\begin{bmatrix} ${a * a} & ${a * b} \\\\ ${a * b} & ${b * b} \\end{bmatrix}`;
}

/** Drag y anywhere; the matrix P = UU^T sends it to its shadow on the line. The goal is a second point with a given shadow. */
export function ShadowPreimageHunt({ u = [2, 1], target = [4, 2], start = [1, 3] }: { u?: Vec; target?: Vec; start?: Vec }) {
  const [y, setY] = useState<Vec>(start);
  const shadow = shadowOn(y, u);
  const { settled: solved, gesture } = useSettled(nearlyEqual(shadow, target) && !nearlyEqual(y, target));
  const across: Vec = [-u[1], u[0]];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Find a point <Tex>{colored(palette.yellow, "\\mathbf y")}</Tex> off the teal line whose shadow <Tex>{`P${colored(palette.yellow, "\\mathbf y")}`}</Tex> lands on the ring.</>}
        success={<>Every point on the dashed line through the ring has that same shadow. <Tex>P</Tex> keeps the part of <Tex>{colored(palette.yellow, "\\mathbf y")}</Tex> along the line and throws away the pink part <Tex>{colored(palette.pink, "\\mathbf z")}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={{ xMin: -2, xMax: 7, yMin: -3, yMax: 7 }} label={`The line through u, a movable point y at ${describeVector(y)}, and its shadow P y at ${describeVector(shadow)}. Drag y or use the arrow keys.`}>
            <FullLine direction={u} color="teal" />
            {solved ? <Segment from={add(target, scale(-4, across))} to={add(target, scale(4, across))} color="glow" /> : null}
            <Marker at={target} color="glow" ring />
            <Segment from={shadow} to={y} color="pink" />
            <Arrow to={shadow} color="teal" />
            <Arrow to={y} color="yellow" />
            <Label at={y} color="yellow" dx={-26}>y</Label>
            <Handle at={y} onMove={setY} color="yellow" label={`Tip of y, at ${describeVector(y)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`P = UU^T = ${projectionMatrixTex(u)}`} />
            <Readout tex={`P${columnTex(y, palette.yellow)} = ${columnTex(shadow, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}
