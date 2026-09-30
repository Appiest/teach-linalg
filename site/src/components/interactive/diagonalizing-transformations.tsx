"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, apply, formatNumber, scale, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, Handle, Label, Marker, Plane, Segment, usePlane, type Bounds } from "./plane";

const BASIS_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -4, yMax: 5 };
const ORBIT_BOUNDS: Bounds = { xMin: -2, xMax: 9, yMin: -3, yMax: 6 };
const GRAPH_BOUNDS: Bounds = { xMin: -4, xMax: 4, yMin: -5, yMax: 5 };
const ORBIT_LENGTH = 9;

const pointKey = (point: Vec) => `${point[0]},${point[1]}`;
const keyPoint = (key: string): Vec => key.split(",").map(Number) as Vec;
const isZero = (point: Vec) => point[0] === 0 && point[1] === 0;
const cross = (a: Vec, b: Vec) => a[0] * b[1] - a[1] * b[0];
const nearZero = (value: number) => Math.abs(value) < 1e-9;

/** Coordinates of x in the basis {b1, b2}, found with Cramer's rule. */
function coordinates(b1: Vec, b2: Vec, x: Vec): Vec {
  const area = cross(b1, b2);
  return [cross(x, b2) / area, cross(b1, x) / area];
}

/** [T]_B = P⁻¹AP: column j holds the B-coordinates of A b_j. */
function basisMatrix(matrix: Matrix2, b1: Vec, b2: Vec): Matrix2 {
  const first = coordinates(b1, b2, apply(matrix, b1));
  const second = coordinates(b1, b2, apply(matrix, b2));
  return [
    [first[0], second[0]],
    [first[1], second[1]],
  ];
}

function matrixTex(matrix: Matrix2, offColor?: string): string {
  const entry = (row: number, col: number) => {
    const text = texNumber(matrix[row][col]);
    const off = row !== col && offColor && !nearZero(matrix[row][col]);
    return off ? `\\textcolor{${offColor}}{${text}}` : text;
  };
  return `\\begin{bmatrix} ${entry(0, 0)} & ${entry(0, 1)} \\\\ ${entry(1, 0)} & ${entry(1, 1)} \\end{bmatrix}`;
}

