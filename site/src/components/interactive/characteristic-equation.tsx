"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { apply, det, formatNumber, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, boundsAround, Handle, Label, Marker, Plane, usePlane } from "./plane";

const minusLambda = (matrix: Matrix2, lambda: number): Matrix2 => [
  [matrix[0][0] - lambda, matrix[0][1]],
  [matrix[1][0], matrix[1][1] - lambda],
];

const columnsOf = (matrix: Matrix2): [Vec, Vec] => [
  [matrix[0][0], matrix[1][0]],
  [matrix[0][1], matrix[1][1]],
];

const charPoly = (matrix: Matrix2) => (lambda: number) => det(minusLambda(matrix, lambda));

const matrixTex = (matrix: Matrix2) =>
  `\\begin{bmatrix} ${matrix[0].map((v) => texNumber(v)).join(" & ")} \\\\ ${matrix[1].map((v) => texNumber(v)).join(" & ")} \\end{bmatrix}`;

const shiftTex = (lambda: number) => (lambda < 0 ? `A + ${texNumber(-lambda)}I` : `A - ${texNumber(lambda)}I`);

function stepsBetween(min: number, max: number, step: number): number[] {
  return Array.from({ length: Math.round((max - min) / step) + 1 }, (_, index) => min + index * step);
}

/** A direction the singular matrix sends to zero, scaled to reach the plane's edge. */
function nullDirection(matrix: Matrix2): Vec {
  const row: Vec = Math.hypot(...matrix[0]) > 1e-9 ? matrix[0] : matrix[1];
  return Math.hypot(...row) > 1e-9 ? [-row[1], row[0]] : [1, 0];
}

const HUNT_BOUNDS = { xMin: -6, xMax: 6, yMin: -5, yMax: 5 };

function FullLine({ direction, color }: { direction: Vec; color: Hue }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg([-40 * direction[0], -40 * direction[1]]);
  const [x2, y2] = toSvg([40 * direction[0], 40 * direction[1]]);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={3.5} strokeOpacity={0.9} strokeLinecap="round" />;
}

function ImageSquare({ matrix }: { matrix: Matrix2 }) {
  const { toSvg } = usePlane();
  const [first, second] = columnsOf(matrix);
  const corners: Vec[] = [[0, 0], first, [first[0] + second[0], first[1] + second[1]], second];
  const color = det(matrix) < 0 ? "pink" : "teal";
  const points = corners.map((corner) => toSvg(corner).join(",")).join(" ");
  return <polygon points={points} fill={hue(color)} fillOpacity={0.3} stroke={hue(color)} strokeWidth={2} strokeLinejoin="round" />;
}

const STRIP = { width: 360, height: 150, pad: 14 };

/** The graph of det(A − λI) over the slider's range, with the current λ and any roots already found. */
function PolynomialStrip({ poly, min, max, lambda, roots }: { poly: (x: number) => number; min: number; max: number; lambda: number; roots: number[] }) {
  const samples = stepsBetween(min, max, (max - min) / 80);
  const values = samples.map(poly);
  const top = Math.max(...values, 1);
  const bottom = Math.min(...values, -1);
  const toX = (x: number) => STRIP.pad + ((x - min) / (max - min)) * (STRIP.width - 2 * STRIP.pad);
  const toY = (y: number) => STRIP.pad + ((top - y) / (top - bottom)) * (STRIP.height - 2 * STRIP.pad);
  const path = samples.map((x, index) => `${index === 0 ? "M" : "L"}${toX(x).toFixed(1)},${toY(values[index]).toFixed(1)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${STRIP.width} ${STRIP.height}`} className="block h-auto w-full rounded-lg bg-surface-sunken" aria-hidden>
      <line x1={STRIP.pad} x2={STRIP.width - STRIP.pad} y1={toY(0)} y2={toY(0)} stroke="var(--palette-axis)" strokeWidth={1.5} />
      <path d={path} fill="none" stroke="var(--palette-text)" strokeWidth={2.5} />
      <line x1={toX(lambda)} x2={toX(lambda)} y1={toY(0)} y2={toY(poly(lambda))} stroke={hue("glow")} strokeWidth={2} strokeDasharray="4 4" />
      {roots.map((root) => (
        <circle key={root} cx={toX(root)} cy={toY(0)} r={9} fill="none" stroke={hue("glow")} strokeWidth={2} />
      ))}
      <circle cx={toX(lambda)} cy={toY(poly(lambda))} r={6} fill={hue("glow")} />
    </svg>
  );
}

