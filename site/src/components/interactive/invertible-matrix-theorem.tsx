"use client";

import { CheckCircle, XCircle } from "@phosphor-icons/react";
import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { describeVector, Goal, Panel, Readout, RichText, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { apply, det, nearlyEqual, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, DEFAULT_BOUNDS, Handle, Label, Marker, Plane, usePlane, type Bounds } from "./plane";

const ORIGIN: Vec = [0, 0];
const FAR = 40;

const columnOf = (matrix: Matrix2, index: 0 | 1): Vec => [matrix[0][index], matrix[1][index]];
const isZero = (v: Vec) => nearlyEqual(v, ORIGIN);

function rankOf(matrix: Matrix2): number {
  if (Math.abs(det(matrix)) > 1e-9) return 2;
  return isZero(columnOf(matrix, 0)) && isZero(columnOf(matrix, 1)) ? 0 : 1;
}

/** A nonzero vector the matrix sends to zero, when there is one: the direction it crushes. */
function crushedDirection(matrix: Matrix2): Vec | null {
  if (rankOf(matrix) !== 1) return null;
  const [[a, b], [c, d]] = matrix;
  const fromTop: Vec = [-b, a];
  return isZero(fromTop) ? [-d, c] : fromTop;
}

function matrixTex(matrix: Matrix2): string {
  const entry = (value: number, column: 0 | 1) => `\\textcolor{${column === 0 ? palette.i_hat : palette.j_hat}}{${texNumber(value)}}`;
  return `\\begin{bmatrix} ${entry(matrix[0][0], 0)} & ${entry(matrix[0][1], 1)} \\\\ ${entry(matrix[1][0], 0)} & ${entry(matrix[1][1], 1)} \\end{bmatrix}`;
}

function ImageGrid({ matrix }: { matrix: Matrix2 }) {
  const { toSvg } = usePlane();
  const reach = 14;
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
        return <line key={index} x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--palette-blue)" strokeOpacity={0.45} strokeWidth={1.2} />;
      })}
    </g>
  );
}

function ThroughOrigin({ direction, color }: { direction: Vec; color: string }) {
  const { toSvg } = usePlane();
  const length = Math.hypot(...direction);
  const [x1, y1] = toSvg([(-FAR * direction[0]) / length, (-FAR * direction[1]) / length]);
  const [x2, y2] = toSvg([(FAR * direction[0]) / length, (FAR * direction[1]) / length]);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={color} strokeWidth={2.5} strokeDasharray="7 6" strokeOpacity={0.9} />;
}

function CrushedMark({ hit }: { hit: boolean }) {
  const { toSvg } = usePlane();
  const [x, y] = toSvg(ORIGIN);
  return <circle cx={x} cy={y} r={hit ? 9 : 13} fill={hit ? "var(--palette-glow)" : "none"} stroke="var(--palette-glow)" strokeWidth={2.5} strokeDasharray={hit ? undefined : "4 4"} className="transition-[r,fill] duration-300" />;
}

const STATEMENTS = [
  "$A$ is invertible",
  "the columns are independent",
  "the columns span $\\mathbb R^2$",
  "$\\operatorname{Nul}A = \\{\\mathbf 0\\}$",
  "$\\operatorname{rank}A = 2$",
  "every $A\\mathbf x = \\mathbf b$ has a solution",
];

function StatementList({ holds }: { holds: boolean }) {
  return (
    <ul className="space-y-1.5 rounded-lg bg-surface-sunken px-4 py-3 text-meta" aria-label={holds ? "Every statement is true" : "Every statement is false"}>
      {STATEMENTS.map((statement) => (
        <li key={statement} className={`flex items-center gap-2.5 transition-opacity duration-300 ${holds ? "text-[var(--palette-teal)]" : "text-text-muted opacity-60"}`}>
          <span className="grid shrink-0">
            <CheckCircle weight="fill" aria-hidden className={`size-4 [grid-area:1/1] ${holds ? "swap-shown" : "swap-hidden"}`} />
            <XCircle aria-hidden className={`size-4 [grid-area:1/1] ${holds ? "swap-hidden" : "swap-shown"}`} />
          </span>
          <span className={holds ? "" : "line-through decoration-1"}>
            <RichText>{statement}</RichText>
          </span>
        </li>
      ))}
    </ul>
  );
}

