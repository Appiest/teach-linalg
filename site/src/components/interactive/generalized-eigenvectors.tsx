"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, apply, nearlyEqual, scale, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, Handle, Label, Marker, Plane, usePlane, type Bounds } from "./plane";

const CHAIN_BOUNDS: Bounds = { xMin: -6, xMax: 6, yMin: -5, yMax: 5 };
const SHEAR_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -4, yMax: 4 };

type Matrix3 = number[][];

const pointKey = (point: Vec) => `${point[0]},${point[1]}`;
const keyPoint = (key: string): Vec => key.split(",").map(Number) as Vec;
const isZero = (point: Vec) => nearlyEqual(point, [0, 0]);
const matrixTex = (rows: number[][]) => `\\begin{bmatrix} ${rows.map((row) => row.map((value) => texNumber(value)).join(" & ")).join(" \\\\ ")} \\end{bmatrix}`;
const shiftTex = (lambda: number) => `A - ${lambda === 1 ? "" : texNumber(lambda)}I`;

function minusLambda(matrix: Matrix2, lambda: number): Matrix2 {
  return [
    [matrix[0][0] - lambda, matrix[0][1]],
    [matrix[1][0], matrix[1][1] - lambda],
  ];
}

/** A nonzero column of the rank-one matrix A − λI, which spans the single eigenline of a defective 2×2 matrix. */
function eigenDirection(shifted: Matrix2): Vec {
  const first: Vec = [shifted[0][0], shifted[1][0]];
  return isZero(first) ? [shifted[0][1], shifted[1][1]] : first;
}

function LineThrough({ direction, color, dashed = false }: { direction: Vec; color: Hue; dashed?: boolean }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg(scale(-40, direction));
  const [x2, y2] = toSvg(scale(40, direction));
  return (
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke={hue(color)}
      strokeWidth={dashed ? 2 : 3.5}
      strokeOpacity={dashed ? 0.6 : 0.9}
      strokeDasharray={dashed ? "6 6" : undefined}
      strokeLinecap="round"
    />
  );
}

/** A line of text whose two versions share one grid cell, so swapping them never changes the height. */
function SwapLine({ first, second, showSecond }: { first: React.ReactNode; second: React.ReactNode; showSecond: boolean }) {
  return (
    <div className="grid">
      <div aria-hidden={showSecond} className={`[grid-area:1/1] ${showSecond ? "swap-hidden" : "swap-shown"}`}>{first}</div>
      <div aria-hidden={!showSecond} className={`[grid-area:1/1] ${showSecond ? "swap-shown" : "swap-hidden"}`}>{second}</div>
    </div>
  );
}

/** Filled boxes for a dimension count, out of a fixed number of places. */
function DimensionSlots({ filled, places, color, label }: { filled: number; places: number; color: Hue; label: string }) {
  return (
    <div className="flex items-center gap-2" role="img" aria-label={label}>
      {Array.from({ length: places }, (_, index) => (
        <span
          key={index}
          className="h-7 w-10 rounded-md transition-colors duration-300"
          style={
            index < filled
              ? { background: `color-mix(in oklab, ${hue(color)} 55%, transparent)` }
              : { background: "var(--color-surface-raised)" }
          }
        />
      ))}
    </div>
  );
}

function CountRow({ label, children }: { label: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3 rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
      <span>{label}</span>
      {children}
    </div>
  );
}

function WholePlaneTint({ shown }: { shown: boolean }) {
  const { bounds, toSvg } = usePlane();
  const [x, y] = toSvg([bounds.xMin, bounds.yMax]);
  const [x2, y2] = toSvg([bounds.xMax, bounds.yMin]);
  return (
    <rect
      x={x}
      y={y}
      width={x2 - x}
      height={y2 - y}
      fill={hue("yellow")}
      fillOpacity={shown ? 0.12 : 0}
      className="transition-[fill-opacity] duration-300"
    />
  );
}

