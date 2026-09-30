"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { apply, det, formatNumber, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, Handle, Label, Marker, Plane, usePlane, type Bounds } from "./plane";

type Eigenpair = { vector: Vec; value: number };

const pairKey = (a: number, b: number) => `${a},${b}`;
const keyPair = (key: string): Vec => key.split(",").map(Number) as Vec;
const cross = (a: Vec, b: Vec) => a[0] * b[1] - a[1] * b[0];
const isZero = (point: Vec) => point[0] === 0 && point[1] === 0;
const trace = (matrix: Matrix2) => matrix[0][0] + matrix[1][1];

const matrixTex = (matrix: Matrix2) =>
  `\\begin{bmatrix} ${matrix[0].map((v) => texNumber(v)).join(" & ")} \\\\ ${matrix[1].map((v) => texNumber(v)).join(" & ")} \\end{bmatrix}`;

/** A statement whose two versions share one grid cell, so swapping them never changes the height. */
function SteadySwap({ first, second, showSecond }: { first: React.ReactNode; second: React.ReactNode; showSecond: boolean }) {
  return (
    <div className="grid">
      <div aria-hidden={showSecond} className={`[grid-area:1/1] ${showSecond ? "swap-hidden" : "swap-shown"}`}>{first}</div>
      <div aria-hidden={!showSecond} className={`[grid-area:1/1] ${showSecond ? "swap-shown" : "swap-hidden"}`}>{second}</div>
    </div>
  );
}

function Curve({ polynomial, color, dashed = false }: { polynomial: (x: number) => number; color: Hue; dashed?: boolean }) {
  const { bounds, toSvg } = usePlane();
  const steps = 160;
  const points = Array.from({ length: steps + 1 }, (_, index) => {
    const x = bounds.xMin + ((bounds.xMax - bounds.xMin) * index) / steps;
    const [sx, sy] = toSvg([x, Math.max(bounds.yMin - 4, Math.min(bounds.yMax + 4, polynomial(x)))]);
    return `${sx.toFixed(1)},${sy.toFixed(1)}`;
  });
  return (
    <polyline
      points={points.join(" ")}
      fill="none"
      stroke={hue(color)}
      strokeWidth={dashed ? 2.5 : 3.5}
      strokeDasharray={dashed ? "7 6" : undefined}
      strokeOpacity={dashed ? 0.75 : 1}
      strokeLinecap="round"
    />
  );
}

function MatchRow({ label, value, target, targetLabel }: { label: string; value: number; target: number; targetLabel: string }) {
  const matches = value === target;
  return (
    <div
      className="flex items-center justify-between gap-3 rounded-lg px-4 py-3 text-meta transition-colors duration-300"
      style={{ background: matches ? "color-mix(in oklab, var(--palette-teal) 16%, transparent)" : "var(--color-surface-sunken)" }}
    >
      <Tex>{`${label} = ${texNumber(value)}`}</Tex>
      <span style={{ color: matches ? "var(--palette-teal)" : "var(--color-text-muted)" }}>
        <Tex>{`${matches ? "=" : "\\ne"} ${targetLabel} = ${texNumber(target)}`}</Tex>
      </span>
    </div>
  );
}

const CURVE_BOUNDS: Bounds = { xMin: -2, xMax: 8, yMin: -3, yMax: 6 };

