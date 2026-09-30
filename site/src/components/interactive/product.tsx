"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, apply, nearlyEqual, scale, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, boundsAround, DEFAULT_BOUNDS, Handle, Label, Marker, Plane, Segment, usePlane, type Bounds } from "./plane";

const GRID_REACH = 14;

const multiply = (left: Matrix2, right: Matrix2): Matrix2 => [
  [left[0][0] * right[0][0] + left[0][1] * right[1][0], left[0][0] * right[0][1] + left[0][1] * right[1][1]],
  [left[1][0] * right[0][0] + left[1][1] * right[1][0], left[1][0] * right[0][1] + left[1][1] * right[1][1]],
];

const columnOf = (matrix: Matrix2, index: 0 | 1): Vec => [matrix[0][index], matrix[1][index]];

const sameMatrix = (left: Matrix2, right: Matrix2) =>
  nearlyEqual(columnOf(left, 0), columnOf(right, 0)) && nearlyEqual(columnOf(left, 1), columnOf(right, 1));

function matrixTex(matrix: Matrix2, colors: [string, string] = [palette.i_hat, palette.j_hat]): string {
  const entry = (value: number, color: string) => `\\textcolor{${color}}{${texNumber(value)}}`;
  const rows = [0, 1].map((row) => `${entry(matrix[row][0], colors[0])} & ${entry(matrix[row][1], colors[1])}`);
  return `\\begin{bmatrix} ${rows.join(" \\\\ ")} \\end{bmatrix}`;
}

function CarriedGrid({ matrix }: { matrix: Matrix2 }) {
  const { toSvg } = usePlane();
  const lines: [Vec, Vec][] = [];
  for (let k = -GRID_REACH; k <= GRID_REACH; k++) {
    lines.push([apply(matrix, [k, -GRID_REACH]), apply(matrix, [k, GRID_REACH])]);
    lines.push([apply(matrix, [-GRID_REACH, k]), apply(matrix, [GRID_REACH, k])]);
  }
  return (
    <g aria-hidden>
      {lines.map(([from, to], index) => {
        const [x1, y1] = toSvg(from);
        const [x2, y2] = toSvg(to);
        return <line key={index} x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--palette-blue)" strokeOpacity={0.45} strokeWidth={1.2} />;
      })}
    </g>
  );
}

/** A fixed window that holds the start, the target, and both trips through the first matrix, so the plane never resizes mid-drag. */
function tripBounds(first: Matrix2, second: Matrix2, start: Vec, target: Vec): Bounds {
  const product = multiply(second, first);
  const det = product[0][0] * product[1][1] - product[0][1] * product[1][0];
  const solution: Vec = [(product[1][1] * target[0] - product[0][1] * target[1]) / det, (product[0][0] * target[1] - product[1][0] * target[0]) / det];
  return boundsAround([start, apply(first, start), apply(product, start), target, solution, apply(first, solution)]);
}

type CompositionProps = { first: Matrix2; second: Matrix2; firstName?: string; secondName?: string; start: Vec; target: Vec };

