"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { add, nearlyEqual, scale, texNumber, type Vec } from "./math";
import { Arrow, boundsAround, DEFAULT_BOUNDS, Handle, Label, Marker, Plane, Segment } from "./plane";


export function VectorExplorer({ start = [3, 2], goal }: { start?: Vec; goal?: Vec }) {
  const [tip, setTip] = useState<Vec>(start);
  const solved = goal ? nearlyEqual(tip, goal) : false;
  const readout = `\\vec v = \\begin{bmatrix} \\textcolor{${palette.i_hat}}{${texNumber(tip[0])}} \\\\ \\textcolor{${palette.j_hat}}{${texNumber(tip[1])}} \\end{bmatrix}`;
  return (
    <Panel>
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
  const solved = goal ? nearlyEqual(sum, goal) : false;
  const readout = `${columnTex(v, palette.yellow)} + ${columnTex(w, palette.blue)} = ${columnTex(sum, palette.teal)}`;
  return (
    <Panel>
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
  const solved = target !== undefined && Math.abs(c - target) < 1e-6;
  const goalPoint = target !== undefined ? scale(target, vector) : undefined;
  return (
    <Panel>
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
  const solved = nearlyEqual(result, target);
  return (
    <Panel>
      <Goal
        solved={solved}
        prompt={<>Choose weights <Tex>a</Tex> and <Tex>b</Tex> so that <Tex>{"a\\,\\vec v + b\\,\\vec w"}</Tex> lands on the ringed point <Tex>{columnTex(target)}</Tex>.</>}
        success={<>You found it: <Tex>{`${texNumber(a)}\\,\\vec v + ${texNumber(b)}\\,\\vec w = ${columnTex(target)}`}</Tex>. Those weights are the only pair that works.</>}
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
