"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, apply, det, nearlyEqual, scale, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, boundsAround, DEFAULT_BOUNDS, Handle, Label, Marker, Plane, Segment, usePlane, type Bounds } from "./plane";
import type { Hue } from "./colors";
import { hue } from "./colors";

const cross = (first: Vec, second: Vec) => first[0] * second[1] - first[1] * second[0];

/** The parallelogram of two columns: its own hue when the orientation is positive, pink when it flips. */
function ColumnShape({ first, second, color, opacity = 0.24 }: { first: Vec; second: Vec; color: Hue; opacity?: number }) {
  const { toSvg } = usePlane();
  const corners: Vec[] = [[0, 0], first, add(first, second), second];
  const fill = cross(first, second) < 0 ? hue("pink") : hue(color);
  return <polygon points={corners.map((corner) => toSvg(corner).join(",")).join(" ")} fill={fill} fillOpacity={opacity} />;
}

function DashedOutline({ corners, color }: { corners: Vec[]; color: Hue }) {
  const { toSvg } = usePlane();
  return <polygon points={corners.map((corner) => toSvg(corner).join(",")).join(" ")} fill="none" stroke={hue(color)} strokeWidth={2} strokeDasharray="5 5" />;
}

function HeightBar({ x, from, to, color }: { x: number; from: number; to: number; color: Hue }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg([x, from]);
  const [, y2] = toSvg([x, to]);
  return <line x1={x1} y1={y1} x2={x1} y2={y2} stroke={hue(color)} strokeWidth={9} strokeLinecap="butt" />;
}

const colored = (color: string, tex: string) => `\\textcolor{${color}}{${tex}}`;
const detTex = (first: string, second: string) => `\\det[\\,${first}\\;\\;${second}\\,]`;