/** The lines k·b1 + t·b2 and k·b2 + t·b1 for integer k, long enough to cross the visible plane. */
function BasisGrid({ b1, b2, color, opacity }: { b1: Vec; b2: Vec; color: Hue; opacity: number }) {
  const { toSvg } = usePlane();
  const reach = 24;
  const lines: [Vec, Vec][] = [];
  for (let k = -reach; k <= reach; k++) {
    for (const [base, direction] of [[scale(k, b1), b2], [scale(k, b2), b1]] as [Vec, Vec][]) {
      lines.push([add(base, scale(-reach, direction)), add(base, scale(reach, direction))]);
    }
  }
  return (
    <g aria-hidden className="transition-opacity duration-300">
      {lines.map(([from, to], index) => {
        const [x1, y1] = toSvg(from);
        const [x2, y2] = toSvg(to);
        return <line key={index} x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeOpacity={opacity} strokeWidth={1.2} />;
      })}
    </g>
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

function isDiagonalBasis(matrix: Matrix2, b1: Vec, b2: Vec): boolean {
  if (nearZero(cross(b1, b2))) return false;
  const inBasis = basisMatrix(matrix, b1, b2);
  return nearZero(inBasis[0][1]) && nearZero(inBasis[1][0]);
}

function basisReadout(matrix: Matrix2, b1: Vec, b2: Vec): string {
  if (nearZero(cross(b1, b2))) return `\\vphantom{\\begin{bmatrix} 0 \\\\ 0 \\end{bmatrix}}\\mathbf b_1, \\mathbf b_2 \\text{ lie on one line}`;
  return `[T]_{\\mathcal B} = ${matrixTex(basisMatrix(matrix, b1, b2), palette.glow)}`;
}

/** Drag both basis vectors; [T]_B = P⁻¹AP updates live, and the goal is a basis that makes it diagonal. */
export function DiagonalBasisHunt({ matrix, start1 = [1, 0], start2 = [0, 1] }: { matrix: Matrix2; start1?: Vec; start2?: Vec }) {
  const [b1, setB1] = useState<Vec>(start1);
  const [b2, setB2] = useState<Vec>(start2);
  const { settled, gesture } = useSettled(`${pointKey(b1)}|${pointKey(b2)}`);
  const [settled1, settled2] = settled.split("|").map(keyPoint);
  const solved = isDiagonalBasis(matrix, settled1, settled2);
  const independent = !nearZero(cross(b1, b2));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf b_1"}</Tex> and <Tex>{"\\mathbf b_2"}</Tex> until both orange entries of <Tex>{"[T]_{\\mathcal B}"}</Tex> become 0.</>}
        success={<>Both basis vectors are eigenvectors, so <Tex>{"A"}</Tex> only stretches along the grid and <Tex>{"[T]_{\\mathcal B}"}</Tex> is diagonal.</>}
      />
      <Workbench
        plane={
          <Plane bounds={BASIS_BOUNDS} label={`Basis vectors b1 at ${describeVector(b1)} and b2 at ${describeVector(b2)}, with their images under A dashed. Drag either tip or use the arrow keys.`}>
            {independent ? <BasisGrid b1={b1} b2={b2} color={solved ? "teal" : "text"} opacity={solved ? 0.45 : 0.22} /> : null}
            <Arrow to={apply(matrix, b1)} color="yellow" dashed />
            <Arrow to={apply(matrix, b2)} color="blue" dashed />
            <Arrow to={b1} color="yellow" />
            <Arrow to={b2} color="blue" />
            <Label at={b1} color="yellow">b₁</Label>
            <Label at={b2} color="blue">b₂</Label>
            <Handle at={b1} onMove={setB1} color="yellow" label={`Tip of b1, at ${describeVector(b1)}`} />
            <Handle at={b2} onMove={setB2} color="blue" label={`Tip of b2, at ${describeVector(b2)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`A = ${matrixTex(matrix)}`} />
            <Readout tex={basisReadout(matrix, b1, b2)} />
            <div className="rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
              Column <Tex>{"j"}</Tex> holds the <Tex>{"\\mathcal B"}</Tex>-coordinates of the dashed arrow <Tex>{"A\\mathbf b_j"}</Tex>. An orange entry is 0 exactly when <Tex>{"A\\mathbf b_j"}</Tex> stays on the line through <Tex>{"\\mathbf b_j"}</Tex>.
            </div>
          </>
        }
      />
    </Panel>
  );
}

function orbitPoints(v1: Vec, v2: Vec, lambdas: [number, number], start: Vec): Vec[] {
  const [c1, c2] = coordinates(v1, v2, start);
  return Array.from({ length: ORBIT_LENGTH }, (_, k) => add(scale(c1 * lambdas[0] ** k, v1), scale(c2 * lambdas[1] ** k, v2)));
}

function OrbitPath({ points }: { points: Vec[] }) {
  return (
    <>
      {points.slice(1).map((point, index) => (
        <Segment key={index} from={points[index]} to={point} color="teal" />
      ))}
    </>
  );
}

function OrbitDots({ points }: { points: Vec[] }) {
  const { toSvg } = usePlane();
  return (
    <g aria-hidden>
      {points.map((point, index) => {
        const [x, y] = toSvg(point);
        return <circle key={index} cx={x} cy={y} r={index === 0 ? 0 : 4} fill={hue("teal")} fillOpacity={0.35 + (0.6 * index) / points.length} />;
      })}
    </g>
  );
}

const lambdaTex = (value: number) => (value === 0.5 ? "\\tfrac12" : texNumber(value));

/** Drag x₀ and watch the orbit x_k = A^k x₀; the v₂ part fades by half each step, so the orbit settles at c₁v₁. */
export function EigenOrbitSettle({ v1, v2, lambdas, target, needed = 2 }: { v1: Vec; v2: Vec; lambdas: [number, number]; target: Vec; needed?: number }) {
  const [start, setStart] = useState<Vec>([1, 2]);
  const [found, setFound] = useState<string[]>([]);
  const { settled, gesture } = useSettled(pointKey(start));
  const settledStart = keyPoint(settled);
  const lands = !isZero(settledStart) && nearZero(coordinates(v1, v2, settledStart)[0] - coordinates(v1, v2, target)[0]);
  if (lands && !found.includes(settled)) setFound([...found, settled]);
  const solved = found.length >= needed;
  const points = orbitPoints(v1, v2, lambdas, start);
  const [c1, c2] = coordinates(v1, v2, start);
  const limit = scale(c1, v1);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf x_0"}</Tex> so its orbit settles on the orange point. Find {needed} different starting points that work.</>}
        success={<>Every start on the line through the target parallel to <Tex>{"\\mathbf v_2"}</Tex> works, because its <Tex>{"\\mathbf v_2"}</Tex> part halves away and its <Tex>{"\\mathbf v_1"}</Tex> part never changes.</>}
      />
      <Workbench
        plane={
          <Plane bounds={ORBIT_BOUNDS} label={`Start x0 at ${describeVector(start)}. Its orbit heads toward ${describeVector(limit)}. The target is ${describeVector(target)}. Drag x0 or use the arrow keys.`}>
            <BasisGrid b1={v1} b2={v2} color="text" opacity={0.16} />
            <Arrow to={v1} color="yellow" />
            <Arrow to={v2} color="blue" />
            <Label at={v1} color="yellow">v₁</Label>
            <Label at={v2} color="blue">v₂</Label>
            <OrbitPath points={points} />
            <OrbitDots points={points} />
            <Marker at={target} color="glow" ring={solved} />
            {found.map((key) => (
              <Marker key={key} at={keyPoint(key)} color="teal" />
            ))}
            <Label at={start} color="teal">x₀</Label>
            <Handle at={start} onMove={setStart} color="teal" label={`Starting point x0, at ${describeVector(start)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`D = \\begin{bmatrix} ${lambdaTex(lambdas[0])} & 0 \\\\ 0 & ${lambdaTex(lambdas[1])} \\end{bmatrix}`} />
            <Readout tex={`[\\mathbf x_0]_{\\mathcal B} = ${columnTex([c1, c2])}`} />
            <Readout tex={`\\mathbf x_k = \\textcolor{${palette.yellow}}{${texNumber(c1)}}\\,\\mathbf v_1 ${c2 < 0 ? "-" : "+"} \\textcolor{${palette.blue}}{${texNumber(Math.abs(c2))}}\\left(${lambdaTex(lambdas[1])}\\right)^{k}\\mathbf v_2`} />
            <div className="rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
              Starts found: <span className="tabular-nums text-[var(--palette-teal)]">{Math.min(found.length, needed)} of {needed}</span>
            </div>
          </>
        }
      />
    </Panel>
  );
}

function polynomialTex(coefficients: Vec): string {
  const [constant, slope] = coefficients;
  if (slope === 0) return texNumber(constant);
  const slopeText = slope === 1 ? "" : slope === -1 ? "-" : texNumber(slope);
  if (constant === 0) return `${slopeText}t`;
  return `${texNumber(constant)} ${slope > 0 ? "+" : "-"} ${Math.abs(slope) === 1 ? "" : texNumber(Math.abs(slope))}t`;
}

function Graph({ coefficients, color, width }: { coefficients: Vec; color: Hue; width: number }) {
  const { toSvg } = usePlane();
  const at = (t: number): Vec => [t, coefficients[0] + coefficients[1] * t];
  const [x1, y1] = toSvg(at(-20));
  const [x2, y2] = toSvg(at(20));
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={width} strokeLinecap="round" />;
}

function stretchOf(image: Vec, p: Vec): number | null {
  if (isZero(p) || !nearZero(cross(p, image))) return null;
  return p[0] !== 0 ? image[0] / p[0] : image[1] / p[1];
}

function directionKey(p: Vec): string {
  const flip = p[0] < 0 || (p[0] === 0 && p[1] < 0) ? -1 : 1;
  const size = Math.abs(p[0]) || Math.abs(p[1]);
  return pointKey([(flip * p[0]) / size, (flip * p[1]) / size]);
}

type Eigenpolynomial = { key: string; coefficients: Vec; stretch: number };

function recordEigenpolynomial(found: Eigenpolynomial[], matrix: Matrix2, p: Vec): Eigenpolynomial[] {
  const stretch = stretchOf(apply(matrix, p), p);
  if (stretch === null) return found;
  const key = directionKey(p);
  return found.some((entry) => entry.key === key) ? found : [...found, { key, coefficients: p, stretch }];
}

/** Choose p(t) = a₀ + a₁t with sliders; T(p) is drawn beside it, and the goal is two polynomials that T only rescales. */
export function EigenPolynomialHunt({ matrix }: { matrix: Matrix2 }) {
  const [p, setP] = useState<Vec>([2, 1]);
  const [found, setFound] = useState<Eigenpolynomial[]>([]);
  const { settled, gesture } = useSettled(pointKey(p));
  const next = recordEigenpolynomial(found, matrix, keyPoint(settled));
  if (next !== found) setFound(next);
  const solved = found.length >= 2;
  const image = apply(matrix, p);
  const stretch = pointKey(p) === settled ? stretchOf(image, p) : null;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Set the coefficients so that <Tex>{"T(p)"}</Tex> is a multiple of <Tex>{"p"}</Tex>. Find two polynomials like that that are not multiples of each other.</>}
        success={<>Both polynomials only get rescaled, so in the basis they form, the matrix of <Tex>{"T"}</Tex> is diagonal.</>}
      />
      <Workbench
        plane={
          <Plane bounds={GRAPH_BOUNDS} label={`Graph of p(t) = ${formatNumber(p[0])} + ${formatNumber(p[1])} t and of T(p)(t) = ${formatNumber(image[0])} + ${formatNumber(image[1])} t.`}>
            <Graph coefficients={image} color="teal" width={stretch === null ? 3 : 4.5} />
            <Graph coefficients={p} color="yellow" width={3} />
            {stretch !== null && p[1] !== 0 ? <Marker at={[-p[0] / p[1], 0]} color="glow" ring /> : null}
          </Plane>
        }
        readout={
          <>
            <Slider label="a_0" value={p[0]} onChange={(value) => setP([value, p[1]])} min={-3} max={3} step={1} color={palette.yellow} />
            <Slider label="a_1" value={p[1]} onChange={(value) => setP([p[0], value])} min={-3} max={3} step={1} color={palette.yellow} />
            <Readout tex={`\\textcolor{${palette.yellow}}{p(t) = ${polynomialTex(p)}}`} />
            <Readout tex={`\\textcolor{${palette.teal}}{T(p)(t) = ${polynomialTex(image)}}`} />
            <div className="rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
              <SwapLine
                showSecond={stretch !== null}
                first={<>Right now <Tex>{"T(p)"}</Tex> is not a multiple of <Tex>{"p"}</Tex>.</>}
                second={<span className="text-[var(--palette-teal)]"><Tex>{`T(p) = ${texNumber(stretch ?? 0)}\\,p`}</Tex>, so <Tex>{"p"}</Tex> is an eigenvector of <Tex>{"T"}</Tex>.</span>}
              />
            </div>
            <div className="rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
              Eigenpolynomials found: <span className="tabular-nums text-[var(--palette-teal)]">{Math.min(found.length, 2)} of 2</span>
            </div>
          </>
        }
      />
    </Panel>
  );
}

