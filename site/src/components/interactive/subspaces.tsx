"use client";

import { CheckCircle, XCircle } from "@phosphor-icons/react";
import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { describeVector, Goal, Panel, Readout, RichText, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, scale, texNumber, type Vec } from "./math";
import { Arrow, Handle, Label, Marker, Plane, usePlane, type Bounds } from "./plane";
import { polynomialTex } from "./vector-spaces";

const SET_COLOR = "var(--palette-purple-gray)";

const vecTex = (v: Vec) => `(${texNumber(v[0])}, ${texNumber(v[1])})`;

function SetLine({ slope, shift, dashed = false, color = SET_COLOR }: { slope: number; shift: number; dashed?: boolean; color?: string }) {
  const { bounds, toSvg } = usePlane();
  const [x1, y1] = toSvg([bounds.xMin, slope * bounds.xMin + shift]);
  const [x2, y2] = toSvg([bounds.xMax, slope * bounds.xMax + shift]);
  return (
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke={color}
      strokeWidth={dashed ? 1.5 : 4}
      strokeOpacity={dashed ? 0.7 : 1}
      strokeDasharray={dashed ? "6 6" : undefined}
      strokeLinecap="round"
    />
  );
}

/** One line of a checklist: a pass or fail icon that swaps in place, then the statement being checked. */
function CheckRow({ passed, letter, tex }: { passed: boolean; letter?: string; tex: string }) {
  return (
    <div className="flex items-center gap-3 rounded-lg bg-surface-sunken px-4 py-3 text-meta">
      <span className="grid shrink-0" aria-hidden>
        <CheckCircle weight="fill" className={`[grid-area:1/1] size-5 text-[var(--palette-teal)] ${passed ? "swap-shown" : "swap-hidden"}`} />
        <XCircle weight="fill" className={`[grid-area:1/1] size-5 text-[var(--palette-glow)] ${passed ? "swap-hidden" : "swap-shown"}`} />
      </span>
      {letter ? <span className="text-text-muted">({letter})</span> : null}
      <span className="min-w-0 overflow-x-auto whitespace-nowrap">
        <Tex>{tex}</Tex>
      </span>
      <span className="sr-only">{passed ? "passes" : "fails"}</span>
    </div>
  );
}

const LINE_SLOPE = 0.5;
const LINE_BOUNDS: Bounds = { xMin: -8, xMax: 8, yMin: -6, yMax: 6 };
const HANDLE_REACH = 4;

const onLine = (point: Vec, shift: number) => Math.abs(point[1] - (LINE_SLOPE * point[0] + shift)) < 1e-9;
const pointOnLine = (x: number, shift: number): Vec => [x, LINE_SLOPE * x + shift];
const clampReach = (x: number) => Math.max(-HANDLE_REACH, Math.min(HANDLE_REACH, x));
const membership = (inside: boolean) => (inside ? "\\in" : "\\notin");

function lineChecks(shift: number, u: Vec, v: Vec, c: number) {
  const sum = add(u, v);
  const multiple = scale(c, u);
  return {
    sum,
    multiple,
    zero: shift === 0,
    sumInside: onLine(sum, shift),
    multipleInside: onLine(multiple, shift),
  };
}

const lineRuleTex = (shift: number) =>
  shift === 0 ? "y = \\tfrac12 x" : `y = \\tfrac12 x ${shift < 0 ? "-" : "+"} ${texNumber(Math.abs(shift))}`;

/**
 * The line y = x/2 + b with u and v riding on it. The learner slides the line until the subspace test passes.
 * Handles move in steps of 2 in x, so every point they reach has whole-number coordinates.
 */
