"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { apply, formatNumber, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, Handle, Label, Marker, Plane, usePlane, type Bounds } from "./plane";

const EIGEN_BOUNDS: Bounds = { xMin: -6, xMax: 6, yMin: -5, yMax: 5 };
const LINE_HUES: Hue[] = ["yellow", "blue"];

const pointKey = (point: Vec) => `${point[0]},${point[1]}`;
const keyPoint = (key: string): Vec => key.split(",").map(Number) as Vec;
const isZero = (point: Vec) => point[0] === 0 && point[1] === 0;
const cross = (a: Vec, b: Vec) => a[0] * b[1] - a[1] * b[0];

const matrixTex = (matrix: Matrix2) =>
  `\\begin{bmatrix} ${matrix[0].map((v) => texNumber(v)).join(" & ")} \\\\ ${matrix[1].map((v) => texNumber(v)).join(" & ")} \\end{bmatrix}`;

/** The stretch factor when A sends x along its own line, or null when A turns x off it. */
function stretchOf(matrix: Matrix2, x: Vec): number | null {
  if (isZero(x)) return null;
  const image = apply(matrix, x);
  if (Math.abs(cross(x, image)) > 1e-9) return null;
  return x[0] !== 0 ? image[0] / x[0] : image[1] / x[1];
}

function gcd(a: number, b: number): number {
  return b === 0 ? Math.abs(a) : gcd(b, a % b);
}

/** One name per line through the origin, so (2, 4) and (-1, -2) count as the same direction. */
function directionKey(x: Vec): string {
  const divisor = gcd(x[0], x[1]) || 1;
  const reduced: Vec = [x[0] / divisor, x[1] / divisor];
  const flip = reduced[0] < 0 || (reduced[0] === 0 && reduced[1] < 0) ? -1 : 1;
  return pointKey([flip * reduced[0], flip * reduced[1]]);
}