/** Drag the columns of A and watch every IMT statement switch together; then find a vector A crushes to zero. */
export function StatementBoard({ matrix: start }: { matrix: Matrix2 }) {
  const [matrix, setMatrix] = useState<Matrix2>(start);
  const [x, setX] = useState<Vec>([1, 1]);
  const image = apply(matrix, x);
  const rank = rankOf(matrix);
  const holds = rank === 2;
  const crushed = crushedDirection(matrix);
  const found = rank === 1 && !isZero(x) && isZero(image);
  const { settled: solved, gesture } = useSettled(found);
  const setColumn = (column: 0 | 1) => (point: Vec) =>
    setMatrix((current) => current.map((row, i) => row.map((value, j) => (j === column ? point[i] : value))) as Matrix2);
  const first = columnOf(matrix, 0);
  const second = columnOf(matrix, 1);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag a column until the statements go dark. Then drag the pink <Tex>{"\\mathbf x"}</Tex> to a nonzero vector that <Tex>A</Tex> sends to <Tex>{"\\mathbf 0"}</Tex>.</>}
        success={<>You found <Tex>{`\\mathbf x = ${describeVector(x)}`}</Tex> in <Tex>{"\\operatorname{Nul}A"}</Tex>. One crushed direction was enough to switch off every statement at once.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DEFAULT_BOUNDS} label="The grid moved by A, its green and red columns, and a pink vector x with its image Ax. Drag the tips or use arrow keys.">
            <ImageGrid matrix={matrix} />
            {crushed ? <ThroughOrigin direction={crushed} color="var(--palette-pink)" /> : null}
            <CrushedMark hit={solved} />
            <Arrow to={first} color="green" />
            <Arrow to={second} color="red" />
            <Arrow to={x} color="pink" width={2.5} />
            <Arrow to={image} color="teal" />
            <Label at={x} color="pink">x</Label>
            <Label at={image} color="teal" dx={10} dy={20}>Ax</Label>
            <Handle at={first} onMove={setColumn(0)} color="green" label={`First column of A, at ${describeVector(first)}`} />
            <Handle at={second} onMove={setColumn(1)} color="red" label={`Second column of A, at ${describeVector(second)}`} />
            <Handle at={x} onMove={setX} color="pink" label={`The vector x, at ${describeVector(x)}. A sends it to ${describeVector(image)}.`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`A = ${matrixTex(matrix)}`} />
            <StatementList holds={holds} />
            <Readout tex={`A\\mathbf x = \\textcolor{${palette.teal}}{${describeVector(image).replaceAll("−", "-")}}`} />
          </>
        }
      />
    </Panel>
  );
}

type Call = { rows: number[][]; invertible: boolean; reason: string };
type Verdict = "invertible" | "singular";

const bmatrix = (rows: number[][]) => `\\begin{bmatrix} ${rows.map((row) => row.map((value) => texNumber(value)).join(" & ")).join(" \\\\ ")} \\end{bmatrix}`;

function VerdictButton({ verdict, chosen, correct, onChoose }: { verdict: Verdict; chosen: boolean; correct: boolean; onChoose: () => void }) {
  const tone = !chosen ? "shadow-lift" : correct ? "ring-2 ring-[var(--palette-teal)] text-[var(--palette-teal)]" : "ring-2 ring-[var(--palette-j-hat)] text-[var(--palette-j-hat)]";
  return (
    <button type="button" aria-pressed={chosen} onClick={onChoose} className={`rounded-lg bg-surface-raised px-3 py-1.5 text-meta font-semibold text-text transition-shadow ${tone}`}>
      {verdict === "invertible" ? "Invertible" : "Singular"}
    </button>
  );
}