function RootSlots({ found, needed }: { found: number[]; needed: number }) {
  return (
    <div className="flex items-center gap-2" role="img" aria-label={`${Math.min(found.length, needed)} of ${needed} found`}>
      {Array.from({ length: needed }, (_, index) => (
        <span
          key={index}
          className="grid h-7 min-w-10 place-items-center rounded-md px-2 text-meta tabular-nums transition-colors duration-300"
          style={
            index < found.length
              ? { background: "color-mix(in oklab, var(--palette-glow) 22%, transparent)", color: hue("glow") }
              : { background: "var(--color-surface-raised)" }
          }
        >
          {index < found.length ? formatNumber(found[index]) : ""}
        </span>
      ))}
    </div>
  );
}

function SwapLine({ first, second, showSecond }: { first: React.ReactNode; second: React.ReactNode; showSecond: boolean }) {
  return (
    <div className="grid">
      <div className={`[grid-area:1/1] ${showSecond ? "swap-hidden" : "swap-shown"}`}>{first}</div>
      <div className={`[grid-area:1/1] ${showSecond ? "swap-shown" : "swap-hidden"}`}>{second}</div>
    </div>
  );
}

function withRoot(found: number[], root: number): number[] {
  return found.includes(root) ? found : [...found, root].sort((a, b) => a - b);
}

/** Remembers every settled λ where det(A − λI) is zero, and whether the slider is resting on one right now. */
function useRootFinder(matrix: Matrix2, lambda: number) {
  const [found, setFound] = useState<number[]>([]);
  const { settled, gesture } = useSettled(lambda);
  const flatSettled = Math.abs(charPoly(matrix)(settled)) < 1e-9;
  if (flatSettled && !found.includes(settled)) setFound(withRoot(found, settled));
  return { found, gesture, flatNow: flatSettled && settled === lambda };
}

function sweepCorners(matrix: Matrix2, min: number, max: number, step: number): Vec[] {
  return stepsBetween(min, max, step).flatMap((value) => {
    const [a, b] = columnsOf(minusLambda(matrix, value));
    return [a, b, [a[0] + b[0], a[1] + b[1]] as Vec];
  });
}

/** Slide λ; the unit square under A − λI flattens exactly where the graph of det(A − λI) crosses zero. */
export function CharacteristicSweep({ matrix, start = 0, min = -1, max = 6, step = 0.5, needed = 2 }: {
  matrix: Matrix2; start?: number; min?: number; max?: number; step?: number; needed?: number;
}) {
  const [lambda, setLambda] = useState(start);
  const { found, gesture, flatNow } = useRootFinder(matrix, lambda);
  const poly = charPoly(matrix);
  const solved = found.length >= needed;
  const shifted = minusLambda(matrix, lambda);
  const [first, second] = columnsOf(shifted);
  const corners = sweepCorners(matrix, min, max, step);
  const roots = stepsBetween(min, max, step).filter((value) => Math.abs(poly(value)) < 1e-9);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide <Tex>{"\\lambda"}</Tex> until <Tex>{"A - \\lambda I"}</Tex> squashes the square flat. Find all {needed} values that do it.</>}
        success={<>The square goes flat at <Tex>{roots.map((value) => texNumber(value)).join(" \\text{ and } ")}</Tex>, exactly where the graph crosses zero. Those are the eigenvalues of <Tex>{"A"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround(corners)} label={`The unit square after A minus ${formatNumber(lambda)} I acts. Its columns land at ${describeVector(first)} and ${describeVector(second)}.`}>
            {flatNow ? <FullLine direction={nullDirection(shifted)} color="glow" /> : null}
            <ImageSquare matrix={shifted} />
            <Arrow to={first} color="green" />
            <Arrow to={second} color="red" />
            {flatNow ? <Marker at={[0, 0]} color="glow" ring /> : null}
          </Plane>
        }
        readout={
          <>
            <Slider label="\lambda" value={lambda} onChange={setLambda} min={min} max={max} step={step} color={palette.glow} />
            <Readout tex={`\\det\\,${matrixTex(shifted)} = ${texNumber(poly(lambda))}`} />
            <PolynomialStrip poly={poly} min={min} max={max} lambda={lambda} roots={found} />
            <div className="flex items-center justify-between gap-3 rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
              <span>Eigenvalues found</span>
              <RootSlots found={found} needed={needed} />
            </div>
          </>
        }
      />
    </Panel>
  );
}

