"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { formatNumber, texNumber, type Vec } from "./math";
import { Arrow, boundsAround, Handle, Label, Marker, Plane, Segment, usePlane } from "./plane";

type Line = { intercept: number; slope: number };

const FIT_BOUNDS = { xMin: -2, xMax: 3, yMin: -1, yMax: 4 };
const PROJECTION_BOUNDS = { xMin: -2, xMax: 3, yMin: -1, yMax: 3 };

/** The line through the two handle heights, read as y = intercept + slope · x. */
function lineThrough(left: Vec, right: Vec): Line {
  const slope = (right[1] - left[1]) / (right[0] - left[0]);
  return { intercept: left[1] - slope * left[0], slope };
}

const predict = (line: Line, x: number) => line.intercept + line.slope * x;

const squaredError = (points: Vec[], line: Line) =>
  points.reduce((total, [x, y]) => total + (y - predict(line, x)) ** 2, 0);

/** The least-squares line from the normal equations for y = β₀ + β₁x. */
function bestLine(points: Vec[]): Line {
  const n = points.length;
  const sumX = points.reduce((total, [x]) => total + x, 0);
  const sumY = points.reduce((total, [, y]) => total + y, 0);
  const sumXX = points.reduce((total, [x]) => total + x * x, 0);
  const sumXY = points.reduce((total, [x, y]) => total + x * y, 0);
  const determinant = n * sumXX - sumX * sumX;
  return { intercept: (sumXX * sumY - sumX * sumXY) / determinant, slope: (n * sumXY - sumX * sumY) / determinant };
}

function WideLine({ line, color, width }: { line: Line; color: Hue; width: number }) {
  const { toSvg, bounds } = usePlane();
  const [x1, y1] = toSvg([bounds.xMin, predict(line, bounds.xMin)]);
  const [x2, y2] = toSvg([bounds.xMax, predict(line, bounds.xMax)]);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={width} strokeLinecap="round" className="transition-[stroke-width] duration-300" />;
}

/** The square on one residual, drawn to the right of the point so its area is the squared miss. */
function ResidualSquare({ point, line, color }: { point: Vec; line: Line; color: Hue }) {
  const { toSvg } = usePlane();
  const predicted = predict(line, point[0]);
  const side = Math.abs(point[1] - predicted);
  const [left, top] = toSvg([point[0], Math.max(point[1], predicted)]);
  const [right, bottom] = toSvg([point[0] + side, Math.min(point[1], predicted)]);
  return (
    <g>
      <rect x={left} y={top} width={right - left} height={bottom - top} fill={hue(color)} fillOpacity={0.22} className="transition-[fill] duration-300" />
      <line x1={left} y1={top} x2={left} y2={bottom} stroke={hue("pink")} strokeWidth={3} />
    </g>
  );
}

const slopeTex = (size: number) => (Math.abs(size - 1) < 1e-9 ? "x" : `${texNumber(size)}\\,x`);

const lineTex = (line: Line) => {
  if (Math.abs(line.slope) < 1e-9) return `y = ${texNumber(line.intercept)}`;
  const sign = line.slope < 0 ? "-" : "+";
  return `y = ${texNumber(line.intercept)} ${sign} ${slopeTex(Math.abs(line.slope))}`;
};