export function ShiftedLineTest({ shift: startShift = 1, u: startU = 2, v: startV = -4, c: startC = 1.5 }: { shift?: number; u?: number; v?: number; c?: number }) {
  const [shift, setShift] = useState(startShift);
  const [uX, setUX] = useState(startU);
  const [vX, setVX] = useState(startV);
  const [c, setC] = useState(startC);
  const u = pointOnLine(uX, shift);
  const v = pointOnLine(vX, shift);
  const checks = lineChecks(shift, u, v, c);
  const allPass = checks.zero && checks.sumInside && checks.multipleInside;
  const { settled: solved, gesture } = useSettled(allPass);
  const { sum, multiple } = checks;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The purple line <Tex>H</Tex> is <Tex>{lineRuleTex(startShift)}</Tex>. Slide it with <Tex>b</Tex> until all three checks pass, whatever <Tex>{"\\mathbf u"}</Tex>, <Tex>{"\\mathbf v"}</Tex> and <Tex>c</Tex> you pick.</>}
        success={<>All three pass. Only the line through the origin, <Tex>{"y = \\tfrac12 x"}</Tex>, keeps every sum and every multiple on it, so it is a subspace.</>}
      />
      <Workbench
        plane={
          <Plane bounds={LINE_BOUNDS} label={`The line y = x/2 + ${shift} with u at ${describeVector(u)} and v at ${describeVector(v)} on it. Drag either tip along the line or use the left and right arrow keys.`}>
            {shift !== 0 ? <SetLine slope={LINE_SLOPE} shift={2 * shift} dashed color="var(--palette-teal)" /> : null}
            <SetLine slope={LINE_SLOPE} shift={shift} />
            <Arrow from={u} to={sum} color="blue" width={2.5} dashed />
            <Arrow to={sum} color="teal" />
            <Arrow to={v} color="blue" />
            <Arrow to={u} color="yellow" />
            <Marker at={multiple} color={checks.multipleInside ? "yellow" : "glow"} ring />
            <Marker at={[0, 0]} color={checks.zero ? "teal" : "glow"} ring={!checks.zero} />
            <Label at={u} color="yellow">u</Label>
            <Label at={v} color="blue" dx={-18}>v</Label>
            <Label at={sum} color="teal" dy={22}>u + v</Label>
            <Label at={multiple} color="yellow" dx={14} dy={20}>cu</Label>
            <Handle at={v} onMove={(point) => setVX(clampReach(point[0]))} color="blue" step={2} label={`Tip of vector v, on the line at ${describeVector(v)}`} />
            <Handle at={u} onMove={(point) => setUX(clampReach(point[0]))} color="yellow" step={2} label={`Tip of vector u, on the line at ${describeVector(u)}`} />
          </Plane>
        }
        readout={
          <>
            <Slider label="b" value={shift} onChange={setShift} min={-1} max={1} step={1} color={palette.purple_gray} />
            <Slider label="c" value={c} onChange={setC} min={-1.5} max={1.5} step={0.5} color={palette.yellow} />
            <p className="text-meta text-text-muted">
              <Tex>{`H: ${lineRuleTex(shift)}`}</Tex>
            </p>
            <CheckRow letter="a" passed={checks.zero} tex={`\\mathbf 0 ${membership(checks.zero)} H`} />
            <CheckRow letter="b" passed={checks.sumInside} tex={`\\textcolor{${palette.teal}}{\\mathbf u + \\mathbf v} = ${vecTex(sum)} ${membership(checks.sumInside)} H`} />
            <CheckRow letter="c" passed={checks.multipleInside} tex={`\\textcolor{${palette.yellow}}{c\\,\\mathbf u} = ${vecTex(multiple)} ${membership(checks.multipleInside)} H`} />
          </>
        }
      />
    </Panel>
  );
}

const QUADRANT_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -5, yMax: 5 };

const inQuadrant = (v: Vec) => v[0] >= 0 && v[1] >= 0;

function QuadrantShading() {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg([0, QUADRANT_BOUNDS.yMax]);
  const [x2, y2] = toSvg([QUADRANT_BOUNDS.xMax, 0]);
  return <rect x={x1} y={y1} width={x2 - x1} height={y2 - y1} fill={SET_COLOR} fillOpacity={0.18} aria-hidden />;
}

