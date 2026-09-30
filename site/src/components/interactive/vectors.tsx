"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { useSettled } from "./gesture";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { add, nearlyEqual, scale, texNumber, type Vec } from "./math";
import { Arrow, boundsAround, DEFAULT_BOUNDS, Handle, Label, Marker, Plane, Segment } from "./plane";


export function VectorExplorer({ start = [3, 2], goal }: { start?: Vec; goal?: Vec }) {
  const [tip, setTip] = useState<Vec>(start);
  const { settled: solved, gesture } = useSettled(goal ? nearlyEqual(tip, goal) : false);
  const readout = `\\vec v = \\begin{bmatrix} \\textcolor{${palette.i_hat}}{${texNumber(tip[0])}} \\\\ \\textcolor{${palette.j_hat}}{${texNumber(tip[1])}} \\end{bmatrix}`;
  return (
    <Panel gesture={gesture}>
      {goal ? (
        <Goal
          solved={solved}
          prompt={<>Drag the tip of <Tex>{"\\vec v"}</Tex> until <Tex>{`\\vec v = ${columnTex(goal)}`}</Tex>.</>}
          success={<>That&rsquo;s it. The first entry is how far right, the second is how far up.</>}
        />
      ) : null}
      <Workbench
        plane={
          <Plane bounds={goal ? boundsAround([goal]) : DEFAULT_BOUNDS} label="Plane with vector v. Drag its tip or use arrow keys.">
            <Segment from={[0, 0]} to={[tip[0], 0]} color="green" />
            <Segment from={[tip[0], 0]} to={tip} color="red" />
            {goal && !solved ? <Marker at={goal} ring /> : null}
            <Arrow to={tip} color="yellow" />
            <Handle at={tip} onMove={setTip} color="yellow" label={`Tip of vector v, at ${describeVector(tip)}`} />
          </Plane>
        }
        readout={<Readout tex={readout} />}
      />
    </Panel>
  );
}

export function AdditionExplorer({ v: startV = [3, 2], w: startW = [-1, 2], goal }: { v?: Vec; w?: Vec; goal?: Vec }) {
  const [v, setV] = useState<Vec>(startV);
  const [w, setW] = useState<Vec>(startW);
  const sum = add(v, w);
  const { settled: solved, gesture } = useSettled(goal ? nearlyEqual(sum, goal) : false);
  const readout = `${columnTex(v, palette.yellow)} + ${columnTex(w, palette.blue)} = ${columnTex(sum, palette.teal)}`;
  return (
    <Panel gesture={gesture}>
      {goal ? (
        <Goal
          solved={solved}
          prompt={<>Move both tips so that <Tex>{`\\vec v + \\vec w = ${columnTex(goal)}`}</Tex>. There are many ways to do it.</>}
          success={<>Nice. Every pair whose entries add up to the target works, and the dashed copy of <Tex>{"\\vec w"}</Tex> always ends at the same place.</>}
        />
      ) : null}
      <Workbench
        plane={
          <Plane bounds={goal ? boundsAround([goal, startV, startW]) : boundsAround([startV, startW])} label="Plane with vectors v and w and their sum. Drag either tip.">
            {goal && !solved ? <Marker at={goal} ring /> : null}
            <Arrow from={v} to={sum} color="blue" width={2.5} dashed />
            <Arrow to={sum} color="teal" />
            <Arrow to={w} color="blue" />
            <Arrow to={v} color="yellow" />
            <Label at={v} color="yellow">v</Label>
            <Label at={w} color="blue" dx={-18}>w</Label>
            <Label at={sum} color="teal">v + w</Label>
            <Handle at={w} onMove={setW} color="blue" label={`Tip of vector w, at ${describeVector(w)}`} />
            <Handle at={v} onMove={setV} color="yellow" label={`Tip of vector v, at ${describeVector(v)}`} />
          </Plane>
        }
        readout={<Readout tex={readout} />}
      />
    </Panel>
  );
}