/** Slide the corner entry b of [[λ, b], [0, λ]]; only b = 0 gives a second independent eigenvector. */
export function MultiplicityGapSlider({ lambda = 2, start = 1 }: { lambda?: number; start?: number }) {
  const [corner, setCorner] = useState(start);
  const { settled, gesture } = useSettled(corner);
  const solved = settled === 0;
  const wholePlane = corner === 0;
  const matrix: Matrix2 = [
    [lambda, corner],
    [0, lambda],
  ];
  const e2: Vec = [0, 1];
  const image = apply(matrix, e2);
  const geometric = wholePlane ? 2 : 1;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide <Tex>{"b"}</Tex> until <Tex>{"A"}</Tex> has two independent eigenvectors, so that its eigenvectors fill the whole plane.</>}
        success={<>Only <Tex>{"b = 0"}</Tex> works. Then <Tex>{`A = ${texNumber(lambda)}I`}</Tex>, every nonzero vector is an eigenvector, and both multiplicities are 2. Every other <Tex>{"b"}</Tex> leaves a single eigenline, so <Tex>{"A"}</Tex> is defective.</>}
      />
      <Workbench
        plane={
          <Plane bounds={SHEAR_BOUNDS} label={`The eigenvectors of A shaded in yellow. The test vector e2 goes to ${describeVector(image)}.`}>
            <WholePlaneTint shown={wholePlane} />
            <LineThrough direction={[1, 0]} color="yellow" />
            <LineThrough direction={e2} color="red" dashed />
            <Arrow to={image} color="teal" />
            <Arrow to={e2} color="red" />
            <Label at={e2} color="red" dx={-30}>e₂</Label>
            <Label at={image} color="teal">Ae₂</Label>
            {wholePlane ? <Marker at={image} color="glow" ring /> : null}
          </Plane>
        }
        readout={
          <>
            <Slider label="b" value={corner} onChange={setCorner} min={-3} max={3} step={1} color={palette.glow} />
            <Readout tex={`A = ${matrixTex(matrix)}`} />
            <CountRow label="Algebraic multiplicity of λ">
              <DimensionSlots filled={2} places={2} color="text" label="2 of 2" />
            </CountRow>
            <CountRow label="Geometric multiplicity of λ">
              <DimensionSlots filled={geometric} places={2} color="yellow" label={`${geometric} of 2`} />
            </CountRow>
          </>
        }
      />
    </Panel>
  );
}

