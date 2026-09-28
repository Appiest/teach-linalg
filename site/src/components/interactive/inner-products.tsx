"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { formatNumber, scale, texNumber, type Vec } from "./math";
import { Arrow, Handle, Label, Plane, usePlane, type Bounds } from "./plane";

const SHADOW_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -4, yMax: 5 };
const UNIT_BOUNDS: Bounds = { xMin: -3, xMax: 3, yMin: -3, yMax: 3 };
const ROW_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -5, yMax: 5 };

const dot = (a: Vec, b: Vec) => a[0] * b[0] + a[1] * b[1];
const length = (a: Vec) => Math.hypot(a[0], a[1]);
const isZero = (a: Vec) => a[0] === 0 && a[1] === 0;
const pointKey = (point: Vec) => `${point[0]},${point[1]}`;
const keyPoint = (key: string): Vec => key.split(",").map(Number) as Vec;

/** Where the perpendicular from the tip of w meets the line through v. */
function shadowFoot(v: Vec, w: Vec): Vec {
  return scale(dot(v, w) / dot(v, v), v);
}

const SHADOW_TEX_COLORS: Record<string, string> = { glow: palette.glow, teal: palette.teal, pink: palette.pink };

function shadowHue(value: number): Hue {
  if (value === 0) return "glow";
  return value > 0 ? "teal" : "pink";
}

function LineThrough({ direction, color, opacity = 0.45, width = 2 }: { direction: Vec; color: Hue; opacity?: number; width?: number }) {
  const { toSvg } = usePlane();
  const reach = 40;
  const [x1, y1] = toSvg(scale(-reach, direction));
  const [x2, y2] = toSvg(scale(reach, direction));
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={width} strokeOpacity={opacity} strokeLinecap="round" />;
}

function ShadowBar({ to, color }: { to: Vec; color: Hue }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg([0, 0]);
  const [x2, y2] = toSvg(to);
  if (Math.hypot(x2 - x1, y2 - y1) < 1) return null;
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={10} strokeOpacity={0.75} strokeLinecap="round" />;
}

function DropLine({ from, to }: { from: Vec; to: Vec }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg(from);
  const [x2, y2] = toSvg(to);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--palette-text-muted)" strokeWidth={2} strokeDasharray="5 5" />;
}

/** The small square in the corner between two perpendicular directions at the origin. */
function RightAngleMark({ first, second, size = 0.4 }: { first: Vec; second: Vec; size?: number }) {
  const { toSvg } = usePlane();
  const a = scale(size / length(first), first);
  const b = scale(size / length(second), second);
  const corners = [a, [a[0] + b[0], a[1] + b[1]] as Vec, b].map(toSvg);
  return <polyline points={corners.map(([x, y]) => `${x},${y}`).join(" ")} fill="none" stroke={hue("glow")} strokeWidth={2.5} />;
}

function UnitCircle() {
  const { toSvg, unit } = usePlane();
  const [cx, cy] = toSvg([0, 0]);
  return <circle cx={cx} cy={cy} r={unit} fill="none" stroke="var(--palette-text-muted)" strokeWidth={2} strokeDasharray="5 5" />;
}

