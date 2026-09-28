"use client";

import { ArrowCounterClockwise, ArrowUUpLeft } from "@phosphor-icons/react";
import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { apply, nearlyEqual, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, DEFAULT_BOUNDS, Handle, Marker, Plane, usePlane } from "./plane";

const GRID_REACH = 14;
const EPSILON = 1e-9;

/** A number as TeX, using a small fraction when it is one, so 1/3 reads as a third instead of 0.33. */
export function fractionTex(value: number): string {
  if (Math.abs(value - Math.round(value)) < EPSILON) return texNumber(Math.round(value));
  for (let denominator = 2; denominator <= 12; denominator++) {
    const numerator = value * denominator;
    if (Math.abs(numerator - Math.round(numerator)) < EPSILON) {
      const sign = value < 0 ? "-" : "";
      return `${sign}\\tfrac{${Math.abs(Math.round(numerator))}}{${denominator}}`;
    }
  }
  return texNumber(value);
}

function ImageGrid({ matrix }: { matrix: Matrix2 }) {
  const { toSvg } = usePlane();
  const lines: [Vec, Vec][] = [];
  for (let k = -GRID_REACH; k <= GRID_REACH; k++) {
    lines.push([apply(matrix, [k, -GRID_REACH]), apply(matrix, [k, GRID_REACH])]);
    lines.push([apply(matrix, [-GRID_REACH, k]), apply(matrix, [GRID_REACH, k])]);
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

function UnitSquare({ matrix, shown }: { matrix: Matrix2; shown: boolean }) {
  const { toSvg } = usePlane();
  const corners: Vec[] = [[0, 0], [1, 0], [1, 1], [0, 1]];
  const points = corners.map((corner) => toSvg(apply(matrix, corner)).join(",")).join(" ");
  return <polygon points={points} fill="var(--palette-teal)" fillOpacity={shown ? 0.35 : 0} className="transition-[fill-opacity] duration-300" />;
}

function BasisArrows({ matrix }: { matrix: Matrix2 }) {
  return (
    <>
      <Arrow to={[matrix[0][0], matrix[1][0]]} color="green" />
      <Arrow to={[matrix[0][1], matrix[1][1]]} color="red" />
    </>
  );
}

function squareTex(matrix: Matrix2, colored = true): string {
  const entry = (value: number, color: string) => (colored ? `\\textcolor{${color}}{${fractionTex(value)}}` : fractionTex(value));
  const rows = matrix.map((row) => `${entry(row[0], palette.i_hat)} & ${entry(row[1], palette.j_hat)}`);
  return `\\begin{bmatrix} ${rows.join(" \\\\ ")} \\end{bmatrix}`;
}

function ChoiceButton({ selected, disabled, onClick, children, label }: { selected?: boolean; disabled?: boolean; onClick: () => void; children: React.ReactNode; label?: string }) {
  return (
    <button
      type="button"
      disabled={disabled}
      aria-pressed={selected}
      aria-label={label}
      onClick={onClick}
      className={`whitespace-nowrap rounded-lg px-3 py-2 text-meta font-semibold transition-colors duration-200 disabled:opacity-40 ${
        selected ? "bg-text text-surface" : "bg-surface-sunken text-text hover:bg-line"
      }`}
    >
      {children}
    </button>
  );
}

type Kind = "replacement" | "interchange" | "scaling";

const KIND_NAMES: Record<Kind, string> = { replacement: "Replacement", interchange: "Interchange", scaling: "Scaling" };

type Move = { matrix: Matrix2; inverse: Matrix2 | null; operation: string; undo: string };

function signedTerm(factor: number, row: string): string {
  if (Math.abs(factor) < EPSILON) return "";
  const size = Math.abs(Math.abs(factor) - 1) < EPSILON ? "" : fractionTex(Math.abs(factor));
  return ` ${factor < 0 ? "-" : "+"} ${size}${row}`;
}

function replacementMove(c: number): Move {
  return {
    matrix: [[1, 0], [c, 1]],
    inverse: [[1, 0], [-c, 1]],
    operation: `R_2 \\leftarrow R_2${signedTerm(c, "R_1")}`,
    undo: `R_2 \\leftarrow R_2${signedTerm(-c, "R_1")}`,
  };
}

function scalingMove(s: number): Move {
  const invertible = Math.abs(s) > EPSILON;
  return {
    matrix: [[1, 0], [0, s]],
    inverse: invertible ? [[1, 0], [0, 1 / s]] : null,
    operation: `R_2 \\leftarrow ${fractionTex(s)}\\,R_2`,
    undo: invertible ? `R_2 \\leftarrow ${fractionTex(1 / s)}\\,R_2` : "",
  };
}

const SWAP_MOVE: Move = { matrix: [[0, 1], [1, 0]], inverse: [[0, 1], [1, 0]], operation: "R_1 \\leftrightarrow R_2", undo: "R_1 \\leftrightarrow R_2" };

function moveFor(kind: Kind, c: number, s: number): Move {
  if (kind === "replacement") return replacementMove(c);
  if (kind === "scaling") return scalingMove(s);
  return SWAP_MOVE;
}

function KindHandle({ kind, c, s, setC, setS }: { kind: Kind; c: number; s: number; setC: (value: number) => void; setS: (value: number) => void }) {
  if (kind === "replacement") {
    return <Handle at={[1, c]} onMove={(point) => setC(point[1])} color="green" label={`Tip of i-hat, moving up and down only. The multiple of row 1 added to row 2 is ${c}`} />;
  }
  if (kind === "scaling") {
    return <Handle at={[0, s]} onMove={(point) => setS(point[1])} color="red" label={`Tip of j-hat, moving up and down only. Row 2 is scaled by ${s}`} />;
  }
  return null;
}

function InverseSlot({ move }: { move: Move }) {
  return (
    <div className="grid rounded-lg bg-surface-sunken px-4 py-3 text-center">
      <div aria-hidden={!move.inverse} className={`[grid-area:1/1] ${move.inverse ? "swap-shown" : "swap-hidden"}`}>
        <Tex display>{move.inverse ? `\\begin{gathered} E^{-1} = ${squareTex(move.inverse)} \\\\ ${move.undo} \\end{gathered}` : "\\begin{gathered} E^{-1} = \\begin{bmatrix} 1 & 0 \\\\ 0 & 1 \\end{bmatrix} \\\\ R_2 \\end{gathered}"}</Tex>
      </div>
      <p aria-hidden={!!move.inverse} className={`[grid-area:1/1] self-center text-meta ${move.inverse ? "swap-hidden" : "swap-shown"}`}>
        Scaling by <Tex>{"0"}</Tex> flattens the plane, and nothing can undo it, so it is not a row operation.
      </p>
    </div>
  );
}

/** One elementary matrix at a time: pick its kind, drag the arrow tip that it moves, and see E, its inverse and its grid. */
export function ElementaryMoves({ target = [1, -2] }: { target?: Vec }) {
  const [kind, setKind] = useState<Kind>("scaling");
  const [c, setC] = useState(0);
  const [s, setS] = useState(2);
  const move = moveFor(kind, c, s);
  const iHat: Vec = [move.matrix[0][0], move.matrix[1][0]];
  const jHat: Vec = [move.matrix[0][1], move.matrix[1][1]];
  const { settled: solved, gesture } = useSettled(nearlyEqual(iHat, target) && nearlyEqual(jHat, [0, 1]));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Find a row operation whose matrix sends <Tex>{"\\hat\\imath"}</Tex> to the ringed point <Tex>{`(${fractionTex(target[0])}, ${fractionTex(target[1])})`}</Tex> and leaves <Tex>{"\\hat\\jmath"}</Tex> where it is.</>}
        success={<>That is <Tex>{`E = ${squareTex(move.matrix, false)}`}</Tex>, the replacement <Tex>{move.operation}</Tex>. Its inverse adds the multiple back.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DEFAULT_BOUNDS} label="The grid after an elementary matrix. Drag the highlighted arrow tip up or down.">
            <ImageGrid matrix={move.matrix} />
            <Marker at={target} color={solved ? "teal" : "glow"} ring={!solved} />
            <BasisArrows matrix={move.matrix} />
            <KindHandle kind={kind} c={c} s={s} setC={setC} setS={setS} />
          </Plane>
        }
        readout={
          <>
            <div role="group" aria-label="Kind of row operation" className="flex flex-wrap gap-2">
              {(Object.keys(KIND_NAMES) as Kind[]).map((name) => (
                <ChoiceButton key={name} selected={kind === name} onClick={() => setKind(name)}>
                  {KIND_NAMES[name]}
                </ChoiceButton>
              ))}
            </div>
            <Readout tex={`\\begin{gathered} E = ${squareTex(move.matrix)} \\\\ ${move.operation} \\end{gathered}`} />
            <InverseSlot move={move} />
          </>
        }
      />
    </Panel>
  );
}