function CallCard({ call, index, chosen, onChoose }: { call: Call; index: number; chosen: Verdict | undefined; onChoose: (verdict: Verdict) => void }) {
  const answer: Verdict = call.invertible ? "invertible" : "singular";
  const right = chosen === answer;
  const wrong = chosen !== undefined && !right;
  return (
    <li className={`flex flex-col gap-3 rounded-lg bg-surface-sunken p-4 transition-shadow duration-300 ${right ? "ring-2 ring-[var(--palette-teal)]" : ""}`} aria-label={`Matrix ${index + 1}`}>
      <div className="text-center">
        <Tex>{bmatrix(call.rows)}</Tex>
      </div>
      <div className="flex justify-center gap-2">
        {(["invertible", "singular"] as Verdict[]).map((verdict) => (
          <VerdictButton key={verdict} verdict={verdict} chosen={chosen === verdict} correct={verdict === answer} onChoose={() => onChoose(verdict)} />
        ))}
      </div>
      <div className="grid text-meta" aria-live="polite">
        <p className={`[grid-area:1/1] text-text-muted ${chosen === undefined ? "swap-shown" : "swap-hidden"}`}>Decide with as little arithmetic as you can.</p>
        <p className={`[grid-area:1/1] text-[var(--palette-j-hat)] ${wrong ? "swap-shown" : "swap-hidden"}`}>Look again at the columns and the pivots.</p>
        <p className={`[grid-area:1/1] text-[var(--palette-teal)] ${right ? "swap-shown" : "swap-hidden"}`}>
          <RichText>{call.reason}</RichText>
        </p>
      </div>
    </li>
  );
}

/** Classify each square matrix as invertible or singular, naming the IMT statement that settles it. */
export function InvertibilityCalls({ calls }: { calls: Call[] }) {
  const [chosen, setChosen] = useState<Record<number, Verdict>>({});
  const allRight = calls.every((call, index) => chosen[index] === (call.invertible ? "invertible" : "singular"));
  const { settled: solved, gesture } = useSettled(allRight);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Mark each matrix invertible or singular. Each one can be settled by a single statement of the theorem.</>}
        success={<>All {calls.length} are right. Each call checked one statement, and the theorem supplied every other one for free.</>}
      />
      <ul className="grid gap-3 sm:grid-cols-2">
        {calls.map((call, index) => (
          <CallCard key={index} call={call} index={index} chosen={chosen[index]} onChoose={(verdict) => setChosen((current) => ({ ...current, [index]: verdict }))} />
        ))}
      </ul>
    </Panel>
  );
}

type SolutionCount = "one" | "none" | "many";

const SOLUTION_TEXT: Record<SolutionCount, string> = {
  one: "\\text{exactly one solution}",
  none: "\\text{no solution}",
  many: "\\text{infinitely many solutions}",
};

function countSolutions(matrix: Matrix2, b: Vec): SolutionCount {
  if (rankOf(matrix) === 2) return "one";
  const reached = columnOf(matrix, 0);
  return Math.abs(reached[0] * b[1] - reached[1] * b[0]) < 1e-9 ? "many" : "none";
}

function solveInvertible(matrix: Matrix2, b: Vec): Vec {
  const [[a, c], [d, e]] = matrix;
  const determinant = det(matrix);
  return [(e * b[0] - c * b[1]) / determinant, (-d * b[0] + a * b[1]) / determinant];
}

function SolidLine({ through, direction }: { through: Vec; direction: Vec }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg([through[0] - FAR * direction[0], through[1] - FAR * direction[1]]);
  const [x2, y2] = toSvg([through[0] + FAR * direction[0], through[1] + FAR * direction[1]]);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--palette-yellow)" strokeWidth={3.5} strokeLinecap="round" />;
}

function SolutionMarks({ matrix, b, count }: { matrix: Matrix2; b: Vec; count: SolutionCount }) {
  if (count === "one") return <Arrow to={solveInvertible(matrix, b)} color="yellow" />;
  const crushed = crushedDirection(matrix);
  if (!crushed) return null;
  return (
    <>
      <ThroughOrigin direction={crushed} color="var(--palette-pink)" />
      <ThroughOrigin direction={columnOf(matrix, 0)} color="var(--palette-teal)" />
      {count === "many" ? <SolidLine through={[b[0] / matrix[0][0], 0]} direction={crushed} /> : null}
    </>
  );
}

