"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { apply, det, formatNumber, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, Handle, Label, Plane, Segment, usePlane, type Bounds } from "./plane";

const SVD_BOUNDS: Bounds = { xMin: -4, xMax: 4, yMin: -4, yMax: 4 };
const CIRCLE_SAMPLES = 96;

const length = (v: Vec) => Math.hypot(v[0], v[1]);
const unitOf = (v: Vec): Vec => [v[0] / length(v), v[1] / length(v)];
const turn = (degrees: number): Matrix2 => {
  const radians = (degrees * Math.PI) / 180;
  return [[Math.cos(radians), -Math.sin(radians)], [Math.sin(radians), Math.cos(radians)]];
};
const times = (left: Matrix2, right: Matrix2): Matrix2 => [
  [left[0][0] * right[0][0] + left[0][1] * right[1][0], left[0][0] * right[0][1] + left[0][1] * right[1][1]],
  [left[1][0] * right[0][0] + left[1][1] * right[1][0], left[1][0] * right[0][1] + left[1][1] * right[1][1]],
];
const transpose = (m: Matrix2): Matrix2 => [[m[0][0], m[1][0]], [m[0][1], m[1][1]]];

/** The singular values of a 2x2 matrix: square roots of the eigenvalues of AᵀA, largest first. */
function singularValues(m: Matrix2): Vec {
  const gram = times(transpose(m), m);
  const trace = gram[0][0] + gram[1][1];
  const gap = Math.sqrt(Math.max(0, trace * trace - 4 * det(gram)));
  return [Math.sqrt((trace + gap) / 2), Math.sqrt(Math.max(0, (trace - gap) / 2))];
}

/** The image of the unit circle under `m`, drawn as a closed outline. */
function CircleImage({ m, color, dashed = false, fill = 0 }: { m: Matrix2; color: Hue | "muted"; dashed?: boolean; fill?: number }) {
  const { toSvg } = usePlane();
  const points = Array.from({ length: CIRCLE_SAMPLES }, (_, index) => {
    const angle = (2 * Math.PI * index) / CIRCLE_SAMPLES;
    return toSvg(apply(m, [Math.cos(angle), Math.sin(angle)])).join(",");
  }).join(" ");
  const stroke = color === "muted" ? "var(--palette-text-muted)" : hue(color);
  return <polygon points={points} fill={stroke} fillOpacity={fill} stroke={stroke} strokeWidth={2.5} strokeDasharray={dashed ? "6 6" : undefined} aria-hidden />;
}

const IDENTITY: Matrix2 = [[1, 0], [0, 1]];

