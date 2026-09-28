"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, nearlyEqual, scale, texNumber, type Vec } from "./math";
import { Arrow, boundsAround, Handle, Label, Marker, Plane, Segment, usePlane } from "./plane";

const dot = (a: Vec, b: Vec) => a[0] * b[0] + a[1] * b[1];
const subtract = (a: Vec, b: Vec): Vec => [a[0] - b[0], a[1] - b[1]];
const length = (v: Vec) => Math.hypot(v[0], v[1]);
const shadowWeight = (x: Vec, onto: Vec) => dot(x, onto) / dot(onto, onto);
const straightened = (x: Vec, onto: Vec): Vec => subtract(x, scale(shadowWeight(x, onto), onto));
const pointKey = (point: Vec) => `${point[0]},${point[1]}`;
const keyPoint = (key: string): Vec => key.split(",").map(Number) as Vec;

/** A thick purple-gray bar from the origin to `to`: the shadow of a vector on an earlier one. */
function ShadowBar({ to }: { to: Vec }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg([0, 0]);
  const [x2, y2] = toSvg(to);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--palette-purple-gray)" strokeWidth={7} strokeLinecap="round" strokeOpacity={0.85} />;
}

/** A small square corner at the origin between two directions, drawn when they are perpendicular. */
function RightCorner({ first, second, shown }: { first: Vec; second: Vec; shown: boolean }) {
  const { toSvg, unit } = usePlane();
  const size = 14 / unit;
  const a = scale(size / length(first), first);
  const b = scale(size / length(second), second);
  const points = [a, add(a, b), b].map((point) => toSvg(point).join(",")).join(" ");
  return (
    <polyline
      points={points}
      fill="none"
      stroke="var(--palette-glow)"
      strokeWidth={2.5}
      className={`transition-opacity duration-300 ${shown ? "opacity-100" : "opacity-0"}`}
    />
  );
}

/** The whole line through the origin along `direction`, faint, so the shadow has somewhere to land. */
function SpanLine({ direction, color }: { direction: Vec; color: string }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg(scale(-20, direction));
  const [x2, y2] = toSvg(scale(20, direction));
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth={1.5} strokeOpacity={0.45} />;
}

/** Slide c and watch x₂ − c·v₁. Only the shadow weight (x₂·v₁)/(v₁·v₁) leaves an arrow perpendicular to v₁. */
export function ShadowSubtractSlider({ v1, x2 }: { v1: Vec; x2: Vec }) {
  const [c, setC] = useState(0);
  const { settled, gesture } = useSettled(c);
  const solved = Math.abs(dot(subtract(x2, scale(settled, v1)), v1)) < 1e-9;
  const result = subtract(x2, scale(c, v1));
  const bounds = boundsAround([v1, x2, add(x2, v1), subtract(x2, scale(2, v1)), scale(2, v1)]);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Choose <Tex>c</Tex> so that <Tex>{"\\mathbf x_2 - c\\,\\mathbf v_1"}</Tex> meets <Tex>{"\\mathbf v_1"}</Tex> at a right angle.</>}
        success={<>That is the shadow weight <Tex>{`\\tfrac{\\mathbf x_2\\cdot\\mathbf v_1}{\\mathbf v_1\\cdot\\mathbf v_1} = \\tfrac{${dot(x2, v1)}}{${dot(v1, v1)}}`}</Tex>. Any other <Tex>c</Tex> leaves some lean along <Tex>{"\\mathbf v_1"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={bounds} label={`v1 at ${describeVector(v1)} and x2 at ${describeVector(x2)}. The blue arrow x2 minus c times v1 is at ${describeVector(result)}.`}>
            <SpanLine direction={v1} color="var(--palette-yellow)" />
            <Arrow to={x2} color="blue" width={2} dashed />
            <Segment from={x2} to={result} color="blue" />
            <ShadowBar to={scale(c, v1)} />
            <Arrow to={v1} color="yellow" />
            <Arrow to={result} color="blue" />
            <RightCorner first={v1} second={result} shown={solved} />
            <Label at={v1} color="yellow">v₁</Label>
            <Label at={x2} color="blue">x₂</Label>
          </Plane>
        }
        readout={
          <>
            <Slider label="c" value={c} onChange={setC} min={-1} max={2} step={0.1} color={palette.purple_gray} />
            <Readout tex={`\\mathbf x_2 - c\\,\\mathbf v_1 = ${columnTex(result, palette.blue)}`} />
            <Readout tex={`\\mathbf v_1 \\cdot (\\mathbf x_2 - c\\,\\mathbf v_1) = ${texNumber(dot(v1, result))}`} />
          </>
        }
      />
    </Panel>
  );
}

