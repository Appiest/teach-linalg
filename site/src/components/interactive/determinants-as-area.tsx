"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, det, nearlyEqual, scale, texNumber, type Vec } from "./math";
import { Arrow, Handle, Marker, Plane, Segment, usePlane, type Bounds } from "./plane";

const ORIGIN: Vec = [0, 0];

function Parallelogram({ first, second, at = ORIGIN, solved = false }: { first: Vec; second: Vec; at?: Vec; solved?: boolean }) {
  const { toSvg } = usePlane();
  const corners = [at, add(at, first), add(add(at, first), second), add(at, second)];
  const points = corners.map((corner) => toSvg(corner).join(",")).join(" ");
  const flipped = det([[first[0], second[0]], [first[1], second[1]]]) < 0;
  const fill = flipped ? "var(--palette-pink)" : "var(--palette-yellow)";
  return (
    <polygon
      points={points}
      fill={fill}
      fillOpacity={0.24}
      stroke={solved ? "var(--palette-teal)" : fill}
      strokeWidth={solved ? 3 : 1.5}
      className="transition-[stroke,stroke-width] duration-300"
    />
  );
}

function RightAngle({ shown }: { shown: boolean }) {
  const { toSvg } = usePlane();
  const path = [[0, 0.4], [0.4, 0.4], [0.4, 0]].map((point) => toSvg(point as Vec).join(",")).join(" L ");
  return (
    <path
      d={`M ${path}`}
      fill="none"
      stroke="var(--palette-teal)"
      strokeWidth={2.5}
      className={`transition-opacity duration-300 ${shown ? "opacity-100" : "opacity-0"}`}
    />
  );
}

const SHEAR_BOUNDS: Bounds = { xMin: -5, xMax: 7, yMin: -1, yMax: 4 };

/** Slide the top edge of a parallelogram along a line parallel to its base: the area readout never moves. */
export function AreaShearSlide({ base, height, start }: { base: number; height: number; start: number }) {
  const [lean, setLean] = useState(start);
  const first: Vec = [base, 0];
  const second: Vec = [lean, height];
  const { settled: solved, gesture } = useSettled(lean === 0);
  const area = det([[base, lean], [0, height]]);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide the red tip along the dashed line until the parallelogram becomes a rectangle. Keep an eye on its area as it leans.</>}
        success={<>It is a rectangle now, <Tex>{`${base} \\times ${height}`}</Tex>. The area was <Tex>{texNumber(area)}</Tex> at every lean, because the base and the height never changed.</>}
      />
      <Workbench
        plane={
          <Plane bounds={SHEAR_BOUNDS} label="A parallelogram on a green base. Drag the red tip left or right along the dashed line, or use the arrow keys.">
            <Segment from={[SHEAR_BOUNDS.xMin, height]} to={[SHEAR_BOUNDS.xMax, height]} color="text" />
            <Parallelogram first={first} second={second} solved={solved} />
            <RightAngle shown={solved} />
            <Arrow to={first} color="green" />
            <Arrow to={second} color="red" />
            <Handle at={second} onMove={(point) => setLean(point[0])} color="red" label={`Top corner of the red side, at ${describeVector(second)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\det\\begin{bmatrix} \\textcolor{${palette.i_hat}}{${base}} & \\textcolor{${palette.j_hat}}{${texNumber(lean)}} \\\\ \\textcolor{${palette.i_hat}}{0} & \\textcolor{${palette.j_hat}}{${height}} \\end{bmatrix} = ${texNumber(area)}`} />
            <Readout tex={`\\text{base} \\times \\text{height} = ${base} \\times ${height} = ${base * height}`} />
          </>
        }
      />
    </Panel>
  );
}

const shifted = (corners: Vec[], shift: Vec): Vec[] => corners.map((corner) => add(corner, shift));

type Sides ={ corner: Vec; first: Vec; second: Vec };

/** The corner sitting on the origin and the two sides that leave it, or null when no corner is on the origin. */
function sidesAtOrigin(corners: Vec[]): Sides | null {
  const index = corners.findIndex((corner) => nearlyEqual(corner, ORIGIN));
  if (index < 0) return null;
  const others = corners.filter((_, i) => i !== index);
  const oppositeIndex = others.findIndex((candidate, i) => {
    const rest = others.filter((_, j) => j !== i);
    return nearlyEqual(candidate, add(rest[0], rest[1]));
  });
  const [first, second] = others.filter((_, i) => i !== oppositeIndex);
  return { corner: corners[index], first, second };
}