/** Drag v₂; the pink push (A − λI)v₂ slides to the origin as v₁, which always lands on the eigenline. */
export function JordanChainBuilder({ matrix, lambda, target, start = [1, 0] }: { matrix: Matrix2; lambda: number; target: Vec; start?: Vec }) {
  const [top, setTop] = useState<Vec>(start);
  const { settled, gesture } = useSettled(pointKey(top));
  const shifted = minusLambda(matrix, lambda);
  const solved = nearlyEqual(apply(shifted, keyPoint(settled)), target);
  const bottom = apply(shifted, top);
  const image = apply(matrix, top);
  const stretched = scale(lambda, top);
  const noChain = isZero(bottom);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf v_2"}</Tex> so that one push lands <Tex>{"\\mathbf v_1 = (A - \\lambda I)\\mathbf v_2"}</Tex> on the orange mark at <Tex>{`(${texNumber(target[0])}, ${texNumber(target[1])})`}</Tex>.</>}
        success={<>You built the chain <Tex>{"\\mathbf v_2 \\to \\mathbf v_1 \\to \\mathbf 0"}</Tex>. Other choices of <Tex>{"\\mathbf v_2"}</Tex> work too: adding any eigenvector to <Tex>{"\\mathbf v_2"}</Tex> leaves the push unchanged.</>}
      />
      <Workbench
        plane={
          <Plane bounds={CHAIN_BOUNDS} label={`v2 at ${describeVector(top)}, A v2 at ${describeVector(image)}, and v1 at ${describeVector(bottom)}. Drag the tip of v2 or use the arrow keys.`}>
            <LineThrough direction={eigenDirection(shifted)} color="yellow" dashed />
            <Marker at={target} color="glow" ring />
            {lambda === 1 ? null : <Arrow to={stretched} color="blue" dashed />}
            <Arrow to={image} color="teal" />
            <Arrow from={stretched} to={image} color="pink" width={3} />
            <Arrow to={bottom} color="yellow" width={5} />
            <Arrow to={top} color="blue" />
            <Label at={top} color="blue">v₂</Label>
            <Label at={image} color="teal" dy={22}>Av₂</Label>
            {noChain ? null : <Label at={bottom} color="yellow" dy={24}>v₁</Label>}
            <Handle at={top} onMove={setTop} color="blue" label={`Tip of v2, at ${describeVector(top)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`${shiftTex(lambda)} = ${matrixTex(shifted)}`} />
            <Readout tex={`(${shiftTex(lambda)})${columnTex(top, palette.blue)} = ${columnTex(bottom, palette.yellow)}`} />
            <Readout tex={`(${shiftTex(lambda)})${columnTex(bottom, palette.yellow)} = ${columnTex(apply(shifted, bottom))}`} />
            <div className="rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
              <SwapLine
                showSecond={noChain}
                first={<>The push lands on the yellow eigenline, and a second push sends it to <Tex>{"\\mathbf 0"}</Tex>.</>}
                second={<>This <Tex>{"\\mathbf v_2"}</Tex> is already an eigenvector, so its push is <Tex>{"\\mathbf 0"}</Tex> and no chain starts.</>}
              />
            </div>
          </>
        }
      />
    </Panel>
  );
}

function multiply(first: Matrix3, second: Matrix3): Matrix3 {
  return first.map((row) => second[0].map((_, j) => row.reduce((sum, value, k) => sum + value * second[k][j], 0)));
}

function power(matrix: Matrix3, exponent: number): Matrix3 {
  return Array.from({ length: exponent - 1 }).reduce<Matrix3>((product) => multiply(product, matrix), matrix);
}

function eliminateBelow(rows: number[][], pivotRow: number, column: number) {
  for (let r = pivotRow + 1; r < rows.length; r += 1) {
    const factor = rows[r][column] / rows[pivotRow][column];
    rows[r] = rows[r].map((value, c) => value - factor * rows[pivotRow][c]);
  }
}

function rank(matrix: Matrix3): number {
  const rows = matrix.map((row) => [...row]);
  let pivotRow = 0;
  for (let column = 0; column < rows[0].length && pivotRow < rows.length; column += 1) {
    const found = rows.findIndex((row, index) => index >= pivotRow && Math.abs(row[column]) > 1e-9);
    if (found < 0) continue;
    [rows[pivotRow], rows[found]] = [rows[found], rows[pivotRow]];
    eliminateBelow(rows, pivotRow, column);
    pivotRow += 1;
  }
  return pivotRow;
}

/** Slide k and watch dim Nul (A − λI)^k grow until it reaches the algebraic multiplicity of λ. */
export function NullPowerClimb({ matrix, lambda, multiplicity }: { matrix: Matrix3; lambda: number; multiplicity: number }) {
  const [exponent, setExponent] = useState(1);
  const { settled, gesture } = useSettled(exponent);
  const size = matrix.length;
  const shifted = matrix.map((row, i) => row.map((value, j) => (i === j ? value - lambda : value)));
  const nullity = (k: number) => size - rank(power(shifted, k));
  const solved = nullity(settled) >= multiplicity;
  const current = nullity(exponent);
  const base = `(A - ${texNumber(lambda)}I)`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Raise <Tex>{"k"}</Tex> until the null space of <Tex>{`${base}^k`}</Tex> is as big as the algebraic multiplicity of <Tex>{`\\lambda = ${texNumber(lambda)}`}</Tex>, which is {multiplicity}.</>}
        success={<>The dimension reached {multiplicity} and stops growing there. That null space is the generalized eigenspace for <Tex>{`\\lambda = ${texNumber(lambda)}`}</Tex>.</>}
      />
      <div className="space-y-4">
        <Slider label="k" value={exponent} onChange={setExponent} min={1} max={size} step={1} color={palette.glow} />
        <Readout tex={`${base}^{${exponent}} = ${matrixTex(power(shifted, exponent))}`} />
        <CountRow label={<Tex>{`\\dim\\operatorname{Nul}${base}^{${exponent}} = ${current}`}</Tex>}>
          <DimensionSlots filled={Math.min(current, multiplicity)} places={multiplicity} color={current >= multiplicity ? "teal" : "yellow"} label={`${current} of ${multiplicity}`} />
        </CountRow>
      </div>
    </Panel>
  );
}

const SWEEP_STEP = 15;
const SWEEP_ANGLES = Array.from({ length: 180 / SWEEP_STEP }, (_, index) => index * SWEEP_STEP);
const SWEEP_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -4, yMax: 4 };
const RAY_LENGTH = 2.5;

const directionAt = (degrees: number): Vec => [Math.cos((degrees * Math.PI) / 180), Math.sin((degrees * Math.PI) / 180)];
const cross = (first: Vec, second: Vec) => first[0] * second[1] - first[1] * second[0];
const keepsLine = (matrix: Matrix2, direction: Vec) => Math.abs(cross(direction, apply(matrix, direction))) < 1e-9;

function tickColor(seen: boolean, eigen: boolean): string {
  if (!seen) return "var(--palette-grid)";
  return eigen ? hue("glow") : hue("text");
}

/** One tick at each end of every line the sweep can visit; visited lines darken and eigenlines glow. */
function SweepTicks({ matrix, visited }: { matrix: Matrix2; visited: number[] }) {
  const { toSvg } = usePlane();
  const ticks = SWEEP_ANGLES.flatMap((degrees) => [degrees, degrees + 180]);
  return (
    <g aria-hidden>
      {ticks.map((degrees) => {
        const direction = directionAt(degrees);
        const [x1, y1] = toSvg(scale(3.3, direction));
        const [x2, y2] = toSvg(scale(3.8, direction));
        const color = tickColor(visited.includes(degrees % 180), keepsLine(matrix, direction));
        return <line key={degrees} x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth={4} strokeLinecap="round" />;
      })}
    </g>
  );
}

/** Sweep a direction through every line and watch where A keeps the arrow on its own line. */
export function ShearRaySweep({ matrix, start = 90 }: { matrix: Matrix2; start?: number }) {
  const [angle, setAngle] = useState(start);
  const [visited, setVisited] = useState<number[]>([start]);
  const { settled: solved, gesture } = useSettled(visited.length === SWEEP_ANGLES.length);
  const direction = directionAt(angle);
  const ray = scale(RAY_LENGTH, direction);
  const image = apply(matrix, ray);
  const onLine = keepsLine(matrix, direction);
  const found = SWEEP_ANGLES.filter((degrees) => visited.includes(degrees) && keepsLine(matrix, directionAt(degrees))).length;
  const turn = (value: number) => {
    setAngle(value);
    setVisited((current) => (current.includes(value) ? current : [...current, value]));
  };

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Turn the blue arrow <Tex>{"\\mathbf u"}</Tex> through every angle from 0° to 165°. The ticks around the edge darken as you visit each line, and a tick glows when <Tex>{"A\\mathbf u"}</Tex> stays on the line through <Tex>{"\\mathbf u"}</Tex>.</>}
        success={<>You visited every line through the origin, and only the horizontal one glows. The shear has a single eigenline, so it has one independent eigenvector even though <Tex>{"\\lambda = 1"}</Tex> is a double root.</>}
      />
      <Workbench
        plane={
          <Plane bounds={SWEEP_BOUNDS} label={`Direction u at ${angle} degrees and its image A u at ${describeVector(image)}.`}>
            <LineThrough direction={direction} color={onLine ? "yellow" : "blue"} dashed={!onLine} />
            <SweepTicks matrix={matrix} visited={visited} />
            <Arrow to={image} color="teal" />
            <Arrow to={ray} color="blue" />
            <Label at={ray} color="blue" dx={-24}>u</Label>
            <Label at={image} color="teal">Au</Label>
            {onLine ? <Marker at={image} color="glow" /> : null}
          </Plane>
        }
        readout={
          <>
            <Slider label="\theta" value={angle} onChange={turn} min={0} max={165} step={SWEEP_STEP} color={palette.blue} />
            <Readout tex={`A${columnTex(ray, palette.blue)} = ${columnTex(image, palette.teal)}`} />
            <CountRow label={`Lines visited: ${visited.length} of ${SWEEP_ANGLES.length}`}>
              <span className="tabular-nums">Eigenlines: {found}</span>
            </CountRow>
          </>
        }
      />
    </Panel>
  );
}

const COORDINATE_BOUNDS: Bounds = { xMin: -5, xMax: 8, yMin: -4, yMax: 4 };

/** Weights of `target` in the basis (first, second), by Cramer's rule. */
function weightsIn(first: Vec, second: Vec, target: Vec): Vec {
  const area = cross(first, second);
  return [cross(target, second) / area, cross(first, target) / area];
}

/** Sliders for a and b build a·v₁ + b·v₂; matching Av₂ reads off the second column of P⁻¹AP. */
export function ChainCoordinates({ matrix, bottom, top }: { matrix: Matrix2; bottom: Vec; top: Vec }) {
  const [a, setA] = useState(0);
  const [b, setB] = useState(0);
  const target = apply(matrix, top);
  const partial = scale(a, bottom);
  const result = add(partial, scale(b, top));
  const { settled: solved, gesture } = useSettled(nearlyEqual(result, target));
  const [weightA, weightB] = weightsIn(bottom, top, target);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Pick weights <Tex>{"a"}</Tex> and <Tex>{"b"}</Tex> so that <Tex>{"a\\,\\mathbf v_1 + b\\,\\mathbf v_2"}</Tex> lands on the ringed point <Tex>{`A\\mathbf v_2 = ${columnTex(target)}`}</Tex>.</>}
        success={<>You found <Tex>{`A\\mathbf v_2 = ${texNumber(weightA)}\\,\\mathbf v_1 + ${texNumber(weightB)}\\,\\mathbf v_2`}</Tex>. These weights form the second column of <Tex>{"P^{-1}AP"}</Tex>, and the <Tex>{texNumber(weightA)}</Tex> on top records the push down the chain.</>}
      />
      <Workbench
        plane={
          <Plane bounds={COORDINATE_BOUNDS} label={`Chain vectors v1 and v2. The combination a v1 + b v2 is at ${describeVector(result)} and the target A v2 is at ${describeVector(target)}.`}>
            <LineThrough direction={bottom} color="yellow" dashed />
            {solved ? <Marker at={target} color="teal" /> : <Marker at={target} ring />}
            <Arrow to={partial} color="yellow" width={2.5} />
            <Arrow from={partial} to={result} color="blue" width={2.5} />
            <Arrow to={result} color="teal" />
            <Arrow to={bottom} color="yellow" />
            <Arrow to={top} color="blue" />
            <Label at={bottom} color="yellow" dy={22}>v₁</Label>
            <Label at={top} color="blue" dx={-8} dy={-14}>v₂</Label>
          </Plane>
        }
        readout={
          <>
            <Slider label="a" value={a} onChange={setA} min={-3} max={3} step={1} color={palette.yellow} />
            <Slider label="b" value={b} onChange={setB} min={-2} max={5} step={1} color={palette.blue} />
            <Readout tex={`${texNumber(a)}${columnTex(bottom, palette.yellow)} + ${texNumber(b)}${columnTex(top, palette.blue)} = ${columnTex(result, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}
