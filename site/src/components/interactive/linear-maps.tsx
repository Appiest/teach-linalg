"use client";

import { useId, useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, nearlyEqual, texNumber, type Vec } from "./math";
import { Arrow, Handle, Label, Marker, Plane, usePlane, type Bounds } from "./plane";

const vecTex = (v: Vec) => `(${texNumber(v[0])}, ${texNumber(v[1])})`;

function ImageParallelogram({ corners }: { corners: Vec[] }) {
  const { toSvg } = usePlane();
  const points = corners.map((corner) => toSvg(corner).join(",")).join(" ");
  return <polygon points={points} fill="var(--palette-teal)" fillOpacity={0.14} aria-hidden />;
}

function GapSegment({ from, to }: { from: Vec; to: Vec }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg(from);
  const [x2, y2] = toSvg(to);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue("glow")} strokeWidth={2.5} strokeDasharray="5 5" aria-hidden />;
}

const SHIFT_BOUNDS: Bounds = { xMin: -4, xMax: 7, yMin: -4, yMax: 6 };

function translationPicture(v: Vec, w: Vec, b: Vec) {
  const tv = add(v, b);
  const tw = add(w, b);
  return { tv, tw, tSum: add(v, add(w, b)), sumOfImages: add(tv, tw) };
}

