"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { apply, nearlyEqual, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, boundsAround, DEFAULT_BOUNDS, Handle, Label, Marker, Plane, usePlane, type Bounds } from "./plane";

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

type CompositionProps = { first: Matrix2; second: Matrix2; firstName?: string; secondName?: string; start: Vec; target: Vec };

/** x is carried by the first matrix and then the second; the learner drags x so the two-step trip lands on a target. */
export function CompositionExplorer({ first, second, firstName = "S", secondName = "R", start, target }: CompositionProps) {
  const [x, setX] = useState<Vec>(start);
  const halfway = apply(first, x);
  const landing = apply(second, halfway);
  const product = multiply(second, first);
  const { settled: solved, gesture } = useSettled(nearlyEqual(landing, target));
  const names = `${secondName}${firstName}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf x"}</Tex> so that applying <Tex>{firstName}</Tex> and then <Tex>{secondName}</Tex> carries it onto the ringed point <Tex>{columnTex(target)}</Tex>.</>}
        success={<>Right. <Tex>{`${names}\\,${columnTex(x)} = ${columnTex(target)}`}</Tex>, so the single matrix <Tex>{names}</Tex> does both steps at once.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([target, x, halfway, landing])} label={`The vector x, its image after ${firstName}, and its image after ${secondName}. Drag the tip of x or use the arrow keys.`}>
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