/** Drag w around a fixed v and watch its shadow on the line of v; the goal is a nonzero w with v·w = 0. */
export function DotShadowHunt({ v = [3, 2], start = [-1, 2] }: { v?: Vec; start?: Vec }) {
  const [w, setW] = useState<Vec>(start);
  const { settled, gesture } = useSettled(pointKey(w));
  const settledW = keyPoint(settled);
  const solved = !isZero(settledW) && dot(v, settledW) === 0;
  const value = dot(v, w);
  const foot = shadowFoot(v, w);
  const color = shadowHue(value);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the tip of <Tex>{"\\mathbf w"}</Tex> until its shadow on the line of <Tex>{"\\mathbf v"}</Tex> disappears, without making <Tex>{"\\mathbf w"}</Tex> zero.</>}
        success={<>The shadow is gone, so <Tex>{"\\mathbf v\\cdot\\mathbf w = 0"}</Tex> and the two arrows meet at a right angle.</>}
      />
      <Workbench
        plane={
          <Plane bounds={SHADOW_BOUNDS} label={`v is fixed at ${describeVector(v)}. w is at ${describeVector(w)}, and v dot w is ${formatNumber(value)}. Drag the tip of w or use the arrow keys.`}>
            <LineThrough direction={v} color="yellow" />
            <ShadowBar to={foot} color={color} />
            {isZero(w) ? null : <DropLine from={w} to={foot} />}
            {solved ? <RightAngleMark first={v} second={settledW} /> : null}
            <Arrow to={v} color="yellow" />
            <Arrow to={w} color="blue" />
            <Label at={v} color="yellow">v</Label>
            <Label at={w} color="blue">w</Label>
            <Handle at={w} onMove={setW} color="blue" label={`Tip of w, at ${describeVector(w)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`${columnTex(v, palette.yellow)} \\cdot ${columnTex(w, palette.blue)} = ${texNumber(v[0])}(${texNumber(w[0])}) + ${texNumber(v[1])}(${texNumber(w[1])})`} />
            <Readout tex={`\\mathbf v\\cdot\\mathbf w = \\textcolor{${SHADOW_TEX_COLORS[color]}}{${texNumber(value)}}`} />
          </>
        }
      />
    </Panel>
  );
}

/** Scale a vector with a slider until its tip lands on the unit circle, pointing the same way. */
export function UnitCircleScale({ vector = [3, 4], start = 0.5 }: { vector?: Vec; start?: number }) {
  const [c, setC] = useState(start);
  const { settled, gesture } = useSettled(c);
  const target = 1 / length(vector);
  const solved = Math.abs(settled - target) < 1e-9;
  const scaled = scale(c, vector);
  const size = Math.abs(c) * length(vector);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Choose <Tex>{"c"}</Tex> so that <Tex>{"c\\,\\mathbf v"}</Tex> is a unit vector pointing the same way as <Tex>{`\\mathbf v = (${vector.map((entry) => texNumber(entry)).join(", ")})`}</Tex>.</>}
        success={<>That is <Tex>{`c = 1/\\|\\mathbf v\\| = 1/${texNumber(length(vector))}`}</Tex>, so the tip sits on the unit circle.</>}
      />
      <Workbench
        plane={
          <Plane bounds={UNIT_BOUNDS} label={`c times v is ${describeVector(scaled)}, with length ${formatNumber(size)}. The dashed circle has radius 1.`}>
            <UnitCircle />
            <Arrow to={scaled} color={solved ? "teal" : "yellow"} width={solved ? 4.5 : 3.5} />
            <Label at={scaled} color={solved ? "teal" : "yellow"}>cv</Label>
          </Plane>
        }
        readout={
          <>
            <Slider label="c" value={c} onChange={(value) => setC(Math.round(value * 100) / 100)} min={-0.5} max={0.5} step={0.02} color={palette.yellow} />
            <Readout tex={`c\\,\\mathbf v = ${columnTex(scaled, palette.yellow)}`} />
            <Readout tex={`\\|c\\,\\mathbf v\\| = ${texNumber(Math.abs(c))} \\cdot ${texNumber(length(vector))} = \\textcolor{${solved ? palette.teal : palette.text}}{${texNumber(size)}}`} />
          </>
        }
      />
    </Panel>
  );
}

/** Drag x until Ax = 0; the solutions form Nul A, the line perpendicular to every row of A. */
export function RowPerpendicularHunt({ rows = [[1, -2], [-2, 4]], start = [1, 1] }: { rows?: [Vec, Vec]; start?: Vec }) {
  const [x, setX] = useState<Vec>(start);
  const { settled, gesture } = useSettled(pointKey(x));
  const settledX = keyPoint(settled);
  const solved = !isZero(settledX) && rows.every((row) => dot(row, settledX) === 0);
  const products = rows.map((row) => dot(row, x));
  const rowTex = `\\begin{bmatrix} ${rows.map((row) => row.map((entry) => texNumber(entry)).join(" & ")).join(" \\\\ ")} \\end{bmatrix}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf x"}</Tex> to a nonzero point where <Tex>{"A\\mathbf x = \\mathbf 0"}</Tex>. Each entry of <Tex>{"A\\mathbf x"}</Tex> is a row of <Tex>{"A"}</Tex> dotted with <Tex>{"\\mathbf x"}</Tex>.</>}
        success={<>Both rows dot to zero with <Tex>{"\\mathbf x"}</Tex>, so it lies on the blue line <Tex>{"\\operatorname{Nul}A = (\\operatorname{Row}A)^\\perp"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={ROW_BOUNDS} label={`The rows of A are ${describeVector(rows[0])} and ${describeVector(rows[1])}. x is at ${describeVector(x)}, and A x is ${describeVector(products as Vec)}. Drag the tip of x or use the arrow keys.`}>
            <LineThrough direction={rows[0]} color="yellow" />
            {solved ? <LineThrough direction={settledX} color="blue" opacity={0.9} width={3.5} /> : null}
            {solved ? <RightAngleMark first={rows[0]} second={settledX} /> : null}
            <Arrow to={rows[0]} color="yellow" />
            <Arrow to={rows[1]} color="yellow" />
            <Arrow to={x} color="text" />
            <Label at={rows[0]} color="yellow">r₁</Label>
            <Label at={rows[1]} color="yellow">r₂</Label>
            <Label at={x} color="text">x</Label>
            <Handle at={x} onMove={setX} color="text" label={`Tip of x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`A\\mathbf x = ${rowTex}${columnTex(x)} = ${columnTex(products)}`} />
            <Readout tex={`\\mathbf r_1\\cdot\\mathbf x = \\textcolor{${products[0] === 0 ? palette.teal : palette.text}}{${texNumber(products[0])}}, \\quad \\mathbf r_2\\cdot\\mathbf x = \\textcolor{${products[1] === 0 ? palette.teal : palette.text}}{${texNumber(products[1])}}`} />
          </>
        }
      />
    </Panel>
  );
}