type BlockRow = [number, number, number, number];
type Block = [BlockRow, BlockRow];
type Operation = { tex: string; apply: (rows: Block) => Block };

const tidy = (value: number) => (Math.abs(value - Math.round(value)) < EPSILON ? Math.round(value) : value);
const combine = (row: BlockRow, other: BlockRow, factor: number): BlockRow => row.map((value, index) => tidy(value + factor * other[index])) as BlockRow;
const scaled = (row: BlockRow, factor: number): BlockRow => row.map((value) => tidy(value * factor)) as BlockRow;

function operationsFor(c: number): Operation[] {
  const cTex = fractionTex(c);
  return [
    { tex: "R_1 \\leftrightarrow R_2", apply: ([first, second]) => [second, first] },
    { tex: `R_1 \\leftarrow R_1${signedTerm(c, "R_2") || " + 0R_2"}`, apply: ([first, second]) => [combine(first, second, c), second] },
    { tex: `R_2 \\leftarrow R_2${signedTerm(c, "R_1") || " + 0R_1"}`, apply: ([first, second]) => [first, combine(second, first, c)] },
    { tex: `R_1 \\leftarrow ${cTex}\\,R_1`, apply: ([first, second]) => [scaled(first, c), second] },
    { tex: `R_2 \\leftarrow ${cTex}\\,R_2`, apply: ([first, second]) => [first, scaled(second, c)] },
  ];
}