/** Pick two roots; the teal curve (λ − λ1)(λ − λ2) matches the dashed characteristic polynomial exactly when the sum is the trace and the product is the determinant. */
export function TraceCurveMatch({ matrix, start = [0, 1], min = -2, max = 8 }: { matrix: Matrix2; start?: Vec; min?: number; max?: number }) {
  const [roots, setRoots] = useState<Vec>(start);
  const { settled, gesture } = useSettled(pairKey(roots[0], roots[1]));
  const [first, second] = keyPair(settled);
  const tr = trace(matrix);
  const dt = det(matrix);
  const solved = first + second === tr && first * second === dt;
  const target = (x: number) => x * x - tr * x + dt;
  const guess = (x: number) => (x - roots[0]) * (x - roots[1]);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide <Tex>{"\\lambda_1"}</Tex> and <Tex>{"\\lambda_2"}</Tex> until the teal curve lands on the dashed characteristic polynomial of <Tex>{`A = ${matrixTex(matrix)}`}</Tex>.</>}
        success={<>The eigenvalues are <Tex>{`${texNumber(Math.min(first, second))}`}</Tex> and <Tex>{`${texNumber(Math.max(first, second))}`}</Tex>. Their sum is the trace <Tex>{texNumber(tr)}</Tex> and their product is the determinant <Tex>{texNumber(dt)}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={CURVE_BOUNDS} label={`Graph of the dashed characteristic polynomial and the teal curve with roots ${formatNumber(roots[0])} and ${formatNumber(roots[1])}.`}>
            <Curve polynomial={target} color="text" dashed />
            <Curve polynomial={guess} color={solved ? "teal" : "pink"} />
            <Marker at={[roots[0], 0]} color="yellow" ring={solved} />
            <Marker at={[roots[1], 0]} color="blue" ring={solved} />
          </Plane>
        }
        readout={
          <>
            <Slider label="\lambda_1" value={roots[0]} onChange={(value) => setRoots([value, roots[1]])} min={min} max={max} step={1} color={palette.yellow} />
            <Slider label="\lambda_2" value={roots[1]} onChange={(value) => setRoots([roots[0], value])} min={min} max={max} step={1} color={palette.blue} />
            <MatchRow label="\lambda_1 + \lambda_2" value={roots[0] + roots[1]} target={tr} targetLabel="\operatorname{tr} A" />
            <MatchRow label="\lambda_1 \lambda_2" value={roots[0] * roots[1]} target={dt} targetLabel="\det A" />
          </>
        }
      />
    </Panel>
  );
}

const SWING_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -5, yMax: 5 };
const SWING_LENGTH = 4.5;

function LineThroughOrigin({ direction, color, bold }: { direction: Vec; color: Hue; bold: boolean }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg([-40 * direction[0], -40 * direction[1]]);
  const [x2, y2] = toSvg([40 * direction[0], 40 * direction[1]]);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={bold ? 6 : 3} strokeOpacity={bold ? 1 : 0.8} strokeLinecap="round" />;
}

function iterates(matrix: Matrix2, start: Vec, count: number): Vec[] {
  const list: Vec[] = [start];
  for (let k = 1; k <= count; k += 1) list.push(apply(matrix, list[k - 1]));
  return list;
}

function rescale(point: Vec): Vec {
  const size = Math.hypot(point[0], point[1]);
  return [(point[0] * SWING_LENGTH) / size, (point[1] * SWING_LENGTH) / size];
}

/** Weights c1, c2 with start = c1 v1 + c2 v2. */
function eigenWeights(start: Vec, first: Vec, second: Vec): Vec {
  const base = cross(first, second);
  return [cross(start, second) / base, cross(first, start) / base];
}

function weightTex(weights: Vec, pairs: [Eigenpair, Eigenpair]): string {
  const power = (pair: Eigenpair, color: string, name: string) =>
    `\\textcolor{${palette.glow}}{${texNumber(pair.value)}^k}\\,\\textcolor{${color}}{\\mathbf ${name}}`;
  const formula = `\\mathbf x_k = c_1 ${power(pairs[0], palette.yellow, "v_1")} + c_2 ${power(pairs[1], palette.blue, "v_2")}`;
  return `\\begin{gathered} ${formula} \\\\ c_1 = ${texNumber(weights[0])},\\quad c_2 = ${texNumber(weights[1])} \\end{gathered}`;
}