/** The translation T(x) = x + b. The learner drags b to make T(v) + T(w) meet T(v + w), which only b = 0 does. */
export function TranslationGap({ v = [2, 1], w = [-1, 2], start = [1, -1] }: { v?: Vec; w?: Vec; start?: Vec }) {
  const [b, setB] = useState<Vec>(start);
  const { tv, tw, tSum, sumOfImages } = translationPicture(v, w, b);
  const { settled: solved, gesture } = useSettled(nearlyEqual(sumOfImages, tSum));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the shift <Tex>{"\\mathbf b"}</Tex> until the pink tip <Tex>{"T(\\mathbf v) + T(\\mathbf w)"}</Tex> lands on the teal dot <Tex>{"T(\\mathbf v + \\mathbf w)"}</Tex>.</>}
        success={<>Only <Tex>{"\\mathbf b = \\mathbf 0"}</Tex> works. The gap between the two always equals <Tex>{"\\mathbf b"}</Tex>, so a real translation is never linear.</>}
      />
      <Workbench
        plane={
          <Plane bounds={SHIFT_BOUNDS} label="Plane showing the translation T(x) = x + b applied to v, w and v + w. Drag the orange point b or use arrow keys.">
            <ImageParallelogram corners={[b, tv, tSum, tw]} />
            <Arrow to={tv} color="yellow" />
            <Arrow to={tw} color="blue" />
            <Arrow from={tv} to={sumOfImages} color="blue" width={2.5} dashed />
            <Arrow to={sumOfImages} color="pink" />
            {solved ? null : <GapSegment from={sumOfImages} to={tSum} />}
            <Marker at={tSum} color="teal" ring={solved} />
            <Label at={tv} color="yellow" dy={18}>T(v)</Label>
            <Label at={tw} color="blue" dx={-52}>T(w)</Label>
            <Label at={sumOfImages} color="pink">T(v) + T(w)</Label>
            <Label at={tSum} color="teal" dx={-86} dy={-12}>T(v + w)</Label>
            <Handle at={b} onMove={setB} color="glow" label={`Shift b, which is also T of zero, at ${describeVector(b)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`T(\\mathbf x) = \\mathbf x + \\textcolor{${palette.glow}}{${vecTex(b)}}`} />
            <Readout tex={`\\textcolor{${palette.pink}}{T(\\mathbf v) + T(\\mathbf w)} = ${vecTex(sumOfImages)}`} />
            <Readout tex={`\\textcolor{${palette.teal}}{T(\\mathbf v + \\mathbf w)} = ${vecTex(tSum)}`} />
          </>
        }
      />
    </Panel>
  );
}

type Poly = (t: number) => number;

type Window = { yMin: number; yMax: number };

const T_MIN = -1.5;
const T_MAX = 1.5;
const GRAPH_WIDTH = 420;
const GRAPH_HEIGHT = 200;

function toGraph(t: number, y: number, window: Window): Vec {
  return [((t - T_MIN) / (T_MAX - T_MIN)) * GRAPH_WIDTH, ((window.yMax - y) / (window.yMax - window.yMin)) * GRAPH_HEIGHT];
}

function curvePath(f: Poly, window: Window): string {
  const steps = 90;
  return Array.from({ length: steps + 1 }, (_, i) => {
    const t = T_MIN + ((T_MAX - T_MIN) * i) / steps;
    const [x, y] = toGraph(t, f(t), window);
    return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
}

type CurveSpec = { f: Poly; color: Hue; width?: number; dashed?: boolean; faint?: boolean };

type DotSpec = { t: number; y: number; color: Hue };

function GraphDots({ dots, window }: { dots: DotSpec[]; window: Window }) {
  return (
    <g aria-hidden>
      {dots.map(({ t, y, color }) => {
        const [x, top] = toGraph(t, y, window);
        return <circle key={t} cx={x} cy={top} r={6.5} fill={hue(color)} stroke="var(--color-surface-sunken)" strokeWidth={2} className="transition-[fill] duration-300" />;
      })}
    </g>
  );
}

function Graph({ window, curves, label, dots = [] }: { window: Window; curves: CurveSpec[]; label: string; dots?: DotSpec[] }) {
  const clipId = `${useId().replaceAll(":", "")}-clip`;
  const [originX, originY] = toGraph(0, 0, window);
  return (
    <svg viewBox={`0 0 ${GRAPH_WIDTH} ${GRAPH_HEIGHT}`} role="img" aria-label={label} className="block h-auto w-full select-none rounded-media bg-surface-sunken">
      <defs>
        <clipPath id={clipId}>
          <rect width={GRAPH_WIDTH} height={GRAPH_HEIGHT} />
        </clipPath>
      </defs>
      <g aria-hidden>
        <line x1={0} x2={GRAPH_WIDTH} y1={originY} y2={originY} stroke="var(--palette-axis)" strokeOpacity={0.9} strokeWidth={1.4} />
        <line x1={originX} x2={originX} y1={0} y2={GRAPH_HEIGHT} stroke="var(--palette-axis)" strokeOpacity={0.9} strokeWidth={1.4} />
      </g>
      <g clipPath={`url(#${clipId})`}>
        {curves.map(({ f, color, width = 3.5, dashed = false, faint = false }, index) => (
          <path
            key={index}
            d={curvePath(f, window)}
            fill="none"
            stroke={dashed && color === "text" ? "var(--palette-text)" : hue(color)}
            strokeOpacity={faint ? 0.45 : 1}
            strokeWidth={width}
            strokeLinecap="round"
            strokeDasharray={dashed ? "7 7" : undefined}
          />
        ))}
      </g>
      <GraphDots dots={dots} window={window} />
    </svg>
  );
}

const p: Poly = (t) => 1 + 2 * t + t * t;
const q: Poly = (t) => t - t ** 3;
const pPrime: Poly = (t) => 2 + 2 * t;
const qPrime: Poly = (t) => 1 - 3 * t * t;

function signedTerm(value: number, body: string, first: boolean): string {
  if (value === 0) return "";
  const size = Math.abs(value);
  const text = body && size === 1 ? body : `${texNumber(size)}${body}`;
  if (first) return value < 0 ? `-${text}` : text;
  return value < 0 ? ` - ${text}` : ` + ${text}`;
}

/** Coefficients [c0, c1, c2, ...] as 1 + 2t - t^2 style TeX. */
function polyTex(coeffs: number[]): string {
  const powers = ["", "t", "t^2", "t^3"];
  const parts: string[] = [];
  coeffs.forEach((value, power) => {
    const term = signedTerm(value, powers[power], parts.length === 0);
    if (term) parts.push(term);
  });
  return parts.length ? parts.join("") : "0";
}

const weight = (value: number) => (value < 0 ? `(${texNumber(value)})` : texNumber(value));

/** Weights a and b on p = 1 + 2t + t^2 and q = t - t^3; the derivative of the combination must hit a target curve. */
export function DerivativeTarget({ target = [2, 1] }: { target?: [number, number] }) {
  const [a, setA] = useState(1);
  const [b, setB] = useState(1);
  const combo: Poly = (t) => a * p(t) + b * q(t);
  const comboPrime: Poly = (t) => a * pPrime(t) + b * qPrime(t);
  const goalPrime: Poly = (t) => target[0] * pPrime(t) + target[1] * qPrime(t);
  const { settled: solved, gesture } = useSettled(a === target[0] && b === target[1]);
  const derivativeCoeffs = (x: number, y: number) => [2 * x + y, 2 * x, -3 * y];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Choose <Tex>a</Tex> and <Tex>b</Tex> so that the derivative of <Tex>{"a\\,\\mathbf p + b\\,\\mathbf q"}</Tex> lands on the dashed curve <Tex>{polyTex(derivativeCoeffs(...target))}</Tex>.</>}
        success={<>That&rsquo;s it. You never had to differentiate the combination, because <Tex>{"D(a\\,\\mathbf p + b\\,\\mathbf q) = a\\,D\\mathbf p + b\\,D\\mathbf q"}</Tex>.</>}
      />
      <Workbench
        plane={
          <div className="space-y-3">
            <Graph
              window={{ yMin: -8, yMax: 12 }}
              label={`Graphs of p in yellow, q in blue and the combination a p + b q in teal, currently ${polyTex([a, 2 * a + b, a, -b])}`}
              curves={[{ f: p, color: "yellow", width: 2, faint: true }, { f: q, color: "blue", width: 2, faint: true }, { f: combo, color: "teal" }]}
            />
            <Graph
              window={{ yMin: -9, yMax: 9 }}
              label={`Derivatives: the target curve dashed, and the derivative of a p + b q in teal, currently ${polyTex(derivativeCoeffs(a, b))}`}
              curves={[{ f: goalPrime, color: solved ? "teal" : "text", width: 2.5, dashed: true }, { f: comboPrime, color: "teal", width: solved ? 5 : 3.5 }]}
            />
          </div>
        }
        readout={
          <>
            <Slider label="a" value={a} onChange={setA} min={-3} max={3} step={0.5} color={palette.yellow} />
            <Slider label="b" value={b} onChange={setB} min={-3} max={3} step={0.5} color={palette.blue} />
            <Readout tex={`\\textcolor{${palette.teal}}{${polyTex([a, 2 * a + b, a, -b])}}`} />
            <Readout tex={`\\begin{aligned} &${weight(a)}\\textcolor{${palette.yellow}}{(2 + 2t)} + ${weight(b)}\\textcolor{${palette.blue}}{(1 - 3t^2)} \\\\ &= \\textcolor{${palette.teal}}{${polyTex(derivativeCoeffs(a, b))}} \\end{aligned}`} />
          </>
        }
      />
    </Panel>
  );
}