export function ScaleExplorer({ vector = [3, 2], target }: { vector?: Vec; target?: number }) {
  const [c, setC] = useState(1);
  const scaled = scale(c, vector);
  const { settled: solved, gesture } = useSettled(target !== undefined && Math.abs(c - target) < 1e-6);
  const goalPoint = target !== undefined ? scale(target, vector) : undefined;
  return (
    <Panel gesture={gesture}>
      {goalPoint ? (
        <Goal
          solved={solved}
          prompt={<>Find the scalar <Tex>c</Tex> that moves the tip of <Tex>{"c\\,\\vec v"}</Tex> onto the ringed point.</>}
          success={<>Right, <Tex>{`c = ${texNumber(target ?? 0)}`}</Tex>. A negative scalar flips the arrow before stretching it.</>}
        />
      ) : null}
      <Workbench
        plane={
          <Plane bounds={boundsAround([scale(2, vector), scale(-2, vector)])} label="Plane with vector v scaled by c">
            {goalPoint && !solved ? <Marker at={goalPoint} ring /> : null}
            <Arrow to={vector} color="text" width={2} dashed />
            <Arrow to={scaled} color="yellow" />
          </Plane>
        }
        readout={
          <>
            <Slider label="c" value={c} onChange={setC} min={-2} max={2} step={0.25} color={palette.yellow} />
            <Readout tex={`c\\,${columnTex(vector)} = ${columnTex(scaled, palette.yellow)}`} />
          </>
        }
      />
    </Panel>
  );
}