/** x is carried by the first matrix and then the second; the learner drags x so the two-step trip lands on a target. */
export function CompositionExplorer({ first, second, firstName = "S", secondName = "R", start, target }: CompositionProps) {
  const [x, setX] = useState<Vec>(start);
  const halfway = apply(first, x);
  const landing = apply(second, halfway);
  const product = multiply(second, first);
  const { settled: solved, gesture } = useSettled(nearlyEqual(landing, target));
  const names = `${secondName}${firstName}`;
  const [bounds] = useState(() => tripBounds(first, second, start, target));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf x"}</Tex> so that applying <Tex>{firstName}</Tex> and then <Tex>{secondName}</Tex> carries it onto the ringed point <Tex>{columnTex(target)}</Tex>.</>}
        success={<>Right. <Tex>{`${names}\\,${columnTex(x)} = ${columnTex(target)}`}</Tex>, so the single matrix <Tex>{names}</Tex> does both steps at once.</>}
      />
      <Workbench
        plane={
          <Plane bounds={bounds} label={`The vector x, its image after ${firstName}, and its image after ${secondName}. Drag the tip of x or use the arrow keys.`}>
            {!solved ? <Marker at={target} ring /> : null}
            <Arrow to={halfway} color="yellow" width={1.5} dashed />
            <Arrow from={x} to={halfway} color="text" width={1.5} dashed />
            <Arrow from={halfway} to={landing} color="text" width={1.5} dashed />
            <Arrow to={landing} color="teal" />
            <Label at={halfway} color="yellow">{`${firstName}x`}</Label>
            <Label at={landing} color="teal">{`${names}x`}</Label>
            <Arrow to={x} color="yellow" />
            {solved ? <Marker at={target} color="teal" /> : null}
            <Handle at={x} onMove={setX} color="yellow" label={`Tip of x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`${firstName}\\mathbf x = ${columnTex(halfway)}`} />
            <Readout tex={`${secondName}(${firstName}\\mathbf x) = ${columnTex(landing, palette.teal)}`} />
            <Readout tex={`${names} = ${matrixTex(product)}`} />
          </>
        }
      />
    </Panel>
  );
}

function guessColor(correct: boolean, fallback: "yellow" | "blue") {
  return correct ? "teal" : fallback;
}

/** The learner places the two columns of AB on the grid that A carries, by reading each column of B as steps along A's columns. */
export function ProductColumns({ a, b }: { a: Matrix2; b: Matrix2 }) {
  const b1 = columnOf(b, 0);
  const b2 = columnOf(b, 1);
  const answer = multiply(a, b);
  const [first, setFirst] = useState<Vec>(b1);
  const [second, setSecond] = useState<Vec>(b2);
  const firstRight = nearlyEqual(first, columnOf(answer, 0));
  const secondRight = nearlyEqual(second, columnOf(answer, 1));
  const { settled: solved, gesture } = useSettled(firstRight && secondRight);
  const guess: Matrix2 = [[first[0], second[0]], [first[1], second[1]]];
  const guessColors: [string, string] = solved ? [palette.teal, palette.teal] : [palette.yellow, palette.blue];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the yellow and blue dots to <Tex>{"A\\mathbf b_1"}</Tex> and <Tex>{"A\\mathbf b_2"}</Tex>. Count steps along the blue grid that <Tex>{"A"}</Tex> carries.</>}
        success={<>Both columns are in place, so <Tex>{`AB = ${matrixTex(answer, [palette.teal, palette.teal])}`}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([b1, b2, columnOf(answer, 0), columnOf(answer, 1)])} label="The grid carried by A, with A's columns in green and red and two draggable guesses for the columns of AB.">
            <CarriedGrid matrix={a} />
            <Arrow to={columnOf(a, 0)} color="green" width={2.5} />
            <Arrow to={columnOf(a, 1)} color="red" width={2.5} />
            <Arrow to={first} color={guessColor(solved, "yellow")} />
            <Arrow to={second} color={guessColor(solved, "blue")} />
            <Label at={first} color={guessColor(solved, "yellow")}>Ab₁</Label>
            <Label at={second} color={guessColor(solved, "blue")}>Ab₂</Label>
            <Handle at={first} onMove={setFirst} color={guessColor(solved, "yellow")} label={`Your guess for A b1, at ${describeVector(first)}`} />
            <Handle at={second} onMove={setSecond} color={guessColor(solved, "blue")} label={`Your guess for A b2, at ${describeVector(second)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`A = ${matrixTex(a)}`} />
            <Readout tex={`B = ${matrixTex(b, [palette.yellow, palette.blue])}`} />
            <Readout tex={`\\begin{bmatrix} A\\mathbf b_1 & A\\mathbf b_2 \\end{bmatrix} \\overset{?}{=} ${matrixTex(guess, guessColors)}`} />
          </>
        }
      />
    </Panel>
  );
}

type Entry = number | "k";

const fill = (matrix: [[Entry, Entry], [Entry, Entry]], k: number): Matrix2 =>
  matrix.map((row) => row.map((entry) => (entry === "k" ? k : entry))) as Matrix2;

const withK = (matrix: [[Entry, Entry], [Entry, Entry]]) =>
  matrix.map((row) => row.map((entry) => (entry === "k" ? "\\textcolor{" + palette.glow + "}{k}" : texNumber(entry))).join(" & ")).join(" \\\\ ");