/** The closed first quadrant Q. The learner looks for a vector in Q and a scalar that throws it out. */
export function QuadrantEscape({ u: startU = [2, 1], c: startC = 2 }: { u?: Vec; c?: number }) {
  const [u, setU] = useState<Vec>(startU);
  const [c, setC] = useState(startC);
  const multiple = scale(c, u);
  const escaped = inQuadrant(u) && !inQuadrant(multiple);
  const { settled: solved, gesture } = useSettled(escaped);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Keep <Tex>{"\\mathbf u"}</Tex> in the shaded quadrant <Tex>Q</Tex>, and choose <Tex>c</Tex> so that <Tex>{"c\\,\\mathbf u"}</Tex> lands outside it.</>}
        success={<>Found one. <Tex>Q</Tex> contains <Tex>{"\\mathbf 0"}</Tex> and is closed under addition, but this multiple of <Tex>{"\\mathbf u"}</Tex> leaves it, so check (c) fails and <Tex>Q</Tex> is not a subspace.</>}
      />
      <Workbench
        plane={
          <Plane bounds={QUADRANT_BOUNDS} label={`Plane with the first quadrant shaded as Q, vector u at ${describeVector(u)} and c u at ${describeVector(multiple)}. Drag the tip of u or use arrow keys.`}>
            <QuadrantShading />
            <Arrow to={multiple} color="teal" />
            <Arrow to={u} color="yellow" />
            {solved ? <Marker at={multiple} color="glow" ring /> : null}
            <Label at={u} color="yellow">u</Label>
            <Label at={multiple} color="teal" dx={12} dy={22}>cu</Label>
            <Handle at={u} onMove={setU} color="yellow" label={`Tip of vector u, at ${describeVector(u)}`} />
          </Plane>
        }
        readout={
          <>
            <Slider label="c" value={c} onChange={setC} min={-2} max={2} step={0.5} color={palette.teal} />
            <p className="text-meta text-text-muted">
              A point is in <Tex>Q</Tex> when both of its entries are at least 0.
            </p>
            <CheckRow passed={inQuadrant(u)} tex={`\\textcolor{${palette.yellow}}{\\mathbf u} = ${vecTex(u)} ${membership(inQuadrant(u))} Q`} />
            <CheckRow passed={inQuadrant(multiple)} tex={`\\textcolor{${palette.teal}}{c\\,\\mathbf u} = ${vecTex(multiple)} ${membership(inQuadrant(multiple))} Q`} />
          </>
        }
      />
    </Panel>
  );
}

type RegionName = "axes" | "disk";

type Region = { contains: (v: Vec) => boolean; rule: string; Shape: () => React.ReactElement };

const REGION_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -5, yMax: 5 };
const DISK_RADIUS = 3;

function AxesShape() {
  const { toSvg } = usePlane();
  const [left, middleY] = toSvg([REGION_BOUNDS.xMin, 0]);
  const [right] = toSvg([REGION_BOUNDS.xMax, 0]);
  const [middleX, top] = toSvg([0, REGION_BOUNDS.yMax]);
  const [, bottom] = toSvg([0, REGION_BOUNDS.yMin]);
  return (
    <g stroke={SET_COLOR} strokeWidth={8} strokeOpacity={0.5} aria-hidden>
      <line x1={left} y1={middleY} x2={right} y2={middleY} />
      <line x1={middleX} y1={top} x2={middleX} y2={bottom} />
    </g>
  );
}

function DiskShape() {
  const { toSvg, unit } = usePlane();
  const [x, y] = toSvg([0, 0]);
  return <circle cx={x} cy={y} r={DISK_RADIUS * unit} fill={SET_COLOR} fillOpacity={0.2} stroke={SET_COLOR} strokeWidth={2} aria-hidden />;
}

const REGIONS: Record<RegionName, Region> = {
  axes: { contains: (v) => v[0] === 0 || v[1] === 0, rule: "x = 0 \\text{ or } y = 0", Shape: AxesShape },
  disk: { contains: (v) => v[0] ** 2 + v[1] ** 2 <= DISK_RADIUS ** 2 + 1e-9, rule: `x^2 + y^2 \\le ${DISK_RADIUS ** 2}`, Shape: DiskShape },
};