/** Fix a1 along the base and drag x until its determinant with a1 matches det[a1 u] + det[a1 v]. */
export function HeightStack({ base = 3, u = [1, 1], v = [-2, 2], start = [2, 1] }: { base?: number; u?: Vec; v?: Vec; start?: Vec }) {
  const [x, setX] = useState<Vec>(start);
  const a1: Vec = [base, 0];
  const goal = base * (u[1] + v[1]);
  const current = base * x[1];
  const { settled: solved, gesture } = useSettled(Math.abs(current - goal) < 1e-6);
  const barX = Math.max(base, u[0], v[0]) + 1.5;
  const a1Tex = colored(palette.i_hat, "\\mathbf a_1");

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf x"}</Tex> so that <Tex>{`${detTex(a1Tex, "\\mathbf x")} = ${detTex(a1Tex, colored(palette.yellow, "\\mathbf u"))} + ${detTex(a1Tex, colored(palette.blue, "\\mathbf v"))}`}</Tex>.</>}
        success={<>Any <Tex>{"\\mathbf x"}</Tex> at height {texNumber(u[1] + v[1])} works, including <Tex>{"\\mathbf u + \\mathbf v"}</Tex>. Only the height above <Tex>{a1Tex}</Tex> counts, and the heights of <Tex>{"\\mathbf u"}</Tex> and <Tex>{"\\mathbf v"}</Tex> stack.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([a1, u, v, add(u, v), [barX + 1, 0]])} label="A fixed green base a1 with ghost vectors u and v and a draggable teal vector x. Bars on the right compare the heights of u, v and x.">
            <ColumnShape first={a1} second={x} color="teal" />
            <Arrow to={u} color="yellow" dashed />
            <Arrow to={v} color="blue" dashed />
            <Arrow to={a1} color="green" />
            <Arrow to={x} color="teal" width={solved ? 5 : 3.5} />
            <HeightBar x={barX} from={0} to={u[1]} color="yellow" />
            <HeightBar x={barX} from={u[1]} to={u[1] + v[1]} color="blue" />
            <HeightBar x={barX + 0.7} from={0} to={x[1]} color="teal" />
            {solved ? <Marker at={[barX + 0.7, x[1]]} color="glow" ring /> : null}
            <Label at={a1} color="green" dx={-6} dy={22}>a₁</Label>
            <Label at={u} color="yellow">u</Label>
            <Label at={v} color="blue" dx={-18}>v</Label>
            <Label at={x} color="teal">x</Label>
            <Handle at={x} onMove={setX} color="teal" label={`Vector x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`${detTex(a1Tex, colored(palette.yellow, "\\mathbf u"))} = ${texNumber(base * u[1])}`} />
            <Readout tex={`${detTex(a1Tex, colored(palette.blue, "\\mathbf v"))} = ${texNumber(base * v[1])}`} />
            <Readout tex={`${detTex(a1Tex, colored(palette.teal, "\\mathbf x"))} = ${texNumber(base)} \\cdot ${texNumber(x[1])} = ${texNumber(current)}`} />
          </>
        }
      />
    </Panel>
  );
}

const UNIT_SQUARE: Vec[] = [[0, 0], [1, 0], [1, 1], [0, 1]];

const matrixTex = (m: Matrix2, colors?: [string, string]) => {
  const cell = (row: number, column: number) => (colors ? colored(colors[column], texNumber(m[row][column])) : texNumber(m[row][column]));
  return `\\begin{bmatrix} ${cell(0, 0)} & ${cell(0, 1)} \\\\ ${cell(1, 0)} & ${cell(1, 1)} \\end{bmatrix}`;
};

const fromColumns = (first: Vec, second: Vec): Matrix2 => [[first[0], second[0]], [first[1], second[1]]];

/** A is fixed; drag the columns of B and watch B's area and then AB's area, which is det A times as large. */
export function ProductAreaHunt({ a = [[2, 1], [-1, 1]], target = -6 }: { a?: Matrix2; target?: number }) {
  const [first, setFirst] = useState<Vec>([1, 0]);
  const [second, setSecond] = useState<Vec>([0, 1]);
  const b = fromColumns(first, second);
  const imageCorners = UNIT_SQUARE.map((corner) => apply(a, apply(b, corner)));
  const product = det(a) * det(b);
  const { settled: solved, gesture } = useSettled(Math.abs(product - target) < 1e-6);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the columns of <Tex>{"B"}</Tex> until <Tex>{`\\det(AB) = ${texNumber(target)}`}</Tex>.</>}
        success={<>You need <Tex>{`\\det B = ${texNumber(target / det(a))}`}</Tex>. Then <Tex>{"B"}</Tex> flips the square and <Tex>{"A"}</Tex> multiplies its area by {texNumber(det(a))}, so <Tex>{`\\det(AB) = ${texNumber(det(a))} \\cdot (${texNumber(det(b))}) = ${texNumber(product)}`}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([[6, 2], [-2, -3]])} label="The unit square, its image under B in yellow and its image under AB in teal. Drag the green and red columns of B.">
            <DashedOutline corners={UNIT_SQUARE} color="text" />
            <ProductImage corners={imageCorners} flipped={product < 0} />
            <ColumnShape first={first} second={second} color="yellow" opacity={0.3} />
            <Arrow to={first} color="green" />
            <Arrow to={second} color="red" />
            {solved ? <Marker at={imageCorners[2]} color="glow" ring /> : null}
            <Handle at={first} onMove={setFirst} color="green" label={`First column of B, at ${describeVector(first)}`} />
            <Handle at={second} onMove={setSecond} color="red" label={`Second column of B, at ${describeVector(second)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`B = ${matrixTex(b, [palette.i_hat, palette.j_hat])}`} />
            <Readout tex={`\\det A = ${texNumber(det(a))}, \\quad \\det B = ${texNumber(det(b))}`} />
            <Readout tex={`\\det(AB) = ${texNumber(det(a))} \\cdot (${texNumber(det(b))}) = ${colored(product < 0 ? palette.pink : palette.teal, texNumber(product))}`} />
          </>
        }
      />
    </Panel>
  );
}

function ProductImage({ corners, flipped }: { corners: Vec[]; flipped: boolean }) {
  const { toSvg } = usePlane();
  const color = flipped ? hue("pink") : hue("teal");
  return <polygon points={corners.map((corner) => toSvg(corner).join(",")).join(" ")} fill={color} fillOpacity={0.3} stroke={color} strokeWidth={2} />;
}

