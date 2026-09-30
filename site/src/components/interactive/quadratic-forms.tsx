"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { formatNumber, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, Handle, Marker, Plane, usePlane, type Bounds } from "./plane";

const TOLERANCE = 1e-9;

const formAt = (m: Matrix2, x: Vec) => m[0][0] * x[0] * x[0] + 2 * m[0][1] * x[0] * x[1] + m[1][1] * x[1] * x[1];
const bilinear = (m: Matrix2, x: Vec, y: Vec) => x[0] * (m[0][0] * y[0] + m[0][1] * y[1]) + x[1] * (m[1][0] * y[0] + m[1][1] * y[1]);
const unit = (v: Vec): Vec => {
  const size = Math.hypot(v[0], v[1]);
  return [v[0] / size, v[1] / size];
};
const isZero = (v: Vec) => v[0] === 0 && v[1] === 0;
const pointKey = (v: Vec) => `${v[0]},${v[1]}`;
const keyPoint = (key: string): Vec => key.split(",").map(Number) as Vec;

function eigenvaluesOf(m: Matrix2): [number, number] {
  const middle = (m[0][0] + m[1][1]) / 2;
  const spread = Math.sqrt(((m[0][0] - m[1][1]) / 2) ** 2 + m[0][1] * m[1][0]);
  return [middle + spread, middle - spread];
}

const matrixTex = (m: Matrix2) =>
  `\\begin{bmatrix} ${texNumber(m[0][0])} & ${texNumber(m[0][1])} \\\\ ${texNumber(m[1][0])} & ${texNumber(m[1][1])} \\end{bmatrix}`;

function signedTerm(value: number, variable: string, color?: string): string {
  const sign = value < 0 ? "-" : "+";
  const body = `${texNumber(Math.abs(value))}\\,${variable}`;
  return `${sign} ${color ? `\\textcolor{${color}}{${body}}` : body}`;
}

/** Stacks every state in one grid cell and shows one, so the height never changes when the state does. */
function StackedSwap({ states, shown }: { states: { key: string; node: React.ReactNode }[]; shown: string }) {
  return (
    <div className="grid">
      {states.map((state) => (
        <div key={state.key} aria-hidden={state.key !== shown} className={`[grid-area:1/1] ${state.key === shown ? "swap-shown" : "swap-hidden"}`}>
          {state.node}
        </div>
      ))}
    </div>
  );
}

