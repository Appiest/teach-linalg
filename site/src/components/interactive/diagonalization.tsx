"use client";

import { ArrowCounterClockwise } from "@phosphor-icons/react";
import { useEffect, useRef, useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { apply, det, nearlyEqual, scale, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, Handle, Label, Marker, Plane, usePlane, type Bounds } from "./plane";

const DIAGONAL_BOUNDS: Bounds = { xMin: -6, xMax: 6, yMin: -4, yMax: 5 };
const MATCH_BOUNDS: Bounds = { xMin: -4, xMax: 7, yMin: -5, yMax: 6 };
const GRID_REACH = 14;

const multiply = (left: Matrix2, right: Matrix2): Matrix2 => [
  [left[0][0] * right[0][0] + left[0][1] * right[1][0], left[0][0] * right[0][1] + left[0][1] * right[1][1]],
  [left[1][0] * right[0][0] + left[1][1] * right[1][0], left[1][0] * right[0][1] + left[1][1] * right[1][1]],
];

const inverse = (m: Matrix2): Matrix2 => {
  const d = det(m);
  return [
    [m[1][1] / d, -m[0][1] / d],
    [-m[1][0] / d, m[0][0] / d],
  ];
};

const fromColumns = (first: Vec, second: Vec): Matrix2 => [[first[0], second[0]], [first[1], second[1]]];
const columnOf = (m: Matrix2, index: 0 | 1): Vec => [m[0][index], m[1][index]];
const sameMatrix = (a: Matrix2, b: Matrix2) => nearlyEqual(columnOf(a, 0), columnOf(b, 0)) && nearlyEqual(columnOf(a, 1), columnOf(b, 1));
const blend = (from: Matrix2, to: Matrix2, s: number): Matrix2 =>
  from.map((row, i) => row.map((value, j) => value + (to[i][j] - value) * s)) as Matrix2;

const pointKey = (point: Vec) => `${point[0]},${point[1]}`;
const keyPoint = (key: string): Vec => key.split(",").map(Number) as Vec;

function matrixTex(m: Matrix2, colors: [string, string] = [palette.text, palette.text]): string {
  const entry = (value: number, column: 0 | 1) => `\\textcolor{${colors[column]}}{${texNumber(value)}}`;
  return `\\begin{bmatrix} ${entry(m[0][0], 0)} & ${entry(m[0][1], 1)} \\\\ ${entry(m[1][0], 0)} & ${entry(m[1][1], 1)} \\end{bmatrix}`;
}

/** Lines k·first + t·second and t·first + k·second: the grid whose axes are `first` and `second`. */
function BasisGrid({ first, second, firstHue, secondHue, opacity = 0.35 }: { first: Vec; second: Vec; firstHue: Hue; secondHue: Hue; opacity?: number }) {
  const { toSvg } = usePlane();
  const lines: { from: Vec; to: Vec; color: Hue; axis: boolean }[] = [];
  for (let k = -GRID_REACH; k <= GRID_REACH; k++) {
    const alongFirst: Vec = [k * second[0], k * second[1]];
    const alongSecond: Vec = [k * first[0], k * first[1]];
    lines.push({ from: [alongFirst[0] - GRID_REACH * first[0], alongFirst[1] - GRID_REACH * first[1]], to: [alongFirst[0] + GRID_REACH * first[0], alongFirst[1] + GRID_REACH * first[1]], color: firstHue, axis: k === 0 });
    lines.push({ from: [alongSecond[0] - GRID_REACH * second[0], alongSecond[1] - GRID_REACH * second[1]], to: [alongSecond[0] + GRID_REACH * second[0], alongSecond[1] + GRID_REACH * second[1]], color: secondHue, axis: k === 0 });
  }
  return (
    <g aria-hidden>
      {lines.map((line, index) => {
        const [x1, y1] = toSvg(line.from);
        const [x2, y2] = toSvg(line.to);
        return (
          <line
            key={index}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            stroke={hue(line.color)}
            strokeOpacity={line.axis ? 0.9 : opacity}
            strokeWidth={line.axis ? 2.5 : 1}
          />
        );
      })}
    </g>
  );
}

function coordinateTex(weights: Vec): string {
  const [first, second] = weights.map((value) => texNumber(value));
  return `${first}\\,\\textcolor{${palette.yellow}}{\\mathbf v_1} + ${second}\\,\\textcolor{${palette.blue}}{\\mathbf v_2}`.replace("+ -", "- ");
}

/** Drag x. The readout shows x and Ax in eigen-coordinates, where A only scales each coordinate by its eigenvalue. */
export function EigenCoordinateTarget({ v1, v2, lambdas, target, start = [1, 0] }: { v1: Vec; v2: Vec; lambdas: Vec; target: Vec; start?: Vec }) {
  const [x, setX] = useState<Vec>(start);
  const basis = fromColumns(v1, v2);
  const matrix = multiply(multiply(basis, [[lambdas[0], 0], [0, lambdas[1]]]), inverse(basis));
  const { settled, gesture } = useSettled(pointKey(x));
  const solved = nearlyEqual(apply(matrix, keyPoint(settled)), target);
  const image = apply(matrix, x);
  const weights = apply(inverse(basis), x);
  const scaled: Vec = [lambdas[0] * weights[0], lambdas[1] * weights[1]];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf x"}</Tex> until <Tex>{"A\\mathbf x"}</Tex> lands on the orange ring at <Tex>{`(${target.map((value) => texNumber(value)).join(", ")})`}</Tex>. The eigen-coordinates below tell you where to aim.</>}
        success={<>That works. In eigen-coordinates <Tex>{"A"}</Tex> multiplied <Tex>{texNumber(weights[0])}</Tex> by <Tex>{texNumber(lambdas[0])}</Tex> and <Tex>{texNumber(weights[1])}</Tex> by <Tex>{texNumber(lambdas[1])}</Tex>, and nothing else happened.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DIAGONAL_BOUNDS} label={`Eigen-grid of v1 and v2. Input x at ${describeVector(x)} and its output A x at ${describeVector(image)}. Drag the tip of x or use the arrow keys.`}>
            <BasisGrid first={v1} second={v2} firstHue="yellow" secondHue="blue" />
            <Arrow to={v1} color="yellow" width={3} />
            <Arrow to={v2} color="blue" width={3} />
            <Marker at={target} color={solved ? "teal" : "glow"} ring />
            <Arrow to={image} color="teal" />
            <Arrow to={x} color="text" />
            <Label at={x} color="text">x</Label>
            <Label at={image} color="teal" dy={22}>Ax</Label>
            <Handle at={x} onMove={setX} color="text" label={`Tip of the input x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\mathbf x = ${coordinateTex(weights)}`} />
            <Readout tex={`A\\mathbf x = ${coordinateTex(scaled)}`} />
            <Readout tex={`A\\mathbf x = ${columnTex(image, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}

type FactorMove = { id: "inverse" | "diagonal" | "basis"; tex: string; matrix: Matrix2 };

const TWEEN_MS = 650;
const easeOut = (s: number) => 1 - (1 - s) ** 3;

/** Eases the drawn matrix toward `target`, so each move plays as motion rather than a jump. */
function useEasedMatrix(target: Matrix2): Matrix2 {
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

function FactorButton({ onClick, disabled, children, label }: { onClick: () => void; disabled?: boolean; children: React.ReactNode; label: string }) {
  return (
    <button
      type="button"
      aria-label={label}
      onClick={onClick}
      disabled={disabled}
      className="inline-flex items-center gap-2 rounded-lg bg-surface-sunken px-4 py-2 text-meta font-semibold text-text shadow-lift transition-[opacity,scale] duration-150 hover:opacity-90 active:scale-[0.96] disabled:cursor-not-allowed disabled:opacity-35"
    >
      {children}
    </button>
  );
}

function productTex(applied: FactorMove[]): string {
  if (applied.length === 0) return "I";
  return [...applied].reverse().map((move) => move.tex).join("");
}

function factorMoves(basis: Matrix2, diagonal: Matrix2): FactorMove[] {
  return [
    { id: "basis", tex: "P", matrix: basis },
    { id: "diagonal", tex: "D", matrix: diagonal },
    { id: "inverse", tex: "P^{-1}", matrix: inverse(basis) },
  ];
}

/** Apply P⁻¹, D and P one at a time. Only the order P⁻¹ first, then D, then P carries u onto Au. */
export function DiagonalFactorSteps({ v1, v2, lambdas, u }: { v1: Vec; v2: Vec; lambdas: Vec; u: Vec }) {
  const basis = fromColumns(v1, v2);
  const diagonal: Matrix2 = [[lambdas[0], 0], [0, lambdas[1]]];
  const matrix = multiply(multiply(basis, diagonal), inverse(basis));
  const moves = factorMoves(basis, diagonal);
  const [applied, setApplied] = useState<FactorMove[]>([]);
  const current = applied.reduce<Matrix2>((product, move) => multiply(move.matrix, product), [[1, 0], [0, 1]]);
  const shown = useEasedMatrix(current);
  const reproduced = applied.length === moves.length && sameMatrix(current, matrix);
  const { settled: solved, gesture } = useSettled(reproduced);
  const finishedWrong = applied.length === moves.length && !reproduced;
  const target = apply(matrix, u);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Use each of <Tex>{"P^{-1}"}</Tex>, <Tex>D</Tex> and <Tex>P</Tex> once to carry <Tex>{"\\mathbf u"}</Tex> onto the orange ring at <Tex>{"A\\mathbf u"}</Tex>.</>}
        success={<>You applied <Tex>{"P^{-1}"}</Tex> first and <Tex>P</Tex> last, so the moves multiply to <Tex>{"PDP^{-1} = A"}</Tex>. The rightmost factor always acts first.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DIAGONAL_BOUNDS} label={`The eigen-grid after the moves so far, with u at ${describeVector(apply(current, u))} and a ring at A u, ${describeVector(target)}.`}>
            <BasisGrid first={apply(shown, v1)} second={apply(shown, v2)} firstHue="yellow" secondHue="blue" opacity={0.3} />
            <Marker at={target} color={solved ? "teal" : "glow"} ring />
            <Arrow to={u} color="text" width={2} dashed />
            <Arrow to={apply(shown, v1)} color="yellow" />
            <Arrow to={apply(shown, v2)} color="blue" />
            <Arrow to={apply(shown, u)} color="text" />
            <Label at={apply(shown, u)} color="text">u</Label>
          </Plane>
        }
        readout={
          <>
            <div className="flex flex-wrap gap-2">
              {[...moves].reverse().map((move) => (
                <FactorButton key={move.id} label={`Apply ${move.tex.replace("^{-1}", " inverse")}`} onClick={() => setApplied((list) => [...list, move])} disabled={applied.some((entry) => entry.id === move.id)}>
                  Apply <Tex>{move.tex}</Tex>
                </FactorButton>
              ))}
              <FactorButton label="Start over" onClick={() => setApplied([])} disabled={applied.length === 0}>
                <ArrowCounterClockwise className="size-4" aria-hidden /> Start over
              </FactorButton>
            </div>
            <Readout tex={`${productTex(applied)} = ${matrixTex(current)}`} />
            <Readout tex={`A = ${matrixTex(matrix)}`} />
            <p className={`text-meta text-text-muted ${finishedWrong ? "swap-shown" : "swap-hidden"}`} aria-live="polite">
              That order lands somewhere else. In a product, the factor on the right acts first.
            </p>
          </>
        }
      />
    </Panel>
  );
}

const cross = (first: Vec, second: Vec) => first[0] * second[1] - first[1] * second[0];
const dot = (first: Vec, second: Vec) => first[0] * second[0] + first[1] * second[1];
const isZeroVector = (v: Vec) => nearlyEqual(v, [0, 0]);
const keepsOwnLine = (matrix: Matrix2, v: Vec) => !isZeroVector(v) && Math.abs(cross(v, apply(matrix, v))) < 1e-9;
const stretchOf = (matrix: Matrix2, v: Vec) => dot(apply(matrix, v), v) / dot(v, v);

function LineAlong({ direction, color }: { direction: Vec; color: Hue }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg(scale(-30, direction));
  const [x2, y2] = toSvg(scale(30, direction));
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={2.5} strokeOpacity={0.7} strokeLinecap="round" />;
}

/** Two versions of a note in one grid cell, so switching between them never changes the height. */
function ReservedNote({ showSecond, first, second }: { showSecond: boolean; first: React.ReactNode; second: React.ReactNode }) {
  return (
    <div className="grid rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
      <p aria-hidden={showSecond} className={`[grid-area:1/1] ${showSecond ? "swap-hidden" : "swap-shown"}`}>{first}</p>
      <p aria-hidden={!showSecond} className={`[grid-area:1/1] ${showSecond ? "swap-shown" : "swap-hidden"}`}>{second}</p>
    </div>
  );
}

function columnVerdictTex(matrix: Matrix2, column: Vec, name: string): string {
  const image = columnTex(apply(matrix, column), palette.teal);
  if (!keepsOwnLine(matrix, column)) return `A\\mathbf ${name} = ${image} \\text{, off the line of } \\mathbf ${name}`;
  return `A\\mathbf ${name} = ${image} = ${texNumber(stretchOf(matrix, column))}\\,\\mathbf ${name}`;
}

/** Drag the two columns of P. AP = PD with D diagonal needs each column to be an eigenvector, and P needs them on different lines. */
export function EigenColumnHunt({ matrix, start = [[1, 0], [0, 1]] }: { matrix: Matrix2; start?: [Vec, Vec] }) {
  const [first, setFirst] = useState<Vec>(start[0]);
  const [second, setSecond] = useState<Vec>(start[1]);
  const bothEigen = keepsOwnLine(matrix, first) && keepsOwnLine(matrix, second);
  const parallel = Math.abs(cross(first, second)) < 1e-9;
  const { settled: solved, gesture } = useSettled(bothEigen && !parallel);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag the columns <Tex>{"\\mathbf p_1"}</Tex> and <Tex>{"\\mathbf p_2"}</Tex> of <Tex>P</Tex> until <Tex>A</Tex> keeps each one on its own line. A column lights up when its teal image lines up with it.</>}
        success={<>Both columns are eigenvectors on different lines. Now each column of <Tex>AP</Tex> is a multiple of the matching column of <Tex>P</Tex>, so <Tex>{"AP = PD"}</Tex> with those multiples on the diagonal of <Tex>D</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DIAGONAL_BOUNDS} label={`Column p1 at ${describeVector(first)} with A p1 at ${describeVector(apply(matrix, first))}, and column p2 at ${describeVector(second)} with A p2 at ${describeVector(apply(matrix, second))}.`}>
            {keepsOwnLine(matrix, first) ? <LineAlong direction={first} color="yellow" /> : null}
            {keepsOwnLine(matrix, second) ? <LineAlong direction={second} color="blue" /> : null}
            <Arrow to={apply(matrix, first)} color="teal" width={2.5} />
            <Arrow to={apply(matrix, second)} color="teal" width={2.5} />
            <Arrow to={first} color="yellow" />
            <Arrow to={second} color="blue" />
            <Label at={first} color="yellow">p₁</Label>
            <Label at={second} color="blue">p₂</Label>
            <Handle at={first} onMove={setFirst} color="yellow" label={`Column p1, at ${describeVector(first)}`} />
            <Handle at={second} onMove={setSecond} color="blue" label={`Column p2, at ${describeVector(second)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={columnVerdictTex(matrix, first, "p_1")} />
            <Readout tex={columnVerdictTex(matrix, second, "p_2")} />
            <ReservedNote
              showSecond={bothEigen && parallel}
              first={<>Each column needs to be an eigenvector, and the two columns need different directions.</>}
              second={<>Both columns sit on one eigenline, so <Tex>P</Tex> has no inverse. Move one column to the other eigenline.</>}
            />
          </>
        }
      />
    </Panel>
  );
}

/** Slide the diagonal of D until PD matches AP column by column; the order of P's columns fixes the order of D's entries. */
export function DiagonalEntryMatch({ matrix, first, second }: { matrix: Matrix2; first: Vec; second: Vec }) {
  const [d1, setD1] = useState(0);
  const [d2, setD2] = useState(0);
  const matches = nearlyEqual(apply(matrix, first), scale(d1, first)) && nearlyEqual(apply(matrix, second), scale(d2, second));
  const { settled: solved, gesture } = useSettled(matches);
  const answer = [stretchOf(matrix, first), stretchOf(matrix, second)].map((value) => texNumber(value));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide <Tex>{"d_1"}</Tex> and <Tex>{"d_2"}</Tex> until each dashed column of <Tex>PD</Tex> covers the matching teal column of <Tex>AP</Tex>.</>}
        success={<>That gives <Tex>{`D = \\begin{bmatrix} ${answer[0]} & 0 \\\\ 0 & ${answer[1]} \\end{bmatrix}`}</Tex>. The first column of <Tex>P</Tex> belongs to <Tex>{answer[0]}</Tex>, so <Tex>{answer[0]}</Tex> goes first on the diagonal.</>}
      />
      <Workbench
        plane={
          <Plane bounds={MATCH_BOUNDS} label={`Columns of P, their images under A, and the columns of P D: d1 p1 at ${describeVector(scale(d1, first))} and d2 p2 at ${describeVector(scale(d2, second))}.`}>
            <Arrow to={apply(matrix, first)} color="teal" width={5} />
            <Arrow to={apply(matrix, second)} color="teal" width={5} />
            <Arrow to={scale(d1, first)} color="yellow" width={2.5} dashed />
            <Arrow to={scale(d2, second)} color="blue" width={2.5} dashed />
            <Arrow to={first} color="yellow" />
            <Arrow to={second} color="blue" />
            <Label at={first} color="yellow" dx={-30}>p₁</Label>
            <Label at={second} color="blue" dx={-30}>p₂</Label>
          </Plane>
        }
        readout={
          <>
            <Slider label="d_1" value={d1} onChange={setD1} min={-3} max={6} step={1} color={palette.yellow} />
            <Slider label="d_2" value={d2} onChange={setD2} min={-3} max={6} step={1} color={palette.blue} />
            <Readout tex={`AP = ${matrixTex(multiply(matrix, fromColumns(first, second)), [palette.teal, palette.teal])}`} />
            <Readout tex={`PD = ${matrixTex(fromColumns(scale(d1, first), scale(d2, second)), [palette.yellow, palette.blue])}`} />
          </>
        }
      />
    </Panel>
  );
}

