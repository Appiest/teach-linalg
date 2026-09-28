"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { apply, formatNumber, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, Handle, Label, Plane, usePlane, type Bounds } from "./plane";

const SYMMETRIC_BOUNDS: Bounds = { xMin: -6, xMax: 6, yMin: -5, yMax: 5 };
const BUILDER_BOUNDS: Bounds = { xMin: -7, xMax: 7, yMin: -5, yMax: 5 };

const length = (v: Vec) => Math.hypot(v[0], v[1]);
const unit = (v: Vec): Vec => [v[0] / length(v), v[1] / length(v)];
const turnQuarter = (v: Vec): Vec => [-v[1], v[0]];
const isOrigin = (v: Vec) => v[0] === 0 && v[1] === 0;

const matrixTex = (matrix: Matrix2) =>
  `\\begin{bmatrix} ${matrix[0].map((v) => texNumber(v)).join(" & ")} \\\\ ${matrix[1].map((v) => texNumber(v)).join(" & ")} \\end{bmatrix}`;

function sameMatrix(a: Matrix2, b: Matrix2): boolean {
  return a.every((row, i) => row.every((value, j) => Math.abs(value - b[i][j]) < 1e-6));
}

/** The image of the unit circle under the matrix, as an SVG path. */
function CircleImage({ matrix, color, dashed = false }: { matrix: Matrix2; color: Hue; dashed?: boolean }) {
  const { toSvg } = usePlane();
  const points = Array.from({ length: 121 }, (_, index) => {
    const angle = (index / 120) * 2 * Math.PI;
    return toSvg(apply(matrix, [Math.cos(angle), Math.sin(angle)]));
  });
  const path = points.map(([x, y], index) => `${index === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  return (
    <path
      d={`${path} Z`}
      fill="none"
      stroke={hue(color)}
      strokeWidth={dashed ? 2 : 3}
      strokeOpacity={dashed ? 0.7 : 1}
      strokeDasharray={dashed ? "7 6" : undefined}
    />
  );
}

function UnitCircle() {
  const { toSvg, unit: scale } = usePlane();
  const [x, y] = toSvg([0, 0]);
  return <circle cx={x} cy={y} r={scale} fill="none" stroke="var(--palette-purple-gray, var(--palette-text))" strokeOpacity={0.6} strokeWidth={2} />;
}

function Eigenline({ direction, color }: { direction: Vec; color: Hue }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg([-40 * direction[0], -40 * direction[1]]);
  const [x2, y2] = toSvg([40 * direction[0], 40 * direction[1]]);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={2.5} strokeOpacity={0.8} strokeDasharray="6 6" />;
}

/** The small orange square at the origin that marks two perpendicular directions. */
function RightAngleMark({ first, second, shown }: { first: Vec; second: Vec; shown: boolean }) {
  const { toSvg } = usePlane();
  const size = 0.45;
  const a = unit(first);
  const b = unit(second);
  const corners: Vec[] = [
    [size * a[0], size * a[1]],
    [size * (a[0] + b[0]), size * (a[1] + b[1])],
    [size * b[0], size * b[1]],
  ];
  const path = corners.map((corner, index) => `${index === 0 ? "M" : "L"}${toSvg(corner).join(",")}`).join(" ");
  return (
    <path
      d={path}
      fill="none"
      stroke="var(--palette-glow)"
      strokeWidth={3}
      className={`transition-opacity duration-300 ${shown ? "opacity-100" : "opacity-0"}`}
    />
  );
}

/** Several messages stacked in one grid cell, so switching between them never changes the height. */
function StackedMessages({ messages, shown }: { messages: React.ReactNode[]; shown: number }) {
  return (
    <div className="grid">
      {messages.map((message, index) => (
        <div key={index} aria-hidden={index !== shown} className={`[grid-area:1/1] ${index === shown ? "swap-shown" : "swap-hidden"}`}>
          {message}
        </div>
      ))}
    </div>
  );
}

type Eigenlines = { kind: "none" } | { kind: "one"; direction: Vec } | { kind: "two"; first: Vec; second: Vec; angle: number };

function eigenvectorFor(matrix: Matrix2, lambda: number): Vec {
  const [[a, b], [c, d]] = matrix;
  if (Math.abs(b) > 1e-9) return [b, lambda - a];
  if (Math.abs(c) > 1e-9) return [lambda - d, c];
  return Math.abs(lambda - a) < 1e-9 ? [1, 0] : [0, 1];
}

function angleBetween(first: Vec, second: Vec): number {
  const cosine = Math.abs(first[0] * second[0] + first[1] * second[1]) / (length(first) * length(second));
  return (Math.acos(Math.min(1, cosine)) * 180) / Math.PI;
}

/** The real eigenlines of a 2x2 matrix: none, one, or two with the angle between them. */
function eigenlinesOf(matrix: Matrix2): Eigenlines {
  const [[a, b], [c, d]] = matrix;
  const discriminant = (a - d) ** 2 + 4 * b * c;
  if (discriminant < -1e-9) return { kind: "none" };
  const root = Math.sqrt(Math.max(0, discriminant));
  const first = eigenvectorFor(matrix, (a + d + root) / 2);
  if (root < 1e-9) return { kind: "one", direction: first };
  const second = eigenvectorFor(matrix, (a + d - root) / 2);
  return { kind: "two", first, second, angle: angleBetween(first, second) };
}

const offDiagonalTex = (value: number) => `\\textcolor{${palette.glow}}{${texNumber(value)}}`;

function EigenlineDrawing({ lines, perpendicular }: { lines: Eigenlines; perpendicular: boolean }) {
  if (lines.kind === "none") return null;
  if (lines.kind === "one") return <Eigenline direction={lines.direction} color="yellow" />;
  return (
    <>
      <Eigenline direction={lines.first} color="yellow" />
      <Eigenline direction={lines.second} color="blue" />
      <RightAngleMark first={lines.first} second={lines.second} shown={perpendicular} />
    </>
  );
}

function eigenlineStatus(lines: Eigenlines): number {
  if (lines.kind === "none") return 0;
  if (lines.kind === "one") return 1;
  return 2;
}

/** Slide the two off-diagonal entries; the eigenlines only meet at a right angle when the matrix is symmetric. */
export function SymmetricPerpendicularHunt({ diagonal = [3, 1], start = [2, 0] }: { diagonal?: [number, number]; start?: [number, number] }) {
  const [upper, setUpper] = useState(start[0]);
  const [lower, setLower] = useState(start[1]);
  const { settled, gesture } = useSettled(`${upper},${lower}`);
  const [settledUpper, settledLower] = settled.split(",").map(Number);
  const matrix: Matrix2 = [[diagonal[0], upper], [lower, diagonal[1]]];
  const lines = eigenlinesOf(matrix);
  const settledLines = eigenlinesOf([[diagonal[0], settledUpper], [settledLower, diagonal[1]]]);
  const solved = settledLines.kind === "two" && Math.abs(settledLines.angle - 90) < 1e-6;
  const current = settled === `${upper},${lower}`;
  const angle = lines.kind === "two" ? lines.angle : 0;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide the two orange entries until the yellow and blue eigenlines meet at a right angle.</>}
        success={<>The eigenlines are perpendicular exactly when the orange entries match, which is when <Tex>{"A^T = A"}</Tex>. The ellipse&rsquo;s axes then lie right on them.</>}
      />
      <Workbench
        plane={
          <Plane bounds={SYMMETRIC_BOUNDS} label={`The unit circle and its image under A, with the eigenlines of A. The top right entry is ${formatNumber(upper)} and the bottom left entry is ${formatNumber(lower)}.`}>
            <UnitCircle />
            <EigenlineDrawing lines={lines} perpendicular={solved && current} />
            <CircleImage matrix={matrix} color="teal" />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`A = \\begin{bmatrix} ${texNumber(diagonal[0])} & ${offDiagonalTex(upper)} \\\\ ${offDiagonalTex(lower)} & ${texNumber(diagonal[1])} \\end{bmatrix}`} />
            <div className="space-y-3">
              <Slider label="a_{12}" value={upper} onChange={setUpper} min={-3} max={3} step={1} color={palette.glow} />
              <Slider label="a_{21}" value={lower} onChange={setLower} min={-3} max={3} step={1} color={palette.glow} />
            </div>
            <div className="rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
              <StackedMessages
                shown={eigenlineStatus(lines)}
                messages={[
                  <>This <Tex>{"A"}</Tex> has no real eigenvalues, so it turns every line through the origin.</>,
                  <>This <Tex>{"A"}</Tex> has a repeated eigenvalue and only one eigenline.</>,
                  <>The eigenlines meet at <span className="tabular-nums">{formatNumber(angle, 1)}°</span>.</>,
                ]}
              />
            </div>
          </>
        }
      />
    </Panel>
  );
}

function spectralSum(direction: Vec, stretches: [number, number]): Matrix2 {
  const first = unit(direction);
  const second = turnQuarter(first);
  const entry = (i: number, j: number) => stretches[0] * first[i] * first[j] + stretches[1] * second[i] * second[j];
  return [
    [entry(0, 0), entry(0, 1)],
    [entry(1, 0), entry(1, 1)],
  ];
}

/** Choose an eigen-direction and two stretches; the sum λ1 u1u1ᵀ + λ2 u2u2ᵀ must rebuild the target matrix. */
export function SpectralEllipseBuilder({ target, start = [1, 0], stretches = [3, 1] }: { target: Matrix2; start?: Vec; stretches?: [number, number] }) {
  const [direction, setDirection] = useState<Vec>(start);
  const [first, setFirst] = useState(stretches[0]);
  const [second, setSecond] = useState(stretches[1]);
  const moveDirection = (next: Vec) => setDirection((previous) => (isOrigin(next) ? previous : next));
  const key = `${direction[0]},${direction[1]},${first},${second}`;
  const { settled, gesture } = useSettled(key);
  const [dx, dy, settledFirst, settledSecond] = settled.split(",").map(Number);
  const solved = sameMatrix(spectralSum([dx, dy], [settledFirst, settledSecond]), target);
  const built = spectralSum(direction, [first, second]);
  const u1 = unit(direction);
  const u2 = turnQuarter(u1);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the yellow handle to aim <Tex>{"\\mathbf u_1"}</Tex>, then set both stretches so the teal ellipse lands on the dashed one.</>}
        success={<>You rebuilt <Tex>{`A = ${matrixTex(target)}`}</Tex> from one eigen-direction and two eigenvalues. Every choice you tried was symmetric, because a sum of <Tex>{"\\lambda\\,\\mathbf u\\mathbf u^T"}</Tex> always is.</>}
      />
      <Workbench
        plane={
          <Plane bounds={BUILDER_BOUNDS} label={`Eigen-direction u1 through ${describeVector(direction)}, stretches ${formatNumber(first)} and ${formatNumber(second)}. The teal ellipse is the image of the unit circle; the dashed ellipse is the target. Drag the handle or use the arrow keys.`}>
            <UnitCircle />
            <Eigenline direction={u1} color="yellow" />
            <Eigenline direction={u2} color="blue" />
            <CircleImage matrix={target} color="text" dashed />
            <CircleImage matrix={built} color="teal" />
            <Arrow to={[first * u1[0], first * u1[1]]} color="yellow" />
            <Arrow to={[second * u2[0], second * u2[1]]} color="blue" />
            <RightAngleMark first={u1} second={u2} shown />
            <Label at={direction} color="yellow" dx={16} dy={-18}>u₁</Label>
            <Handle at={direction} onMove={moveDirection} color="yellow" label={`Point on the u1 line, at ${describeVector(direction)}`} />
          </Plane>
        }
        readout={
          <>
            <div className="space-y-3">
              <Slider label="\lambda_1" value={first} onChange={setFirst} min={0} max={6} step={1} color={palette.yellow} />
              <Slider label="\lambda_2" value={second} onChange={setSecond} min={0} max={6} step={1} color={palette.blue} />
            </div>
            <Readout tex={`\\begin{aligned} &\\textcolor{${palette.yellow}}{\\lambda_1\\mathbf u_1\\mathbf u_1^T} + \\textcolor{${palette.blue}}{\\lambda_2\\mathbf u_2\\mathbf u_2^T} \\\\ &= \\textcolor{${palette.teal}}{${matrixTex(built)}} \\end{aligned}`} />
            <Readout tex={`\\text{target } A = ${matrixTex(target)}`} />
          </>
        }
      />
    </Panel>
  );
}