/** Drag x0 and slide k; every rescaled iterate A^k x0 swings toward the dominant eigenline unless x0 has no dominant piece. */
export function IterateSwing({ matrix, pairs, start = [1, 0] }: { matrix: Matrix2; pairs: [Eigenpair, Eigenpair]; start?: Vec }) {
  const [x0, setX0] = useState<Vec>(start);
  const [steps, setSteps] = useState(3);
  const { settled, gesture } = useSettled(pairKey(x0[0], x0[1]));
  const settledStart = keyPair(settled);
  const solved = !isZero(settledStart) && cross(settledStart, pairs[1].vector) === 0;
  const path = isZero(x0) ? [] : iterates(matrix, x0, steps);
  const weights = eigenWeights(x0, pairs[0].vector, pairs[1].vector);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Almost every start swings onto the yellow line as <Tex>{"k"}</Tex> grows. Drag <Tex>{"\\mathbf x_0"}</Tex> to a nonzero start whose arrows never do.</>}
        success={<>A start on the blue line has no yellow piece, so <Tex>{"c_1 = 0"}</Tex> and <Tex>{`A^k\\mathbf x_0 = ${texNumber(pairs[1].value)}^k\\mathbf x_0`}</Tex> stays on the blue line forever.</>}
      />
      <Workbench
        plane={
          <Plane bounds={SWING_BOUNDS} label={`Start x0 at ${describeVector(x0)} with ${steps} steps of A drawn at one length. Drag the tip of x0 or use the arrow keys.`}>
            <LineThroughOrigin direction={pairs[0].vector} color="yellow" bold={false} />
            <LineThroughOrigin direction={pairs[1].vector} color="blue" bold={solved} />
            {path.map((point, index) => (
              <g key={index} opacity={index === path.length - 1 ? 1 : 0.2 + (0.5 * index) / path.length}>
                <Arrow to={rescale(point)} color="teal" width={index === path.length - 1 ? 4.5 : 2.5} />
              </g>
            ))}
            {path.length > 1 ? <Label at={rescale(path[path.length - 1])} color="teal" dy={22}>{`x${steps}`}</Label> : null}
            <Arrow to={x0} color="text" />
            {solved ? <Marker at={x0} color="glow" ring /> : null}
            <Handle at={x0} onMove={setX0} color="text" label={`Tip of the start x0, at ${describeVector(x0)}`} />
          </Plane>
        }
        readout={
          <>
            <Slider label="k" value={steps} onChange={setSteps} min={0} max={6} step={1} color={palette.teal} />
            <Readout tex={`\\mathbf x_{${steps}} = A^{${steps}}${columnTex(x0)} = ${columnTex(path[path.length - 1] ?? [0, 0], palette.teal)}`} />
            <Readout tex={weightTex(weights, pairs)} />
            <div className="rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
              <SteadySwap
                showSecond={solved}
                first={<>The yellow piece grows by <Tex>{texNumber(pairs[0].value)}</Tex> each step and the blue piece by <Tex>{texNumber(pairs[1].value)}</Tex>, so yellow takes over.</>}
                second={<span className="text-[var(--palette-teal)]">This start has no yellow piece, so nothing pulls it toward the yellow line.</span>}
              />
            </div>
          </>
        }
      />
    </Panel>
  );
}

const SHIFT_HUES: Hue[] = ["yellow", "blue"];

function LaneLabel({ at, children }: { at: Vec; children: string }) {
  const { toSvg } = usePlane();
  const [x, y] = toSvg(at);
  return (
    <text x={x + 12} y={y + 10} fill="var(--palette-text)" fontSize={30} fontStyle="italic" fontFamily="KaTeX_Math, serif" paintOrder="stroke" stroke="var(--color-surface-sunken)" strokeWidth={6}>
      {children}
    </text>
  );
}

function ShiftLane({ values, shift }: { values: number[]; shift: number }) {
  return (
    <>
      {values.map((value, index) => (
        <g key={index}>
          <Marker at={[value, 1]} color={SHIFT_HUES[index]} />
          <Arrow from={[value, 1]} to={[value + shift, 0]} color={SHIFT_HUES[index]} width={2.5} dashed />
          <Marker at={[value + shift, 0]} color={value + shift === 0 ? "glow" : SHIFT_HUES[index]} ring={value + shift === 0} />
        </g>
      ))}
    </>
  );
}