function ImageSquare({ matrix, lit }: { matrix: Matrix2; lit: boolean }) {
  const { toSvg } = usePlane();
  const corners: Vec[] = [[0, 0], [1, 0], [1, 1], [0, 1]];
  const points = corners.map((corner) => toSvg(apply(matrix, corner)).join(",")).join(" ");
  return <polygon points={points} fill={lit ? "var(--palette-teal)" : "var(--palette-yellow)"} fillOpacity={0.25} className="transition-[fill] duration-300" />;
}

function SquarePicture({ matrix, bounds, name, lit }: { matrix: Matrix2; bounds: Bounds; name: string; lit: boolean }) {
  return (
    <div className="min-w-0 space-y-2">
      <Plane bounds={bounds} label={`The unit square after ${name}, with where i-hat and j-hat land.`}>
        <ImageSquare matrix={matrix} lit={lit} />
        <Arrow to={columnOf(matrix, 0)} color="green" />
        <Arrow to={columnOf(matrix, 1)} color="red" />
      </Plane>
      <Readout tex={`${name} = ${matrixTex(matrix)}`} />
    </div>
  );
}

/** Two products of the same pair in both orders; the learner slides k until they match. */
export function CommuteHunt({ a, b, start = 1 }: { a: Matrix2; b: [[Entry, Entry], [Entry, Entry]]; start?: number }) {
  const [k, setK] = useState(start);
  const bNow = fill(b, k);
  const ab = multiply(a, bNow);
  const ba = multiply(bNow, a);
  const { settled: solved, gesture } = useSettled(sameMatrix(ab, ba));
  const extremes = [-3, 3].flatMap((value) => {
    const bAt = fill(b, value);
    return [multiply(a, bAt), multiply(bAt, a)].flatMap((m) => [columnOf(m, 0), columnOf(m, 1), apply(m, [1, 1])]);
  });
  const bounds = boundsAround(extremes, { ...DEFAULT_BOUNDS, xMin: -2, xMax: 2, yMin: -2, yMax: 2 });

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide <Tex>{"k"}</Tex> until <Tex>{"AB"}</Tex> and <Tex>{"BA"}</Tex> move the square to the same place.</>}
        success={<>At <Tex>{`k = ${texNumber(k)}`}</Tex> the two orders agree, so these two matrices commute. Every other <Tex>{"k"}</Tex> gives <Tex>{"AB \\neq BA"}</Tex>.</>}
      />
      <div className="space-y-4">
        <Readout tex={`A = ${matrixTex(a, [palette.text, palette.text])} \\qquad B = \\begin{bmatrix} ${withK(b)} \\end{bmatrix}`} />
        <Slider label="k" value={k} onChange={setK} min={-3} max={3} step={1} color={palette.glow} />
        <div className="grid gap-4 sm:grid-cols-2">
          <SquarePicture matrix={ab} bounds={bounds} name="AB" lit={solved} />
          <SquarePicture matrix={ba} bounds={bounds} name="BA" lit={solved} />
        </div>
      </div>
    </Panel>
  );
}

const solveTwoByTwo = (matrix: Matrix2, target: Vec): Vec => {
  const determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0];
  return [(matrix[1][1] * target[0] - matrix[0][1] * target[1]) / determinant, (matrix[0][0] * target[1] - matrix[1][0] * target[0]) / determinant];
};

