"use client";

import { useId, useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, texNumber, type Vec } from "./math";
import { Arrow, Handle, Label, Marker, Plane, usePlane, type Bounds } from "./plane";

type Coefficients = [number, number, number];

const combine = (a: number, p: Coefficients, b: number, q: Coefficients): Coefficients => [
  a * p[0] + b * q[0],
  a * p[1] + b * q[1],
  a * p[2] + b * q[2],
];

const sameCoefficients = (p: Coefficients, q: Coefficients) => p.every((value, index) => Math.abs(value - q[index]) < 1e-9);

const evaluate = (coeffs: Coefficients, t: number) => coeffs[0] + coeffs[1] * t + coeffs[2] * t * t;

const POWERS = ["", "t", "t^2"];

/** "2\,p - q" style text for a weighted sum of two named vectors. */
function weightedSumTex(a: number, first: string, b: number, second: string): string {
  const weight = (value: number) => (Math.abs(value) === 1 ? "" : `${texNumber(Math.abs(value))}\\,`);
  const lead = `${a < 0 ? "-" : ""}${weight(a)}${first}`;
  return `${lead} ${b < 0 ? "-" : "+"} ${weight(b)}${second}`;
}

function polynomialTerm(value: number, power: number, first: boolean): string {
  const size = Math.abs(value);
  const body = power > 0 && size === 1 ? POWERS[power] : `${texNumber(size)}${POWERS[power]}`;
  if (first) return value < 0 ? `-${body}` : body;
  return value < 0 ? ` - ${body}` : ` + ${body}`;
}

/** 1 + 2t - t^2 style text for a list of coefficients, with zero terms left out. */
export function polynomialTex(coeffs: Coefficients): string {
  const terms = coeffs.flatMap((value, power) => (value === 0 ? [] : [{ value, power }]));
  if (terms.length === 0) return "0";
  return terms.map(({ value, power }, index) => polynomialTerm(value, power, index === 0)).join("");
}

const GRAPH = { tMin: -0.5, tMax: 2.5, yMin: -7, yMax: 9, width: 420, height: 360 };

const toGraph = (t: number, y: number): Vec => [
  ((t - GRAPH.tMin) / (GRAPH.tMax - GRAPH.tMin)) * GRAPH.width,
  ((GRAPH.yMax - y) / (GRAPH.yMax - GRAPH.yMin)) * GRAPH.height,
];

function curvePath(coeffs: Coefficients): string {
  const steps = 90;
  const points = Array.from({ length: steps + 1 }, (_, i) => {
    const t = GRAPH.tMin + ((GRAPH.tMax - GRAPH.tMin) * i) / steps;
    const [x, y] = toGraph(t, evaluate(coeffs, t));
    return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  });
  return points.join(" ");
}

function GraphGrid() {
  const ts = [0, 1, 2];
  const ys = [-6, -4, -2, 0, 2, 4, 6, 8];
  return (
    <g aria-hidden>
      {ys.map((y) => {
        const [, py] = toGraph(0, y);
        return <line key={`y${y}`} x1={0} x2={GRAPH.width} y1={py} y2={py} stroke={y === 0 ? "var(--palette-axis)" : "var(--palette-grid)"} strokeOpacity={y === 0 ? 0.9 : 0.4} strokeWidth={y === 0 ? 1.6 : 1} />;
      })}
      {ts.map((t) => {
        const [px] = toGraph(t, 0);
        return <line key={`t${t}`} x1={px} x2={px} y1={0} y2={GRAPH.height} stroke={t === 0 ? "var(--palette-axis)" : "var(--palette-grid)"} strokeOpacity={t === 0 ? 0.9 : 0.4} strokeWidth={t === 0 ? 1.6 : 1} />;
      })}
      {[1, 2].map((t) => {
        const [px, py] = toGraph(t, 0);
        return <text key={`tl${t}`} x={px + 4} y={py + 16} fill="var(--palette-text-muted)" fontSize={13}>{t}</text>;
      })}
      <text x={GRAPH.width - 14} y={toGraph(0, 0)[1] - 8} fill="var(--palette-text-muted)" fontSize={15} fontStyle="italic" fontFamily="KaTeX_Math, serif">t</text>
    </g>
  );
}