/** Aim a unit vector x with a handle anywhere on the grid; x points toward it. The goal is the longest Ax. */
export function LongestStretchHunt({ matrix, start = [0, 2] }: { matrix: Matrix2; start?: Vec }) {
  const [aim, setAim] = useState<Vec>(start);
  const [largest] = singularValues(matrix);
  const x = unitOf(aim);
  const image = apply(matrix, x);
  const reach = length(image);
  const { settled, gesture } = useSettled(reach);
  const solved = settled >= largest - 1e-9;
  const moveAim = (point: Vec) => {
    if (point[0] !== 0 || point[1] !== 0) setAim(point);
  };

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the handle to aim the unit vector <Tex>{"\\mathbf x"}</Tex>. Make <Tex>{"A\\mathbf x"}</Tex> reach as far as it can.</>}
        success={<>That is the longest output, <Tex>{`\\|A\\mathbf x\\| = \\sigma_1 = ${texNumber(largest)}`}</Tex>. This <Tex>{"\\mathbf x"}</Tex> is <Tex>{"\\pm\\mathbf v_1"}</Tex>, and <Tex>{"A\\mathbf x"}</Tex> lies on the ellipse&apos;s long axis.</>}
      />
      <Workbench
        plane={
          <Plane bounds={SVD_BOUNDS} label={`Unit circle and its image ellipse under A. The unit vector x is ${describeVector(x)} and A x is ${describeVector(image)}. Drag the aiming handle or use the arrow keys.`}>
            <CircleImage m={IDENTITY} color="muted" dashed />
            <CircleImage m={matrix} color="teal" fill={0.1} />
            <Segment from={[0, 0]} to={aim} color="text" />
            <Arrow to={image} color={solved ? "yellow" : "teal"} />
            <Arrow to={x} color={solved ? "yellow" : "text"} />
            <Label at={image} color={solved ? "yellow" : "teal"}>Ax</Label>
            <Handle at={aim} onMove={moveAim} color="text" label={`Aiming handle at ${describeVector(aim)}; x points toward it`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\mathbf x = \\begin{bmatrix} ${texNumber(x[0])} \\\\ ${texNumber(x[1])} \\end{bmatrix}`} />
            <Readout tex={`\\|A\\mathbf x\\| = \\textcolor{${palette.teal}}{${texNumber(reach)}}`} />
          </>
        }
      />
    </Panel>
  );
}

type EllipseTarget = { sigmas: Vec; turn: number };

const matchesShape = (a: Matrix2, b: Matrix2) => {
  const first = times(a, transpose(a));
  const second = times(b, transpose(b));
  return [0, 1].every((i) => [0, 1].every((j) => Math.abs(first[i][j] - second[i][j]) < 1e-6));
};

function stretchTex(sigmas: Vec): string {
  const [first, second] = sigmas.map((value) => `\\textcolor{${palette.glow}}{${texNumber(value)}}`);
  return `\\Sigma = \\begin{bmatrix} ${first} & 0 \\\\ 0 & ${second} \\end{bmatrix}`;
}

function turnTex(degrees: number): string {
  const [[a, b], [c, d]] = turn(degrees);
  return `U = \\begin{bmatrix} ${texNumber(a)} & ${texNumber(b)} \\\\ ${texNumber(c)} & ${texNumber(d)} \\end{bmatrix}`;
}

/** Sliders for σ₁, σ₂ and U's turn. The circle's image U Σ (circle) must match a dashed target ellipse. */
export function SvdEllipseMatch({ target }: { target: EllipseTarget }) {
  const [first, setFirst] = useState(1);
  const [second, setSecond] = useState(1);
  const [degrees, setDegrees] = useState(0);
  const current = times(turn(degrees), [[first, 0], [0, second]]);
  const goal = times(turn(target.turn), [[target.sigmas[0], 0], [0, target.sigmas[1]]]);
  const { settled: solved, gesture } = useSettled(matchesShape(current, goal));
  const axes: Vec[] = [apply(current, [1, 0]), apply(current, [0, 1])];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Stretch with <Tex>\Sigma</Tex>, then turn with <Tex>U</Tex>, until the teal ellipse lands on the larger dashed ellipse.</>}
        success={<>The ellipses match. Its half-axes have lengths <Tex>{`${texNumber(target.sigmas[0])}`}</Tex> and <Tex>{`${texNumber(target.sigmas[1])}`}</Tex>, so those are the singular values. <Tex>{"V^T"}</Tex> was never needed because turning a circle leaves it the same circle.</>}
      />
      <Workbench
        plane={
          <Plane bounds={SVD_BOUNDS} label={`The unit circle stretched by ${formatNumber(first)} and ${formatNumber(second)} and turned by ${degrees} degrees, with a dashed target ellipse.`}>
            <CircleImage m={IDENTITY} color="muted" dashed />
            <CircleImage m={goal} color="text" dashed />
            <CircleImage m={current} color="teal" fill={solved ? 0.2 : 0.08} />
            <Arrow to={axes[0]} color="yellow" />
            <Arrow to={axes[1]} color="blue" />
          </Plane>
        }
        readout={
          <>
            <Slider label="\sigma_1" value={first} onChange={setFirst} min={0.5} max={3.5} step={0.5} color="var(--palette-yellow)" />
            <Slider label="\sigma_2" value={second} onChange={setSecond} min={0.5} max={3.5} step={0.5} color="var(--palette-blue)" />
            <Slider label="\theta" value={degrees} onChange={setDegrees} min={0} max={180} step={15} color="var(--palette-text)" />
            <Readout tex={stretchTex([first, second])} />
            <Readout tex={turnTex(degrees)} />
          </>
        }
      />
    </Panel>
  );
}

const PICTURE_ROWS = 90;
const PICTURE_COLS = 135;
const BARS_SHOWN = 30;
const JACOBI_SWEEPS = 12;

/** The same formula-drawn landscape as the video: a sky, a round sun and two ridges of hills. */
function landscape(rows: number, cols: number): number[][] {
  return Array.from({ length: rows }, (_, row) => {
    const y = (row + 0.5) / rows;
    return Array.from({ length: cols }, (_, col) => {
      const x = (col + 0.5) / cols;
      const near = 0.72 + 0.07 * Math.sin(2 * Math.PI * 0.8 * x + 2.0) + 0.03 * Math.sin(2 * Math.PI * 4.3 * x);
      const far = 0.52 + 0.09 * Math.sin(2 * Math.PI * 1.3 * x + 0.5) + 0.04 * Math.sin(2 * Math.PI * 3.1 * x + 1.2);
      const sun = (x - 0.72) ** 2 * (cols / rows) ** 2 + (y - 0.3) ** 2 < 0.12 ** 2;
      if (y > near) return 0.12;
      if (y > far) return 0.32;
      return sun ? 0.97 : 0.42 + 0.4 * (1 - y);
    });
  });
}

type Layers = { values: number[]; left: number[][]; scaledRight: number[][] };

function rotatePair(columns: number[][], p: number, q: number, cos: number, sin: number) {
  const a = columns[p];
  const b = columns[q];
  for (let i = 0; i < a.length; i++) {
    const first = a[i];
    a[i] = cos * first - sin * b[i];
    b[i] = sin * first + cos * b[i];
  }
}

const dot = (a: number[], b: number[]) => a.reduce((sum, value, i) => sum + value * b[i], 0);

/** One-sided Jacobi: turn pairs of columns of W = Aᵀ until they are orthogonal, recording the turns in J. */
function orthogonalizeColumns(w: number[][], j: number[][]) {
  for (let sweep = 0; sweep < JACOBI_SWEEPS; sweep++) {
    for (let p = 0; p < w.length - 1; p++) {
      for (let q = p + 1; q < w.length; q++) {
        const alpha = dot(w[p], w[p]);
        const beta = dot(w[q], w[q]);
        const gamma = dot(w[p], w[q]);
        if (Math.abs(gamma) < 1e-12 * Math.sqrt(alpha * beta) || gamma === 0) continue;
        const zeta = (beta - alpha) / (2 * gamma);
        const t = Math.sign(zeta || 1) / (Math.abs(zeta) + Math.sqrt(1 + zeta * zeta));
        const cos = 1 / Math.sqrt(1 + t * t);
        rotatePair(w, p, q, cos, cos * t);
        rotatePair(j, p, q, cos, cos * t);
      }
    }
  }
}

/** The SVD of the picture as layers: A = Σ left[i] ⊗ scaledRight[i], with scaledRight[i] = σᵢ vᵢ. */
function pictureLayers(picture: number[][]): Layers {
  const rows = picture.length;
  const w = picture.map((row) => [...row]);
  const j = Array.from({ length: rows }, (_, index) => Array.from({ length: rows }, (_, k) => (k === index ? 1 : 0)));
  orthogonalizeColumns(w, j);
  const order = w.map((column, index) => ({ index, norm: Math.sqrt(dot(column, column)) })).sort((a, b) => b.norm - a.norm);
  return {
    values: order.map((entry) => entry.norm),
    left: order.map((entry) => j[entry.index]),
    scaledRight: order.map((entry) => w[entry.index]),
  };
}

function rankCopy(layers: Layers, k: number): Float64Array {
  const cols = layers.scaledRight[0].length;
  const rows = layers.left[0].length;
  const copy = new Float64Array(rows * cols);
  for (let layer = 0; layer < k; layer++) {
    const left = layers.left[layer];
    const right = layers.scaledRight[layer];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) copy[r * cols + c] += left[r] * right[c];
    }
  }
  return copy;
}

function relativeError(values: number[], k: number): number {
  const total = values.reduce((sum, value) => sum + value * value, 0);
  const dropped = values.slice(k).reduce((sum, value) => sum + value * value, 0);
  return Math.sqrt(dropped / total);
}

const channels = (color: string) => [1, 3, 5].map((offset) => parseInt(color.slice(offset, offset + 2), 16));

function PictureCanvas({ pixels, rows, cols }: { pixels: Float64Array; rows: number; cols: number }) {
  const canvas = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const context = canvas.current?.getContext("2d");
    if (!context) return;
    const dark = channels(palette.background);
    const light = channels(palette.text);
    const image = context.createImageData(cols, rows);
    pixels.forEach((value, index) => {
      const level = Math.min(1, Math.max(0, value));
      dark.forEach((channel, c) => (image.data[4 * index + c] = channel + level * (light[c] - channel)));
      image.data[4 * index + 3] = 255;
    });
    context.putImageData(image, 0, 0);
  }, [pixels, rows, cols]);
  return <canvas ref={canvas} width={cols} height={rows} role="img" aria-label="The picture rebuilt from its first k layers" className="block h-auto w-full rounded-media [image-rendering:pixelated]" />;
}

function SingularBars({ values, kept }: { values: number[]; kept: number }) {
  const shown = values.slice(0, BARS_SHOWN);
  const width = 300;
  const height = 110;
  const step = width / shown.length;
  const tall = (value: number) => Math.max(2, ((Math.log10(value) + 1) / 3) * height);
  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="block h-auto w-full" aria-hidden>
      {shown.map((value, index) => (
        <rect
          key={index}
          x={index * step + step * 0.15}
          y={height - tall(value)}
          width={step * 0.7}
          height={tall(value)}
          fill={index < kept ? "var(--palette-teal)" : "var(--palette-text-muted)"}
          fillOpacity={index < kept ? 0.95 : 0.35}
          className="transition-[fill-opacity] duration-200"
        />
      ))}
    </svg>
  );
}

const smallestRankWithin = (values: number[], tolerance: number) => values.findIndex((_, k) => k > 0 && relativeError(values, k) <= tolerance);

/** Slide k to rebuild a picture from its first k singular layers. The goal is the smallest k within a tolerance. */
export function RankCopyBudget({ tolerance = 0.05 }: { tolerance?: number }) {
  const layers = useMemo(() => pictureLayers(landscape(PICTURE_ROWS, PICTURE_COLS)), []);
  const [k, setK] = useState(1);
  const pixels = useMemo(() => rankCopy(layers, k), [layers, k]);
  const best = useMemo(() => smallestRankWithin(layers.values, tolerance), [layers, tolerance]);
  const { settled, gesture } = useSettled(k);
  const solved = settled === best;
  const error = relativeError(layers.values, k);
  const percent = formatNumber(tolerance * 100, 1);
  const stored = k * (PICTURE_ROWS + PICTURE_COLS + 1);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Find the smallest <Tex>k</Tex> whose copy is within {percent}% of the original picture.</>}
        success={<>Rank <Tex>{String(best)}</Tex> is the smallest copy within {percent}%. It stores <Tex>{`${best}(90 + 135 + 1) = ${(best * (PICTURE_ROWS + PICTURE_COLS + 1)).toLocaleString("en-US").replace(",", "{,}")}`}</Tex> numbers instead of <Tex>{"12{,}150"}</Tex>.</>}
      />
      <Workbench
        plane={
          <div className={`rounded-media p-1 transition-shadow duration-300 ${solved ? "shadow-[0_0_0_2px_var(--palette-teal)]" : ""}`}>
            <PictureCanvas pixels={pixels} rows={PICTURE_ROWS} cols={PICTURE_COLS} />
          </div>
        }
        readout={
          <>
            <Slider label="k" value={k} onChange={setK} min={1} max={BARS_SHOWN} step={1} color="var(--palette-teal)" />
            <SingularBars values={layers.values} kept={k} />
            <Readout tex={`\\text{error} = \\textcolor{${error <= tolerance ? palette.teal : palette.glow}}{${formatNumber(error * 100, 1)}\\%}`} />
            <Readout tex={`\\text{stored} = ${stored.toLocaleString("en-US").replace(",", "{,}")}`} />
          </>
        }
      />
    </Panel>
  );
}

const dot2 = (a: Vec, b: Vec) => a[0] * b[0] + a[1] * b[1];
const perpendicularTo = (v: Vec): Vec => [-v[1], v[0]];

/** Aim a pair of perpendicular unit inputs; the goal is the turn where their outputs are perpendicular too. */
export function PerpendicularPairHunt({ matrix, start = [1, 0] }: { matrix: Matrix2; start?: Vec }) {
  const [aim, setAim] = useState<Vec>(start);
  const first = unitOf(aim);
  const second = perpendicularTo(first);
  const outputs: Vec[] = [apply(matrix, first), apply(matrix, second)];
  const overlap = dot2(outputs[0], outputs[1]);
  const { settled: solved, gesture } = useSettled(Math.abs(overlap) < 1e-9);
  const moveAim = (point: Vec) => {
    if (point[0] !== 0 || point[1] !== 0) setAim(point);
  };

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The two inputs always meet at a right angle. Turn them until their outputs <Tex>{"A\\mathbf x"}</Tex> and <Tex>{"A\\mathbf y"}</Tex> meet at a right angle too.</>}
        success={<>These inputs are the right singular vectors <Tex>{"\\mathbf v_1"}</Tex> and <Tex>{"\\mathbf v_2"}</Tex> (up to sign and order). Their outputs are the two axes of the ellipse, with lengths <Tex>{`${texNumber(singularValues(matrix)[0])}`}</Tex> and <Tex>{`${texNumber(singularValues(matrix)[1])}`}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={SVD_BOUNDS} label={`Perpendicular unit inputs ${describeVector(first)} and ${describeVector(second)}, and their outputs ${describeVector(outputs[0])} and ${describeVector(outputs[1])}. Drag the aiming handle or use the arrow keys.`}>
            <CircleImage m={IDENTITY} color="muted" dashed />
            <CircleImage m={matrix} color="teal" fill={0.1} />
            <Segment from={[0, 0]} to={aim} color="text" />
            <Arrow to={outputs[0]} color="yellow" />
            <Arrow to={outputs[1]} color="blue" />
            <Arrow to={first} color="yellow" width={2} />
            <Arrow to={second} color="blue" width={2} />
            <Label at={outputs[0]} color="yellow">Ax</Label>
            <Label at={outputs[1]} color="blue">Ay</Label>
            <Handle at={aim} onMove={moveAim} color="yellow" label={`Aiming handle at ${describeVector(aim)}; x points toward it and y is x turned a quarter turn`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\mathbf x\\cdot\\mathbf y = 0`} />
            <Readout tex={`(A\\mathbf x)\\cdot(A\\mathbf y) = \\textcolor{${solved ? palette.teal : palette.glow}}{${texNumber(overlap)}}`} />
          </>
        }
      />
    </Panel>
  );
}