function LevelCurve({ matrix, level }: { matrix: Matrix2; level: number }) {
  const { toSvg } = usePlane();
  const points = Array.from({ length: 181 }, (_, index) => {
    const angle = (2 * Math.PI * index) / 180;
    const direction: Vec = [Math.cos(angle), Math.sin(angle)];
    const radius = Math.sqrt(level / formAt(matrix, direction));
    const [x, y] = toSvg([radius * direction[0], radius * direction[1]]);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  return <polyline points={points.join(" ")} fill="none" stroke={hue("teal")} strokeWidth={3.5} strokeLinejoin="round" />;
}

function AxisLine({ direction, color, bold }: { direction: Vec; color: Hue; bold: boolean }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg([-40 * direction[0], -40 * direction[1]]);
  const [x2, y2] = toSvg([40 * direction[0], 40 * direction[1]]);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={bold ? 5 : 2.5} strokeOpacity={bold ? 1 : 0.75} strokeDasharray={bold ? undefined : "8 6"} />;
}

function turnedFormTex(matrix: Matrix2, axis: Vec): string {
  const first = unit(axis);
  const second: Vec = [-first[1], first[0]];
  const cross = 2 * bilinear(matrix, first, second);
  const crossColor = Math.abs(cross) < TOLERANCE ? palette.teal : palette.glow;
  return `Q = ${texNumber(formAt(matrix, first))}\\,y_1^2 ${signedTerm(Math.abs(cross) < TOLERANCE ? 0 : cross, "y_1y_2", crossColor)} ${signedTerm(formAt(matrix, second), "y_2^2")}`;
}

const TURN_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -4, yMax: 4 };

/** Drag the direction of the new y1 axis; the y2 axis stays perpendicular, and the cross term vanishes on the eigenvectors. */
export function QuadraticAxisTurner({ matrix, level, start = [1, 0] }: { matrix: Matrix2; level: number; start?: Vec }) {
  const [tip, setTip] = useState<Vec>(start);
  const { settled, gesture } = useSettled(pointKey(tip));
  const settledTip = keyPoint(settled);
  const solved = !isZero(settledTip) && Math.abs(bilinear(matrix, unit(settledTip), [-unit(settledTip)[1], unit(settledTip)[0]])) < TOLERANCE;
  const direction = isZero(tip) ? null : unit(tip);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The teal ellipse is <Tex>{`\\mathbf x^TA\\mathbf x = ${level}`}</Tex>. Drag the tip of the yellow <Tex>{"y_1"}</Tex> axis until the cross term <Tex>{"y_1y_2"}</Tex> disappears.</>}
        success={<>The cross term is gone, so these are the principal axes of the ellipse. The two coefficients left over are the eigenvalues of <Tex>{"A"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={TURN_BOUNDS} label={`Ellipse x transpose A x equals ${level}, with new axes turned toward ${describeVector(tip)}. Drag the tip or use the arrow keys.`}>
            <LevelCurve matrix={matrix} level={level} />
            {direction ? <AxisLine direction={direction} color="yellow" bold={solved} /> : null}
            {direction ? <AxisLine direction={[-direction[1], direction[0]]} color="blue" bold={solved} /> : null}
            <Arrow to={tip} color="yellow" />
            {solved ? <Marker at={tip} color="glow" ring /> : null}
            <Handle at={tip} onMove={setTip} color="yellow" label={`Tip of the new y1 axis, at ${describeVector(tip)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`A = ${matrixTex(matrix)}`} />
            <Readout tex={direction ? turnedFormTex(matrix, tip) : "\\text{Pick a nonzero direction}"} />
          </>
        }
      />
    </Panel>
  );
}

const VIEW_AZIMUTH = (-45 * Math.PI) / 180;
const VIEW_ELEVATION = (30 * Math.PI) / 180;
const VIEW_SIZE = 360;
const VIEW_UNIT = 105;
const VIEW_Z = 0.12;
const MESH_RADIUS = 1.3;
const MESH_RINGS = 8;
const MESH_SPOKES = 36;

type Point3 = [number, number, number];

function project(point: Point3): Vec {
  const [x, y, z] = point;
  const across = -x * Math.sin(VIEW_AZIMUTH) + y * Math.cos(VIEW_AZIMUTH);
  const depth = x * Math.cos(VIEW_AZIMUTH) + y * Math.sin(VIEW_AZIMUTH);
  const up = z * Math.cos(VIEW_ELEVATION) - depth * Math.sin(VIEW_ELEVATION);
  return [VIEW_SIZE / 2 + VIEW_UNIT * across, VIEW_SIZE * 0.52 - VIEW_UNIT * up];
}

const towardViewer = (point: Point3) =>
  (point[0] * Math.cos(VIEW_AZIMUTH) + point[1] * Math.sin(VIEW_AZIMUTH)) * Math.cos(VIEW_ELEVATION) + point[2] * Math.sin(VIEW_ELEVATION);

type Cell = { depth: number; height: number; corners: Point3[] };

function meshCells(matrix: Matrix2): Cell[] {
  const lift = (radius: number, angle: number): Point3 => {
    const x: Vec = [radius * Math.cos(angle), radius * Math.sin(angle)];
    return [x[0], x[1], VIEW_Z * formAt(matrix, x)];
  };
  const cells: Cell[] = [];
  for (let ring = 0; ring < MESH_RINGS; ring++) {
    const inner = (MESH_RADIUS * ring) / MESH_RINGS;
    const outer = (MESH_RADIUS * (ring + 1)) / MESH_RINGS;
    for (let spoke = 0; spoke < MESH_SPOKES; spoke++) {
      const from = (2 * Math.PI * spoke) / MESH_SPOKES;
      const to = (2 * Math.PI * (spoke + 1)) / MESH_SPOKES;
      const corners = [lift(inner, from), lift(outer, from), lift(outer, to), lift(inner, to)];
      const depth = corners.reduce((sum, corner) => sum + towardViewer(corner), 0) / 4;
      const height = corners.reduce((sum, corner) => sum + corner[2], 0) / 4;
      cells.push({ depth, height, corners });
    }
  }
  return cells.sort((a, b) => a.depth - b.depth);
}

function FloorLines() {
  const reach = 1.7;
  const lines: [Point3, Point3][] = [
    [[-reach, 0, 0], [reach, 0, 0]],
    [[0, -reach, 0], [0, reach, 0]],
  ];
  return (
    <g aria-hidden>
      {lines.map(([from, to], index) => {
        const [x1, y1] = project(from);
        const [x2, y2] = project(to);
        return <line key={index} x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--palette-axis)" strokeOpacity={0.6} strokeWidth={1.5} />;
      })}
    </g>
  );
}

function Surface({ matrix }: { matrix: Matrix2 }) {
  return (
    <g>
      {meshCells(matrix).map((cell, index) => (
        <polygon
          key={index}
          points={cell.corners.map((corner) => project(corner).map((value) => value.toFixed(1)).join(",")).join(" ")}
          fill={hue(cell.height < -TOLERANCE ? "pink" : "teal")}
          fillOpacity={0.5}
          stroke={hue(cell.height < -TOLERANCE ? "pink" : "teal")}
          strokeOpacity={0.55}
          strokeWidth={0.8}
        />
      ))}
    </g>
  );
}

function definitenessOf(eigenvalues: [number, number]): string {
  const [high, low] = eigenvalues;
  if (low > TOLERANCE) return "positive definite";
  if (high < -TOLERANCE) return "negative definite";
  if (low < -TOLERANCE && high > TOLERANCE) return "indefinite";
  return high > TOLERANCE ? "positive semidefinite" : "negative semidefinite";
}

const KINDS = ["positive definite", "positive semidefinite", "indefinite", "negative semidefinite", "negative definite"];

const METER_BOUNDS: Bounds = { xMin: -4, xMax: 8, yMin: -1, yMax: 1 };

function EigenMeter({ eigenvalues }: { eigenvalues: [number, number] }) {
  return (
    <Plane bounds={METER_BOUNDS} label={`Eigenvalues ${formatNumber(eigenvalues[0])} and ${formatNumber(eigenvalues[1])} on a number line.`}>
      <Marker at={[eigenvalues[0], 0]} color="yellow" />
      <Marker at={[eigenvalues[1], 0]} color="blue" ring={Math.abs(eigenvalues[1]) < TOLERANCE} />
    </Plane>
  );
}

/** Slide the off-diagonal entry b of [[a, b], [b, d]] and watch the graph of x^T A x bend from a bowl through a trough into a saddle. */
export function QuadraticSurfaceShaper({ a, d, start = 0, min = -4, max = 4 }: { a: number; d: number; start?: number; min?: number; max?: number }) {
  const [b, setB] = useState(start);
  const { settled, gesture } = useSettled(b);
  const solved = Math.abs(a * d - settled * settled) < TOLERANCE;
  const matrix: Matrix2 = [[a, b], [b, d]];
  const eigenvalues = eigenvaluesOf(matrix);
  const kind = definitenessOf(eigenvalues);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide <Tex>{"b"}</Tex> until the bowl flattens into a trough, a surface that stays at height <Tex>{"0"}</Tex> along a whole line.</>}
        success={<>Here <Tex>{"\\det A = 0"}</Tex>, so one eigenvalue is <Tex>{"0"}</Tex>. The surface is flat along that eigenvector, and the form is positive semidefinite.</>}
      />
      <Workbench
        plane={
          <svg
            viewBox={`0 0 ${VIEW_SIZE} ${VIEW_SIZE}`}
            role="img"
            aria-label={`Graph of z equals x transpose A x over a disk. The form is ${kind}.`}
            className="block h-auto w-full rounded-media bg-surface-sunken"
          >
            <FloorLines />
            <Surface matrix={matrix} />
          </svg>
        }
        readout={
          <>
            <Slider label="b" value={b} onChange={setB} min={min} max={max} step={0.5} color={palette.glow} />
            <Readout tex={`A = \\begin{bmatrix} ${texNumber(a)} & \\textcolor{${palette.glow}}{${texNumber(b)}} \\\\ \\textcolor{${palette.glow}}{${texNumber(b)}} & ${texNumber(d)} \\end{bmatrix}`} />
            <Readout tex={`\\textcolor{${palette.yellow}}{\\lambda_1 = ${texNumber(eigenvalues[0])}},\\quad \\textcolor{${palette.blue}}{\\lambda_2 = ${texNumber(eigenvalues[1])}}`} />
            <EigenMeter eigenvalues={eigenvalues} />
            <div className="rounded-lg bg-surface-sunken px-4 py-3 text-center text-body" style={{ color: kind === "indefinite" ? palette.pink : palette.teal }}>
              <StackedSwap shown={kind} states={KINDS.map((name) => ({ key: name, node: <span>{name}</span> }))} />
            </div>
          </>
        }
      />
    </Panel>
  );
}

const CIRCLE_BOUNDS: Bounds = { xMin: -3, xMax: 3, yMin: -3, yMax: 3 };
const METER_TOP = 8;

function UnitCircle() {
  const { toSvg, unit: scale } = usePlane();
  const [cx, cy] = toSvg([0, 0]);
  return <circle cx={cx} cy={cy} r={scale} fill="none" stroke="var(--palette-text)" strokeOpacity={0.7} strokeWidth={2} strokeDasharray="5 5" />;
}

function ValueBar({ value, best }: { value: number; best: number }) {
  const width = (share: number) => `${Math.max(0, Math.min(1, share / METER_TOP)) * 100}%`;
  return (
    <div className="relative h-3 w-full overflow-hidden rounded-full bg-surface-sunken" aria-hidden>
      <div className="absolute inset-y-0 left-0 rounded-full bg-[var(--palette-teal)] transition-[width] duration-200" style={{ width: width(value) }} />
      <div className="absolute inset-y-0 w-1 bg-[var(--palette-glow)]" style={{ left: width(best) }} />
    </div>
  );
}

/** Aim a direction; its point on the unit circle gives Q, and the largest Q on the circle is the top eigenvalue. */
export function QuadraticCircleMax({ matrix, start = [1, -1] }: { matrix: Matrix2; start?: Vec }) {
  const [tip, setTip] = useState<Vec>(start);
  const [best, setBest] = useState(isZero(start) ? 0 : formAt(matrix, unit(start)));
  const { settled, gesture } = useSettled(pointKey(tip));
  const top = eigenvaluesOf(matrix)[0];
  const settledTip = keyPoint(settled);
  const solved = !isZero(settledTip) && Math.abs(formAt(matrix, unit(settledTip)) - top) < TOLERANCE;
  const point = isZero(tip) ? null : unit(tip);
  const value = point ? formAt(matrix, point) : 0;
  if (value > best) setBest(value);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Aim the arrow so that the orange point on the unit circle makes <Tex>{`Q(\\mathbf x) = \\mathbf x^T${matrixTex(matrix)}\\mathbf x`}</Tex> as large as it can be.</>}
        success={<>The largest value of <Tex>{"Q"}</Tex> on the unit circle is the biggest eigenvalue of <Tex>{"A"}</Tex>, and the arrow now points along its eigenvector.</>}
      />
      <Workbench
        plane={
          <Plane bounds={CIRCLE_BOUNDS} label={`Unit circle with a direction toward ${describeVector(tip)}. Drag the tip or use the arrow keys.`}>
            <UnitCircle />
            <Arrow to={tip} color="text" width={2.5} />
            {point ? <Marker at={point} color="glow" ring={solved} /> : null}
            <Handle at={tip} onMove={setTip} color="text" label={`Direction tip, at ${describeVector(tip)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={point ? `\\begin{gathered} \\mathbf x = (${texNumber(point[0])},\\ ${texNumber(point[1])}) \\\\ \\textcolor{${palette.teal}}{Q(\\mathbf x) = ${texNumber(value)}} \\end{gathered}` : "\\text{Pick a nonzero direction}"} />
            <ValueBar value={value} best={best} />
            <p className="text-meta text-text-muted">
              Best so far: <Tex>{texNumber(best)}</Tex>
            </p>
          </>
        }
      />
    </Panel>
  );
}

const LEVEL_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -4, yMax: 4 };

function polynomialTex(m: Matrix2, x: Vec): string {
  const cross = 2 * m[0][1];
  return `${texNumber(m[0][0])}(${texNumber(x[0])})^2 ${cross < 0 ? "-" : "+"} ${texNumber(Math.abs(cross))}(${texNumber(x[0])})(${texNumber(x[1])}) + ${texNumber(m[1][1])}(${texNumber(x[1])})^2`;
}

/** Drag a point; the readout evaluates the form there. The goal is another whole-number point on the level curve through a given one. */
export function LevelPointHunt({ matrix, level, known, start = [1, 0] }: { matrix: Matrix2; level: number; known: Vec; start?: Vec }) {
  const [x, setX] = useState<Vec>(start);
  const value = formAt(matrix, x);
  const { settled: solved, gesture } = useSettled(Math.abs(value - level) < TOLERANCE && pointKey(x) !== pointKey(known));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The yellow point <Tex>{`(${known[0]}, ${known[1]})`}</Tex> gives <Tex>{`Q = ${level}`}</Tex>. Find a different grid point where <Tex>Q</Tex> is also <Tex>{`${level}`}</Tex>.</>}
        success={<>This point lies on the same teal curve. The curve is the set of all points where <Tex>{`Q = ${level}`}</Tex>, and the cross term is what tilts it.</>}
      />
      <Workbench
        plane={
          <Plane bounds={LEVEL_BOUNDS} label={`The curve where Q equals ${level}, a known point at ${describeVector(known)}, and a movable point at ${describeVector(x)} where Q is ${formatNumber(value)}. Drag the point or use the arrow keys.`}>
            <LevelCurve matrix={matrix} level={level} />
            <Marker at={known} color="yellow" />
            {solved ? <Marker at={x} color="glow" ring /> : null}
            <Handle at={x} onMove={setX} color="blue" label={`Point x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`A = ${matrixTex(matrix)}`} />
            <Readout tex={`Q = ${polynomialTex(matrix, x)} = \\textcolor{${solved ? palette.teal : palette.text}}{${texNumber(value)}}`} />
          </>
        }
      />
    </Panel>
  );
}

/** The two directions where the form is zero, as slopes x₂/x₁, when the form takes both signs. */
function zeroSlopes(m: Matrix2): number[] {
  const discriminant = m[0][1] ** 2 - m[0][0] * m[1][1];
  if (discriminant <= 0 || m[1][1] === 0) return [];
  const root = Math.sqrt(discriminant);
  return [(-m[0][1] + root) / m[1][1], (-m[0][1] - root) / m[1][1]];
}

/** Drag a point to hunt for a spot where a form with all positive coefficients still comes out negative. */
export function NegativeDirectionHunt({ matrix, start = [1, 1] }: { matrix: Matrix2; start?: Vec }) {
  const [x, setX] = useState<Vec>(start);
  const value = formAt(matrix, x);
  const { settled: solved, gesture } = useSettled(value < -TOLERANCE);
  const arrowColor: Hue = value < -TOLERANCE ? "pink" : "teal";

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Every coefficient of <Tex>Q</Tex> is positive. Find a point where <Tex>Q</Tex> is negative anyway.</>}
        success={<>Between the two dashed lines, <Tex>Q</Tex> is negative, and along them it is exactly zero. A form that takes both signs is indefinite, and its matrix has one negative eigenvalue.</>}
      />
      <Workbench
        plane={
          <Plane bounds={LEVEL_BOUNDS} label={`A movable point at ${describeVector(x)} where Q is ${formatNumber(value)}. Drag the point or use the arrow keys.`}>
            {solved ? zeroSlopes(matrix).map((slope) => <AxisLine key={slope} direction={unit([1, slope])} color="glow" bold={false} />) : null}
            <Arrow to={x} color={arrowColor} />
            <Handle at={x} onMove={setX} color={arrowColor} label={`Point x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`Q = ${polynomialTex(matrix, x)}`} />
            <Readout tex={`Q = \\textcolor{${value < -TOLERANCE ? palette.pink : palette.teal}}{${texNumber(value)}}`} />
          </>
        }
      />
    </Panel>
  );
}