type Quadratic = [number, number, number];

const quadratic = (c: Quadratic): Poly => (t) => c[0] + c[1] * t + c[2] * t * t;
const quadraticPrime = (c: Quadratic): Poly => (t) => c[1] + 2 * c[2] * t;
const sameList = (x: number[], y: number[]) => x.every((value, index) => value === y[index]);

/** The learner builds r = a0 + a1 t + a2 t^2 with the same derivative as p but a different formula. */
export function SharedDerivativeHunt({ p: base = [1, 2, 1] }: { p?: Quadratic }) {
  const [r, setR] = useState<Quadratic>([0, 0, 0]);
  const setEntry = (index: number) => (value: number) => setR((old) => old.map((entry, i) => (i === index ? value : entry)) as Quadratic);
  const sameDerivative = r[1] === base[1] && r[2] === base[2];
  const { settled: solved, gesture } = useSettled(sameDerivative && !sameList(r, base));
  const baseDerivative = [base[1], 2 * base[2]];
  const rDerivative = [r[1], 2 * r[2]];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Build a polynomial <Tex>{"\\mathbf r"}</Tex> that is different from <Tex>{`\\mathbf p = ${polyTex(base)}`}</Tex> but has exactly the same derivative.</>}
        success={<>Found one. <Tex>{"\\mathbf r"}</Tex> and <Tex>{"\\mathbf p"}</Tex> differ by the constant <Tex>{texNumber(r[0] - base[0])}</Tex>, yet <Tex>{`D\\mathbf r = D\\mathbf p = ${polyTex(baseDerivative)}`}</Tex>. Two inputs share one output, so <Tex>D</Tex> is not one-to-one.</>}
      />
      <Workbench
        plane={
          <div className="space-y-3">
            <Graph
              window={{ yMin: -5, yMax: 8 }}
              label={`Graphs of p in yellow and r in teal, currently ${polyTex(r)}`}
              curves={[{ f: quadratic(base), color: "yellow" }, { f: quadratic(r), color: "teal" }]}
            />
            <Graph
              window={{ yMin: -8, yMax: 8 }}
              label={`Derivatives: D p in yellow and D r in teal, currently ${polyTex(rDerivative)}`}
              curves={[{ f: quadraticPrime(base), color: "yellow", width: 6, faint: true }, { f: quadraticPrime(r), color: "teal", dashed: sameDerivative, width: 3 }]}
            />
          </div>
        }
        readout={
          <>
            <Slider label="a_0" value={r[0]} onChange={setEntry(0)} min={-3} max={3} step={1} color={palette.teal} />
            <Slider label="a_1" value={r[1]} onChange={setEntry(1)} min={-3} max={3} step={1} color={palette.teal} />
            <Slider label="a_2" value={r[2]} onChange={setEntry(2)} min={-2} max={2} step={1} color={palette.teal} />
            <Readout tex={`\\textcolor{${palette.teal}}{\\mathbf r = ${polyTex(r)}}`} />
            <Readout tex={`\\textcolor{${palette.teal}}{D\\mathbf r = ${polyTex(rDerivative)}}`} />
            <Readout tex={`\\textcolor{${palette.yellow}}{D\\mathbf p = ${polyTex(baseDerivative)}}`} />
          </>
        }
      />
    </Panel>
  );
}