/** Drag two handles to pick a line; the pink squares on the residuals show the total the line is trying to shrink. */
export function ResidualSquaresFit({ points, handleXs = [-2, 3], start = [1, 1] }: { points: Vec[]; handleXs?: [number, number]; start?: [number, number] }) {
  const [heights, setHeights] = useState<[number, number]>(start);
  const left: Vec = [handleXs[0], heights[0]];
  const right: Vec = [handleXs[1], heights[1]];
  const line = lineThrough(left, right);
  const best = bestLine(points);
  const total = squaredError(points, line);
  const { settled: solved, gesture } = useSettled(Math.abs(total - squaredError(points, best)) < 1e-9);
  const bounds = boundsAround([...points, [handleXs[0], -1], [handleXs[1], 5]], FIT_BOUNDS);
  const squareColor: Hue = solved ? "teal" : "pink";

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the two teal handles to move the line. Make the total pink area, the sum of the squared residuals, as small as it can be.</>}
        success={<>This is the least-squares line <Tex>{lineTex(best)}</Tex>. Its squares add up to <Tex>{texNumber(squaredError(points, best))}</Tex>, and every other line gives a bigger total.</>}
      />
      <Workbench
        plane={
          <Plane bounds={bounds} label={`${points.length} data points and the line ${formatNumber(line.intercept)} plus ${formatNumber(line.slope)} x. The squared residuals add up to ${formatNumber(total)}.`}>
            {points.map((point) => (
              <ResidualSquare key={point.join(",")} point={point} line={line} color={squareColor} />
            ))}
            <WideLine line={line} color="teal" width={solved ? 5 : 3.5} />
            {points.map((point) => (
              <Marker key={point.join(",")} at={point} color="yellow" />
            ))}
            <Handle at={left} color="teal" step={0.5} label="Left end of the line. Up and down arrows move it." onMove={(point) => setHeights([point[1], heights[1]])} />
            <Handle at={right} color="teal" step={0.5} label="Right end of the line. Up and down arrows move it." onMove={(point) => setHeights([heights[0], point[1]])} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\textcolor{${palette.teal}}{${lineTex(line)}}`} />
            <Readout tex={`\\textcolor{${palette.pink}}{r_1^2 + \\dots + r_${points.length}^2 = ${texNumber(total, 3)}}`} />
          </>
        }
      />
    </Panel>
  );
}

/** The orange corner that marks a right angle at `foot` between directions `first` and `second`. */
function RightAngle({ foot, first, second, size = 0.4 }: { foot: Vec; first: Vec; second: Vec; size?: number }) {
  const { toSvg } = usePlane();
  const unit = (v: Vec): Vec => [v[0] / Math.hypot(...v), v[1] / Math.hypot(...v)];
  const [u, w] = [unit(first), unit(second)];
  const corners: Vec[] = [
    [foot[0] + size * u[0], foot[1] + size * u[1]],
    [foot[0] + size * (u[0] + w[0]), foot[1] + size * (u[1] + w[1])],
    [foot[0] + size * w[0], foot[1] + size * w[1]],
  ];
  const path = corners.map((corner, index) => `${index === 0 ? "M" : "L"}${toSvg(corner).join(",")}`).join(" ");
  return <path d={path} fill="none" stroke={hue("glow")} strokeWidth={2.5} />;
}

function SpanLine({ direction }: { direction: Vec }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg([-40 * direction[0], -40 * direction[1]]);
  const [x2, y2] = toSvg([40 * direction[0], 40 * direction[1]]);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue("teal")} strokeWidth={2} strokeOpacity={0.4} />;
}

/** Slide the weight x; the residual b − xa is shortest exactly when it meets Col A at a right angle. */
export function ProjectionRightAngle({ column, b, start = 2.5, min = -1, max = 3, step = 0.25 }: {
  column: Vec; b: Vec; start?: number; min?: number; max?: number; step?: number;
}) {
  const [weight, setWeight] = useState(start);
  const best = (column[0] * b[0] + column[1] * b[1]) / (column[0] ** 2 + column[1] ** 2);
  const { settled: solved, gesture } = useSettled(Math.abs(weight - best) < 1e-9);
  const image: Vec = [weight * column[0], weight * column[1]];
  const residual: Vec = [b[0] - image[0], b[1] - image[1]];
  const distance = Math.hypot(...residual);
  const dot = column[0] * residual[0] + column[1] * residual[1];
  const bounds = boundsAround([b, [max * column[0], max * column[1]], [min * column[0], min * column[1]]], PROJECTION_BOUNDS);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide <Tex>{"x"}</Tex> until <Tex>{"A x"}</Tex> on the teal line is as close to <Tex>{"\\mathbf b"}</Tex> as it can get.</>}
        success={<>At <Tex>{`\\hat x = ${texNumber(best)}`}</Tex> the pink residual meets the line at a right angle, so <Tex>{"\\mathbf a^T(\\mathbf b - A\\hat x) = 0"}</Tex>. That is the normal equation for this one-column <Tex>{"A"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={bounds} label={`Col A is the line through ${column.join(", ")}. A x sits at ${formatNumber(image[0])}, ${formatNumber(image[1])}, and its distance to b is ${formatNumber(distance)}.`}>
            <SpanLine direction={column} />
            <Arrow to={column} color="green" />
            <Label at={column} color="green" dx={8} dy={24}>a</Label>
            <Arrow to={b} color="yellow" />
            <Label at={b} color="yellow">b</Label>
            <Arrow to={image} color="teal" width={4.5} />
            <Segment from={image} to={b} color="pink" dashed={false} />
            {solved ? <RightAngle foot={image} first={residual} second={[-column[0], -column[1]]} /> : null}
            <Marker at={image} color="teal" />
          </Plane>
        }
        readout={
          <>
            <Slider label="x" value={weight} onChange={setWeight} min={min} max={max} step={step} color={palette.teal} />
            <Readout tex={`\\textcolor{${palette.pink}}{\\|\\mathbf b - A x\\| = ${texNumber(distance, 3)}}`} />
            <Readout tex={`\\mathbf a^T(\\mathbf b - A x) = ${texNumber(dot)}`} />
          </>
        }
      />
    </Panel>
  );
}

const BALANCE_BOUNDS = { xMin: -1, xMax: 4, yMin: -1, yMax: 5 };

function ResidualSticks({ points, predictAt }: { points: Vec[]; predictAt: (x: number) => number }) {
  return (
    <>
      {points.map((point) => (
        <Segment key={point.join(",")} from={point} to={[point[0], predictAt(point[0])]} color="pink" dashed={false} />
      ))}
    </>
  );
}

const columnOf = (entries: number[], color?: string) => {
  const body = `\\begin{bmatrix} ${entries.map((entry) => texNumber(entry)).join(" \\\\ ")} \\end{bmatrix}`;
  return color ? `\\textcolor{${color}}{${body}}` : body;
};

const zeroColor = (value: number) => (Math.abs(value) < 1e-9 ? palette.teal : palette.glow);

/** Two sliders set the line; the readouts are the dot products of the residual vector with the two columns of X. */
export function ResidualBalance({ points, start = [0, 0] }: { points: Vec[]; start?: [number, number] }) {
  const [beta0, setBeta0] = useState(start[0]);
  const [beta1, setBeta1] = useState(start[1]);
  const line = { intercept: beta0, slope: beta1 };
  const residuals = points.map(([x, y]) => y - predict(line, x));
  const withOnes = residuals.reduce((total, r) => total + r, 0);
  const withXs = residuals.reduce((total, r, index) => total + r * points[index][0], 0);
  const { settled: solved, gesture } = useSettled(Math.abs(withOnes) < 1e-9 && Math.abs(withXs) < 1e-9);
  const best = bestLine(points);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Move the line until the residual vector is perpendicular to both columns of <Tex>X</Tex>, so both dot products read <Tex>0</Tex>.</>}
        success={<>Both dot products are zero, which is the normal equations <Tex>{"X^T(\\mathbf y - X\\boldsymbol\\beta) = \\mathbf 0"}</Tex>. The line is <Tex>{lineTex(best)}</Tex>, the least-squares line.</>}
      />
      <Workbench
        plane={
          <Plane bounds={BALANCE_BOUNDS} label={`${points.length} data points, the line ${formatNumber(beta0)} plus ${formatNumber(beta1)} x, and pink residual sticks.`}>
            <WideLine line={line} color="teal" width={solved ? 5 : 3.5} />
            <ResidualSticks points={points} predictAt={(x) => predict(line, x)} />
            {points.map((point) => (
              <Marker key={point.join(",")} at={point} color="yellow" />
            ))}
          </Plane>
        }
        readout={
          <>
            <Slider label="\beta_0" value={beta0} onChange={setBeta0} min={-2} max={3} step={0.5} color={palette.i_hat} />
            <Slider label="\beta_1" value={beta1} onChange={setBeta1} min={-2} max={3} step={0.5} color={palette.j_hat} />
            <Readout tex={`\\mathbf y - X\\boldsymbol\\beta = ${columnOf(residuals, palette.pink)}`} />
            <Readout tex={`${columnOf(points.map(() => 1), palette.i_hat)}\\cdot\\textcolor{${palette.pink}}{\\mathbf r} = \\textcolor{${zeroColor(withOnes)}}{${texNumber(withOnes)}}`} />
            <Readout tex={`${columnOf(points.map(([x]) => x), palette.j_hat)}\\cdot\\textcolor{${palette.pink}}{\\mathbf r} = \\textcolor{${zeroColor(withXs)}}{${texNumber(withXs)}}`} />
          </>
        }
      />
    </Panel>
  );
}

type Coefficients = [number, number, number];

const PARABOLA_BOUNDS = { xMin: -2, xMax: 3, yMin: -1, yMax: 6 };
const parabolaAt = ([c0, c1, c2]: Coefficients, x: number) => c0 + c1 * x + c2 * x * x;

function determinant3(m: number[][]): number {
  return m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
}

/** The least-squares parabola from the 3×3 normal equations, solved by Cramer's rule. */
function bestParabola(points: Vec[]): Coefficients {
  const rows = points.map(([x]) => [1, x, x * x]);
  const gram = [0, 1, 2].map((i) => [0, 1, 2].map((j) => rows.reduce((total, row) => total + row[i] * row[j], 0)));
  const right = [0, 1, 2].map((i) => rows.reduce((total, row, k) => total + row[i] * points[k][1], 0));
  const whole = determinant3(gram);
  const swapped = (column: number) => gram.map((row, i) => row.map((entry, j) => (j === column ? right[i] : entry)));
  return [0, 1, 2].map((column) => determinant3(swapped(column)) / whole) as Coefficients;
}

function ParabolaCurve({ coefficients, color, width }: { coefficients: Coefficients; color: Hue; width: number }) {
  const { toSvg } = usePlane();
  const samples = Array.from({ length: 61 }, (_, index) => PARABOLA_BOUNDS.xMin + (index * (PARABOLA_BOUNDS.xMax - PARABOLA_BOUNDS.xMin)) / 60);
  const path = samples.map((x) => toSvg([x, parabolaAt(coefficients, x)]).map((value) => value.toFixed(1)).join(",")).join(" ");
  return <polyline points={path} fill="none" stroke={hue(color)} strokeWidth={width} strokeLinejoin="round" />;
}

const designTex = (points: Vec[]) => `X = \\begin{bmatrix} ${points.map(([x]) => `1 & ${texNumber(x)} & ${texNumber(x * x)}`).join(" \\\\ ")} \\end{bmatrix}`;

/** Three sliders shape a parabola; the fit is still least squares because the model is linear in the three weights. */
export function ParabolaFit({ points }: { points: Vec[] }) {
  const [coefficients, setCoefficients] = useState<Coefficients>([1, 0, 0]);
  const total = points.reduce((sum, [x, y]) => sum + (y - parabolaAt(coefficients, x)) ** 2, 0);
  const best = bestParabola(points);
  const bestTotal = points.reduce((sum, [x, y]) => sum + (y - parabolaAt(best, x)) ** 2, 0);
  const { settled: solved, gesture } = useSettled(Math.abs(total - bestTotal) < 1e-9);
  const set = (index: number) => (value: number) => setCoefficients((current) => current.map((entry, i) => (i === index ? value : entry)) as Coefficients);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Shape the parabola <Tex>{"y = \\beta_0 + \\beta_1 x + \\beta_2 x^2"}</Tex> so the sum of squared residuals is as small as it can be.</>}
        success={<>The best parabola is <Tex>{`y = ${texNumber(best[0])} ${best[1] < 0 ? "-" : "+"} ${texNumber(Math.abs(best[1]))}x + ${texNumber(best[2])}x^2`}</Tex> with total <Tex>{texNumber(bestTotal)}</Tex>. The normal equations <Tex>{"X^TX\\boldsymbol\\beta = X^T\\mathbf y"}</Tex> find it with a third column of <Tex>{"x^2"}</Tex> values in <Tex>X</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={PARABOLA_BOUNDS} label={`${points.length} data points and the parabola with weights ${coefficients.map((entry) => formatNumber(entry)).join(", ")}. The squared residuals add up to ${formatNumber(total)}.`}>
            <ParabolaCurve coefficients={coefficients} color="teal" width={solved ? 5 : 3.5} />
            <ResidualSticks points={points} predictAt={(x) => parabolaAt(coefficients, x)} />
            {points.map((point) => (
              <Marker key={point.join(",")} at={point} color="yellow" />
            ))}
          </Plane>
        }
        readout={
          <>
            <Slider label="\beta_0" value={coefficients[0]} onChange={set(0)} min={-1} max={3} step={0.5} color={palette.teal} />
            <Slider label="\beta_1" value={coefficients[1]} onChange={set(1)} min={-2} max={2} step={0.5} color={palette.teal} />
            <Slider label="\beta_2" value={coefficients[2]} onChange={set(2)} min={-1} max={2} step={0.5} color={palette.teal} />
            <Readout tex={designTex(points)} />
            <Readout tex={`\\textcolor{${palette.pink}}{r_1^2 + \\dots + r_${points.length}^2 = ${texNumber(total, 3)}}`} />
          </>
        }
      />
    </Panel>
  );
}