function LineThrough({ direction, color, dashed = false }: { direction: Vec; color: Hue; dashed?: boolean }) {
  const { toSvg } = usePlane();
  const reach = 40;
  const [x1, y1] = toSvg([-reach * direction[0], -reach * direction[1]]);
  const [x2, y2] = toSvg([reach * direction[0], reach * direction[1]]);
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

function FoundSlots({ labels, needed, colors }: { labels: string[]; needed: number; colors: Hue[] }) {
  return (
    <div className="flex items-center gap-2" role="img" aria-label={`${Math.min(labels.length, needed)} of ${needed} found`}>
      {Array.from({ length: needed }, (_, index) => (
        <span
          key={index}
          className="grid h-7 min-w-10 place-items-center whitespace-nowrap rounded-md px-2 text-meta tabular-nums transition-colors duration-300"
          style={
            index < labels.length
              ? { background: `color-mix(in oklab, ${hue(colors[index % colors.length])} 22%, transparent)`, color: hue(colors[index % colors.length]) }
              : { boxShadow: "inset 0 0 0 2px var(--color-surface-raised)", background: "var(--color-surface-raised)" }
          }
        >
          {index < labels.length ? labels[index] : ""}
        </span>
      ))}
    </div>
  );
}

/** A line of text whose two versions share one grid cell, so swapping them never changes the height. */
function SwapLine({ first, second, showSecond }: { first: React.ReactNode; second: React.ReactNode; showSecond: boolean }) {
  return (
    <div className="grid">
      <div className={`[grid-area:1/1] ${showSecond ? "swap-hidden" : "swap-shown"}`}>{first}</div>
      <div className={`[grid-area:1/1] ${showSecond ? "swap-shown" : "swap-hidden"}`}>{second}</div>
    </div>
  );
}

type Finding = { key: string; stretch: number };

function recordFinding(found: Finding[], matrix: Matrix2, settled: Vec): Finding[] {
  const stretch = stretchOf(matrix, settled);
  if (stretch === null) return found;
  const key = directionKey(settled);
  return found.some((entry) => entry.key === key) ? found : [...found, { key, stretch }];
}

/** Drag x and watch Ax; every settled x that A only stretches marks its whole line as an eigen-direction. */
export function EigenDirectionHunt({ matrix, start = [2, 1], needed = 2 }: { matrix: Matrix2; start?: Vec; needed?: number }) {
  const [x, setX] = useState<Vec>(start);
  const [found, setFound] = useState<Finding[]>([]);
  const { settled, gesture } = useSettled(pointKey(x));
  const settledX = keyPoint(settled);
  const next = recordFinding(found, matrix, settledX);
  if (next !== found) setFound(next);
  const solved = found.length >= needed;
  const image = apply(matrix, x);
  const settledStretch = stretchOf(matrix, settledX);
  const onLine = settledStretch !== null && pointKey(x) === settled;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf x"}</Tex> until <Tex>{"A\\mathbf x"}</Tex> lands on the dashed line through <Tex>{"\\mathbf x"}</Tex>. Find {needed} different lines like that.</>}
        success={<>You found both eigen-directions. Along them <Tex>{"A"}</Tex> multiplies by <Tex>{found.map((entry) => `{${texNumber(entry.stretch)}}`).join(" \\text{ and } ")}</Tex>, and every other direction gets turned.</>}
      />
      <Workbench
        plane={
          <Plane bounds={EIGEN_BOUNDS} label={`Input x at ${describeVector(x)} and its output A x at ${describeVector(image)}. Drag the tip of x or use the arrow keys.`}>
            {found.map((entry, index) => (
              <LineThrough key={entry.key} direction={keyPoint(entry.key)} color={LINE_HUES[index % LINE_HUES.length]} />
            ))}
            {isZero(x) ? null : <LineThrough direction={x} color="text" dashed />}
            <Arrow to={image} color="teal" width={onLine ? 5 : 3.5} />
            <Arrow to={x} color="text" />
            {onLine ? <Marker at={image} color="glow" ring /> : null}
            <Label at={x} color="text">x</Label>
            <Label at={image} color="teal" dy={22}>Ax</Label>
            <Handle at={x} onMove={setX} color="text" label={`Tip of the input x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`${matrixTex(matrix)}${columnTex(x)} = ${columnTex(image, palette.teal)}`} />
            <div className="rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
              <SwapLine
                showSecond={onLine}
                first={<>Right now <Tex>{"A\\mathbf x"}</Tex> is not a multiple of <Tex>{"\\mathbf x"}</Tex>.</>}
                second={<span className="text-[var(--palette-teal)]"><Tex>{`A\\mathbf x = ${texNumber(settledStretch ?? 0)}\\,\\mathbf x`}</Tex>, so <Tex>{"\\mathbf x"}</Tex> is an eigenvector.</span>}
              />
            </div>
            <div className="flex items-center justify-between gap-3 rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
              <span>Eigenvalues found</span>
              <FoundSlots labels={found.map((entry) => formatNumber(entry.stretch))} needed={needed} colors={LINE_HUES} />
            </div>
          </>
        }
      />
    </Panel>
  );
}

const minusLambda = (matrix: Matrix2, lambda: number): Matrix2 => [
  [matrix[0][0] - lambda, matrix[0][1]],
  [matrix[1][0], matrix[1][1] - lambda],
];

/** Drag x; the pink gap from λx to Ax is (A − λI)x, and the inputs where it closes form the eigenspace. */
export function EigenGapHunt({ matrix, lambda, start = [2, 0], needed = 2 }: { matrix: Matrix2; lambda: number; start?: Vec; needed?: number }) {
  const [x, setX] = useState<Vec>(start);
  const [found, setFound] = useState<string[]>([]);
  const { settled, gesture } = useSettled(pointKey(x));
  const settledX = keyPoint(settled);
  const shifted = minusLambda(matrix, lambda);
  const closes = !isZero(settledX) && isZero(apply(shifted, settledX));
  if (closes && !found.includes(settled)) setFound([...found, settled]);
  const solved = found.length >= needed;
  const image = apply(matrix, x);
  const stretched: Vec = [lambda * x[0], lambda * x[1]];
  const gap = apply(shifted, x);
  const lambdaTex = lambda === 1 ? "" : texNumber(lambda);
  const shiftTex = `A - ${lambdaTex}I`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The pink gap runs from <Tex>{`${lambdaTex}\\mathbf x`}</Tex> to <Tex>{"A\\mathbf x"}</Tex>. Close it at {needed} different nonzero inputs.</>}
        success={<>The gap closes on a whole line. That line is the eigenspace <Tex>{`\\operatorname{Nul}(${shiftTex})`}</Tex>, and every nonzero point on it is an eigenvector for <Tex>{`\\lambda = ${texNumber(lambda)}`}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={EIGEN_BOUNDS} label={`Input x at ${describeVector(x)}, its output A x at ${describeVector(image)}, and ${texNumber(lambda)} x at ${describeVector(stretched)}. Drag the tip of x or use the arrow keys.`}>
            {solved ? <LineThrough direction={keyPoint(found[0])} color="yellow" /> : null}
            <Arrow to={stretched} color="yellow" dashed />
            <Arrow to={image} color="teal" />
            <Arrow from={stretched} to={image} color="pink" width={3} />
            <Arrow to={x} color="text" />
            {found.map((key) => (
              <Marker key={key} at={keyPoint(key)} color="glow" />
            ))}
            <Label at={x} color="text">x</Label>
            <Label at={image} color="teal" dy={22}>Ax</Label>
            <Handle at={x} onMove={setX} color="text" label={`Tip of the input x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`${shiftTex} = ${matrixTex(shifted)}`} />
            <Readout tex={`(${shiftTex})${columnTex(x)} = ${columnTex(gap, palette.pink)}`} />
            <div className="flex items-center justify-between gap-3 rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
              <span>Inputs where the gap closes</span>
              <FoundSlots labels={found.map((key) => describeVector(keyPoint(key)))} needed={needed} colors={["glow"]} />
            </div>
          </>
        }
      />
    </Panel>
  );
}

