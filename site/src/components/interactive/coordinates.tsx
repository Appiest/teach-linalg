"use client";

import { useId, useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, nearlyEqual, scale, texNumber, type Vec } from "./math";
import { Arrow, boundsAround, Handle, Label, Marker, Plane, usePlane } from "./plane";
import { polynomialTex } from "./vector-spaces";

/** The weights c with c1·b1 + c2·b2 = x, found with the inverse of [b1 b2]. */
function coordinatesOf(x: Vec, b1: Vec, b2: Vec): Vec {
  const determinant = b1[0] * b2[1] - b2[0] * b1[1];
  return [(x[0] * b2[1] - b2[0] * x[1]) / determinant, (b1[0] * x[1] - x[0] * b1[1]) / determinant];
}

function BasisLine({ through, direction }: { through: Vec; direction: Vec }) {
  const { toSvg, bounds } = usePlane();
  const reach = (bounds.xMax - bounds.xMin + bounds.yMax - bounds.yMin) / Math.hypot(...direction);
  const [x1, y1] = toSvg(add(through, scale(-reach, direction)));
  const [x2, y2] = toSvg(add(through, scale(reach, direction)));
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--palette-purple-gray)" strokeWidth={1.2} strokeOpacity={0.55} />;
}

/** Lines at whole-number multiples of b1 and b2: the address grid a basis lays on the plane. */
function BasisGrid({ b1, b2, reach = 12 }: { b1: Vec; b2: Vec; reach?: number }) {
  const weights = Array.from({ length: 2 * reach + 1 }, (_, i) => i - reach);
  return (
    <g aria-hidden>
      {weights.map((k) => <BasisLine key={`a${k}`} through={scale(k, b1)} direction={b2} />)}
      {weights.map((k) => <BasisLine key={`b${k}`} through={scale(k, b2)} direction={b1} />)}
    </g>
  );
}

const coordinateTex = (c: Vec) =>
  `\\begin{bmatrix} \\textcolor{${palette.i_hat}}{${texNumber(c[0])}} \\\\ \\textcolor{${palette.j_hat}}{${texNumber(c[1])}} \\end{bmatrix}`;

/** Drag x around the plane and read its address on the basis grid; the goal is a point with given B-coordinates. */
export function CoordinateFinder({ b1 = [2, 1], b2 = [-1, 2], target = [-1, 2], start = [3, 4] }: { b1?: Vec; b2?: Vec; target?: Vec; start?: Vec }) {
  const [x, setX] = useState<Vec>(start);
  const coords = coordinatesOf(x, b1, b2);
  const { settled: solved, gesture } = useSettled(nearlyEqual(coords, target));
  const corner = scale(coords[0], b1);
  const goalPoint = add(scale(target[0], b1), scale(target[1], b2));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Move <Tex>{"\\mathbf x"}</Tex> to the point whose coordinates relative to <Tex>{"\\mathcal B"}</Tex> are <Tex>{coordinateTex(target)}</Tex>.</>}
        success={<>Found it. <Tex>{`\\mathbf x = ${texNumber(target[0])}\\,\\mathbf b_1 + ${texNumber(target[1])}\\,\\mathbf b_2 = ${columnTex(goalPoint)}`}</Tex>, so the same point has standard entries <Tex>{`(${texNumber(goalPoint[0])}, ${texNumber(goalPoint[1])})`}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([b1, b2, goalPoint, start])} label="Plane with the basis grid of b1 and b2 and a draggable point x. The dashed path walks c1 steps of b1, then c2 steps of b2.">
            <BasisGrid b1={b1} b2={b2} />
            <Arrow to={corner} color="green" width={2.5} dashed />
            <Arrow from={corner} to={x} color="red" width={2.5} dashed />
            <Arrow to={b1} color="green" />
            <Arrow to={b2} color="red" />
            <Arrow to={x} color="yellow" width={solved ? 5 : 3.5} />
            {solved ? <Marker at={x} color="glow" ring /> : null}
            <Label at={b1} color="green" dx={6} dy={18}>b₁</Label>
            <Label at={b2} color="red" dx={-26}>b₂</Label>
            <Label at={x} color="yellow">x</Label>
            <Handle at={x} onMove={setX} color="yellow" label={`Point x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\mathbf x = ${columnTex(x, palette.yellow)}`} />
            <Readout tex={`[\\mathbf x]_{\\mathcal B} = ${coordinateTex(coords)}`} />
            <p className="text-meta text-text-muted">
              The dashed path walks <Tex>{`c_1 = ${texNumber(coords[0])}`}</Tex> along <Tex>{"\\mathbf b_1"}</Tex>, then <Tex>{`c_2 = ${texNumber(coords[1])}`}</Tex> along <Tex>{"\\mathbf b_2"}</Tex>.
            </p>
          </>
        }
      />
    </Panel>
  );
}

type Coefficients = [number, number, number];

const GRAPH = { tMin: -1.5, tMax: 1.5, yMin: -6, yMax: 12, width: 420, height: 340 };

const toGraph = (t: number, y: number): Vec => [
  ((t - GRAPH.tMin) / (GRAPH.tMax - GRAPH.tMin)) * GRAPH.width,
  ((GRAPH.yMax - y) / (GRAPH.yMax - GRAPH.yMin)) * GRAPH.height,
];

const evaluate = (coeffs: Coefficients, t: number) => coeffs[0] + coeffs[1] * t + coeffs[2] * t * t;