const sideDet = ({ first, second }: Sides) => det([[first[0], second[0]], [first[1], second[1]]]);

function detTex(sides: Sides | null): string {
  if (!sides) return "\\det\\begin{bmatrix} \\mathbf u & \\mathbf v \\end{bmatrix} = \\ ?";
  const { first, second } = sides;
  const entries = `\\textcolor{${palette.i_hat}}{${texNumber(first[0])}} & \\textcolor{${palette.j_hat}}{${texNumber(second[0])}} \\\\ \\textcolor{${palette.i_hat}}{${texNumber(first[1])}} & \\textcolor{${palette.j_hat}}{${texNumber(second[1])}}`;
  return `\\det\\begin{bmatrix} ${entries} \\end{bmatrix} = ${texNumber(sideDet(sides))}`;
}

const CORNER_BOUNDS: Bounds = { xMin: -6, xMax: 7, yMin: -6, yMax: 7 };

/** Drag a parallelogram until one corner sits on the origin; the two sides leaving that corner become the columns. */
export function CornerToOrigin({ corners }: { corners: Vec[] }) {
  const [anchor, setAnchor] = useState<Vec>(corners[0]);
  const moved = shifted(corners, add(anchor, scale(-1, corners[0])));
  const landedKey = sidesAtOrigin(moved) ? anchor.join(",") : "";
  const { settled: settledKey, gesture } = useSettled(landedKey);
  const sides = settledKey ? sidesAtOrigin(shifted(corners, add(settledKey.split(",").map(Number) as Vec, scale(-1, corners[0])))) : null;
  const solved = sides !== null;
  const resting = solved && settledKey === landedKey;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the parallelogram until one of its corners sits on the origin. Then its two sides at that corner become the columns of a matrix.</>}
        success={<>The sides leaving the origin are the columns <Tex>{"\\textcolor{" + palette.i_hat + "}{\\mathbf u}"}</Tex> and <Tex>{"\\textcolor{" + palette.j_hat + "}{\\mathbf v}"}</Tex>, and the fourth corner is <Tex>{"\\mathbf u + \\mathbf v"}</Tex>. Sliding the shape did not change its area.</>}
      />
      <Workbench
        plane={
          <Plane bounds={CORNER_BOUNDS} label="A parallelogram you can slide around the plane. Drag the orange corner or use the arrow keys.">
            <ParallelogramThrough corners={moved} solved={resting} />
            {resting && sides ? <Arrow to={sides.first} color="green" /> : null}
            {resting && sides ? <Arrow to={sides.second} color="red" /> : null}
            {moved.map((corner, index) => (index === 0 ? null : <Marker key={index} at={corner} color="text" />))}
            <Marker at={ORIGIN} color="teal" ring={!solved} />
            <Handle at={anchor} onMove={setAnchor} color="glow" label={`Corner of the parallelogram, at ${describeVector(anchor)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\textcolor{${palette.glow}}{\\text{corner}} = (${texNumber(anchor[0])}, ${texNumber(anchor[1])})`} />
            <Readout tex={detTex(sides)} />
            <Readout tex={`\\text{area} = ${sides ? texNumber(Math.abs(sideDet(sides))) : "\\ ?"}`} />
          </>
        }
      />
    </Panel>
  );
}

/** A parallelogram drawn from its four corners in any order: the corner opposite the first is the one that is not its neighbour. */
function ParallelogramThrough({ corners, solved }: { corners: Vec[]; solved: boolean }) {
  const [start, ...rest] = corners;
  const oppositeIndex = rest.findIndex((candidate, i) => {
    const others = rest.filter((_, j) => j !== i);
    return nearlyEqual(add(candidate, start), add(others[0], others[1]));
  });
  const [left, right] = rest.filter((_, i) => i !== oppositeIndex);
  return <Parallelogram first={add(left, scale(-1, start))} second={add(right, scale(-1, start))} at={start} solved={solved} />;
}

const columnsDetTex = (first: Vec, second: Vec) =>
  `\\det\\begin{bmatrix} \\textcolor{${palette.i_hat}}{${texNumber(first[0])}} & \\textcolor{${palette.j_hat}}{${texNumber(second[0])}} \\\\ \\textcolor{${palette.i_hat}}{${texNumber(first[1])}} & \\textcolor{${palette.j_hat}}{${texNumber(second[1])}} \\end{bmatrix} = ${texNumber(det([[first[0], second[0]], [first[1], second[1]]]))}`;