function startBlock(matrix: Matrix2): Block {
  return [
    [matrix[0][0], matrix[0][1], 1, 0],
    [matrix[1][0], matrix[1][1], 0, 1],
  ];
}

const leftHalf = (rows: Block): Matrix2 => [[rows[0][0], rows[0][1]], [rows[1][0], rows[1][1]]];
const rightHalf = (rows: Block): Matrix2 => [[rows[0][2], rows[0][3]], [rows[1][2], rows[1][3]]];
const isIdentity = (matrix: Matrix2) => nearlyEqual([matrix[0][0], matrix[1][1]], [1, 1]) && nearlyEqual([matrix[0][1], matrix[1][0]], [0, 0]);

function blockTex(rows: Block, solved: boolean): string {
  const right = solved ? palette.teal : palette.text;
  const colors = [palette.i_hat, palette.j_hat, right, right];
  const body = rows.map((row) => row.map((value, index) => `\\textcolor{${colors[index]}}{${fractionTex(value)}}`).join(" & ")).join(" \\\\ ");
  return `\\left[\\begin{array}{rr|rr} ${body} \\end{array}\\right]`;
}

function productTex(count: number): string {
  if (count === 0) return "I";
  if (count <= 4) return Array.from({ length: count }, (_, index) => `E_{${count - index}}`).join("");
  return `E_{${count}} \\cdots E_1`;
}

function StepLog({ steps }: { steps: string[] }) {
  const last = steps.length === 0 ? "\\text{none yet}" : `E_{${steps.length}}:\\ ${steps[steps.length - 1]}`;
  return (
    <div className="rounded-lg bg-surface-sunken px-4 py-2 text-meta text-text-muted">
      <p className="flex h-8 items-center gap-1.5 whitespace-nowrap">
        Last step <Tex>{last}</Tex>
      </p>
      <p className="flex h-8 items-center gap-1.5 whitespace-nowrap">
        Right half <Tex>{`= ${productTex(steps.length)}`}</Tex>
      </p>
    </div>
  );
}

/** Row reduce [A | I] with real row operations while the grid of the left half moves; reaching I leaves A⁻¹ on the right. */
export function InverseBuilder({ matrix = [[0, 2], [1, 1]] }: { matrix?: Matrix2 }) {
  const [c, setC] = useState(-1);
  const [history, setHistory] = useState<Operation[]>([]);
  const rows = history.reduce((current, operation) => operation.apply(current), startBlock(matrix));
  const left = leftHalf(rows);
  const { settled: solved, gesture } = useSettled(isIdentity(left));
  const operations = operationsFor(c);
  const scalingByZero = Math.abs(c) < EPSILON;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Use row operations to turn the left half into <Tex>{"I"}</Tex>. Each one acts on the whole row, so the right half changes too.</>}
        success={<>The left half is <Tex>{"I"}</Tex>, so the right half is <Tex>{`A^{-1} = ${squareTex(rightHalf(rows), false)}`}</Tex>, the product of your elementary matrices.</>}
      />
      <Workbench
        plane={
          <Plane bounds={DEFAULT_BOUNDS} label="The grid after the left half of the augmented matrix. Green and red arrows are its columns.">
            <ImageGrid matrix={left} />
            <BasisArrows matrix={left} />
            <UnitSquare matrix={left} shown={solved} />
          </Plane>
        }
        readout={
          <>
            <div className="grid min-h-32 items-center rounded-lg bg-surface-sunken px-4 py-3 text-center">
              <Tex display>{blockTex(rows, solved)}</Tex>
            </div>
            <Slider label="c" value={c} onChange={setC} min={-3} max={3} step={0.5} color={palette.text} />
            <div role="group" aria-label="Row operations" className="grid grid-cols-1 gap-2">
              {operations.map((operation, index) => (
                <ChoiceButton
                  key={index}
                  disabled={scalingByZero && index >= 3}
                  label={`Apply ${operation.tex}`}
                  onClick={() => setHistory((current) => [...current, operation])}
                >
                  <Tex>{operation.tex}</Tex>
                </ChoiceButton>
              ))}
              <div className="flex gap-2">
                <ChoiceButton label="Undo the last row operation" onClick={() => setHistory((current) => current.slice(0, -1))}>
                  <span className="inline-flex items-center gap-1.5"><ArrowUUpLeft className="size-4" aria-hidden /> Undo</span>
                </ChoiceButton>
                <ChoiceButton label="Start over" onClick={() => setHistory([])}>
                  <span className="inline-flex items-center gap-1.5"><ArrowCounterClockwise className="size-4" aria-hidden /> Start over</span>
                </ChoiceButton>
              </div>
            </div>
            <StepLog steps={history.map((operation) => operation.tex)} />
          </>
        }
      />
    </Panel>
  );
}