/** Slide c; each eigenvalue of A + cI is an eigenvalue of A moved by c, and the matrix turns singular when one of them reaches 0. */
export function ShiftToSingular({ matrix, eigenvalues, min = -8, max = 8 }: { matrix: Matrix2; eigenvalues: [number, number]; min?: number; max?: number }) {
  const [shift, setShift] = useState(0);
  const [found, setFound] = useState<number[]>([]);
  const { settled, gesture } = useSettled(shift);
  const targets = eigenvalues.map((value) => -value);
  if (targets.includes(settled) && !found.includes(settled)) setFound([...found, settled]);
  const solved = targets.every((value) => found.includes(value));
  const shifted: Matrix2 = [
    [matrix[0][0] + shift, matrix[0][1]],
    [matrix[1][0], matrix[1][1] + shift],
  ];
  const singular = eigenvalues.some((value) => value + shift === 0);
  const bounds: Bounds = { xMin: Math.min(...eigenvalues) + min - 5, xMax: Math.max(...eigenvalues) + max + 1, yMin: -1, yMax: 2 };

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide <Tex>{"c"}</Tex> until <Tex>{"A + cI"}</Tex> is not invertible. There are two values that do it, so find both.</>}
        success={<>At <Tex>{`c = ${[...found].sort((a, b) => a - b).map((value) => texNumber(value)).join(" \\text{ and } c = ")}`}</Tex> an eigenvalue of <Tex>{"A + cI"}</Tex> lands on <Tex>{"0"}</Tex>. Those are <Tex>{"c = -\\lambda"}</Tex> for each eigenvalue <Tex>{"\\lambda"}</Tex> of <Tex>{"A"}</Tex>.</>}
      />
      <div className="space-y-4">
        <Plane bounds={bounds} label={`Eigenvalues of A on the top row and of A plus ${formatNumber(shift)} I on the bottom row.`}>
          <LaneLabel at={[bounds.xMin, 1]}>A</LaneLabel>
          <LaneLabel at={[bounds.xMin, 0]}>A + cI</LaneLabel>
          <ShiftLane values={eigenvalues} shift={shift} />
        </Plane>
        <Slider label="c" value={shift} onChange={setShift} min={min} max={max} step={1} color={palette.glow} />
        <Readout tex={`\\det(A + cI) = \\det${matrixTex(shifted)} = ${texNumber(det(shifted))}`} />
        <div className="rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
          <SteadySwap
            showSecond={singular}
            first={<>The eigenvalues of <Tex>{"A + cI"}</Tex> are <Tex>{eigenvalues.map((value) => texNumber(value + shift)).join(",\\ ")}</Tex>, and neither is <Tex>{"0"}</Tex>.</>}
            second={<span className="text-[var(--palette-teal)]">An eigenvalue of <Tex>{"A + cI"}</Tex> is <Tex>{"0"}</Tex>, so its determinant, the product of the eigenvalues, is <Tex>{"0"}</Tex> too.</span>}
          />
        </div>
      </div>
    </Panel>
  );
}

/** base^k as TeX, writing negative powers as fractions so 2^-3 reads 1/8 instead of a rounded decimal. */
function powerValueTex(base: number, k: number): string {
  const value = base ** k;
  if (Number.isInteger(value)) return texNumber(value);
  const sign = value < 0 ? "-" : "";
  return `${sign}\\tfrac{1}{${texNumber(Math.abs(1 / value))}}`;
}

function powerLineTex(pair: Eigenpair, k: number, color: string, name: string): string {
  const base = pair.value < 0 ? `(${texNumber(pair.value)})` : texNumber(pair.value);
  const vector = `\\textcolor{${color}}{\\mathbf ${name}}`;
  return `A^{${k}}${vector} = ${base}^{${k}}${vector} = ${powerValueTex(pair.value, k)}\\,${vector}`;
}

function powerWithFactor(value: number, factor: number, min: number, max: number): number {
  const candidates = Array.from({ length: max - min + 1 }, (_, index) => min + index);
  return candidates.find((k) => Math.abs(value ** k - factor) < 1e-9) ?? min;
}

/** Slide the power k: each eigenvector of A stays on its line and is scaled by its own eigenvalue to the k, negative k included. */
export function PowerLineStretch({ pairs, factor = 0.25, min = -3, max = 2 }: { pairs: [Eigenpair, Eigenpair]; factor?: number; min?: number; max?: number }) {
  const [k, setK] = useState(1);
  const answer = powerWithFactor(pairs[0].value, factor, min, max);
  const { settled: solved, gesture } = useSettled(k === answer);
  const images = pairs.map((pair): Vec => [pair.value ** k * pair.vector[0], pair.value ** k * pair.vector[1]]);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Choose the power <Tex>{"k"}</Tex> so that <Tex>{"A^k"}</Tex> shrinks the yellow eigenvector to <Tex>{powerValueTex(1 / factor, -1)}</Tex> of its length.</>}
        success={<>At <Tex>{`k = ${answer}`}</Tex>, <Tex>{`A^{${answer}} = (A^{-1})^{${-answer}}`}</Tex> multiplies the yellow line by <Tex>{powerValueTex(pairs[0].value, answer)}</Tex> and the blue line by <Tex>{powerValueTex(pairs[1].value, answer)}</Tex>. The eigenvectors never moved off their lines.</>}
      />
      <Workbench
        plane={
          <Plane bounds={SWING_BOUNDS} label={`The yellow and blue eigenvector lines, with each eigenvector and its image under A to the power ${k}.`}>
            <LineThroughOrigin direction={pairs[0].vector} color="yellow" bold={false} />
            <LineThroughOrigin direction={pairs[1].vector} color="blue" bold={false} />
            <Arrow to={pairs[0].vector} color="text" width={2} dashed />
            <Arrow to={pairs[1].vector} color="text" width={2} dashed />
            <Arrow to={images[0]} color={solved ? "teal" : "yellow"} width={4.5} />
            <Arrow to={images[1]} color="blue" width={4.5} />
          </Plane>
        }
        readout={
          <>
            <Slider label="k" value={k} onChange={setK} min={min} max={max} step={1} color={palette.glow} />
            <Readout tex={powerLineTex(pairs[0], k, palette.yellow, "v_1")} />
            <Readout tex={powerLineTex(pairs[1], k, palette.blue, "v_2")} />
          </>
        }
      />
    </Panel>
  );
}

