"use client";

import { useId, useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { apply, nearlyEqual, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, Handle, Label, Marker, Plane, Segment, usePlane, type Bounds } from "./plane";

const vecTex = (v: Vec) => `(${texNumber(v[0])}, ${texNumber(v[1])})`;
const colored = (color: string, body: string) => `\\textcolor{${color}}{${body}}`;
const minus = (a: Vec, b: Vec): Vec => [a[0] - b[0], a[1] - b[1]];

/** A nonzero vector that a singular 2x2 matrix sends to zero. */
function kernelDirection(matrix: Matrix2): Vec {
  const [[a, b], [c, d]] = matrix;
  return a !== 0 || b !== 0 ? [-b, a] : [-d, c];
}

function KernelLine({ direction }: { direction: Vec }) {
  const { toSvg } = usePlane();
  const reach = 40;
  const [x1, y1] = toSvg([-reach * direction[0], -reach * direction[1]]);
  const [x2, y2] = toSvg([reach * direction[0], reach * direction[1]]);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue("pink")} strokeWidth={2.5} strokeOpacity={0.7} strokeDasharray="6 6" aria-hidden />;
}

function DifferenceMarks({ u, v, direction }: { u: Vec; v: Vec; direction: Vec }) {
  const difference = minus(u, v);
  return (
    <>
      <KernelLine direction={direction} />
      <Segment from={v} to={u} color="pink" />
      <Arrow to={difference} color="pink" />
      <Label at={difference} color="pink" dy={24}>u − v</Label>
      <Marker at={[0, 0]} color="glow" ring />
    </>
  );
}

const DIFFERENCE_BOUNDS: Bounds = { xMin: -5, xMax: 6, yMin: -4, yMax: 5 };

function isSecondInput(matrix: Matrix2, u: Vec, key: string): boolean {
  const v = key.split(",").map(Number) as Vec;
  return !nearlyEqual(u, v) && nearlyEqual(apply(matrix, u), apply(matrix, v));
}

/** u is fixed. The learner drags v to a different input with the same output, and the difference u - v shows up in the kernel. */
export function DifferenceInKernel({ matrix = [[1, -2], [-1, 2]], u = [1, 1], start = [1, -1] }: { matrix?: Matrix2; u?: Vec; start?: Vec }) {
  const [v, setV] = useState<Vec>(start);
  const { settled, gesture } = useSettled(`${v[0]},${v[1]}`);
  const solved = isSecondInput(matrix, u, settled);
  const imageU = apply(matrix, u);
  const imageV = apply(matrix, v);
  const difference = minus(u, v);
  const matrixTex = `\\begin{bmatrix} ${matrix[0].map((entry) => texNumber(entry)).join(" & ")} \\\\ ${matrix[1].map((entry) => texNumber(entry)).join(" & ")} \\end{bmatrix}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf v"}</Tex> to a different input that <Tex>T</Tex> sends to the same output as <Tex>{"\\mathbf u"}</Tex>.</>}
        success={<>Both land on <Tex>{vecTex(imageU)}</Tex>. Their difference <Tex>{`\\mathbf u - \\mathbf v = ${vecTex(difference)}`}</Tex> lands on <Tex>{"\\mathbf 0"}</Tex>, so it lies on the pink kernel line.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DIFFERENCE_BOUNDS} label={`Input u at ${describeVector(u)} and input v at ${describeVector(v)}, with outputs T(u) at ${describeVector(imageU)} and T(v) at ${describeVector(imageV)}. Drag v or use the arrow keys.`}>
            {solved ? <DifferenceMarks u={u} v={v} direction={kernelDirection(matrix)} /> : null}
            <Arrow to={imageU} color="teal" />
            <Arrow to={imageV} color="teal" width={2.5} dashed />
            <Marker at={imageV} color="teal" ring={solved} />
            <Arrow to={u} color="yellow" />
            <Arrow to={v} color="blue" />
            <Label at={u} color="yellow">u</Label>
            <Label at={v} color="blue">v</Label>
            <Label at={imageU} color="teal" dx={-44}>T(u)</Label>
            <Handle at={v} onMove={setV} color="blue" label={`Tip of the input v, at ${describeVector(v)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`T(\\mathbf x) = ${matrixTex}\\mathbf x`} />
            <Readout tex={`\\begin{gathered} ${colored(palette.teal, `T(\\mathbf u) = ${vecTex(imageU)}`)} \\\\ ${colored(palette.teal, `T(\\mathbf v) = ${vecTex(imageV)}`)} \\end{gathered}`} />
            <Readout tex={`\\begin{gathered} ${colored(palette.pink, `\\mathbf u - \\mathbf v = ${vecTex(difference)}`)} \\\\ ${colored(palette.pink, `T(\\mathbf u - \\mathbf v) = ${vecTex(apply(matrix, difference))}`)} \\end{gathered}`} />
          </>
        }
      />
    </Panel>
  );
}