function regionChecks(region: Region, u: Vec, v: Vec, c: number) {
  const sum = add(u, v);
  const multiple = scale(c, u);
  const inputsInside = region.contains(u) && region.contains(v);
  const sumInside = region.contains(sum);
  const multipleInside = region.contains(multiple);
  return { sum, multiple, sumInside, multipleInside, escaped: inputsInside && !(sumInside && multipleInside) };
}

/** A shaded set H in the plane. The learner keeps u and v inside H and hunts for a sum or multiple that lands outside. */
export function CounterexampleHunt({ region: regionName, u: startU, v: startV, c: startC = 1, success }: { region: RegionName; u: Vec; v: Vec; c?: number; success: string }) {
  const region = REGIONS[regionName];
  const [u, setU] = useState<Vec>(startU);
  const [v, setV] = useState<Vec>(startV);
  const [c, setC] = useState(startC);
  const checks = regionChecks(region, u, v, c);
  const { settled: solved, gesture } = useSettled(checks.escaped);
  const { Shape, contains } = region;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Keep <Tex>{"\\mathbf u"}</Tex> and <Tex>{"\\mathbf v"}</Tex> inside the purple set <Tex>H</Tex>. Then find a sum <Tex>{"\\mathbf u + \\mathbf v"}</Tex> or a multiple <Tex>{"c\\,\\mathbf u"}</Tex> that lands outside it.</>}
        success={<RichText>{success}</RichText>}
      />
      <Workbench
        plane={
          <Plane bounds={REGION_BOUNDS} label={`The set H drawn in purple. Vector u is at ${describeVector(u)} and v is at ${describeVector(v)}. Drag either tip or use the arrow keys.`}>
            <Shape />
            <Arrow from={u} to={checks.sum} color="blue" width={2} dashed />
            <Arrow from={v} to={checks.sum} color="yellow" width={2} dashed />
            <Arrow to={checks.sum} color="teal" />
            <Arrow to={checks.multiple} color="pink" width={2.5} />
            <Arrow to={v} color="blue" />
            <Arrow to={u} color="yellow" />
            {solved && !checks.sumInside ? <Marker at={checks.sum} color="glow" ring /> : null}
            {solved && !checks.multipleInside ? <Marker at={checks.multiple} color="glow" ring /> : null}
            <Label at={u} color="yellow">u</Label>
            <Label at={v} color="blue" dx={-18}>v</Label>
            <Label at={checks.sum} color="teal" dy={22}>u + v</Label>
            <Label at={checks.multiple} color="pink" dx={12} dy={20}>cu</Label>
            <Handle at={v} onMove={setV} color="blue" label={`Tip of vector v, at ${describeVector(v)}`} />
            <Handle at={u} onMove={setU} color="yellow" label={`Tip of vector u, at ${describeVector(u)}`} />
          </Plane>
        }
        readout={
          <>
            <Slider label="c" value={c} onChange={setC} min={-2} max={3} step={0.5} color={palette.pink} />
            <p className="text-meta text-text-muted">
              <Tex>{`H: ${region.rule}`}</Tex>
            </p>
            <CheckRow passed={contains(u)} tex={`\\textcolor{${palette.yellow}}{\\mathbf u} = ${vecTex(u)} ${membership(contains(u))} H`} />
            <CheckRow passed={contains(v)} tex={`\\textcolor{${palette.blue}}{\\mathbf v} = ${vecTex(v)} ${membership(contains(v))} H`} />
            <CheckRow passed={checks.sumInside} tex={`\\textcolor{${palette.teal}}{\\mathbf u + \\mathbf v} = ${vecTex(checks.sum)} ${membership(checks.sumInside)} H`} />
            <CheckRow passed={checks.multipleInside} tex={`\\textcolor{${palette.pink}}{c\\,\\mathbf u} = ${vecTex(checks.multiple)} ${membership(checks.multipleInside)} H`} />
          </>
        }
      />
    </Panel>
  );
}

type Samples = [number, number, number];

const SAMPLE_TS: Samples = [-1, 0, 1];
const GRAPH_BOUNDS: Bounds = { xMin: -3, xMax: 3, yMin: -4, yMax: 5 };