type Pair = { lambda: number; x: Vec };

function recordPair(pairs: Pair[], matrix: Matrix2, lambda: number, x: Vec): Pair[] {
  if (x[0] === 0 && x[1] === 0) return pairs;
  const image = apply(minusLambda(matrix, lambda), x);
  if (image[0] !== 0 || image[1] !== 0) return pairs;
  return pairs.some((pair) => pair.lambda === lambda) ? pairs : [...pairs, { lambda, x }];
}

const pairKey = (lambda: number, x: Vec) => `${lambda}|${x[0]},${x[1]}`;

function parsePair(key: string): { lambda: number; x: Vec } {
  const [lambda, point] = key.split("|");
  return { lambda: Number(lambda), x: point.split(",").map(Number) as Vec };
}

/** Pick λ, then drag x until (A − λI)x lands on 0. Each eigenvalue needs its own nonzero x. */
export function EigenpairHunt({ matrix, start = [2, 0], lambdaStart = 0, min = -2, max = 6, needed = 2 }: {
  matrix: Matrix2; start?: Vec; lambdaStart?: number; min?: number; max?: number; needed?: number;
}) {
  const [x, setX] = useState<Vec>(start);
  const [lambda, setLambda] = useState(lambdaStart);
  const [pairs, setPairs] = useState<Pair[]>([]);
  const { settled, gesture } = useSettled(pairKey(lambda, x));
  const reading = parsePair(settled);
  const next = recordPair(pairs, matrix, reading.lambda, reading.x);
  if (next !== pairs) setPairs(next);
  const solved = pairs.length >= needed;
  const shifted = minusLambda(matrix, lambda);
  const gap = apply(shifted, x);
  const singular = Math.abs(det(minusLambda(matrix, reading.lambda))) < 1e-9;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>For each eigenvalue, set <Tex>{"\\lambda"}</Tex> and drag <Tex>{"\\mathbf x"}</Tex> so the pink arrow <Tex>{"(A - \\lambda I)\\mathbf x"}</Tex> shrinks to <Tex>{"\\mathbf 0"}</Tex>. Find {needed} eigenpairs.</>}
        success={<>Both eigenspaces now glow on the plane. Any nonzero <Tex>{"\\mathbf x"}</Tex> on a glowing line solves <Tex>{"(A - \\lambda I)\\mathbf x = \\mathbf 0"}</Tex> for its <Tex>{"\\lambda"}</Tex>, so it spans that eigenspace.</>}
      />
      <Workbench
        plane={
          <Plane bounds={HUNT_BOUNDS}label={`Input x at ${describeVector(x)}. A minus lambda I sends it to ${describeVector(gap)}. Drag the tip of x or use the arrow keys.`}>
            {pairs.map((pair, index) => (
              <FullLine key={pair.lambda} direction={pair.x} color={index % 2 === 0 ? "yellow" : "blue"} />
            ))}
            <Arrow to={gap} color="pink" />
            <Arrow to={x} color="text" />
            <Label at={x} color="text">x</Label>
            <Handle at={x} onMove={setX} color="text" label={`Tip of the input x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Slider label="\lambda" value={lambda} onChange={setLambda} min={min} max={max} step={1} color={palette.glow} />
            <Readout tex={`${shiftTex(lambda)} = ${matrixTex(shifted)}`} />
            <Readout tex={`(${shiftTex(lambda)})${columnTex(x)} = ${columnTex(gap, palette.pink)}`} />
            <div className="rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
              <SwapLine
                showSecond={singular}
                first={<>At this <Tex>{"\\lambda"}</Tex> the determinant of <Tex>{"A - \\lambda I"}</Tex> is not zero, so only <Tex>{"\\mathbf x = \\mathbf 0"}</Tex> lands on <Tex>{"\\mathbf 0"}</Tex>.</>}
                second={<span className="text-[var(--palette-teal)]">Here <Tex>{"\\det(A - \\lambda I) = 0"}</Tex>, so a whole line of inputs lands on <Tex>{"\\mathbf 0"}</Tex>.</span>}
              />
            </div>
            <div className="flex items-center justify-between gap-3 rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
              <span>Eigenpairs found</span>
              <RootSlots found={pairs.map((pair) => pair.lambda)} needed={needed} />
            </div>
          </>
        }
      />
    </Panel>
  );
}