/** Drag b and read x from two parallelogram areas: det[b a2] / det A and det[a1 b] / det A. */
export function CramerAreas({ a1 = [2, 1], a2 = [-1, 2], target = [-1, 2], start = [3, 4] }: { a1?: Vec; a2?: Vec; target?: Vec; start?: Vec }) {
  const [b, setB] = useState<Vec>(start);
  const detA = cross(a1, a2);
  const areas: Vec = [cross(b, a2), cross(a1, b)];
  const x: Vec = [areas[0] / detA, areas[1] / detA];
  const { settled: solved, gesture } = useSettled(nearlyEqual(x, target));
  const goalPoint = add(scale(target[0], a1), scale(target[1], a2));
  const bTex = colored(palette.yellow, "\\mathbf b");

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{bTex}</Tex> so that the solution of <Tex>{`A\\mathbf x = ${bTex}`}</Tex> is <Tex>{`\\mathbf x = (${texNumber(target[0])}, ${texNumber(target[1])})`}</Tex>.</>}
        success={<>Now <Tex>{`${bTex} = ${texNumber(target[0])}\\,\\mathbf a_1 + ${texNumber(target[1])}\\,\\mathbf a_2`}</Tex>. The two areas are <Tex>{`${texNumber(areas[0])}`}</Tex> and <Tex>{`${texNumber(areas[1])}`}</Tex>, and dividing each by <Tex>{`\\det A = ${texNumber(detA)}`}</Tex> gives the entries of <Tex>{"\\mathbf x"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([a1, a2, goalPoint, start, add(start, a2), add(a1, start)])} label="Columns a1 in green and a2 in red, with a draggable yellow vector b. The parallelogram of b and a2 is shaded yellow and the parallelogram of a1 and b teal; pink means a negative area.">
            <ColumnShape first={b} second={a2} color="yellow" opacity={0.22} />
            <ColumnShape first={a1} second={b} color="teal" opacity={0.22} />
            <Segment from={b} to={add(b, a2)} color="yellow" />
            <Segment from={b} to={add(a1, b)} color="teal" />
            <Arrow to={a1} color="green" />
            <Arrow to={a2} color="red" />
            <Arrow to={b} color="yellow" width={solved ? 5 : 3.5} />
            {solved ? <Marker at={b} color="glow" ring /> : null}
            <Label at={a1} color="green" dx={4} dy={20}>a₁</Label>
            <Label at={a2} color="red" dx={-26}>a₂</Label>
            <Label at={b} color="yellow">b</Label>
            <Handle at={b} onMove={setB} color="yellow" label={`Vector b, at ${describeVector(b)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\det A = ${texNumber(detA)}`} />
            <Readout tex={`${texNumber(detA)}\\,x_1 = \\det[\\,${bTex}\\;\\;\\mathbf a_2\\,] = ${texNumber(areas[0])}`} />
            <Readout tex={`${texNumber(detA)}\\,x_2 = \\det[\\,\\mathbf a_1\\;\\;${bTex}\\,] = ${texNumber(areas[1])}`} />
            <Readout tex={`\\mathbf x = (${texNumber(x[0])},\\ ${texNumber(x[1])})`} />
          </>
        }
      />
    </Panel>
  );
}

/** The part of the line n·p = r that crosses the window, walking along whichever axis the line is less steep against. */
function lineAcross(normal: Vec, r: number, bounds: Bounds): [Vec, Vec] {
  if (Math.abs(normal[1]) >= Math.abs(normal[0])) {
    const yAt = (x: number) => (r - normal[0] * x) / normal[1];
    return [[bounds.xMin, yAt(bounds.xMin)], [bounds.xMax, yAt(bounds.xMax)]];
  }
  const xAt = (y: number) => (r - normal[1] * y) / normal[0];
  return [[xAt(bounds.yMin), bounds.yMin], [xAt(bounds.yMax), bounds.yMax]];
}

function EquationLine({ normal, r, color }: { normal: Vec; r: number; color: Hue }) {
  const { bounds } = usePlane();
  if (normal[0] === 0 && normal[1] === 0) return null;
  const [from, to] = lineAcross(normal, r, bounds);
  return <Segment from={from} to={to} color={color} dashed={false} />;
}

function equationTex(first: number, second: number, r: number, color: string): string {
  const sign = second < 0 ? "-" : "+";
  return colored(color, `${texNumber(first)}\\,x_1 ${sign} ${texNumber(Math.abs(second))}\\,x_2 = ${texNumber(r)}`);
}

function cramerSolutionTex(s: number, off: number, rhs: Vec): string {
  const detA = s * s - off * off;
  if (detA === 0) return `\\mathbf x: \\text{ none}`;
  const x1 = (rhs[0] * s - off * rhs[1]) / detA;
  const x2 = (s * rhs[1] - off * rhs[0]) / detA;
  return `\\mathbf x = (${texNumber(x1)},\\ ${texNumber(x2)})`;
}