type Quadratic = [number, number, number];

const T_MIN = -1.3;
const T_MAX = 1.8;
const Y_MIN = -4;
const Y_MAX = 6;
const GRAPH_WIDTH = 420;
const GRAPH_HEIGHT = 260;

const evaluate = (p: Quadratic, t: number) => p[0] + p[1] * t + p[2] * t * t;

function toGraph(t: number, y: number): Vec {
  return [((t - T_MIN) / (T_MAX - T_MIN)) * GRAPH_WIDTH, ((Y_MAX - y) / (Y_MAX - Y_MIN)) * GRAPH_HEIGHT];
}

function curvePath(p: Quadratic): string {
  const steps = 90;
  return Array.from({ length: steps + 1 }, (_, i) => {
    const t = T_MIN + ((T_MAX - T_MIN) * i) / steps;
    const [x, y] = toGraph(t, evaluate(p, t));
    return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
}

const PINS: { t: number; color: Hue }[] = [
  { t: 0, color: "green" },
  { t: 1, color: "red" },
];

function PinnedGraph({ p, solved, label }: { p: Quadratic; solved: boolean; label: string }) {
  const clipId = `${useId().replaceAll(":", "")}-clip`;
  const [originX, originY] = toGraph(0, 0);
  return (
    <svg viewBox={`0 0 ${GRAPH_WIDTH} ${GRAPH_HEIGHT}`} role="img" aria-label={label} className="block h-auto w-full select-none rounded-media bg-surface-sunken">
      <defs>
        <clipPath id={clipId}>
          <rect width={GRAPH_WIDTH} height={GRAPH_HEIGHT} />
        </clipPath>
      </defs>
      <g aria-hidden>
        <line x1={0} x2={GRAPH_WIDTH} y1={originY} y2={originY} stroke="var(--palette-axis)" strokeOpacity={0.9} strokeWidth={1.4} />
        <line x1={originX} x2={originX} y1={0} y2={GRAPH_HEIGHT} stroke="var(--palette-axis)" strokeOpacity={0.5} strokeWidth={1.2} />
        {PINS.map(({ t, color }) => {
          const [x] = toGraph(t, 0);
          return <line key={t} x1={x} x2={x} y1={0} y2={GRAPH_HEIGHT} stroke={hue(color)} strokeWidth={2} strokeDasharray="6 6" />;
        })}
      </g>
      <g clipPath={`url(#${clipId})`} aria-hidden>
        <path d={curvePath(p)} fill="none" stroke={hue(solved ? "pink" : "yellow")} strokeWidth={solved ? 5 : 3.5} strokeLinecap="round" className="transition-[stroke-width] duration-300" />
        {PINS.map(({ t, color }) => {
          const [x, y] = toGraph(t, evaluate(p, t));
          return (
            <g key={t}>
              {solved ? <circle cx={x} cy={y} r={12} fill="none" stroke={hue("glow")} strokeWidth={2} strokeDasharray="4 4" /> : null}
              <circle cx={x} cy={y} r={6} fill={hue(color)} />
            </g>
          );
        })}
      </g>
    </svg>
  );
}

function signedTerm(value: number, body: string, first: boolean): string {
  if (value === 0) return "";
  const size = Math.abs(value);
  const text = body && size === 1 ? body : `${texNumber(size)}${body}`;
  if (first) return value < 0 ? `-${text}` : text;
  return value < 0 ? ` - ${text}` : ` + ${text}`;
}

function quadraticTex(p: number[]): string {
  const parts: string[] = [];
  p.forEach((value, power) => {
    const term = signedTerm(value, ["", "t", "t^2", "t^3"][power], parts.length === 0);
    if (term) parts.push(term);
  });
  return parts.length ? parts.join("") : "0";
}

const inKernel = (p: Quadratic) => p.some((entry) => entry !== 0) && evaluate(p, 0) === 0 && evaluate(p, 1) === 0;

/** T(p) = (p(0), p(1)) on P2. The learner sets coefficients until a nonzero p passes through both pins at height 0. */
export function EvaluationKernel({ start = [1, 1, 0] }: { start?: Quadratic }) {
  const [p, setP] = useState<Quadratic>(start);
  const setEntry = (index: number) => (value: number) => setP((old) => old.map((entry, i) => (i === index ? value : entry)) as Quadratic);
  const { settled, gesture } = useSettled(p.join(","));
  const solved = inKernel(settled.split(",").map(Number) as Quadratic);
  const at0 = evaluate(p, 0);
  const at1 = evaluate(p, 1);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Build a nonzero <Tex>{"\\mathbf p"}</Tex> that <Tex>T</Tex> sends to <Tex>{"(0, 0)"}</Tex>, so its graph crosses both pins at height 0.</>}
        success={<><Tex>{`\\mathbf p = ${quadraticTex(p)}`}</Tex> is in <Tex>{"\\ker T"}</Tex>. It equals <Tex>{`${texNumber(p[2])}(t^2 - t)`}</Tex>, as every kernel vector of this <Tex>T</Tex> does.</>}
      />
      <Workbench
        plane={
          <PinnedGraph
            p={p}
            solved={solved}
            label={`Graph of p = ${quadraticTex(p)} with dashed pins at t = 0 and t = 1. The curve reads ${at0} at t = 0 and ${at1} at t = 1.`}
          />
        }
        readout={
          <>
            <Slider label="a_0" value={p[0]} onChange={setEntry(0)} min={-3} max={3} step={1} color={palette.yellow} />
            <Slider label="a_1" value={p[1]} onChange={setEntry(1)} min={-3} max={3} step={1} color={palette.yellow} />
            <Slider label="a_2" value={p[2]} onChange={setEntry(2)} min={-3} max={3} step={1} color={palette.yellow} />
            <Readout tex={`\\mathbf p = ${quadraticTex(p)}`} />
            <Readout tex={`T(\\mathbf p) = \\begin{bmatrix} ${colored(palette.i_hat, texNumber(at0))} \\\\ ${colored(palette.j_hat, texNumber(at1))} \\end{bmatrix}`} />
          </>
        }
      />
    </Panel>
  );
}