const CRUSH_BOUNDS: Bounds = { xMin: -5, xMax: 5, yMin: -5, yMax: 5 };
const SPOKEN_COUNT: Record<SolutionCount, string> = { one: "exactly one solution", none: "no solution", many: "infinitely many solutions" };

/** Slide k and drag b: a square matrix either solves every b exactly once, or crushes a line and misses most targets. */
export function CrushAndMiss({ start = 1 }: { start?: number }) {
  const [k, setK] = useState(start);
  const [b, setB] = useState<Vec>([3, 1]);
  const matrix: Matrix2 = [[1, 2], [2, k]];
  const count = countSolutions(matrix, b);
  const { settled: solved, gesture } = useSettled(count === "many" && !isZero(b));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Find a nonzero target <Tex>{"\\mathbf b"}</Tex> that <Tex>{"A\\mathbf x = \\mathbf b"}</Tex> reaches in infinitely many ways. You will need to change <Tex>{"k"}</Tex> too.</>}
        success={<>At <Tex>{"k = 4"}</Tex> the matrix crushes the pink line, so each reachable target is hit along a whole yellow line. The same <Tex>{"k"}</Tex> leaves every target off the teal line unreachable.</>}
      />
      <Workbench
        plane={
          <Plane bounds={CRUSH_BOUNDS} label={`Target b at ${describeVector(b)} for k = ${k}. A x = b has ${SPOKEN_COUNT[count]}.`}>
            <SolutionMarks matrix={matrix} b={b} count={count} />
            <Marker at={b} color="teal" ring={count === "none"} />
            <Label at={b} color="teal">b</Label>
            <Handle at={b} onMove={setB} color="teal" label={`Target b, at ${describeVector(b)}`} />
          </Plane>
        }
        readout={
          <>
            <Slider label="k" value={k} onChange={setK} min={1} max={6} step={1} color={palette.j_hat} />
            <Readout tex={`A = ${matrixTex(matrix)}`} />
            <Readout tex={SOLUTION_TEXT[count]} />
          </>
        }
      />
    </Panel>
  );
}

function echelonTex(k: number): string {
  const last = k - 3;
  const lastColor = last === 0 ? palette.glow : palette.teal;
  return `\\begin{bmatrix} \\textcolor{${palette.teal}}{1} & 0 & 2 \\\\ 0 & \\textcolor{${palette.teal}}{1} & -1 \\\\ 0 & 0 & \\textcolor{${lastColor}}{${texNumber(last)}} \\end{bmatrix}`;
}

/** Slide the corner entry of a 3x3 matrix and watch the third pivot of its echelon form appear and vanish. */
export function ThirdPivotSlider() {
  const [k, setK] = useState(0);
  const { settled: solved, gesture } = useSettled(k === 3);
  const singular = k === 3;
  const matrix = `\\begin{bmatrix} 1 & 0 & 2 \\\\ 0 & 1 & -1 \\\\ 2 & 1 & \\textcolor{${palette.j_hat}}{${texNumber(k)}} \\end{bmatrix}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Slide <Tex>{"k"}</Tex> until the echelon form loses its third pivot.</>}
        success={<>At <Tex>{"k = 3"}</Tex> only two pivots remain, so every statement of the theorem fails together. For example, <Tex>{"(-2, 1, 1)"}</Tex> is a nonzero vector in the null space.</>}
      />
      <div className="grid items-start gap-5 md:grid-cols-2">
        <div className="min-w-0 space-y-4">
          <Slider label="k" value={k} onChange={setK} min={0} max={6} step={1} color={palette.j_hat} />
          <Readout tex={`A = ${matrix}`} />
        </div>
        <div className="min-w-0 space-y-4">
          <Readout tex={`A \\sim ${echelonTex(k)}`} />
          <div className={`rounded-lg px-4 py-3 transition-colors duration-300 ${singular ? "bg-[color-mix(in_oklab,var(--palette-glow)_14%,transparent)]" : "bg-surface-sunken"}`}>
            <Tex>{singular ? "2 \\text{ pivots, so } A \\text{ is singular}" : "3 \\text{ pivots, so } A \\text{ is invertible}"}</Tex>
          </div>
        </div>
      </div>
    </Panel>
  );
}