function Curve({ coeffs, color, width = 3.5, dashed = false }: { coeffs: Coefficients; color: Hue; width?: number; dashed?: boolean }) {
  return <path d={curvePath(coeffs)} fill="none" stroke={hue(color)} strokeWidth={width} strokeLinecap="round" strokeDasharray={dashed ? "7 7" : undefined} />;
}

function PolynomialGraph({ label, children }: { label: string; children: React.ReactNode }) {
  const clipId = `${useId().replaceAll(":", "")}-clip`;
  return (
    <svg viewBox={`0 0 ${GRAPH.width} ${GRAPH.height}`} role="img" aria-label={label} className="block h-auto w-full select-none rounded-media bg-surface-sunken">
      <defs>
        <clipPath id={clipId}>
          <rect width={GRAPH.width} height={GRAPH.height} />
        </clipPath>
      </defs>
      <GraphGrid />
      <g clipPath={`url(#${clipId})`}>{children}</g>
    </svg>
  );
}

/** Weights a and b on two polynomials, drawn as curves and read as coefficient columns, with a target curve to match. */
export function PolynomialCombiner({ p, q, target }: { p: Coefficients; q: Coefficients; target: Coefficients }) {
  const [a, setA] = useState(1);
  const [b, setB] = useState(1);
  const result = combine(a, p, b, q);
  const { settled: solved, gesture } = useSettled(sameCoefficients(result, target));
  const weighted = weightedSumTex(a, columnTex(p, palette.yellow), b, columnTex(q, palette.blue));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Choose weights <Tex>a</Tex> and <Tex>b</Tex> so that the teal curve <Tex>{"a\\,\\mathbf p + b\\,\\mathbf q"}</Tex> lands on the dashed target <Tex>{polynomialTex(target)}</Tex>.</>}
        success={<>That&rsquo;s it. The curves match exactly when the coefficient columns match, so <Tex>{`${weightedSumTex(a, "\\mathbf p", b, "\\mathbf q")} = ${polynomialTex(target)}`}</Tex>.</>}
      />
      <Workbench
        plane={
          <PolynomialGraph label={`Graphs of p, q, the target and the combination a p + b q, which is currently ${polynomialTex(result)}`}>
            <Curve coeffs={p} color="yellow" width={2} />
            <Curve coeffs={q} color="blue" width={2} />
            <Curve coeffs={target} color={solved ? "teal" : "text"} width={2.5} dashed />
            <Curve coeffs={result} color="teal" width={solved ? 5 : 3.5} />
          </PolynomialGraph>
        }
        readout={
          <>
            <Slider label="a" value={a} onChange={setA} min={-3} max={3} step={0.5} color={palette.yellow} />
            <Slider label="b" value={b} onChange={setB} min={-3} max={3} step={0.5} color={palette.blue} />
            <Readout tex={weighted} />
            <Readout tex={`= ${columnTex(result, palette.teal)} \\;\\leftrightarrow\\; \\textcolor{${palette.teal}}{${polynomialTex(result)}}`} />
          </>
        }
      />
    </Panel>
  );
}

const inW = (v: Vec) => v[0] * v[1] >= 0;

function Shading({ bounds }: { bounds: Bounds }) {
  const { toSvg } = usePlane();
  const rect = (from: Vec, to: Vec, key: string) => {
    const [x1, y1] = toSvg(from);
    const [x2, y2] = toSvg(to);
    return <rect key={key} x={Math.min(x1, x2)} y={Math.min(y1, y2)} width={Math.abs(x2 - x1)} height={Math.abs(y2 - y1)} fill="var(--palette-purple-gray)" fillOpacity={0.16} />;
  };
  return <g aria-hidden>{[rect([0, 0], [bounds.xMax, bounds.yMax], "first"), rect([0, 0], [bounds.xMin, bounds.yMin], "third")]}</g>;
}

const factorTex = (value: number) => (value < 0 ? `(${texNumber(value)})` : texNumber(value));

