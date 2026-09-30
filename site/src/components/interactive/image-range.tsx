"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, RichText, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, apply, det, nearlyEqual, scale, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, DEFAULT_BOUNDS, Handle, Label, Marker, Plane, Segment, usePlane } from "./plane";

const isZero = (v: Vec) => v[0] === 0 && v[1] === 0;
const pointKey = (v: Vec) => `${v[0]},${v[1]}`;
const keyPoint = (key: string): Vec => key.split(",").map(Number) as Vec;

function FullLine({ through = [0, 0], direction, color, dashed = false, width = 4 }: { through?: Vec; direction: Vec; color: Hue; dashed?: boolean; width?: number }) {
  const { toSvg } = usePlane();
  const reach = 40;
  const [x1, y1] = toSvg(add(through, scale(-reach, direction)));
  const [x2, y2] = toSvg(add(through, scale(reach, direction)));
  return (
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke={hue(color)}
      strokeWidth={width}
      strokeOpacity={dashed ? 0.75 : 0.9}
      strokeDasharray={dashed ? "7 6" : undefined}
      strokeLinecap="round"
    />
  );
}

function WholePlaneTint({ shown }: { shown: boolean }) {
  const { toSvg, bounds } = usePlane();
  const [x, y] = toSvg([bounds.xMin, bounds.yMax]);
  const [x2, y2] = toSvg([bounds.xMax, bounds.yMin]);
  return (
    <rect
      aria-hidden
      x={x}
      y={y}
      width={x2 - x}
      height={y2 - y}
      fill="var(--palette-teal)"
      fillOpacity={shown ? 0.14 : 0}
      className="transition-[fill-opacity] duration-300"
    />
  );
}

/** A nonzero vector sent to zero by a rank-one matrix with columns first and second: second = k first gives (k, -1). */
function kernelDirection(first: Vec, second: Vec): Vec {
  if (isZero(first)) return [1, 0];
  const k = (second[0] * first[0] + second[1] * first[1]) / (first[0] ** 2 + first[1] ** 2);
  return [k, -1];
}

/** One cell per input dimension, pink for crushed and teal for surviving. */
function DimensionBar({ kernelDim, total, lit }: { kernelDim: number; total: number; lit: boolean }) {
  return (
    <div aria-hidden className={`flex gap-1 rounded-lg p-1.5 transition-shadow duration-300 ${lit ? "ring-2 ring-[var(--palette-teal)]" : ""}`}>
      {Array.from({ length: total }, (_, index) => (
        <span
          key={index}
          className="h-6 flex-1 rounded-sm transition-colors duration-300"
          style={{ background: index < kernelDim ? "var(--palette-pink)" : "var(--palette-teal)" }}
        />
      ))}
    </div>
  );
}

function rangeDimension(first: Vec, second: Vec): number {
  if (det([[first[0], second[0]], [first[1], second[1]]]) !== 0) return 2;
  return isZero(first) && isZero(second) ? 0 : 1;
}

function RangePicture({ first, second, rank }: { first: Vec; second: Vec; rank: number }) {
  const lineDirection = isZero(first) ? second : first;
  return (
    <>
      <WholePlaneTint shown={rank === 2} />
      {rank === 1 ? <FullLine direction={lineDirection} color="teal" /> : null}
      {rank === 1 ? <FullLine direction={kernelDirection(first, second)} color="pink" dashed width={2.5} /> : null}
    </>
  );
}