const isNonzeroKernelVector = (matrix: Matrix2, key: string) => {
  const x = key.split(",").map(Number) as Vec;
  return !nearlyEqual(x, [0, 0]) && nearlyEqual(apply(matrix, x), [0, 0]);
};

/** Drag x until T sends it to zero. Once it does, the whole kernel line lights up. */
export function ZeroLanding({ matrix = [[2, -4], [-1, 2]], start = [1, 1] }: { matrix?: Matrix2; start?: Vec }) {
  const [x, setX] = useState<Vec>(start);
  const { settled, gesture } = useSettled(`${x[0]},${x[1]}`);
  const solved = isNonzeroKernelVector(matrix, settled);
  const image = apply(matrix, x);
  const matrixTex = `\\begin{bmatrix} ${matrix[0].map((entry) => texNumber(entry)).join(" & ")} \\\\ ${matrix[1].map((entry) => texNumber(entry)).join(" & ")} \\end{bmatrix}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf x"}</Tex> to a nonzero input that <Tex>T</Tex> sends to <Tex>{"\\mathbf 0"}</Tex>. The teal arrow is <Tex>{"T(\\mathbf x)"}</Tex>, and it disappears when it lands on zero.</>}
        success={<>That input is in <Tex>{"\\ker T"}</Tex>. So is every point on the pink line through the origin, because the kernel is closed under scaling.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DIFFERENCE_BOUNDS} label={`Input x at ${describeVector(x)} and its output T(x) at ${describeVector(image)}. Drag x or use the arrow keys.`}>
            {solved ? <KernelLine direction={kernelDirection(matrix)} /> : null}
            <Arrow to={image} color="teal" />
            <Marker at={[0, 0]} color={solved ? "glow" : "text"} ring={solved} />
            <Arrow to={x} color="yellow" />
            <Label at={x} color="yellow">x</Label>
            <Handle at={x} onMove={setX} color="yellow" label={`Tip of the input x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`T(\\mathbf x) = ${matrixTex}\\mathbf x`} />
            <Readout tex={`\\begin{gathered} ${colored(palette.yellow, `\\mathbf x = ${vecTex(x)}`)} \\\\ ${colored(palette.teal, `T(\\mathbf x) = ${vecTex(image)}`)} \\end{gathered}`} />
          </>
        }
      />
    </Panel>
  );
}

type Cubic = [number, number, number, number];