/** A rank-one matrix squashes the circle flat. The goal is a nonzero input that A sends to the origin. */
export function CollapsedDirectionHunt({ matrix, start = [1, 0] }: { matrix: Matrix2; start?: Vec }) {
  const [x, setX] = useState<Vec>(start);
  const image = apply(matrix, x);
  const isZeroVector = (v: Vec) => Math.abs(v[0]) < 1e-9 && Math.abs(v[1]) < 1e-9;
  const { settled: solved, gesture } = useSettled(isZeroVector(image) && !isZeroVector(x));
  const [largest, smallest] = singularValues(matrix);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>This <Tex>A</Tex> flattens the whole circle onto a segment. Find a nonzero input <Tex>{"\\mathbf x"}</Tex> with <Tex>{"A\\mathbf x = \\mathbf 0"}</Tex>.</>}
        success={<>This direction is <Tex>{"\\mathbf v_2"}</Tex>, the one with <Tex>{`\\sigma_2 = 0`}</Tex>, and it spans <Tex>{"\\operatorname{Nul}A"}</Tex>. Only one singular value is nonzero, so the rank is 1.</>}
      />
      <Workbench
        plane={
          <Plane bounds={SVD_BOUNDS} label={`Input x at ${describeVector(x)} and its output A x at ${describeVector(image)}. Drag x or use the arrow keys.`}>
            <CircleImage m={IDENTITY} color="muted" dashed />
            <CircleImage m={matrix} color="teal" />
            <Arrow to={image} color="teal" />
            <Arrow to={x} color="yellow" width={2.5} />
            {solved ? <Segment from={[-4 * x[0], -4 * x[1]]} to={[4 * x[0], 4 * x[1]]} color="glow" /> : null}
            <Label at={x} color="yellow">x</Label>
            <Handle at={x} onMove={setX} color="yellow" label={`Input x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`A${`\\begin{bmatrix} ${texNumber(x[0])} \\\\ ${texNumber(x[1])} \\end{bmatrix}`} = \\begin{bmatrix} ${texNumber(image[0])} \\\\ ${texNumber(image[1])} \\end{bmatrix}`} />
            <Readout tex={`\\sigma_1 = ${texNumber(largest)}, \\quad \\sigma_2 = ${texNumber(smallest)}`} />
          </>
        }
      />
    </Panel>
  );
}