const STRETCH_BOUNDS: Bounds = { xMin: -5, xMax: 6, yMin: -9, yMax: 9 };

/** Scale only the second column by k: the parallelogram's signed area follows k times the original determinant. */
export function ColumnStretch({ first = [2, 1], second = [1, 3], target = -10 }: { first?: Vec; second?: Vec; target?: number }) {
  const [k, setK] = useState(1);
  const stretched = scale(k, second);
  const { settled: solved, gesture } = useSettled(Math.abs(det([[first[0], stretched[0]], [first[1], stretched[1]]]) - target) < 1e-9);
  const original = det([[first[0], second[0]], [first[1], second[1]]]);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Scale only the red column by <Tex>k</Tex> until the determinant is <Tex>{texNumber(target)}</Tex>. The original determinant is <Tex>{texNumber(original)}</Tex>.</>}
        success={<>With <Tex>{`k = ${texNumber(target / original)}`}</Tex> the area is <Tex>{`${texNumber(Math.abs(target / original))}`}</Tex> times as big, and the negative sign turned the parallelogram pink because the red side now points the other way.</>}
      />
      <Workbench
        plane={
          <Plane bounds={STRETCH_BOUNDS} label={`Parallelogram on the green column ${describeVector(first)} and the red column ${describeVector(stretched)}`}>
            <Parallelogram first={first} second={stretched} solved={solved} />
            <Arrow to={first} color="green" />
            <Arrow to={stretched} color="red" />
          </Plane>
        }
        readout={
          <>
            <Slider label="k" value={k} onChange={setK} min={-3} max={3} step={0.5} color={palette.j_hat} />
            <Readout tex={columnsDetTex(first, stretched)} />
            <Readout tex={`${texNumber(k)} \\times ${texNumber(original)} = ${texNumber(k * original)}`} />
          </>
        }
      />
    </Panel>
  );
}

const DEGREE = Math.PI / 180;
const onCircle = (radius: number, angle: number): Vec => [
  Math.round(radius * Math.cos(angle * DEGREE) * 100) / 100 + 0,
  Math.round(radius * Math.sin(angle * DEGREE) * 100) / 100 + 0,
];

function TurnArc({ angle, radius }: { angle: number; radius: number }) {
  const { toSvg } = usePlane();
  const sweep = angle > 180 ? angle - 360 : angle;
  const points = Array.from({ length: 25 }, (_, i) => toSvg(onCircle(radius, (sweep * i) / 24)).join(","));
  return <polyline points={points.join(" ")} fill="none" stroke="var(--palette-glow)" strokeWidth={2.5} strokeLinecap="round" />;
}

/** Turn the red column around the circle: the determinant is 4 sin(theta), so its sign says which way the turn from green to red goes. */
export function SignSweep({ target = -2 }: { target?: number }) {
  const [angle, setAngle] = useState(90);
  const first: Vec = [2, 0];
  const second = onCircle(2, angle);
  const exact = 4 * Math.sin(angle * DEGREE);
  const { settled: solved, gesture } = useSettled(Math.abs(exact - target) < 1e-9);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Turn the red column by <Tex>{"\\theta"}</Tex> degrees until <Tex>{`\\det A = ${texNumber(target)}`}</Tex>. The orange arc shows the shorter turn from green to red.</>}
        success={<>The area is <Tex>{texNumber(Math.abs(target))}</Tex> and the sign is negative, so the shorter turn from green to red runs clockwise and the fill is pink. The mirror image of this angle across the vertical axis gives the same determinant.</>}
      />
      <Workbench
        plane={
          <Plane bounds={{ xMin: -3, xMax: 5, yMin: -3, yMax: 3 }} label={`Green column (2, 0) and red column at angle ${angle} degrees`}>
            <Parallelogram first={first} second={second} solved={solved} />
            <TurnArc angle={angle} radius={0.8} />
            <Arrow to={first} color="green" />
            <Arrow to={second} color="red" />
          </Plane>
        }
        readout={
          <>
            <Slider label="\theta" value={angle} onChange={setAngle} min={0} max={345} step={15} color={palette.j_hat} />
            <Readout tex={columnsDetTex(first, second)} />
          </>
        }
      />
    </Panel>
  );
}