/** Coefficients (a0, a1, a2) of the parabola through the given values at t = -1, 0, 1. */
function parabolaThrough([left, middle, right]: Samples): Samples {
  return [middle, (right - left) / 2, (left + right) / 2 - middle];
}

const valueAt = (coeffs: Samples, t: number) => coeffs[0] + coeffs[1] * t + coeffs[2] * t * t;

function GraphCurve({ coeffs, color, dashed = false }: { coeffs: Samples; color: Hue; dashed?: boolean }) {
  const { toSvg } = usePlane();
  const steps = 80;
  const path = Array.from({ length: steps + 1 }, (_, i) => {
    const t = GRAPH_BOUNDS.xMin + ((GRAPH_BOUNDS.xMax - GRAPH_BOUNDS.xMin) * i) / steps;
    const [x, y] = toSvg([t, valueAt(coeffs, t)]);
    return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
  return <path d={path} fill="none" stroke={hue(color)} strokeWidth={dashed ? 2.5 : 3.5} strokeDasharray={dashed ? "7 7" : undefined} strokeLinecap="round" />;
}

/**
 * A set of polynomials in P2 defined by one condition p(at) = value. The learner drags the values of p at t = -1, 0, 1
 * until p meets the condition, then reads off whether p + q meets it too.
 */
export function PolynomialSetTest({ at, value, q, start, success }: { at: number; value: number; q: Samples; start: Samples; success: string }) {
  const [samples, setSamples] = useState<Samples>(start);
  const p = parabolaThrough(samples);
  const sum: Samples = [p[0] + q[0], p[1] + q[1], p[2] + q[2]];
  const pInside = Math.abs(valueAt(p, at) - value) < 1e-9;
  const sumInside = Math.abs(valueAt(sum, at) - value) < 1e-9;
  const { settled: solved, gesture } = useSettled(pInside);
  const moveSample = (index: number) => (point: Vec) => setSamples((current) => current.map((old, i) => (i === index ? point[1] : old)) as Samples);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The set <Tex>H</Tex> holds the polynomials with <Tex>{`\\mathbf p(${at}) = ${value}`}</Tex>, so their graphs pass through the ringed point. The blue <Tex>{"\\mathbf q"}</Tex> is already in <Tex>H</Tex>. Drag the yellow handles until <Tex>{"\\mathbf p"}</Tex> is in <Tex>H</Tex> too, then look at the dashed teal sum.</>}
        success={<RichText>{success}</RichText>}
      />
      <Workbench
        plane={
          <Plane bounds={GRAPH_BOUNDS} label={`Graphs of p in yellow, q in blue and p + q in dashed teal, with the point (${at}, ${value}) ringed. Each yellow handle sets the value of p at one t and moves with the up and down arrow keys.`}>
            <GraphCurve coeffs={q} color="blue" />
            <GraphCurve coeffs={sum} color="teal" dashed />
            <GraphCurve coeffs={p} color="yellow" />
            <Marker at={[at, value]} color={pInside ? "teal" : "glow"} ring />
            <Marker at={[at, valueAt(sum, at)]} color={sumInside ? "teal" : "glow"} />
            {SAMPLE_TS.map((t, index) => (
              <Handle key={t} at={[t, samples[index]]} onMove={moveSample(index)} color="yellow" label={`Value of p at t = ${t}, now ${samples[index]}`} />
            ))}
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\textcolor{${palette.yellow}}{\\mathbf p(t)} = ${polynomialTex(p)}`} />
            <CheckRow passed={pInside} tex={`\\textcolor{${palette.yellow}}{\\mathbf p(${at})} = ${texNumber(valueAt(p, at))}`} />
            <CheckRow passed tex={`\\textcolor{${palette.blue}}{\\mathbf q(${at})} = ${texNumber(valueAt(q, at))}`} />
            <CheckRow passed={sumInside} tex={`\\textcolor{${palette.teal}}{(\\mathbf p + \\mathbf q)(${at})} = ${texNumber(valueAt(sum, at))}`} />
          </>
        }
      />
    </Panel>
  );
}