/** Drag the second column of a 2x2 matrix until the range collapses from the whole plane to a line. */
export function RangeCollapse({ first, start }: { first: Vec; start: Vec }) {
  const [second, setSecond] = useState<Vec>(start);
  const rank = rangeDimension(first, second);
  const { settled, gesture } = useSettled(pointKey(second));
  const settledSecond = keyPoint(settled);
  const solved = !isZero(settledSecond) && rangeDimension(first, settledSecond) === 1;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the red column <Tex>{"\\mathbf a_2"}</Tex> so the range of <Tex>{"T(\\mathbf x) = A\\mathbf x"}</Tex> shrinks from the whole plane to a line. Keep <Tex>{"\\mathbf a_2 \\neq \\mathbf 0"}</Tex>.</>}
        success={<>Now <Tex>{"\\mathbf a_2"}</Tex> is a multiple of <Tex>{"\\mathbf a_1"}</Tex>, so every output lies on the teal line and <Tex>{"T"}</Tex> is not onto. The range lost a dimension and the kernel, dashed pink, gained one.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DEFAULT_BOUNDS} label={`Columns a1 at ${describeVector(first)} and a2 at ${describeVector(second)}. The range is ${rank === 2 ? "the whole plane" : "a line"}. Drag the tip of a2 or use the arrow keys.`}>
            <RangePicture first={first} second={second} rank={rank} />
            <Arrow to={first} color="green" />
            <Arrow to={second} color="red" />
            <Label at={first} color="green">a₁</Label>
            <Label at={second} color="red">a₂</Label>
            <Handle at={second} onMove={setSecond} color="red" label={`Tip of the second column a2, at ${describeVector(second)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`A = \\begin{bmatrix} \\textcolor{${palette.i_hat}}{${texNumber(first[0])}} & \\textcolor{${palette.j_hat}}{${texNumber(second[0])}} \\\\ \\textcolor{${palette.i_hat}}{${texNumber(first[1])}} & \\textcolor{${palette.j_hat}}{${texNumber(second[1])}} \\end{bmatrix}`} />
            <DimensionBar kernelDim={2 - rank} total={2} lit={solved} />
            <Readout tex={`\\begin{aligned} \\textcolor{${palette.pink}}{\\dim\\ker T} &= \\textcolor{${palette.pink}}{${2 - rank}} \\\\ \\textcolor{${palette.teal}}{\\dim\\operatorname{range}T} &= \\textcolor{${palette.teal}}{${rank}} \\end{aligned}`} />
          </>
        }
      />
    </Panel>
  );
}

function SplitArrows({ x, floorPart }: { x: Vec; floorPart: Vec }) {
  return (
    <>
      <Arrow to={floorPart} color="blue" width={5} />
      {nearlyEqual(x, floorPart) ? null : <Segment from={floorPart} to={x} color="pink" dashed={false} />}
      <Arrow to={x} color="yellow" />
    </>
  );
}

/** Drag x to find the one input on the blue complement line that T sends to b; the rest of the preimage appears once found. */
export function ComplementLanding({
  matrix,
  kernel,
  complement,
  target,
  start,
  prompt,
  success,
}: {
  matrix: Matrix2;
  kernel: Vec;
  complement: Vec;
  target: Vec;
  start: Vec;
  prompt: string;
  success: string;
}) {
  const [x, setX] = useState<Vec>(start);
  const { settled, gesture } = useSettled(pointKey(x));
  const settledX = keyPoint(settled);
  const onComplement = settledX[0] * complement[1] - settledX[1] * complement[0] === 0;
  const solved = onComplement && nearlyEqual(apply(matrix, settledX), target);
  const kernelWeight = (x[0] * complement[1] - x[1] * complement[0]) / (kernel[0] * complement[1] - kernel[1] * complement[0]);
  const floorPart: Vec = [x[0] - kernelWeight * kernel[0], x[1] - kernelWeight * kernel[1]];
  const output = apply(matrix, x);

  return (
    <Panel gesture={gesture}>
      <Goal solved={solved} prompt={<RichText>{prompt}</RichText>} success={<RichText>{success}</RichText>} />
      <Workbench
        plane={
          <Plane bounds={DEFAULT_BOUNDS} label={`Input x at ${describeVector(x)}, its output T(x) at ${describeVector(output)}, and the target b at ${describeVector(target)}. Drag the tip of x or use the arrow keys.`}>
            <FullLine direction={complement} color="blue" width={2.5} />
            <FullLine direction={kernel} color="pink" dashed width={2.5} />
            <FullLine direction={apply(matrix, complement)} color="teal" width={2} />
            {solved ? <FullLine through={settledX} direction={kernel} color="yellow" dashed width={2.5} /> : null}
            <Marker at={target} ring />
            <SplitArrows x={x} floorPart={floorPart} />
            <Arrow to={output} color="teal" />
            <Label at={x} color="yellow">x</Label>
            <Label at={output} color="teal" dy={22}>T(x)</Label>
            <Handle at={x} onMove={setX} color="yellow" label={`Tip of the input x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\textcolor{${palette.yellow}}{\\mathbf x} = ${columnTex(floorPart, palette.blue)} + ${columnTex(scale(kernelWeight, kernel), palette.pink)}`} />
            <Readout tex={`T(\\textcolor{${palette.yellow}}{\\mathbf x}) = T${columnTex(floorPart, palette.blue)} = ${columnTex(output, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}

const matrixTex2 = (m: Matrix2) => `\\begin{bmatrix} ${texNumber(m[0][0])} & ${texNumber(m[0][1])} \\\\ ${texNumber(m[1][0])} & ${texNumber(m[1][1])} \\end{bmatrix}`;

/** A rank-one map: drag the input and watch the output slide along the range line until it lands on the ringed b. */
export function RangeProbe({ matrix = [[1, 2], [2, 4]], target = [-2, -4], start = [1, 0] }: { matrix?: Matrix2; target?: Vec; start?: Vec }) {
  const [x, setX] = useState<Vec>(start);
  const { settled, gesture } = useSettled(pointKey(x));
  const solved = nearlyEqual(apply(matrix, keyPoint(settled)), target);
  const output = apply(matrix, x);
  const rangeDirection: Vec = isZero([matrix[0][0], matrix[1][0]]) ? [matrix[0][1], matrix[1][1]] : [matrix[0][0], matrix[1][0]];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the input <Tex>{"\\mathbf x"}</Tex> so that its output <Tex>{"T(\\mathbf x)"}</Tex> lands on the ringed point <Tex>{`\\mathbf b = ${columnTex(target)}`}</Tex>. Watch where the output is allowed to go.</>}
        success={<>You reached <Tex>{"\\mathbf b"}</Tex>, so it is in the range. Every output stays on the teal line, so a point off that line could never be reached.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DEFAULT_BOUNDS} label={`Input x at ${describeVector(x)} and its output T(x) at ${describeVector(output)}, which always lies on the teal range line. Drag x or use the arrow keys.`}>
            <FullLine direction={rangeDirection} color="teal" width={2.5} />
            <Marker at={target} color={solved ? "teal" : "glow"} ring />
            <Arrow to={output} color="teal" />
            <Arrow to={x} color="yellow" />
            <Label at={x} color="yellow">x</Label>
            <Label at={output} color="teal" dy={22}>T(x)</Label>
            <Handle at={x} onMove={setX} color="yellow" label={`Tip of the input x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`T(\\mathbf x) = ${matrixTex2(matrix)}\\mathbf x`} />
            <Readout tex={`${columnTex(x, palette.yellow)} \\mapsto ${columnTex(output, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}

function spanDimension(columns: Vec[]): number {
  const nonzero = columns.filter((column) => !isZero(column));
  if (nonzero.length === 0) return 0;
  const [first] = nonzero;
  return nonzero.some((column) => det([[first[0], column[0]], [first[1], column[1]]]) !== 0) ? 2 : 1;
}

function ColumnsRange({ columns, rank }: { columns: Vec[]; rank: number }) {
  const direction = columns.find((column) => !isZero(column)) ?? [1, 0];
  return (
    <>
      <WholePlaneTint shown={rank === 2} />
      {rank === 1 ? <FullLine direction={direction} color="teal" /> : null}
    </>
  );
}

/** A map from R^3 to R^2 with two fixed parallel columns. Drag the third column and watch the three input dimensions split between kernel and range. */
export function ThirdColumnBudget({ first = [1, 2], second = [-2, -4], start = [2, 0] }: { first?: Vec; second?: Vec; start?: Vec }) {
  const [third, setThird] = useState<Vec>(start);
  const rank = spanDimension([first, second, third]);
  const { settled, gesture } = useSettled(pointKey(third));
  const solved = spanDimension([first, second, keyPoint(settled)]) === 1;
  const entry = (color: string, value: number) => `\\textcolor{${color}}{${texNumber(value)}}`;
  const matrix = `\\begin{bmatrix} ${entry(palette.i_hat, first[0])} & ${entry(palette.j_hat, second[0])} & ${entry(palette.blue, third[0])} \\\\ ${entry(palette.i_hat, first[1])} & ${entry(palette.j_hat, second[1])} & ${entry(palette.blue, third[1])} \\end{bmatrix}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>This <Tex>{"T:\\mathbb R^3 \\to \\mathbb R^2"}</Tex> has three columns. Drag the blue third column until the range shrinks to a line, and watch the kernel grow to make up the difference.</>}
        success={<>All three columns lie on one line, so <Tex>{"\\dim\\operatorname{range}T = 1"}</Tex> and <Tex>{"\\dim\\ker T = 2"}</Tex>. The three input dimensions are still all accounted for.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DEFAULT_BOUNDS} label={`Three columns in the plane: ${describeVector(first)}, ${describeVector(second)} and a draggable third column at ${describeVector(third)}. The range is ${rank === 2 ? "the whole plane" : "a line"}.`}>
            <ColumnsRange columns={[first, second, third]} rank={rank} />
            <Arrow to={first} color="green" />
            <Arrow to={second} color="red" />
            <Arrow to={third} color="blue" />
            <Label at={first} color="green">a₁</Label>
            <Label at={second} color="red">a₂</Label>
            <Label at={third} color="blue">a₃</Label>
            <Handle at={third} onMove={setThird} color="blue" label={`Tip of the third column a3, at ${describeVector(third)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`A = ${matrix}`} />
            <DimensionBar kernelDim={3 - rank} total={3} lit={solved} />
            <Readout tex={`\\begin{aligned} \\textcolor{${palette.pink}}{\\dim\\ker T} &= \\textcolor{${palette.pink}}{${3 - rank}} \\\\ \\textcolor{${palette.teal}}{\\dim\\operatorname{range}T} &= \\textcolor{${palette.teal}}{${rank}} \\end{aligned}`} />
          </>
        }
      />
    </Panel>
  );
}
