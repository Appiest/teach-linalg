"use client";

import { ArrowCounterClockwise } from "@phosphor-icons/react";
import { useEffect, useRef, useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, RichText, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { apply, det, nearlyEqual, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, DEFAULT_BOUNDS, Handle, Label, Marker, Plane, Segment, usePlane } from "./plane";

const IDENTITY: Matrix2 = [[1, 0], [0, 1]];
const E1: Vec = [1, 0];
const E2: Vec = [0, 1];

const multiply = (left: Matrix2, right: Matrix2): Matrix2 => [
  [left[0][0] * right[0][0] + left[0][1] * right[1][0], left[0][0] * right[0][1] + left[0][1] * right[1][1]],
  [left[1][0] * right[0][0] + left[1][1] * right[1][0], left[1][0] * right[0][1] + left[1][1] * right[1][1]],
];

const blend = (from: Matrix2, to: Matrix2, s: number): Matrix2 =>
  from.map((row, i) => row.map((value, j) => value + (to[i][j] - value) * s)) as Matrix2;

const isIdentity = (matrix: Matrix2) => IDENTITY.every((row, i) => row.every((value, j) => Math.abs(matrix[i][j] - value) < 1e-9));

const fromColumns = (first: Vec, second: Vec): Matrix2 => [[first[0], second[0]], [first[1], second[1]]];

function matrixTex(matrix: Matrix2, colors: [string, string] = [palette.text, palette.text]): string {
  const entry = (value: number, column: 0 | 1) => `\\textcolor{${colors[column]}}{${texNumber(value)}}`;
  return `\\begin{bmatrix} ${entry(matrix[0][0], 0)} & ${entry(matrix[0][1], 1)} \\\\ ${entry(matrix[1][0], 0)} & ${entry(matrix[1][1], 1)} \\end{bmatrix}`;
}

function MatrixGrid({ matrix, reach = 14 }: { matrix: Matrix2; reach?: number }) {
  const { toSvg } = usePlane();
  const lines: [Vec, Vec][] = [];
  for (let k = -reach; k <= reach; k++) {
    lines.push([apply(matrix, [k, -reach]), apply(matrix, [k, reach])]);
    lines.push([apply(matrix, [-reach, k]), apply(matrix, [reach, k])]);
  }
  return (
    <g aria-hidden>
      {lines.map(([from, to], index) => {
        const [x1, y1] = toSvg(from);
        const [x2, y2] = toSvg(to);
        return <line key={index} x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--palette-blue)" strokeOpacity={0.5} strokeWidth={1.2} />;
      })}
    </g>
  );
}

function TargetRing({ at, color, hit }: { at: Vec; color: Hue; hit: boolean }) {
  const { toSvg } = usePlane();
  const [x, y] = toSvg(at);
  return (
    <circle
      cx={x}
      cy={y}
      r={hit ? 9 : 13}
      fill={hit ? "var(--palette-teal)" : "none"}
      stroke={hit ? "var(--palette-teal)" : hue(color)}
      strokeWidth={2.5}
      strokeDasharray={hit ? undefined : "4 4"}
      className="transition-[r,fill] duration-300"
    />
  );
}

/** The learner builds A⁻¹ one column at a time: each pink column must be a point that A sends onto î or ĵ. */
export function InverseColumnsHunt({ matrix }: { matrix: Matrix2 }) {
  const [first, setFirst] = useState<Vec>(E1);
  const [second, setSecond] = useState<Vec>(E2);
  const firstImage = apply(matrix, first);
  const secondImage = apply(matrix, second);
  const firstHit = nearlyEqual(firstImage, E1);
  const secondHit = nearlyEqual(secondImage, E2);
  const { settled: solved, gesture } = useSettled(firstHit && secondHit);
  const candidate = fromColumns(first, second);
  const product = multiply(matrix, candidate);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the pink columns of <Tex>C</Tex> until <Tex>A</Tex> sends the first onto <Tex>{"\\hat\\imath"}</Tex> and the second onto <Tex>{"\\hat\\jmath"}</Tex>. Then <Tex>{"AC = I"}</Tex>.</>}
        success={<>You built <Tex>{`A^{-1} = ${matrixTex(candidate)}`}</Tex>. Each of its columns is the point that <Tex>A</Tex> moves onto a basis arrow.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DEFAULT_BOUNDS} label="Two pink columns you can drag, and the green and red arrows showing where A sends them. Drag the pink tips or use arrow keys.">
            <TargetRing at={E1} color="green" hit={solved} />
            <TargetRing at={E2} color="red" hit={solved} />
            <Arrow to={firstImage} color="green" />
            <Arrow to={secondImage} color="red" />
            <Arrow to={first} color="pink" width={2.5} />
            <Arrow to={second} color="pink" width={2.5} />
            <Label at={first} color="pink">c₁</Label>
            <Label at={second} color="pink" dx={-24}>c₂</Label>
            <Handle at={first} onMove={setFirst} color="pink" label={`First column of C, at ${describeVector(first)}. A sends it to ${describeVector(firstImage)}.`} />
            <Handle at={second} onMove={setSecond} color="pink" label={`Second column of C, at ${describeVector(second)}. A sends it to ${describeVector(secondImage)}.`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`A = ${matrixTex(matrix, [palette.i_hat, palette.j_hat])}`} />
            <Readout tex={`C = ${matrixTex(candidate, [palette.pink, palette.pink])}`} />
            <Readout tex={`AC = ${matrixTex(product, [palette.i_hat, palette.j_hat])}`} />
          </>
        }
      />
    </Panel>
  );
}