function membershipTex(name: string, v: Vec, color: string): string {
  const product = texNumber(v[0] * v[1]);
  const member = inW(v) ? "\\in" : "\\notin";
  return `\\textcolor{${color}}{${name}} ${member} W: \\; ${factorTex(v[0])} \\cdot ${factorTex(v[1])} = ${product}`;
}

function MembershipRow({ tex }: { tex: string }) {
  return (
    <div className="overflow-x-auto whitespace-nowrap rounded-lg bg-surface-sunken px-4 py-3 text-center text-meta">
      <Tex>{tex}</Tex>
    </div>
  );
}

const CLOSURE_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -5, yMax: 5 };

/** Two vectors inside the first and third quadrants; the learner hunts for a pair whose sum escapes. */
export function ClosureHunt({ u: startU = [2, 1], v: startV = [1, 3] }: { u?: Vec; v?: Vec }) {
  const [u, setU] = useState<Vec>(startU);
  const [v, setV] = useState<Vec>(startV);
  const sum = add(u, v);
  const escaped = inW(u) && inW(v) && !inW(sum);
  const { settled: solved, gesture } = useSettled(escaped);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Keep <Tex>{"\\mathbf u"}</Tex> and <Tex>{"\\mathbf v"}</Tex> in the shaded set <Tex>{"W"}</Tex>, but move them so that <Tex>{"\\mathbf u + \\mathbf v"}</Tex> lands outside it.</>}
        success={<>Found one. Both vectors are in <Tex>W</Tex> but their sum is not, so <Tex>W</Tex> is not closed under addition and is not a vector space.</>}
      />
      <Workbench
        plane={
          <Plane bounds={CLOSURE_BOUNDS} label="Plane with the first and third quadrants shaded as the set W, vectors u and v and their sum. Drag either tip or use arrow keys.">
            <Shading bounds={CLOSURE_BOUNDS} />
            <Arrow from={u} to={sum} color="blue" width={2.5} dashed />
            <Arrow to={sum} color="teal" />
            <Arrow to={v} color="blue" />
            <Arrow to={u} color="yellow" />
            {solved ? <Marker at={sum} color="glow" ring /> : null}
            <Label at={u} color="yellow">u</Label>
            <Label at={v} color="blue" dx={-18}>v</Label>
            <Label at={sum} color="teal" dy={22}>u + v</Label>
            <Handle at={v} onMove={setV} color="blue" label={`Tip of vector v, at ${describeVector(v)}`} />
            <Handle at={u} onMove={setU} color="yellow" label={`Tip of vector u, at ${describeVector(u)}`} />
          </Plane>
        }
        readout={
          <>
            <p className="text-meta text-text-muted">
              A point <Tex>{"(x, y)"}</Tex> is in <Tex>W</Tex> when <Tex>{"xy \\geq 0"}</Tex>.
            </p>
            <MembershipRow tex={membershipTex("\\mathbf u", u, palette.yellow)} />
            <MembershipRow tex={membershipTex("\\mathbf v", v, palette.blue)} />
            <MembershipRow tex={membershipTex("\\mathbf u + \\mathbf v", sum, palette.teal)} />
          </>
        }
      />
    </Panel>
  );
}

const NEGATIVE_START: Coefficients = [0, 0, 0];