const combine = (c: Vec, first: Vec, second: Vec): Vec => [c[0] * first[0] + c[1] * second[0], c[0] * first[1] + c[1] * second[1]];

const signedTex = (value: number) => `${value < 0 ? "-" : "+"} ${texNumber(Math.abs(value))}`;

function iterateFormulaTex(weights: Vec, pairs: [Eigenpair, Eigenpair]): string {
  const term = (pair: Eigenpair, color: string, name: string) => {
    const base = pair.value < 0 ? `(${texNumber(pair.value)})` : texNumber(pair.value);
    return `\\cdot ${base}^k\\,\\textcolor{${color}}{\\mathbf ${name}}`;
  };
  return `\\mathbf x_k = ${texNumber(weights[0])} ${term(pairs[0], palette.yellow, "v_1")} ${signedTex(weights[1])} ${term(pairs[1], palette.blue, "v_2")}`;
}

/** Slide the weights until c1 v1 + c2 v2 reaches the start x0; those weights are all it takes to write every A^k x0. */
export function EigenWeightSplit({ pairs, target }: { pairs: [Eigenpair, Eigenpair]; target: Vec }) {
  const [c1, setC1] = useState(1);
  const [c2, setC2] = useState(0);
  const [v1, v2] = [pairs[0].vector, pairs[1].vector];
  const first: Vec = [c1 * v1[0], c1 * v1[1]];
  const sum = combine([c1, c2], v1, v2);
  const answer = eigenWeights(target, v1, v2);
  const { settled: solved, gesture } = useSettled(Math.abs(sum[0] - target[0]) < 1e-9 && Math.abs(sum[1] - target[1]) < 1e-9);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Split the start <Tex>{`\\mathbf x_0 = ${columnTex(target)}`}</Tex> into eigenvector pieces: choose <Tex>{"c_1"}</Tex> and <Tex>{"c_2"}</Tex> so that <Tex>{"c_1\\mathbf v_1 + c_2\\mathbf v_2"}</Tex> lands on the ring.</>}
        success={<>With <Tex>{`c_1 = ${texNumber(answer[0])}`}</Tex> and <Tex>{`c_2 = ${texNumber(answer[1])}`}</Tex>, every later step is known at once: <Tex>{iterateFormulaTex(answer, pairs)}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={SWING_BOUNDS} label={`The yellow piece c1 v1 and the blue piece c2 v2 added tip to tail, reaching ${describeVector(sum)}. The ring marks x0 at ${describeVector(target)}.`}>
            <LineThroughOrigin direction={v1} color="yellow" bold={false} />
            <LineThroughOrigin direction={v2} color="blue" bold={false} />
            <Marker at={target} color={solved ? "teal" : "glow"} ring />
            <Arrow to={first} color="yellow" width={4} />
            <Arrow from={first} to={sum} color="blue" width={4} />
            <Arrow to={sum} color="teal" width={solved ? 5 : 3} />
          </Plane>
        }
        readout={
          <>
            <Slider label="c_1" value={c1} onChange={setC1} min={-3} max={4} step={0.5} color={palette.yellow} />
            <Slider label="c_2" value={c2} onChange={setC2} min={-3} max={3} step={0.5} color={palette.blue} />
            <Readout tex={`${texNumber(c1)}${columnTex(v1, palette.yellow)} ${signedTex(c2)}${columnTex(v2, palette.blue)} = ${columnTex(sum, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}