const fold = (x: Vec): Vec => [x[0], Math.abs(x[1])];
const INPUT_BOUNDS: Bounds = { xMin: -3, xMax: 3, yMin: -3, yMax: 3 };
const OUTPUT_BOUNDS: Bounds = { xMin: -6, xMax: 6, yMin: -1, yMax: 7 };

/** The fold T(x1, x2) = (x1, |x2|) keeps zero fixed; drag u and v until T(u + v) and T(u) + T(v) split apart. */
export function AdditivityHunt({ u: startU = [1, 1], v: startV = [2, 1] }: { u?: Vec; v?: Vec }) {
  const [u, setU] = useState<Vec>(startU);
  const [v, setV] = useState<Vec>(startV);
  const sum = add(u, v);
  const imageOfSum = fold(sum);
  const sumOfImages = add(fold(u), fold(v));
  const { settled: solved, gesture } = useSettled(!nearlyEqual(imageOfSum, sumOfImages));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The fold <Tex>{"T(x_1, x_2) = (x_1, |x_2|)"}</Tex> sends <Tex>{"\\mathbf 0"}</Tex> to <Tex>{"\\mathbf 0"}</Tex>. Drag <Tex>{"\\mathbf u"}</Tex> and <Tex>{"\\mathbf v"}</Tex> until the teal dot <Tex>{"T(\\mathbf u + \\mathbf v)"}</Tex> and the pink tip <Tex>{"T(\\mathbf u) + T(\\mathbf v)"}</Tex> come apart.</>}
        success={<>One failing pair is enough, so the fold is not linear even though <Tex>{"T(\\mathbf 0) = \\mathbf 0"}</Tex>. It fails whenever the second entries of <Tex>{"\\mathbf u"}</Tex> and <Tex>{"\\mathbf v"}</Tex> have opposite signs.</>}
      />
      <div className="grid gap-4 sm:grid-cols-[1fr_1.4fr]">
        <figure className="min-w-0">
          <Plane bounds={INPUT_BOUNDS} label={`Inputs u at ${describeVector(u)} and v at ${describeVector(v)}`}>
            <Arrow to={u} color="yellow" />
            <Arrow to={v} color="blue" />
            <Label at={u} color="yellow">u</Label>
            <Label at={v} color="blue">v</Label>
            <Handle at={u} onMove={setU} color="yellow" label={`Input u, at ${describeVector(u)}`} />
            <Handle at={v} onMove={setV} color="blue" label={`Input v, at ${describeVector(v)}`} />
          </Plane>
          <figcaption className="mt-2 text-center text-meta text-text-muted">Inputs</figcaption>
        </figure>
        <figure className="min-w-0">
          <Plane bounds={OUTPUT_BOUNDS} label={`Outputs: T(u) + T(v) at ${describeVector(sumOfImages)} and T(u + v) at ${describeVector(imageOfSum)}`}>
            <Arrow to={fold(u)} color="yellow" width={2.5} />
            <Arrow from={fold(u)} to={sumOfImages} color="blue" width={2.5} />
            <Arrow to={sumOfImages} color="pink" />
            {solved ? <GapSegment from={sumOfImages} to={imageOfSum} /> : null}
            <Marker at={imageOfSum} color="teal" ring={!solved} />
          </Plane>
          <figcaption className="mt-2 text-center text-meta text-text-muted">Outputs</figcaption>
        </figure>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <Readout tex={`\\textcolor{${palette.teal}}{T(\\mathbf u + \\mathbf v)} = ${vecTex(imageOfSum)}`} />
        <Readout tex={`\\textcolor{${palette.pink}}{T(\\mathbf u) + T(\\mathbf v)} = ${vecTex(sumOfImages)}`} />
      </div>
    </Panel>
  );
}