type Matrix3 = [[number, number, number], [number, number, number], [number, number, number]];

function shiftedTriangularTex(matrix: Matrix3, lambda: number): string {
  const rows = matrix.map((row, i) =>
    row
      .map((value, j) => {
        if (i !== j) return texNumber(value);
        const entry = value - lambda;
        return entry === 0 ? `\\textcolor{${palette.glow}}{\\mathbf{0}}` : `\\textcolor{${palette.glow}}{${texNumber(entry)}}`;
      })
      .join(" & "),
  );
  return `T - ${lambda < 0 ? `(${texNumber(lambda)})` : texNumber(lambda)}I = \\begin{bmatrix} ${rows.join(" \\\\ ")} \\end{bmatrix}`;
}

/** Slide λ; whenever a diagonal entry of T − λI hits zero, a free variable appears and λ joins the eigenvalues. */
export function DiagonalZeroHunt({ matrix, start = 0, min = -4, max = 6 }: { matrix: Matrix3; start?: number; min?: number; max?: number }) {
  const [lambda, setLambda] = useState(start);
  const [found, setFound] = useState<number[]>([]);
  const { settled, gesture } = useSettled(lambda);
  const diagonal = matrix.map((row, i) => row[i]);
  const eigenvalues = [...new Set(diagonal)];
  if (eigenvalues.includes(settled) && !found.includes(settled)) setFound([...found, settled]);
  const solved = found.length >= eigenvalues.length;
  const zeroAt = diagonal.findIndex((value) => value === settled);
  const hasFree = zeroAt >= 0 && settled === lambda;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide <Tex>{"\\lambda"}</Tex> until <Tex>{"T - \\lambda I"}</Tex> gets a free variable. Find all {eigenvalues.length} values that do it.</>}
        success={<>The eigenvalues are <Tex>{[...found].sort((a, b) => a - b).map((value) => texNumber(value)).join(",\\ ")}</Tex>, exactly the diagonal of <Tex>{"T"}</Tex>.</>}
      />
      <div className="space-y-4">
        <Slider label="\lambda" value={lambda} onChange={setLambda} min={min} max={max} step={1} color={palette.glow} />
        <Readout tex={shiftedTriangularTex(matrix, lambda)} />
        <div className="rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
          <SwapLine
            showSecond={hasFree}
            first={<>Every diagonal entry is nonzero, so each column has a pivot and only <Tex>{"\\mathbf x = \\mathbf 0"}</Tex> solves <Tex>{"(T - \\lambda I)\\mathbf x = \\mathbf 0"}</Tex>.</>}
            second={<span className="text-[var(--palette-teal)]">Diagonal entry {zeroAt + 1} is <Tex>{"0"}</Tex>, so column {zeroAt + 1} has no pivot and <Tex>{`x_${zeroAt + 1}`}</Tex> is free.</span>}
          />
        </div>
        <div className="flex items-center justify-between gap-3 rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
          <span>Eigenvalues found</span>
          <FoundSlots labels={found.map((value) => formatNumber(value))} needed={eigenvalues.length} colors={["glow"]} />
        </div>
      </div>
    </Panel>
  );
}