/** Runs the column rule backward: the learner sets the weights in a column of B so that A's columns, scaled and chained, reach a column of AB. */
export function ColumnWeights({ a, target }: { a: Matrix2; target: Vec }) {
  const [top, setTop] = useState(0);
  const [bottom, setBottom] = useState(0);
  const a1 = columnOf(a, 0);
  const a2 = columnOf(a, 1);
  const firstLeg = scale(top, a1);
  const result = add(firstLeg, scale(bottom, a2));
  const { settled: solved, gesture } = useSettled(nearlyEqual(result, target));
  const answer = solveTwoByTwo(a, target);
  const [bounds] = useState(() => boundsAround([target, a1, a2, scale(answer[0], a1)]));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The first column of <Tex>{"AB"}</Tex> is the ringed point <Tex>{columnTex(target)}</Tex>. Set the two entries of <Tex>{"\\mathbf b_1"}</Tex> so that <Tex>{"A\\mathbf b_1"}</Tex> lands on it.</>}
        success={<>Right. <Tex>{`\\mathbf b_1 = ${columnTex(answer)}`}</Tex>, because <Tex>{`${texNumber(answer[0])}\\,\\mathbf a_1 + ${texNumber(answer[1])}\\,\\mathbf a_2`}</Tex> is the first column of <Tex>{"AB"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={bounds} label="The columns of A in green and red, a chain of their multiples ending at A b1 in teal, and a ringed target point. Use the two sliders.">
            {!solved ? <Marker at={target} ring /> : null}
            <Arrow to={a1} color="green" width={1.5} dashed />
            <Arrow to={a2} color="red" width={1.5} dashed />
            <Arrow to={result} color="teal" width={2.5} />
            <Arrow to={firstLeg} color="green" />
            <Arrow from={firstLeg} to={result} color="red" />
            {solved ? <Marker at={target} color="teal" /> : null}
          </Plane>
        }
        readout={
          <>
            <Slider label="b_{11}" value={top} onChange={setTop} min={-3} max={3} step={1} color={palette.i_hat} />
            <Slider label="b_{21}" value={bottom} onChange={setBottom} min={-3} max={3} step={1} color={palette.j_hat} />
            <Readout tex={`A = ${matrixTex(a)}`} />
            <Readout tex={`\\begin{aligned} A\\mathbf b_1 &= ${texNumber(top)}${columnTex(a1, palette.i_hat)} + ${texNumber(bottom)}${columnTex(a2, palette.j_hat)} \\\\ &= ${columnTex(result, palette.teal)} \\end{aligned}`} />
          </>
        }
      />
    </Panel>
  );
}

const isZero = (v: Vec) => nearlyEqual(v, [0, 0]);

function killsBoth(matrix: Matrix2, first: Vec, second: Vec): boolean {
  if (isZero(first) || isZero(second) || nearlyEqual(first, second)) return false;
  return isZero(apply(matrix, first)) && isZero(apply(matrix, second));
}

const ZERO_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -4, yMax: 4 };

/** The learner drags two different nonzero columns of B until M sends both to the origin, so MB is the zero matrix. */
export function ZeroProductHunt({ matrix, start = [[1, 1], [2, 0]] }: { matrix: Matrix2; start?: [Vec, Vec] }) {
  const [first, setFirst] = useState<Vec>(start[0]);
  const [second, setSecond] = useState<Vec>(start[1]);
  const firstImage = apply(matrix, first);
  const secondImage = apply(matrix, second);
  const { settled: solved, gesture } = useSettled(killsBoth(matrix, first, second));
  const reach = scale(20, columnOf(matrix, 0));
  const nullDirection: Vec = [-matrix[0][1], matrix[0][0]];
  const product: Matrix2 = [[firstImage[0], secondImage[0]], [firstImage[1], secondImage[1]]];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the two columns of <Tex>{"B"}</Tex> to two different spots, neither of them the origin, so that <Tex>{"M"}</Tex> sends both of them to <Tex>{"\\mathbf 0"}</Tex>.</>}
        success={<>Now <Tex>{"MB"}</Tex> is the zero matrix, although neither <Tex>{"M"}</Tex> nor <Tex>{"B"}</Tex> is zero. Every column that works is a multiple of <Tex>{columnTex(nullDirection)}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={ZERO_BOUNDS} label="Two draggable columns of B in yellow and blue, and their images under M in teal, which always land on the dashed teal line.">
            <Segment from={scale(-1, reach)} to={reach} color="teal" />
            <Arrow to={firstImage} color="teal" width={2} />
            <Arrow to={secondImage} color="teal" width={2} />
            <Arrow to={first} color="yellow" />
            <Arrow to={second} color="blue" />
            <Label at={first} color="yellow">b₁</Label>
            <Label at={second} color="blue">b₂</Label>
            {solved ? <Marker at={[0, 0]} color="teal" ring /> : null}
            <Handle at={first} onMove={setFirst} color="yellow" label={`Column b1 of B, at ${describeVector(first)}`} />
            <Handle at={second} onMove={setSecond} color="blue" label={`Column b2 of B, at ${describeVector(second)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`M = ${matrixTex(matrix)}`} />
            <Readout tex={`B = ${matrixTex([[first[0], second[0]], [first[1], second[1]]], [palette.yellow, palette.blue])}`} />
            <Readout tex={`MB = ${matrixTex(product, [palette.teal, palette.teal])}`} />
          </>
        }
      />
    </Panel>
  );
}