/** Sliders build p in P2; the dots show T(p) = (p(0), p(1)). A nonzero p with both dots at zero shows T is not one-to-one. */
export function EvaluationZeros() {
  const [c, setC] = useState<Quadratic>([1, 0, 0]);
  const setEntry = (index: number) => (value: number) => setC((old) => old.map((entry, i) => (i === index ? value : entry)) as Quadratic);
  const f = quadratic(c);
  const image: Vec = [f(0), f(1)];
  const nonzero = c.some((entry) => entry !== 0);
  const { settled: solved, gesture } = useSettled(nonzero && image[0] === 0 && image[1] === 0);
  const dotColor = (value: number): Hue => (value === 0 ? "teal" : "glow");

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The map <Tex>{"T(\\mathbf p) = (\\mathbf p(0), \\mathbf p(1))"}</Tex> reads off the two dots. Build a nonzero <Tex>{"\\mathbf p"}</Tex> that <Tex>T</Tex> sends to <Tex>{"(0, 0)"}</Tex>.</>}
        success={<>Every multiple of <Tex>{"t - t^2"}</Tex> passes through both dots at height zero. It has the same image as the zero polynomial, so <Tex>T</Tex> is not one-to-one.</>}
      />
      <Workbench
        plane={
          <Graph
            window={{ yMin: -6, yMax: 6 }}
            label={`Graph of p = ${polyTex(c)}, with p(0) = ${image[0]} and p(1) = ${image[1]}`}
            curves={[{ f, color: "yellow" }]}
            dots={[{ t: 0, y: image[0], color: dotColor(image[0]) }, { t: 1, y: image[1], color: dotColor(image[1]) }]}
          />
        }
        readout={
          <>
            <Slider label="a_0" value={c[0]} onChange={setEntry(0)} min={-3} max={3} step={1} color={palette.yellow} />
            <Slider label="a_1" value={c[1]} onChange={setEntry(1)} min={-3} max={3} step={1} color={palette.yellow} />
            <Slider label="a_2" value={c[2]} onChange={setEntry(2)} min={-3} max={3} step={1} color={palette.yellow} />
            <Readout tex={`\\textcolor{${palette.yellow}}{\\mathbf p = ${polyTex(c)}}`} />
            <Readout tex={`T(\\mathbf p) = ${vecTex(image)}`} />
          </>
        }
      />
    </Panel>
  );
}