const TWIN_WINDOW = { tMin: -1.6, tMax: 1.6, yMin: -7, yMax: 7, width: 420, height: 300 };
const evaluateCubic = (p: Cubic, t: number) => p[0] + p[1] * t + p[2] * t * t + p[3] * t * t * t;
const secondDerivative = (p: Cubic): Cubic => [2 * p[2], 6 * p[3], 0, 0];

function cubicPath(p: Cubic): string {
  const { tMin, tMax, yMin, yMax, width, height } = TWIN_WINDOW;
  return Array.from({ length: 91 }, (_, i) => {
    const t = tMin + ((tMax - tMin) * i) / 90;
    const x = ((t - tMin) / (tMax - tMin)) * width;
    const y = ((yMax - evaluateCubic(p, t)) / (yMax - yMin)) * height;
    return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
}

function TwinGraph({ base, p, solved, label }: { base: Cubic; p: Cubic; solved: boolean; label: string }) {
  const clipId = `${useId().replaceAll(":", "")}-clip`;
  const { width, height } = TWIN_WINDOW;
  return (
    <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label} className="block h-auto w-full select-none rounded-media bg-surface-sunken">
      <defs>
        <clipPath id={clipId}>
          <rect width={width} height={height} />
        </clipPath>
      </defs>
      <g aria-hidden>
        <line x1={0} x2={width} y1={height / 2} y2={height / 2} stroke="var(--palette-axis)" strokeOpacity={0.9} strokeWidth={1.4} />
        <line x1={width / 2} x2={width / 2} y1={0} y2={height} stroke="var(--palette-axis)" strokeOpacity={0.5} strokeWidth={1.2} />
      </g>
      <g clipPath={`url(#${clipId})`} aria-hidden fill="none" strokeLinecap="round">
        <path d={cubicPath(secondDerivative(p))} stroke={hue("teal")} strokeWidth={solved ? 5 : 3.5} className="transition-[stroke-width] duration-300" />
        <path d={cubicPath(base)} stroke={hue("text")} strokeOpacity={0.6} strokeWidth={2.5} strokeDasharray="7 7" />
        <path d={cubicPath(p)} stroke={hue("yellow")} strokeWidth={3.5} />
      </g>
    </svg>
  );
}

function isTwin(base: Cubic, key: string): boolean {
  const p = key.split(",").map(Number) as Cubic;
  const different = p.some((entry, i) => entry !== base[i]);
  return different && p[2] === base[2] && p[3] === base[3];
}

/** T(p) = p'' on P3. Starting from a fixed cubic, find a different cubic with the same second derivative; the difference lies in ker T = Span{1, t}. */
export function SecondDerivativeTwins({ base = [0, 0, 0, 1] }: { base?: Cubic }) {
  const [p, setP] = useState<Cubic>(base);
  const setEntry = (index: number) => (value: number) => setP((old) => old.map((entry, i) => (i === index ? value : entry)) as Cubic);
  const { settled, gesture } = useSettled(p.join(","));
  const solved = isTwin(base, settled);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Let <Tex>{"T(\\mathbf p) = \\mathbf p''"}</Tex>. Change <Tex>{"\\mathbf p"}</Tex> so that it differs from the dashed <Tex>{quadraticTex(base)}</Tex> but its second derivative, the teal curve, stays the same.</>}
        success={<>Both have the same second derivative. The difference <Tex>{`\\mathbf p - ${quadraticTex(base)}`}</Tex> has no <Tex>{"t^2"}</Tex> or <Tex>{"t^3"}</Tex> term, so it lies in <Tex>{"\\ker T = \\operatorname{Span}\\{1, t\\}"}</Tex>.</>}
      />
      <Workbench
        plane={<TwinGraph base={base} p={p} solved={solved} label={`Graph of p = ${quadraticTex(p)} in yellow, the fixed cubic ${quadraticTex(base)} dashed, and the second derivative of p in teal.`} />}
        readout={
          <>
            {["a_0", "a_1", "a_2", "a_3"].map((name, index) => (
              <Slider key={name} label={name} value={p[index]} onChange={setEntry(index)} min={-3} max={3} step={1} color={palette.yellow} />
            ))}
            <Readout tex={colored(palette.yellow, `\\mathbf p = ${quadraticTex(p)}`)} />
            <Readout tex={colored(palette.teal, `\\mathbf p'' = ${quadraticTex(secondDerivative(p))}`)} />
          </>
        }
      />
    </Panel>
  );
}
