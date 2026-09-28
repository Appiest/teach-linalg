"use client";

import { CheckCircle, Circle } from "@phosphor-icons/react";
import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, apply, nearlyEqual, scale, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, boundsAround, Handle, Label, Marker, Plane, usePlane } from "./plane";

/** The weights w with w1·u + w2·v = x. */
function weightsOf(x: Vec, u: Vec, v: Vec): Vec {
  const determinant = u[0] * v[1] - v[0] * u[1];
  return [(x[0] * v[1] - v[0] * x[1]) / determinant, (u[0] * x[1] - x[0] * u[1]) / determinant];
}

function GridLine({ through, direction, stroke, opacity }: { through: Vec; direction: Vec; stroke: string; opacity: number }) {
  const { toSvg, bounds } = usePlane();
  const reach = (bounds.xMax - bounds.xMin + bounds.yMax - bounds.yMin) / Math.hypot(...direction);
  const [x1, y1] = toSvg(add(through, scale(-reach, direction)));
  const [x2, y2] = toSvg(add(through, scale(reach, direction)));
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={stroke} strokeWidth={1.2} strokeOpacity={opacity} />;
}

/** The lines through whole-number multiples of u and v: the address grid of the basis {u, v}. */
function AddressGrid({ u, v, stroke, opacity = 0.5, reach = 14 }: { u: Vec; v: Vec; stroke: string; opacity?: number; reach?: number }) {
  const weights = Array.from({ length: 2 * reach + 1 }, (_, i) => i - reach);
  return (
    <g aria-hidden>
      {weights.map((k) => <GridLine key={`u${k}`} through={scale(k, u)} direction={v} stroke={stroke} opacity={opacity} />)}
      {weights.map((k) => <GridLine key={`v${k}`} through={scale(k, v)} direction={u} stroke={stroke} opacity={opacity} />)}
    </g>
  );
}

const B_GRID = "var(--palette-purple-gray)";
const C_GRID = "var(--palette-pink)";
const B_TEX: string[] = [palette.i_hat, palette.j_hat];
const C_TEX: string[] = [palette.pink, palette.blue];

const pairTex = (entries: Vec, colors: string[]) =>
  `\\begin{bmatrix} \\textcolor{${colors[0]}}{${texNumber(entries[0])}} \\\\ \\textcolor{${colors[1]}}{${texNumber(entries[1])}} \\end{bmatrix}`;

const matrixTex = (columns: [Vec, Vec], colors: string[] = [palette.i_hat, palette.j_hat]) =>
  `\\begin{bmatrix} \\textcolor{${colors[0]}}{${texNumber(columns[0][0])}} & \\textcolor{${colors[1]}}{${texNumber(columns[1][0])}} \\\\ \\textcolor{${colors[0]}}{${texNumber(columns[0][1])}} & \\textcolor{${colors[1]}}{${texNumber(columns[1][1])}} \\end{bmatrix}`;

type TwoBases = { b1: Vec; b2: Vec; c1: Vec; c2: Vec };