const COLUMN_BOUNDS: Bounds = { xMin: -4, xMax: 8, yMin: -4, yMax: 6 };
const pairTex = (pair: Vec) => `(${texNumber(pair[0])}, ${texNumber(pair[1])})`;

/** Sliders for the B-coordinates of A b_j: the weights that rebuild A b_j from b1 and b2 are column j of [T]_B. */
export function BasisColumnBuilder({ matrix, b1, b2, column = 1 }: { matrix: Matrix2; b1: Vec; b2: Vec; column?: 0 | 1 }) {
  const [a, setA] = useState(0);
  const [b, setB] = useState(0);
  const target = apply(matrix, column === 0 ? b1 : b2);
  const partial = scale(a, b1);
  const result = add(partial, scale(b, b2));
  const { settled: solved, gesture } = useSettled(nearZero(result[0] - target[0]) && nearZero(result[1] - target[1]));
  const answer = coordinates(b1, b2, target);
  const name = `\\mathbf b_${column + 1}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Pick weights so that <Tex>{`a\\,\\mathbf b_1 + b\\,\\mathbf b_2`}</Tex> lands on the ringed point <Tex>{`A${name} = ${pairTex(target)}`}</Tex>. Those weights are column {column + 1} of <Tex>{"[T]_{\\mathcal B}"}</Tex>.</>}
        success={<>Column {column + 1} of <Tex>{"[T]_{\\mathcal B}"}</Tex> is <Tex>{pairTex(answer)}</Tex>, the coordinates of <Tex>{`A${name}`}</Tex> on the slanted grid. The standard entries <Tex>{pairTex(target)}</Tex> are a different description of the same arrow.</>}
      />
      <Workbench
        plane={
          <Plane bounds={COLUMN_BOUNDS} label={`Grid of b1 and b2. The combination a b1 + b b2 is at ${describeVector(result)} and the target A b${column + 1} is at ${describeVector(target)}.`}>
            <BasisGrid b1={b1} b2={b2} color="text" opacity={0.18} />
            {solved ? <Marker at={target} color="teal" /> : <Marker at={target} ring />}
            <Arrow to={partial} color="yellow" width={2.5} />
            <Arrow from={partial} to={result} color="blue" width={2.5} />
            <Arrow to={result} color="teal" />
            <Arrow to={b1} color="yellow" />
            <Arrow to={b2} color="blue" />
            <Label at={b1} color="yellow" dx={-26}>b₁</Label>
            <Label at={b2} color="blue" dy={22}>b₂</Label>
          </Plane>
        }
        readout={
          <>
            <Slider label="a" value={a} onChange={setA} min={-3} max={5} step={1} color={palette.yellow} />
            <Slider label="b" value={b} onChange={setB} min={-3} max={3} step={1} color={palette.blue} />
            <Readout tex={`${texNumber(a)}${columnTex(b1, palette.yellow)} + ${texNumber(b)}${columnTex(b2, palette.blue)} = ${columnTex(result, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}

const STANDARD_BOUNDS: Bounds = { xMin: -4, xMax: 5, yMin: -3, yMax: 4 };
const EIGEN_BOUNDS: Bounds = { xMin: -3, xMax: 3, yMin: -3, yMax: 3 };

/** One map in two coordinate systems: drag x on the standard plane and watch [x]_B go to D[x]_B on the eigen plane. */
export function TwoCoordinateMap({ matrix, b1, b2, target }: { matrix: Matrix2; b1: Vec; b2: Vec; target: Vec }) {
  const [x, setX] = useState<Vec>([1, 0]);
  const lambdas: Vec = [basisMatrix(matrix, b1, b2)[0][0], basisMatrix(matrix, b1, b2)[1][1]];
  const image = apply(matrix, x);
  const weights = coordinates(b1, b2, x);
  const imageWeights = coordinates(b1, b2, image);
  const { settled, gesture } = useSettled(pointKey(x));
  const settledImage = coordinates(b1, b2, apply(matrix, keyPoint(settled)));
  const solved = nearZero(settledImage[0] - target[0]) && nearZero(settledImage[1] - target[1]);
  const answerWeights: Vec = [target[0] / lambdas[0], target[1] / lambdas[1]];
  const answerX = add(scale(answerWeights[0], b1), scale(answerWeights[1], b2));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf x"}</Tex> on the left until the eigen-coordinates of <Tex>{"A\\mathbf x"}</Tex>, shown on the right, reach the ring at <Tex>{pairTex(target)}</Tex>.</>}
        success={<>On the left, <Tex>{pairTex(answerX)}</Tex> goes to <Tex>{pairTex(apply(matrix, answerX))}</Tex>. On the right, the same move reads <Tex>{`${pairTex(answerWeights)} \\mapsto ${pairTex(target)}`}</Tex>, which is just <Tex>D</Tex> scaling each coordinate.</>}
      />
      <Workbench
        plane={
          <Plane bounds={STANDARD_BOUNDS} label={`Standard coordinates. x at ${describeVector(x)} and A x at ${describeVector(image)}. Drag the tip of x or use the arrow keys.`}>
            <BasisGrid b1={b1} b2={b2} color="text" opacity={0.18} />
            <Arrow to={b1} color="yellow" width={2.5} />
            <Arrow to={b2} color="blue" width={2.5} />
            <Arrow to={image} color="teal" />
            <Arrow to={x} color="text" />
            <Label at={x} color="text">x</Label>
            <Label at={image} color="teal" dy={22}>Ax</Label>
            <Handle at={x} onMove={setX} color="text" label={`Tip of x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Plane bounds={EIGEN_BOUNDS} label={`Eigen-coordinates. [x]_B at ${describeVector(weights)} and [A x]_B at ${describeVector(imageWeights)}.`}>
              {solved ? <Marker at={target} color="teal" /> : <Marker at={target} ring />}
              <Arrow to={[1, 0]} color="yellow" width={2.5} />
              <Arrow to={[0, 1]} color="blue" width={2.5} />
              <Arrow to={imageWeights} color="teal" />
              <Arrow to={weights} color="text" />
            </Plane>
            <Readout tex={`[\\mathbf x]_{\\mathcal B} = ${columnTex(weights)}`} />
            <Readout tex={`[A\\mathbf x]_{\\mathcal B} = ${columnTex(imageWeights, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}