function inverseTex(matrix: Matrix2): string {
  const determinant = det(matrix);
  if (Math.abs(determinant) < 1e-9) return "A^{-1} \\text{ does not exist}";
  const [[a, b], [c, d]] = matrix;
  const adjugate: Matrix2 = [[d, -b], [-c, a]];
  return `A^{-1} = \\frac{1}{${texNumber(determinant)}}${matrixTex(adjugate)}`;
}

function SpanLine({ direction }: { direction: Vec }) {
  const { toSvg } = usePlane();
  const length = Math.hypot(...direction);
  const reach = 40 / length;
  const [x1, y1] = toSvg([-reach * direction[0], -reach * direction[1]]);
  const [x2, y2] = toSvg([reach * direction[0], reach * direction[1]]);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--palette-teal)" strokeWidth={4} strokeLinecap="round" />;
}

function UnitSquare({ matrix }: { matrix: Matrix2 }) {
  const { toSvg } = usePlane();
  const corners: Vec[] = [[0, 0], [1, 0], [1, 1], [0, 1]];
  const points = corners.map((corner) => toSvg(apply(matrix, corner)).join(",")).join(" ");
  return <polygon points={points} fill="var(--palette-yellow)" fillOpacity={0.22} />;
}

/** Drag the columns of A until ad − bc = 0 and the grid falls onto one line. */
export function SingularHunt({ matrix: start }: { matrix: Matrix2 }) {
  const [matrix, setMatrix] = useState<Matrix2>(start);
  const first: Vec = [matrix[0][0], matrix[1][0]];
  const second: Vec = [matrix[0][1], matrix[1][1]];
  const flattened = Math.abs(det(matrix)) < 1e-9 && !nearlyEqual(first, [0, 0]);
  const { settled: solved, gesture } = useSettled(flattened);
  const setColumn = (column: 0 | 1) => (point: Vec) =>
    setMatrix((current) => current.map((row, i) => row.map((value, j) => (j === column ? point[i] : value))) as Matrix2);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\hat\\imath"}</Tex> and <Tex>{"\\hat\\jmath"}</Tex> until <Tex>{"ad - bc = 0"}</Tex>, keeping the green column away from the origin.</>}
        success={<>The two columns now lie on one line, so <Tex>A</Tex> squashes the whole plane onto it. Many points share each landing spot, and no matrix can send them back.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DEFAULT_BOUNDS} label="Grid transformed by A with its unit square shaded. Drag the green and red column tips or use arrow keys.">
            <MatrixGrid matrix={matrix} />
            <UnitSquare matrix={matrix} />
            {solved ? <SpanLine direction={first} /> : null}
            <Arrow to={first} color="green" />
            <Arrow to={second} color="red" />
            <Handle at={first} onMove={setColumn(0)} color="green" label={`Where i-hat lands, at ${describeVector(first)}`} />
            <Handle at={second} onMove={setColumn(1)} color="red" label={`Where j-hat lands, at ${describeVector(second)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`A = ${matrixTex(matrix, [palette.i_hat, palette.j_hat])}`} />
            <Readout tex={`ad - bc = ${texNumber(det(matrix))}`} />
            <Readout tex={inverseTex(matrix)} />
          </>
        }
      />
    </Panel>
  );
}

type Move = { id: "shear" | "turn"; tex: string; label: string; matrix: Matrix2 };

const SHEAR: Matrix2 = [[1, 1], [0, 1]];
const TURN: Matrix2 = [[0, -1], [1, 0]];
const UNDO_MOVES: Move[] = [
  { id: "shear", tex: "S^{-1}", label: "Undo the shear", matrix: [[1, -1], [0, 1]] },
  { id: "turn", tex: "R^{-1}", label: "Undo the turn", matrix: [[0, 1], [-1, 0]] },
];
const START = multiply(TURN, SHEAR);
const POINT: Vec = [1, 1];
const TWEEN_MS = 520;

const easeOut = (s: number) => 1 - (1 - s) ** 3;

/** Eases the drawn matrix toward `target` so each undo plays as motion instead of a jump. */
function useTweenedMatrix(target: Matrix2): Matrix2 {
  const [shown, setShown] = useState<Matrix2>(target);
  const shownRef = useRef(target);
  useEffect(() => {
    const from = shownRef.current;
    const began = performance.now();
    let frame = 0;
    const step = (now: number) => {
      const s = Math.min(1, (now - began) / TWEEN_MS);
      const next = blend(from, target, easeOut(s));
      shownRef.current = next;
      setShown(next);
      if (s < 1) frame = requestAnimationFrame(step);
    };
    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [target]);
  return shown;
}

function MoveButton({ onClick, disabled, children, label }: { onClick: () => void; disabled?: boolean; children: React.ReactNode; label?: string }) {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      disabled={disabled}
      className="inline-flex items-center gap-2 rounded-lg bg-surface-sunken px-4 py-2 text-meta font-semibold text-text shadow-lift transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-35"
    >
      {children}
    </button>
  );
}

function historyTex(applied: Move[]): string {
  const undone = [...applied].reverse().map((move) => move.tex).join("");
  return `${undone}\\,(RS) = `;
}

/** The grid has been sheared, then turned. The learner undoes the two moves and only the reverse order brings it home. */
export function UndoOrder() {
  const [applied, setApplied] = useState<Move[]>([]);
  const current = applied.reduce<Matrix2>((matrix, move) => multiply(move.matrix, matrix), START);
  const shown = useTweenedMatrix(current);
  const home = isIdentity(current);
  const { settled: solved, gesture } = useSettled(home);
  const point = apply(shown, POINT);
  const finishedWrong = applied.length === UNDO_MOVES.length && !home;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>This grid was sheared by <Tex>S</Tex> and then turned by <Tex>R</Tex>. Undo both moves so the yellow arrow returns to its ring.</>}
        success={<>Home. You undid the turn first and the shear second, so <Tex>{"(RS)^{-1} = S^{-1}R^{-1}"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DEFAULT_BOUNDS} label="A grid that was sheared and then turned, with a yellow arrow and the ring where it started.">
            <MatrixGrid matrix={shown} />
            <Marker at={POINT} color={solved ? "teal" : "yellow"} ring />
            <Arrow to={apply(shown, E1)} color="green" />
            <Arrow to={apply(shown, E2)} color="red" />
            <Arrow to={point} color="yellow" />
          </Plane>
        }
        readout={
          <>
            <div className="flex flex-wrap gap-2">
              {UNDO_MOVES.map((move) => (
                <MoveButton key={move.id} onClick={() => setApplied((list) => [...list, move])} disabled={applied.includes(move)}>
                  {move.label} <Tex>{move.tex}</Tex>
                </MoveButton>
              ))}
              <MoveButton onClick={() => setApplied([])} disabled={applied.length === 0} label="Start over">
                <ArrowCounterClockwise className="size-4" aria-hidden /> Start over
              </MoveButton>
            </div>
            <Readout tex={`${historyTex(applied)}${matrixTex(current, [palette.i_hat, palette.j_hat])}`} />
            <p className={`text-meta text-text-muted ${finishedWrong ? "swap-shown" : "swap-hidden"}`} aria-live="polite">
              <RichText>{"That order leaves the grid skewed. The last move made has to be the first one undone."}</RichText>
            </p>
          </>
        }
      />
    </Panel>
  );
}

const LANDING_BOUNDS = { xMin: -5, xMax: 5, yMin: -4, yMax: 5 };

function allDistinct(points: Vec[]): boolean {
  return points.every((point, i) => points.every((other, j) => i === j || !nearlyEqual(point, other)));
}

function LandingTrail({ from, to }: { from: Vec; to: Vec }) {
  return (
    <>
      <Segment from={from} to={to} color="text" />
      <Marker at={to} color="teal" />
    </>
  );
}

/** A singular matrix sends many inputs to one output: the learner drags three different points onto the same landing spot. */
export function SameLanding({ matrix, target, starts }: { matrix: Matrix2; target: Vec; starts: [Vec, Vec, Vec] }) {
  const [points, setPoints] = useState<Vec[]>(starts);
  const images = points.map((point) => apply(matrix, point));
  const allLand = images.every((image) => nearlyEqual(image, target));
  const { settled: solved, gesture } = useSettled(allLand && allDistinct(points));
  const movePoint = (index: number) => (point: Vec) => setPoints((current) => current.map((old, i) => (i === index ? point : old)));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the three yellow points to three different places so that <Tex>M</Tex> sends every one of them onto the ringed point <Tex>{columnTex(target)}</Tex>.</>}
        success={<>Three different inputs share one output. An inverse would have to send <Tex>{columnTex(target)}</Tex> back to all three at once, so <Tex>M</Tex> has no inverse.</>}
      />
      <Workbench
        plane={
          <Plane bounds={LANDING_BOUNDS} label="Three draggable yellow points, each joined by a dashed line to the teal dot where M sends it, and a ringed target point.">
            <Marker at={target} color={solved ? "teal" : "glow"} ring />
            {points.map((point, i) => (
              <LandingTrail key={i} from={point} to={images[i]} />
            ))}
            {points.map((point, i) => (
              <Handle key={i} at={point} onMove={movePoint(i)} color="yellow" label={`Point x${i + 1}, at ${describeVector(point)}. M sends it to ${describeVector(images[i])}.`} />
            ))}
          </Plane>
        }
        readout={
          <>
            <Readout tex={`M = ${matrixTex(matrix, [palette.i_hat, palette.j_hat])}`} />
            {images.map((image, i) => (
              <Readout key={i} tex={`M\\mathbf x_${i + 1} = ${columnTex(image, palette.teal)}`} />
            ))}
          </>
        }
      />
    </Panel>
  );
}

const SLIDER_BOUNDS = { xMin: -5, xMax: 8, yMin: -1, yMax: 7 };

function Parallelogram({ first, second, flat }: { first: Vec; second: Vec; flat: boolean }) {
  const { toSvg } = usePlane();
  const corners: Vec[] = [[0, 0], first, [first[0] + second[0], first[1] + second[1]], second];
  const points = corners.map((corner) => toSvg(corner).join(",")).join(" ");
  return <polygon points={points} fill={flat ? "var(--palette-teal)" : "var(--palette-yellow)"} fillOpacity={0.22} stroke={flat ? "var(--palette-teal)" : "none"} strokeWidth={3} />;
}

/** One entry of A is a slider; the learner finds the value that makes ad − bc zero and watches the parallelogram go flat. */
export function DeterminantSlider({ second, bottom, start = 0 }: { second: Vec; bottom: number; start?: number }) {
  const [h, setH] = useState(start);
  const first: Vec = [h, bottom];
  const determinant = h * second[1] - second[0] * bottom;
  const { settled: solved, gesture } = useSettled(Math.abs(determinant) < 1e-9);
  const answer = (second[0] * bottom) / second[1];
  const entry = `\\textcolor{${palette.glow}}{${texNumber(h)}}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide <Tex>h</Tex> until the parallelogram built from the two columns has no area left.</>}
        success={<>At <Tex>{`h = ${texNumber(answer)}`}</Tex> the green column lies on the same line as the red one, so <Tex>{"ad - bc = 0"}</Tex> and the matrix is singular.</>}
      />
      <Workbench
        plane={
          <Plane bounds={SLIDER_BOUNDS} label="The two columns of the matrix, green and red, and the shaded parallelogram they span. Use the slider for h.">
            <Parallelogram first={first} second={second} flat={solved} />
            <Arrow to={first} color="green" />
            <Arrow to={second} color="red" />
          </Plane>
        }
        readout={
          <>
            <Slider label="h" value={h} onChange={setH} min={-4} max={6} step={1} color={palette.glow} />
            <Readout tex={`A = \\begin{bmatrix} ${entry} & ${texNumber(second[0])} \\\\ ${texNumber(bottom)} & ${texNumber(second[1])} \\end{bmatrix}`} />
            <Readout tex={`\\begin{aligned} ad - bc &= ${texNumber(second[1])}(${entry}) - ${texNumber(second[0])}(${texNumber(bottom)}) \\\\ &= ${texNumber(determinant)} \\end{aligned}`} />
          </>
        }
      />
    </Panel>
  );
}