/** Drag one point over two overlaid grids and read its address in each; the goal names a B-address to find. */
export function TwoAddresses({ b1 = [2, 1], b2 = [-1, 2], c1 = [1, 0], c2 = [-1, 1], target = [1, 1], start = [3, 4] }: TwoBases & { target?: Vec; start?: Vec }) {
  const [x, setX] = useState<Vec>(start);
  const inB = weightsOf(x, b1, b2);
  const inC = weightsOf(x, c1, c2);
  const { settled: solved, gesture } = useSettled(nearlyEqual(inB, target));
  const goalPoint = add(scale(target[0], b1), scale(target[1], b2));
  const goalInC = weightsOf(goalPoint, c1, c2);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Move <Tex>{"\\mathbf x"}</Tex> to the point with <Tex>{`[\\mathbf x]_{\\mathcal B} = ${pairTex(target, B_TEX)}`}</Tex>, then read its address in <Tex>{"\\mathcal C"}</Tex>.</>}
        success={<>That point is <Tex>{`${texNumber(target[0])}\\,\\mathbf b_1 + ${texNumber(target[1])}\\,\\mathbf b_2`}</Tex>, and the very same point is <Tex>{`${texNumber(goalInC[0])}\\,\\mathbf c_1 + ${texNumber(goalInC[1])}\\,\\mathbf c_2`}</Tex> on the pink grid.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([b1, b2, c1, c2, goalPoint, start])} label="Plane with two overlaid grids: purple-gray for the basis b1, b2 and pink for the basis c1, c2, with a draggable point x.">
            <AddressGrid u={b1} v={b2} stroke={B_GRID} opacity={0.6} />
            <AddressGrid u={c1} v={c2} stroke={C_GRID} opacity={0.35} />
            <Arrow to={c1} color="pink" />
            <Arrow to={c2} color="blue" />
            <Arrow to={b1} color="green" />
            <Arrow to={b2} color="red" />
            <Arrow to={x} color="yellow" width={solved ? 5 : 3.5} />
            {solved ? <Marker at={x} color="glow" ring /> : null}
            <Label at={b1} color="green" dx={6} dy={18}>b₁</Label>
            <Label at={b2} color="red" dx={-26}>b₂</Label>
            <Label at={c1} color="pink" dx={-4} dy={20}>c₁</Label>
            <Label at={c2} color="blue" dx={-26}>c₂</Label>
            <Label at={x} color="yellow">x</Label>
            <Handle at={x} onMove={setX} color="yellow" label={`Point x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`[\\mathbf x]_{\\mathcal B} = ${pairTex(inB, B_TEX)}`} />
            <Readout tex={`[\\mathbf x]_{\\mathcal C} = ${pairTex(inC, C_TEX)}`} />
          </>
        }
      />
    </Panel>
  );
}

function ColumnStatus({ done, index }: { done: boolean; index: number }) {
  return (
    <div className={`flex items-center gap-3 rounded-lg px-4 py-2 transition-colors duration-300 ${done ? "bg-[color-mix(in_oklab,var(--palette-teal)_16%,transparent)]" : "bg-surface-sunken"}`}>
      <span className="grid shrink-0">
        <CheckCircle weight="fill" aria-hidden className={`size-5 text-[var(--palette-teal)] [grid-area:1/1] ${done ? "swap-shown" : "swap-hidden"}`} />
        <Circle aria-hidden className={`size-5 text-text-muted [grid-area:1/1] ${done ? "swap-hidden" : "swap-shown"}`} />
      </span>
      <span className={done ? "text-text" : "text-text-muted"}>
        Column {index} lands on <Tex>{`\\mathbf b_${index}`}</Tex>
      </span>
      <span className="sr-only">{done ? "matches" : "does not match yet"}</span>
    </div>
  );
}

function ColumnWalk({ weights, c1, c2, end }: { weights: Vec; c1: Vec; c2: Vec; end: "green" | "red" }) {
  const corner = scale(weights[0], c1);
  const tip = add(corner, scale(weights[1], c2));
  return (
    <>
      <Arrow to={corner} color="pink" width={2.5} dashed />
      <Arrow from={corner} to={tip} color="blue" width={2.5} dashed />
      <Marker at={tip} color={end} />
    </>
  );
}

/** Four sliders set the two columns of P; each column walks along c1 and c2 and should land on its b vector. */
export function ChangeMatrixBuilder({ b1 = [2, 1], b2 = [-1, 2], c1 = [1, 0], c2 = [-1, 1] }: TwoBases) {
  const [columns, setColumns] = useState<[Vec, Vec]>([[1, 0], [0, 1]]);
  const lands = (index: 0 | 1, target: Vec) => nearlyEqual(add(scale(columns[index][0], c1), scale(columns[index][1], c2)), target);
  const { settled, gesture } = useSettled(`${lands(0, b1)}-${lands(1, b2)}`);
  const [firstDone, secondDone] = settled.split("-").map((flag) => flag === "true");
  const solved = firstDone && secondDone;
  const setEntry = (column: 0 | 1, row: 0 | 1) => (value: number) =>
    setColumns((current) => current.map((col, j) => (j === column ? (col.map((entry, i) => (i === row ? value : entry)) as Vec) : col)) as [Vec, Vec]);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Set each column of <Tex>{"P_{\\mathcal C \\leftarrow \\mathcal B}"}</Tex> so its walk along <Tex>{"\\mathbf c_1"}</Tex> and <Tex>{"\\mathbf c_2"}</Tex> ends on the tip of <Tex>{"\\mathbf b_1"}</Tex> or <Tex>{"\\mathbf b_2"}</Tex>.</>}
        success={<>Both columns land. Column <Tex>{"j"}</Tex> is <Tex>{"[\\mathbf b_j]_{\\mathcal C}"}</Tex>, so <Tex>{`P_{\\mathcal C \\leftarrow \\mathcal B} = ${matrixTex(columns)}`}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([b1, b2, c1, c2], { xMin: -4, xMax: 5, yMin: -2, yMax: 4 })} label="Plane with the pink grid of c1 and c2. Dashed walks follow each column of P, ending at a green dot for column 1 and a red dot for column 2.">
            <AddressGrid u={c1} v={c2} stroke={C_GRID} opacity={0.4} />
            <Arrow to={c1} color="pink" />
            <Arrow to={c2} color="blue" />
            <Arrow to={b1} color="green" width={firstDone ? 5 : 3.5} />
            <Arrow to={b2} color="red" width={secondDone ? 5 : 3.5} />
            <ColumnWalk weights={columns[0]} c1={c1} c2={c2} end="green" />
            <ColumnWalk weights={columns[1]} c1={c1} c2={c2} end="red" />
            {firstDone ? <Marker at={b1} color="glow" ring /> : null}
            {secondDone ? <Marker at={b2} color="glow" ring /> : null}
            <Label at={b1} color="green" dx={8} dy={18}>b₁</Label>
            <Label at={b2} color="red" dx={-26}>b₂</Label>
          </Plane>
        }
        readout={
          <>
            <Slider label="p_{11}" value={columns[0][0]} onChange={setEntry(0, 0)} min={-4} max={4} step={1} color={palette.i_hat} />
            <Slider label="p_{21}" value={columns[0][1]} onChange={setEntry(0, 1)} min={-4} max={4} step={1} color={palette.i_hat} />
            <Slider label="p_{12}" value={columns[1][0]} onChange={setEntry(1, 0)} min={-4} max={4} step={1} color={palette.j_hat} />
            <Slider label="p_{22}" value={columns[1][1]} onChange={setEntry(1, 1)} min={-4} max={4} step={1} color={palette.j_hat} />
            <Readout tex={`P_{\\mathcal C \\leftarrow \\mathcal B} = ${matrixTex(columns)}`} />
            <ColumnStatus done={firstDone} index={1} />
            <ColumnStatus done={secondDone} index={2} />
          </>
        }
      />
    </Panel>
  );
}

/** Drag x and watch T(x) = Ax, read in B coordinates; the goal is an output with given B-coordinates. */
export function SimilarityHunt({ matrix = [[1, 2], [1, 0]], b1 = [2, 1], b2 = [-1, 2], target = [1, 1], start = [1, 1] }: { matrix?: Matrix2; b1?: Vec; b2?: Vec; target?: Vec; start?: Vec }) {
  const [x, setX] = useState<Vec>(start);
  const image = apply(matrix, x);
  const inB = weightsOf(x, b1, b2);
  const imageInB = weightsOf(image, b1, b2);
  const { settled: solved, gesture } = useSettled(nearlyEqual(imageInB, target));
  const matrixInB: [Vec, Vec] = [weightsOf(apply(matrix, b1), b1, b2), weightsOf(apply(matrix, b2), b1, b2)];
  const teal: string[] = [palette.teal, palette.teal];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Find the input <Tex>{"\\mathbf x"}</Tex> whose output has <Tex>{`[T(\\mathbf x)]_{\\mathcal B} = ${pairTex(target, teal)}`}</Tex>, so that <Tex>{"T(\\mathbf x) = \\mathbf b_1 + \\mathbf b_2"}</Tex>.</>}
        success={<>Here <Tex>{`[\\mathbf x]_{\\mathcal B} = ${pairTex(inB, B_TEX)}`}</Tex>, and <Tex>{`[T]_{\\mathcal B}${pairTex(inB, B_TEX)} = ${pairTex(imageInB, teal)}`}</Tex>. The <Tex>{"\\mathcal B"}</Tex>-matrix does the whole job in <Tex>{"\\mathcal B"}</Tex> coordinates.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([b1, b2, add(b1, b2), start])} label="Plane with the purple-gray grid of b1 and b2, a draggable input x in yellow and its image T(x) in teal.">
            <AddressGrid u={b1} v={b2} stroke={B_GRID} opacity={0.6} />
            <Arrow to={b1} color="green" />
            <Arrow to={b2} color="red" />
            <Arrow to={image} color="teal" width={solved ? 5 : 3.5} />
            <Arrow to={x} color="yellow" />
            {solved ? <Marker at={image} color="glow" ring /> : null}
            <Label at={b1} color="green" dx={6} dy={18}>b₁</Label>
            <Label at={b2} color="red" dx={-26}>b₂</Label>
            <Label at={image} color="teal">T(x)</Label>
            <Label at={x} color="yellow" dx={10} dy={20}>x</Label>
            <Handle at={x} onMove={setX} color="yellow" label={`Input x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`[T]_{\\mathcal B} = P^{-1}AP = ${matrixTex(matrixInB, teal)}`} />
            <Readout tex={`[\\mathbf x]_{\\mathcal B} = ${pairTex(inB, B_TEX)}`} />
            <Readout tex={`[T(\\mathbf x)]_{\\mathcal B} = ${pairTex(imageInB, teal)}`} />
            <Readout tex={`T(\\mathbf x) = ${columnTex(image, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}
