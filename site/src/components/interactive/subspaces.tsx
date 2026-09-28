"use client";

import { CheckCircle, XCircle } from "@phosphor-icons/react";
import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { describeVector, Goal, Panel, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, scale, texNumber, type Vec } from "./math";
import { Arrow, Handle, Label, Marker, Plane, usePlane, type Bounds } from "./plane";

const SET_COLOR = "var(--palette-purple-gray)";

const vecTex = (v: Vec) => `(${texNumber(v[0])}, ${texNumber(v[1])})`;

const scalarTex = (c: number) => (c < 0 ? `(${texNumber(c)})` : texNumber(c));

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
        success={<>Found one. <Tex>Q</Tex> contains <Tex>{"\\mathbf 0"}</Tex> and is closed under addition, but <Tex>{`${scalarTex(c)}\\,${vecTex(u)} = ${vecTex(multiple)}`}</Tex> leaves it, so check (c) fails and <Tex>Q</Tex> is not a subspace.</>}
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