/** The learner builds the negative of p coefficient by coefficient, until p + n is the zero polynomial lying flat on the axis. */
export function NegativeFinder({ p }: { p: Coefficients }) {
  const [n, setN] = useState<Coefficients>(NEGATIVE_START);
  const sum = combine(1, p, 1, n);
  const { settled: solved, gesture } = useSettled(sameCoefficients(sum, [0, 0, 0]));
  const setEntry = (index: number) => (value: number) => setN((current) => current.map((old, i) => (i === index ? value : old)) as Coefficients);
  const negative = combine(-1, p, 0, p);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Set the three coefficients of <Tex>{"\\mathbf n"}</Tex> so that the teal curve <Tex>{"\\mathbf p + \\mathbf n"}</Tex> lies flat on the <Tex>t</Tex>-axis at every <Tex>t</Tex>.</>}
        success={<>The sum is the zero polynomial, so <Tex>{`-\\mathbf p = ${polynomialTex(negative)}`}</Tex>. Every coefficient of <Tex>{"\\mathbf p"}</Tex> flipped its sign.</>}
      />
      <Workbench
        plane={
          <PolynomialGraph label={`Graphs of p in yellow, n in blue and p + n in teal, which is currently ${polynomialTex(sum)}`}>
            <Curve coeffs={p} color="yellow" width={2.5} />
            <Curve coeffs={n} color="blue" width={2.5} />
            <Curve coeffs={sum} color="teal" width={solved ? 5 : 3.5} />
          </PolynomialGraph>
        }
        readout={
          <>
            {[0, 1, 2].map((index) => (
              <Slider key={index} label={`n_${index}`} value={n[index]} onChange={setEntry(index)} min={-3} max={3} step={1} color={palette.blue} />
            ))}
            <Readout tex={`\\mathbf n = \\textcolor{${palette.blue}}{${polynomialTex(n)}}`} />
            <Readout tex={`\\mathbf p + \\mathbf n = \\textcolor{${palette.teal}}{${polynomialTex(sum)}}`} />
          </>
        }
      />
    </Panel>
  );
}

const inUpperHalf = (v: Vec) => v[1] >= 0;

function UpperShading({ bounds }: { bounds: Bounds }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg([bounds.xMin, bounds.yMax]);
  const [x2, y2] = toSvg([bounds.xMax, 0]);
  return <rect aria-hidden x={x1} y={y1} width={x2 - x1} height={y2 - y1} fill="var(--palette-purple-gray)" fillOpacity={0.16} />;
}

const ESCAPE_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -5, yMax: 5 };

/** The upper half-plane is closed under addition; the learner finds a vector in it and a scalar that throws it out. */
export function ScalingEscape({ start = [1, 2] }: { start?: Vec }) {
  const [u, setU] = useState<Vec>(start);
  const [c, setC] = useState(1);
  const scaled: Vec = [c * u[0], c * u[1]];
  const { settled: solved, gesture } = useSettled(inUpperHalf(u) && !inUpperHalf(scaled));
  const member = (v: Vec) => (inUpperHalf(v) ? "\\in" : "\\notin");

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The shaded set <Tex>H</Tex> is every point with <Tex>{"y \\geq 0"}</Tex>. Keep <Tex>{"\\mathbf u"}</Tex> in <Tex>H</Tex>, and find a scalar <Tex>c</Tex> that sends <Tex>{"c\\,\\mathbf u"}</Tex> outside it.</>}
        success={<>Rule 6 fails, because <Tex>{"\\mathbf u"}</Tex> is in <Tex>H</Tex> and <Tex>{"c\\,\\mathbf u"}</Tex> is not. Any negative <Tex>c</Tex> works on a vector above the axis, so <Tex>H</Tex> has no negatives either.</>}
      />
      <Workbench
        plane={
          <Plane bounds={ESCAPE_BOUNDS} label="Plane with the upper half shaded as the set H, a draggable vector u and its multiple c u. Drag the tip of u or use arrow keys, and use the slider for c.">
            <UpperShading bounds={ESCAPE_BOUNDS} />
            <Arrow to={scaled} color="teal" />
            <Arrow to={u} color="yellow" />
            {solved ? <Marker at={scaled} color="glow" ring /> : null}
            <Label at={u} color="yellow">u</Label>
            <Label at={scaled} color="teal" dy={22}>cu</Label>
            <Handle at={u} onMove={setU} color="yellow" label={`Tip of vector u, at ${describeVector(u)}`} />
          </Plane>
        }
        readout={
          <>
            <Slider label="c" value={c} onChange={setC} min={-2} max={2} step={0.5} color={palette.teal} />
            <MembershipRow tex={`\\textcolor{${palette.yellow}}{\\mathbf u} = ${columnTex(u)} ${member(u)} H`} />
            <MembershipRow tex={`\\textcolor{${palette.teal}}{c\\,\\mathbf u} = ${columnTex(scaled)} ${member(scaled)} H`} />
          </>
        }
      />
    </Panel>
  );
}
