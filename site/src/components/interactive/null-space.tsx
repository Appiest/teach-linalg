"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { describeVector, Goal, Panel, Readout, RichText, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { apply, nearlyEqual, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, Handle, Label, Marker, Plane, usePlane, type Bounds } from "./plane";

const COLLECTOR_BOUNDS: Bounds = { xMin: -6, xMax: 6, yMin: -5, yMax: 5 };

const pointKey = (point: Vec) => `${point[0]},${point[1]}`;
const keyPoint = (key: string): Vec => key.split(",").map(Number) as Vec;
const isZero = (point: Vec) => point[0] === 0 && point[1] === 0;

/** A nonzero vector that a singular 2x2 matrix sends to zero. */
function nullDirection(matrix: Matrix2): Vec {
  const [[a, b], [c, d]] = matrix;
  return a !== 0 || b !== 0 ? [-b, a] : [-d, c];
}

function landsOnTarget(matrix: Matrix2, point: Vec, target: Vec): boolean {
  const counts = !(isZero(target) && isZero(point));
  return counts && nearlyEqual(apply(matrix, point), target);
}

function LineThrough({ point, direction, color, faint = false }: { point: Vec; direction: Vec; color: Hue; faint?: boolean }) {
  const { toSvg } = usePlane();
  const reach = 40;
  const [x1, y1] = toSvg([point[0] - reach * direction[0], point[1] - reach * direction[1]]);
  const [x2, y2] = toSvg([point[0] + reach * direction[0], point[1] + reach * direction[1]]);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={faint ? 2 : 4} strokeOpacity={faint ? 0.55 : 1} strokeDasharray={faint ? "6 6" : undefined} strokeLinecap="round" />;
}

function FoundSlots({ found, needed, color }: { found: number; needed: number; color: Hue }) {
  return (
    <div className="flex items-center gap-2" role="img" aria-label={`${Math.min(found, needed)} of ${needed} inputs found`}>
      {Array.from({ length: needed }, (_, index) => (
        <span
          key={index}
          className="size-4 rounded-full transition-colors duration-300"
          style={index < found ? { background: hue(color) } : { boxShadow: "inset 0 0 0 2px var(--color-text-muted)" }}
        />
      ))}
    </div>
  );
}

/** The target ring, a stamp per input found, and once solved the full line of solutions (with the null space dashed when they differ). */
function HuntMarks({ solved, found, target, direction, color }: { solved: boolean; found: string[]; target: Vec; direction: Vec; color: Hue }) {
  const showLine = solved && found.length > 0;
  return (
    <>
      {showLine && !isZero(target) ? <LineThrough point={[0, 0]} direction={direction} color="pink" faint /> : null}
      {showLine ? <LineThrough point={keyPoint(found[0])} direction={direction} color={color} /> : null}
      <Marker at={target} color="glow" ring />
      {found.map((key) => (
        <Marker key={key} at={keyPoint(key)} color={color} />
      ))}
    </>
  );
}

const matrixTex = (matrix: Matrix2) => `\\begin{bmatrix} ${matrix[0].map((v) => texNumber(v)).join(" & ")} \\\\ ${matrix[1].map((v) => texNumber(v)).join(" & ")} \\end{bmatrix}`;
const colTex = (v: Vec, color?: string) => {
  const body = `\\begin{bmatrix} ${texNumber(v[0])} \\\\ ${texNumber(v[1])} \\end{bmatrix}`;
  return color ? `\\textcolor{${color}}{${body}}` : body;
};