function curvePath(coeffs: Coefficients): string {
  const steps = 90;
  return Array.from({ length: steps + 1 }, (_, i) => {
    const t = GRAPH.tMin + ((GRAPH.tMax - GRAPH.tMin) * i) / steps;
    const [x, y] = toGraph(t, evaluate(coeffs, t));
    return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
}

function GraphLines() {
  const [originX, originY] = toGraph(0, 0);
  const levels = [-4, 0, 4, 8];
  return (
    <g aria-hidden>
      {levels.map((y) => {
        const [, py] = toGraph(0, y);
        return <line key={y} x1={0} x2={GRAPH.width} y1={py} y2={py} stroke={y === 0 ? "var(--palette-axis)" : "var(--palette-grid)"} strokeOpacity={y === 0 ? 0.9 : 0.4} strokeWidth={y === 0 ? 1.6 : 1} />;
      })}
      {[-1, 1].map((t) => {
        const [px] = toGraph(t, 0);
        return <line key={t} x1={px} x2={px} y1={0} y2={GRAPH.height} stroke="var(--palette-grid)" strokeOpacity={0.4} strokeWidth={1} />;
      })}
      <line x1={originX} x2={originX} y1={0} y2={GRAPH.height} stroke="var(--palette-axis)" strokeOpacity={0.9} strokeWidth={1.6} />
      {levels.filter((y) => y !== 0).map((y) => (
        <text key={`l${y}`} x={originX + 5} y={toGraph(0, y)[1] - 4} fill="var(--palette-text-muted)" fontSize={13}>{y}</text>
      ))}
      <text x={GRAPH.width - 14} y={originY - 8} fill="var(--palette-text-muted)" fontSize={15} fontStyle="italic" fontFamily="KaTeX_Math, serif">t</text>
    </g>
  );
}

function Curve({ coeffs, color, width = 3.5, dashed = false }: { coeffs: Coefficients; color: Hue; width?: number; dashed?: boolean }) {
  return <path d={curvePath(coeffs)} fill="none" stroke={hue(color)} strokeWidth={width} strokeLinecap="round" strokeDasharray={dashed ? "7 7" : undefined} />;
}

function CurveGraph({ label, children }: { label: string; children: React.ReactNode }) {
  const clipId = `${useId().replaceAll(":", "")}-clip`;
  return (
    <svg viewBox={`0 0 ${GRAPH.width} ${GRAPH.height}`} role="img" aria-label={label} className="block h-auto w-full select-none rounded-media bg-surface-sunken">
      <defs>
        <clipPath id={clipId}>
          <rect width={GRAPH.width} height={GRAPH.height} />
        </clipPath>
      </defs>
      <GraphLines />
      <g clipPath={`url(#${clipId})`}>{children}</g>
    </svg>
  );
}

const WEIGHT_COLORS = [palette.i_hat, palette.j_hat, palette.blue];

function combine(weights: Coefficients, basis: Coefficients[]): Coefficients {
  return [0, 1, 2].map((power) => basis.reduce((total, element, index) => total + weights[index] * element[power], 0)) as Coefficients;
}

const sameCoefficients = (p: Coefficients, q: Coefficients) => p.every((value, index) => Math.abs(value - q[index]) < 1e-9);

function weightedTerm(name: string, index: number): string {
  const weight = `\\textcolor{${WEIGHT_COLORS[index]}}{c_${index + 1}}`;
  return name === "1" ? weight : `${weight}\\,${name}`;
}

/** The weighted basis split over two lines so it fits beside the graph. */
function weightedBasisTex(names: string[]): string {
  const terms = names.map(weightedTerm);
  return `\\begin{aligned} &${terms.slice(0, 2).join(" + ")} \\\\ &+ ${terms.slice(2).join(" + ")} \\end{aligned}`;
}

/** Three sliders weight a non-standard basis of P2; the learner matches a target polynomial and reads off its coordinates. */
export function PolynomialCoordinates({ basis, names, target }: { basis: Coefficients[]; names: string[]; target: Coefficients }) {
  const [weights, setWeights] = useState<Coefficients>([0, 0, 0]);
  const result = combine(weights, basis);
  const { settled: solved, gesture } = useSettled(sameCoefficients(result, target));
  const setWeight = (index: number) => (value: number) => setWeights((current) => current.map((old, i) => (i === index ? value : old)) as Coefficients);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Choose the weights so the teal curve lands on the dashed target <Tex>{`\\mathbf p(t) = ${polynomialTex(target)}`}</Tex>.</>}
        success={<>Exactly. <Tex>{`[\\mathbf p]_{\\mathcal B} = ${columnTex(weights)}`}</Tex>, which is not the coefficient column <Tex>{columnTex(target)}</Tex>. Coordinates depend on the basis.</>}
      />
      <Workbench
        plane={
          <CurveGraph label={`Graph of the target p and of the weighted sum, which is currently ${polynomialTex(result)}`}>
            <Curve coeffs={target} color={solved ? "teal" : "text"} width={2.5} dashed />
            <Curve coeffs={result} color="teal" width={solved ? 5 : 3.5} />
          </CurveGraph>
        }
        readout={
          <>
            {names.map((name, index) => (
              <Slider key={name} label={`c_${index + 1}`} value={weights[index]} onChange={setWeight(index)} min={-8} max={8} step={1} color={WEIGHT_COLORS[index]} />
            ))}
            <Readout tex={`${weightedBasisTex(names)}`} />
            <Readout tex={`= \\textcolor{${palette.teal}}{${polynomialTex(result)}}`} />
          </>
        }
      />
    </Panel>
  );
}