/** Drag x₂. Gram–Schmidt turns it into v₂ = x₂ − proj; every x₂ on the line through the target parallel to v₁ gives the same v₂. */
export function StraightenedTargetHunt({ v1, target, start }: { v1: Vec; target: Vec; start: Vec }) {
  const [x2, setX2] = useState<Vec>(start);
  const { settled, gesture } = useSettled(pointKey(x2));
  const settledX2 = keyPoint(settled);
  const solved = nearlyEqual(straightened(settledX2, v1), target) && !nearlyEqual(settledX2, target);
  const shadow = scale(shadowWeight(x2, v1), v1);
  const v2 = straightened(x2, v1);
  const bounds = boundsAround([v1, target, start]);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf x_2"}</Tex> so that subtracting its shadow leaves exactly the vector at the orange ring. Start from a spot other than the ring.</>}
        success={<>Every point on the dashed line works. Sliding <Tex>{"\\mathbf x_2"}</Tex> along <Tex>{"\\mathbf v_1"}</Tex> changes only its shadow, and the shadow is thrown away.</>}
      />
      <Workbench
        plane={
          <Plane bounds={bounds} label={`v1 at ${describeVector(v1)}. x2 at ${describeVector(x2)} straightens to v2 at ${describeVector(v2)}. Target ring at ${describeVector(target)}. Drag x2 or use the arrow keys.`}>
            <SpanLine direction={v1} color="var(--palette-yellow)" />
            {solved ? <Segment from={subtract(target, scale(10, v1))} to={add(target, scale(10, v1))} color="teal" /> : null}
            <Marker at={target} color={solved ? "teal" : "glow"} ring />
            <ShadowBar to={shadow} />
            <Segment from={x2} to={shadow} color="blue" />
            <Arrow to={v1} color="yellow" />
            <Arrow to={x2} color="blue" width={2} />
            <Arrow to={v2} color="teal" />
            <RightCorner first={v1} second={v2} shown={length(v2) > 1e-6} />
            <Label at={v1} color="yellow">v₁</Label>
            <Label at={v2} color="teal" dy={22}>v₂</Label>
            <Handle at={x2} onMove={setX2} color="blue" label={`Tip of x2, at ${describeVector(x2)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\mathbf x_2 = ${columnTex(x2, palette.blue)}`} />
            <Readout tex={`\\tfrac{\\mathbf x_2\\cdot\\mathbf v_1}{\\mathbf v_1\\cdot\\mathbf v_1} = ${texNumber(shadowWeight(x2, v1))}`} />
            <Readout tex={`\\mathbf v_2 = ${columnTex(v2, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}

type Weights = { r11: number; r12: number; r22: number };

function rMatrixTex({ r11, r12, r22 }: Weights): string {
  return `\\begin{bmatrix} ${texNumber(r11)} & ${texNumber(r12)} \\\\ \\textcolor{${palette.glow}}{0} & ${texNumber(r22)} \\end{bmatrix}`;
}

/** Set the weights of R so that r₁₁u₁ lands on x₁ and r₁₂u₁ + r₂₂u₂ lands on x₂: the columns of A = QR. */
export function QrWeightSliders({ u1, u2, x1, x2 }: { u1: Vec; u2: Vec; x1: Vec; x2: Vec }) {
  const [weights, setWeights] = useState<Weights>({ r11: 1, r12: 1, r22: 1 });
  const { settled, gesture } = useSettled(weights);
  const firstBuilt = (w: Weights) => scale(w.r11, u1);
  const secondBuilt = (w: Weights) => add(scale(w.r12, u1), scale(w.r22, u2));
  const solved = nearlyEqual(firstBuilt(settled), x1) && nearlyEqual(secondBuilt(settled), x2);
  const along = scale(weights.r12, u1);
  const bounds = boundsAround([x1, x2, scale(6, u1), scale(6, u2), add(scale(6, u1), scale(6, u2))]);
  const set = (key: keyof Weights) => (value: number) => setWeights((current) => ({ ...current, [key]: value }));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Set the weights so the yellow arrow lands on <Tex>{"\\mathbf x_1"}</Tex> and the teal arrow lands on <Tex>{"\\mathbf x_2"}</Tex>.</>}
        success={<>These weights are the columns of <Tex>R</Tex>. Its lower-left entry is 0 because <Tex>{"\\mathbf x_1"}</Tex> points along <Tex>{"\\mathbf u_1"}</Tex> and needs no <Tex>{"\\mathbf u_2"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={bounds} label={`Orthonormal u1 at ${describeVector(u1)} and u2 at ${describeVector(u2)}. Rings mark x1 at ${describeVector(x1)} and x2 at ${describeVector(x2)}.`}>
            <SpanLine direction={u1} color="var(--palette-yellow)" />
            <Marker at={x1} color={solved ? "teal" : "glow"} ring />
            <Marker at={x2} color={solved ? "teal" : "glow"} ring />
            <Arrow to={firstBuilt(weights)} color="yellow" />
            <Arrow to={along} color="yellow" width={2} dashed />
            <Arrow from={along} to={secondBuilt(weights)} color="blue" width={2.5} />
            <Arrow to={secondBuilt(weights)} color="teal" />
            <Arrow to={u1} color="yellow" width={5} />
            <Arrow to={u2} color="blue" width={5} />
            <RightCorner first={u1} second={u2} shown />
            <Label at={x1} color="text" dy={24}>x₁</Label>
            <Label at={x2} color="text">x₂</Label>
          </Plane>
        }
        readout={
          <>
            <Slider label="r_{11}" value={weights.r11} onChange={set("r11")} min={0} max={6} step={0.5} color={palette.yellow} />
            <Slider label="r_{12}" value={weights.r12} onChange={set("r12")} min={0} max={6} step={0.5} color={palette.yellow} />
            <Slider label="r_{22}" value={weights.r22} onChange={set("r22")} min={0} max={6} step={0.5} color={palette.blue} />
            <Readout tex={`R = ${rMatrixTex(weights)}`} />
            <Readout tex={`A = \\begin{bmatrix} ${texNumber(x1[0])} & ${texNumber(x2[0])} \\\\ ${texNumber(x1[1])} & ${texNumber(x2[1])} \\end{bmatrix}`} />
          </>
        }
      />
    </Panel>
  );
}