/** Drag x until A x lands on the target; each distinct settled hit is stamped, and enough hits reveal the whole line of them. */
export function LandingHunt({
  matrix,
  target = [0, 0],
  start = [1, 1],
  needed = 2,
  prompt,
  success,
}: {
  matrix: Matrix2;
  target?: Vec;
  start?: Vec;
  needed?: number;
  prompt: string;
  success: string;
}) {
  const [x, setX] = useState<Vec>(start);
  const [found, setFound] = useState<string[]>([]);
  const { settled, gesture } = useSettled(pointKey(x));
  if (landsOnTarget(matrix, keyPoint(settled), target) && !found.includes(settled)) setFound([...found, settled]);
  const solved = found.length >= needed;
  const homogeneous = isZero(target);
  const stampColor: Hue = homogeneous ? "pink" : "yellow";
  const output = apply(matrix, x);

  return (
    <Panel gesture={gesture}>
      <Goal solved={solved} prompt={<RichText>{prompt}</RichText>} success={<RichText>{success}</RichText>} />
      <Workbench
        plane={
          <Plane bounds={COLLECTOR_BOUNDS} label={`Input x at ${describeVector(x)} and its output A x at ${describeVector(output)}. Drag the tip of x or use the arrow keys.`}>
            <HuntMarks solved={solved} found={found} target={target} direction={nullDirection(matrix)} color={stampColor} />
            <Arrow to={output} color="teal" />
            <Arrow to={x} color="yellow" />
            <Label at={x} color="yellow">x</Label>
            <Label at={output} color="teal" dy={22}>Ax</Label>
            <Handle at={x} onMove={setX} color="yellow" label={`Tip of the input x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`${matrixTex(matrix)}${colTex(x, palette.yellow)} = ${colTex(output, palette.teal)}`} />
            <div className="flex items-center justify-between gap-3 rounded-lg bg-surface-sunken px-4 py-3 text-meta text-text-muted">
              <span>
                Inputs that land on <Tex>{homogeneous ? "\\mathbf 0" : `\\mathbf b = ${colTex(target)}`}</Tex>
              </span>
              <FoundSlots found={found.length} needed={needed} color={stampColor} />
            </div>
          </>
        }
      />
    </Panel>
  );
}

type Vec4 = [number, number, number, number];

const combine = (s: number, u: Vec4, t: number, v: Vec4): Vec4 => u.map((entry, i) => s * entry + t * v[i]) as Vec4;

function columnWithMatches(entries: Vec4, target: Vec4, freeRows: number[], matched: boolean) {
  const rows = entries.map((entry, i) => {
    const color = matched && entry === target[i] ? palette.teal : freeRows.includes(i) ? palette.glow : palette.text;
    return `\\textcolor{${color}}{${texNumber(entry)}}`;
  });
  return `\\begin{bmatrix} ${rows.join(" \\\\ ")} \\end{bmatrix}`;
}

const weightTex = (value: number) => (value < 0 ? `(${texNumber(value)})` : texNumber(value));

const plainColumn = (entries: number[], color: string) => `\\textcolor{${color}}{\\begin{bmatrix} ${entries.map((e) => texNumber(e)).join(" \\\\ ")} \\end{bmatrix}}`;

/** Two sliders weight the null-space basis vectors; the free rows of the result read the weights back directly. */
export function FreeWeights({ u, v, target, freeRows = [1, 3] }: { u: Vec4; v: Vec4; target: Vec4; freeRows?: number[] }) {
  const [s, setS] = useState(0);
  const [t, setT] = useState(0);
  const { settled, gesture } = useSettled(`${s},${t}`);
  const [settledS, settledT] = settled.split(",").map(Number);
  const settledX = combine(settledS, u, settledT, v);
  const solved = settledX.every((entry, i) => entry === target[i]);
  const x = combine(s, u, t, v);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Build <Tex>{`\\mathbf x = ${plainColumn(target, palette.pink)}`}</Tex> from the basis. Look at rows {freeRows[0] + 1} and {freeRows[1] + 1} first.</>}
        success={<>Rows {freeRows[0] + 1} and {freeRows[1] + 1} of <Tex>{"\\mathbf x"}</Tex> are the weights themselves, so <Tex>{`x_${freeRows[0] + 1} = ${texNumber(s)}`}</Tex> and <Tex>{`x_${freeRows[1] + 1} = ${texNumber(t)}`}</Tex> is the only way to build it.</>}
      />
      <div className="grid items-start gap-5 md:grid-cols-[1fr_1.35fr]">
        <div className="space-y-4">
          <Slider label={`x_${freeRows[0] + 1}`} value={s} onChange={setS} min={-3} max={3} step={1} color={palette.yellow} />
          <Slider label={`x_${freeRows[1] + 1}`} value={t} onChange={setT} min={-3} max={3} step={1} color={palette.blue} />
        </div>
        <Readout
          tex={`\\mathbf x = ${weightTex(s)}${plainColumn(u, palette.yellow)} + ${weightTex(t)}${plainColumn(v, palette.blue)} = ${columnWithMatches(x, target, freeRows, solved)}`}
        />
      </div>
    </Panel>
  );
}