export function CombinationTarget({ v = [3, 2], w = [-1, 2], target }: { v?: Vec; w?: Vec; target: Vec }) {
  const [a, setA] = useState(1);
  const [b, setB] = useState(0);
  const av = scale(a, v);
  const result = add(av, scale(b, w));
  const { settled: solved, gesture } = useSettled(nearlyEqual(result, target));
  const determinant = v[0] * w[1] - v[1] * w[0];
  const answerA = (target[0] * w[1] - target[1] * w[0]) / determinant;
  const answerB = (v[0] * target[1] - v[1] * target[0]) / determinant;
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Choose weights <Tex>a</Tex> and <Tex>b</Tex> so that <Tex>{"a\\,\\vec v + b\\,\\vec w"}</Tex> lands on the ringed point <Tex>{columnTex(target)}</Tex>.</>}
        success={<>You found it: <Tex>{`${texNumber(answerA)}\\,\\vec v ${answerB < 0 ? "-" : "+"} ${texNumber(Math.abs(answerB))}\\,\\vec w = ${columnTex(target)}`}</Tex>. Those weights are the only pair that works.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([target, v, w])} label="Linear combination of v and w with adjustable weights">
            {!solved ? <Marker at={target} ring /> : null}
            <Arrow to={v} color="yellow" width={1.5} dashed />
            <Arrow to={w} color="blue" width={1.5} dashed />
            <Arrow to={av} color="yellow" />
            <Arrow from={av} to={result} color="blue" />
            <Arrow to={result} color="teal" />
            {solved ? <Marker at={target} color="teal" /> : null}
          </Plane>
        }
        readout={
          <>
            <Slider label="a" value={a} onChange={setA} min={-3} max={3} step={0.5} color={palette.yellow} />
            <Slider label="b" value={b} onChange={setB} min={-3} max={3} step={0.5} color={palette.blue} />
            <Readout tex={`${texNumber(a)}${columnTex(v, palette.yellow)} + ${texNumber(b)}${columnTex(w, palette.blue)} = ${columnTex(result, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}

export function DifferenceExplorer({ u: startU = [4, 1], v: startV = [1, 3], goal }: { u?: Vec; v?: Vec; goal: Vec }) {
  const [u, setU] = useState<Vec>(startU);
  const [v, setV] = useState<Vec>(startV);
  const difference = add(u, scale(-1, v));
  const { settled: solved, gesture } = useSettled(nearlyEqual(difference, goal));
  const readout = `${columnTex(u, palette.yellow)} - ${columnTex(v, palette.blue)} = ${columnTex(difference, palette.teal)}`;
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Move the tips so that <Tex>{`\\vec u - \\vec v = ${columnTex(goal)}`}</Tex>. Watch the dashed arrow from the tip of <Tex>{"\\vec v"}</Tex> to the tip of <Tex>{"\\vec u"}</Tex>.</>}
        success={<>That works. The difference <Tex>{"\\vec u - \\vec v"}</Tex> is the trip from the tip of <Tex>{"\\vec v"}</Tex> to the tip of <Tex>{"\\vec u"}</Tex>, moved back to start at the origin.</>}
      />
      <Workbench
        plane={
          <Plane bounds={{ xMin: -5, xMax: 6, yMin: -4, yMax: 5 }} label="Plane with vectors u and v and their difference. Drag either tip.">
            <Arrow from={v} to={u} color="teal" width={2.5} dashed />
            <Arrow to={difference} color="teal" />
            <Arrow to={v} color="blue" />
            <Arrow to={u} color="yellow" />
            <Label at={u} color="yellow">u</Label>
            <Label at={v} color="blue" dx={-18}>v</Label>
            <Label at={difference} color="teal">u − v</Label>
            <Handle at={v} onMove={setV} color="blue" label={`Tip of vector v, at ${describeVector(v)}`} />
            <Handle at={u} onMove={setU} color="yellow" label={`Tip of vector u, at ${describeVector(u)}`} />
          </Plane>
        }
        readout={<Readout tex={readout} />}
      />
    </Panel>
  );
}

const GRID_REACH = 12;

function SkewedGrid({ v, w }: { v: Vec; w: Vec }) {
  const lines = [];
  for (let k = -GRID_REACH; k <= GRID_REACH; k += 1) {
    lines.push(<Segment key={`v${k}`} from={add(scale(k, v), scale(-GRID_REACH, w))} to={add(scale(k, v), scale(GRID_REACH, w))} color="blue" dashed={false} />);
    lines.push(<Segment key={`w${k}`} from={add(scale(k, w), scale(-GRID_REACH, v))} to={add(scale(k, w), scale(GRID_REACH, v))} color="yellow" dashed={false} />);
  }
  return <g opacity={0.22}>{lines}</g>;
}

export function GridWeights({ v, w, target }: { v: Vec; w: Vec; target: Vec }) {
  const [a, setA] = useState(0);
  const [b, setB] = useState(0);
  const av = scale(a, v);
  const result = add(av, scale(b, w));
  const { settled: solved, gesture } = useSettled(nearlyEqual(result, target));
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Count grid steps to reach the ringed point. Each yellow step is one <Tex>{"\\vec v"}</Tex> and each blue step is one <Tex>{"\\vec w"}</Tex>.</>}
        success={<>You read the weights straight off the slanted grid. On this grid, the weights are the point&rsquo;s coordinates.</>}
      />
      <Workbench
        plane={
          <Plane bounds={{ xMin: -8, xMax: 5, yMin: -3, yMax: 5 }} label="Slanted grid made of multiples of v and w, with a ringed target point">
            <SkewedGrid v={v} w={w} />
            {!solved ? <Marker at={target} ring /> : null}
            <Arrow to={av} color="yellow" />
            <Arrow from={av} to={result} color="blue" />
            {solved ? <Marker at={target} color="teal" /> : null}
          </Plane>
        }
        readout={
          <>
            <Slider label="a" value={a} onChange={setA} min={-4} max={4} step={0.5} color={palette.yellow} />
            <Slider label="b" value={b} onChange={setB} min={-4} max={4} step={0.5} color={palette.blue} />
            <Readout tex={`${texNumber(a)}${columnTex(v, palette.yellow)} + ${texNumber(b)}${columnTex(w, palette.blue)} = ${columnTex(result, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}
