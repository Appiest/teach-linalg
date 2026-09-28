"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { useSettled } from "./gesture";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { hue, type Hue } from "./colors";
import { add, scale, texNumber, type Vec } from "./math";
import { Arrow, boundsAround, Handle, Label, Marker, Plane, Segment, usePlane } from "./plane";

const cross = (a: Vec, b: Vec) => a[0] * b[1] - a[1] * b[0];
const isZero = (v: Vec) => v[0] === 0 && v[1] === 0;

function Line({ through, direction, color, width, opacity }: { through: Vec; direction: Vec; color: Hue; width: number; opacity: number }) {
  const { toSvg, bounds } = usePlane();
  const span = bounds.xMax - bounds.xMin + bounds.yMax - bounds.yMin + Math.hypot(...through);
  const reach = span / Math.max(Math.hypot(...direction), 1e-9);
  const [x1, y1] = toSvg(add(through, scale(-reach, direction)));
  const [x2, y2] = toSvg(add(through, scale(reach, direction)));
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={width} strokeOpacity={opacity} strokeLinecap="round" />;
}

const MAX_LINES_PER_FAMILY = 200;

/** The whole-number weights k whose line k·offset + t·direction crosses the visible plane. */
function weightsCovering(offset: Vec, direction: Vec, corners: Vec[]): number[] {
  const denominator = cross(direction, offset);
  if (denominator === 0) return [0];
  const reached = corners.map((corner) => cross(direction, corner) / denominator);
  const low = Math.max(Math.floor(Math.min(...reached)), -MAX_LINES_PER_FAMILY / 2);
  const high = Math.min(Math.ceil(Math.max(...reached)), MAX_LINES_PER_FAMILY / 2);
  return Array.from({ length: high - low + 1 }, (_, i) => low + i);
}

/** Lines of a·v + t·w and t·v + b·w for whole-number weights, enough of them to reach every corner of the plane. */
function SkewedGrid({ v, w }: { v: Vec; w: Vec }) {
  const { bounds } = usePlane();
  const corners: Vec[] = [[bounds.xMin, bounds.yMin], [bounds.xMin, bounds.yMax], [bounds.xMax, bounds.yMin], [bounds.xMax, bounds.yMax]];
  return (
    <g aria-hidden>
      {isZero(w) ? null : weightsCovering(v, w, corners).map((k) => <Line key={`v${k}`} through={scale(k, v)} direction={w} color="teal" width={1.2} opacity={0.45} />)}
      {isZero(v) ? null : weightsCovering(w, v, corners).map((k) => <Line key={`w${k}`} through={scale(k, w)} direction={v} color="teal" width={1.2} opacity={0.45} />)}
    </g>
  );
}

function spanName(v: Vec, w: Vec): string {
  if (isZero(v) && isZero(w)) return "\\{\\vec 0\\}";
  return cross(v, w) === 0 ? "\\text{a line}" : "\\mathbb{R}^2";
}

export function SpanPainter({ v: startV = [3, 2], w: startW = [-1, 2] }: { v?: Vec; w?: Vec }) {
  const [v, setV] = useState<Vec>(startV);
  const [w, setW] = useState<Vec>(startW);
  const collapsed = !isZero(v) && cross(v, w) === 0;
  const { settled: solved, gesture } = useSettled(collapsed);
  const determinant = cross(v, w);
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The teal lines show where <Tex>{"a\\vec v + b\\vec w"}</Tex> can land. Move <Tex>{"\\vec w"}</Tex> until the span shrinks to a single line.</>}
        success={<>Now <Tex>{"\\vec w"}</Tex> is a multiple of <Tex>{"\\vec v"}</Tex>, so every combination is a multiple of <Tex>{"\\vec v"}</Tex> and lands on the one teal line.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([startV, startW])} label="Plane with vectors v and w and the lines their combinations cover. Drag either tip.">
            <SkewedGrid v={v} w={w} />
            {solved ? <Line through={[0, 0]} direction={v} color="teal" width={4} opacity={1} /> : null}
            <Arrow to={w} color="blue" />
            <Arrow to={v} color="yellow" />
            <Label at={v} color="yellow">v</Label>
            <Label at={w} color="blue" dx={-18}>w</Label>
            <Handle at={w} onMove={setW} color="blue" label={`Tip of vector w, at ${describeVector(w)}`} />
            <Handle at={v} onMove={setV} color="yellow" label={`Tip of vector v, at ${describeVector(v)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\begin{aligned} &\\operatorname{Span}\\{${columnTex(v, palette.yellow)}, ${columnTex(w, palette.blue)}\\} \\\\ &= ${spanName(v, w)} \\end{aligned}`} />
            <Readout tex={`v_1 w_2 - v_2 w_1 = ${texNumber(determinant)}`} />
          </>
        }
      />
    </Panel>
  );
}

export function EntryHunt({ v = [2, 1], w = [-4, -2], x = 4, answer = 2, min = -3, max = 4 }: {
  v?: Vec; w?: Vec; x?: number; answer?: number; min?: number; max?: number;
}) {
  const [h, setH] = useState(min);
  const b: Vec = [x, h];
  const { settled: solved, gesture } = useSettled(h === answer);
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Every <Tex>{`\\vec b = \\begin{bmatrix} ${texNumber(x)} \\\\ h \\end{bmatrix}`}</Tex> sits on the dashed line. Find the <Tex>h</Tex> that puts <Tex>{"\\vec b"}</Tex> in <Tex>{"\\operatorname{Span}\\{\\vec v, \\vec w\\}"}</Tex>.</>}
        success={<>Right, <Tex>{`h = ${texNumber(answer)}`}</Tex>. The dashed line crosses the span in exactly one place, so only one <Tex>h</Tex> works.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([v, w, [x, min], [x, max]])} label={`Span of v and w, and the vector b equal to (${x}, h)`}>
            <Line through={[0, 0]} direction={v} color="teal" width={3} opacity={0.8} />
            <Segment from={[x, min - 1]} to={[x, max + 1]} color="text" />
            <Arrow to={w} color="blue" />
            <Arrow to={v} color="yellow" />
            <Arrow to={b} color="pink" />
            <Label at={v} color="yellow" dx={-6} dy={-14}>v</Label>
            <Label at={w} color="blue" dx={-18} dy={18}>w</Label>
            <Label at={b} color="pink">b</Label>
            {solved ? <Marker at={b} color="teal" /> : null}
          </Plane>
        }
        readout={
          <>
            <Slider label="h" value={h} onChange={setH} min={min} max={max} step={1} color={palette.pink} />
            <Readout tex={`x_1${columnTex(v, palette.yellow)} + x_2${columnTex(w, palette.blue)} = ${columnTex(b, palette.pink)}`} />
          </>
        }
      />
    </Panel>
  );
}