/** Slide the parameter s in the system s x1 + off x2 = r1, off x1 + s x2 = r2 and find where Cramer's rule has no answer. */
export function CramerParameterLines({ off = 2, rhs = [3, 1] }: { off?: number; rhs?: Vec }) {
  const [s, setS] = useState(0);
  const detA = s * s - off * off;
  const { settled: solved, gesture } = useSettled(detA === 0);
  const meets = detA !== 0;
  const point: Vec = meets ? [(rhs[0] * s - off * rhs[1]) / detA, (s * rhs[1] - off * rhs[0]) / detA] : [0, 0];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide <Tex>{"s"}</Tex> to find a value where Cramer&apos;s rule breaks down.</>}
        success={<>At <Tex>{`s = \\pm ${texNumber(off)}`}</Tex> the determinant <Tex>{`s^2 - ${texNumber(off * off)}`}</Tex> is <Tex>{"0"}</Tex>. The two lines are parallel and never meet, so there is no solution for Cramer&apos;s formula to give.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DEFAULT_BOUNDS} label={`The lines of the two equations with s = ${s}. ${meets ? "They cross at one point." : "They are parallel."}`}>
            <EquationLine normal={[s, off]} r={rhs[0]} color="yellow" />
            <EquationLine normal={[off, s]} r={rhs[1]} color="blue" />
            {meets ? <Marker at={point} color="teal" /> : null}
          </Plane>
        }
        readout={
          <>
            <Slider label="s" value={s} onChange={setS} min={-4} max={4} step={0.5} color={palette.glow} />
            <Readout tex={equationTex(s, off, rhs[0], palette.yellow)} />
            <Readout tex={equationTex(off, s, rhs[1], palette.blue)} />
            <Readout tex={`\\det A = s^2 - ${texNumber(off * off)} = ${texNumber(detA)}`} />
            <Readout tex={cramerSolutionTex(s, off, rhs)} />
          </>
        }
      />
    </Panel>
  );
}

function StretchedShapes({ corner, solved }: { corner: Vec; solved: boolean }) {
  const { toSvg, unit } = usePlane();
  const [cx, cy] = toSvg([0, 0]);
  const [a, b] = corner;
  const fill = solved ? hue("teal") : hue("yellow");
  const rectangle: Vec[] = [[0, 0], [a, 0], [a, b], [0, b]];
  return (
    <g>
      <circle cx={cx} cy={cy} r={unit} fill="none" stroke={hue("text")} strokeOpacity={0.6} strokeWidth={2} strokeDasharray="5 5" />
      <ellipse cx={cx} cy={cy} rx={Math.abs(a) * unit} ry={Math.abs(b) * unit} fill={fill} fillOpacity={0.18} stroke={fill} strokeWidth={2} />
      <polygon points={rectangle.map((point) => toSvg(point).join(",")).join(" ")} fill={fill} fillOpacity={0.3} />
      <DashedOutline corners={UNIT_SQUARE} color="text" />
    </g>
  );
}

/** Drag the corner (a, b) of the stretch diag(a, b): the unit square and the unit disk both grow by |ab|. */
export function EllipseAreaStretch({ target = 6 }: { target?: number }) {
  const [corner, setCorner] = useState<Vec>([1, 1]);
  const factor = Math.abs(corner[0] * corner[1]);
  const { settled: solved, gesture } = useSettled(factor === target);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the corner to set <Tex>{"A = \\begin{bmatrix} a & 0 \\\\ 0 & b \\end{bmatrix}"}</Tex> so that the ellipse has area <Tex>{`${texNumber(target)}\\pi`}</Tex>.</>}
        success={<>Any <Tex>{"a"}</Tex> and <Tex>{"b"}</Tex> with <Tex>{`|ab| = ${texNumber(target)}`}</Tex> work. The square grew from <Tex>{"1"}</Tex> to <Tex>{texNumber(target)}</Tex> and the disk from <Tex>{"\\pi"}</Tex> to <Tex>{`${texNumber(target)}\\pi`}</Tex>, because <Tex>{"A"}</Tex> scales every area by <Tex>{"|\\det A|"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DEFAULT_BOUNDS} label={`The dashed unit disk and unit square, and their images under the stretch with a = ${corner[0]} and b = ${corner[1]}.`}>
            <StretchedShapes corner={corner} solved={solved} />
            <Handle at={corner} onMove={setCorner} color="glow" label={`Corner of the stretched square, at ${describeVector(corner)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\det A = ${texNumber(corner[0])} \\cdot ${texNumber(corner[1])} = ${texNumber(corner[0] * corner[1])}`} />
            <Readout tex={`\\text{square: } 1 \\to ${texNumber(factor)}`} />
            <Readout tex={`\\text{disk: } \\pi \\to ${texNumber(factor)}\\pi`} />
          </>
        }
      />
    </Panel>
  );
}
