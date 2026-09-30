"use client";

import { Check } from "@phosphor-icons/react";
import { useId, useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, nearlyEqual, scale, texNumber, type Vec } from "./math";
import { Arrow, Handle, Label, Marker, Plane, Segment, usePlane } from "./plane";
import { polynomialTex } from "./vector-spaces";

type Coefficients = [number, number, number];
type Window = { tMin: number; tMax: number; yMin: number; yMax: number };

const WIDTH = 420;
const HEIGHT = 340;
const BASIS_HUES: Hue[] = ["green", "red", "blue"];
const BASIS_TEX_COLORS = [palette.i_hat, palette.j_hat, palette.blue];

const evaluate = (coeffs: Coefficients, t: number) => coeffs[0] + coeffs[1] * t + coeffs[2] * t * t;
const sameCoefficients = (p: Coefficients, q: Coefficients) => p.every((value, index) => Math.abs(value - q[index]) < 1e-9);
const derivative = (p: Coefficients): Coefficients => [p[1], 2 * p[2], 0];

function toGraph(window: Window, t: number, y: number): Vec {
  return [
    ((t - window.tMin) / (window.tMax - window.tMin)) * WIDTH,
    ((window.yMax - y) / (window.yMax - window.yMin)) * HEIGHT,
  ];
}

function curvePath(window: Window, coeffs: Coefficients): string {
  const steps = 90;
  return Array.from({ length: steps + 1 }, (_, i) => {
    const t = window.tMin + ((window.tMax - window.tMin) * i) / steps;
    const [x, y] = toGraph(window, t, evaluate(coeffs, t));
    return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
}

function GraphGrid({ window }: { window: Window }) {
  const [originX, originY] = toGraph(window, 0, 0);
  const levels = Array.from({ length: Math.floor(window.yMax / 2) - Math.ceil(window.yMin / 2) + 1 }, (_, i) => 2 * (Math.ceil(window.yMin / 2) + i));
  const ticks = Array.from({ length: Math.floor(window.tMax) - Math.ceil(window.tMin) + 1 }, (_, i) => Math.ceil(window.tMin) + i);
  return (
    <g aria-hidden>
      {levels.map((y) => {
        const [, py] = toGraph(window, 0, y);
        return <line key={`y${y}`} x1={0} x2={WIDTH} y1={py} y2={py} stroke="var(--palette-grid)" strokeOpacity={0.35} strokeWidth={1} />;
      })}
      {ticks.map((t) => {
        const [px] = toGraph(window, t, 0);
        return <line key={`t${t}`} x1={px} x2={px} y1={0} y2={HEIGHT} stroke="var(--palette-grid)" strokeOpacity={0.35} strokeWidth={1} />;
      })}
      <line x1={0} x2={WIDTH} y1={originY} y2={originY} stroke="var(--palette-axis)" strokeOpacity={0.9} strokeWidth={1.6} />
      <line x1={originX} x2={originX} y1={0} y2={HEIGHT} stroke="var(--palette-axis)" strokeOpacity={0.9} strokeWidth={1.6} />
      <text x={WIDTH - 14} y={originY - 8} fill="var(--palette-text-muted)" fontSize={15} fontStyle="italic" fontFamily="KaTeX_Math, serif">t</text>
    </g>
  );
}

function Curve({ window, coeffs, color, width = 3.5, dashed = false }: { window: Window; coeffs: Coefficients; color: Hue; width?: number; dashed?: boolean }) {
  return (
    <path
      d={curvePath(window, coeffs)}
      fill="none"
      stroke={hue(color)}
      strokeWidth={width}
      strokeLinecap="round"
      strokeDasharray={dashed ? "7 7" : undefined}
      className="transition-[stroke-width] duration-150"
    />
  );
}

function Graph({ window, label, children }: { window: Window; label: string; children: React.ReactNode }) {
  const clipId = `${useId().replaceAll(":", "")}-clip`;
  return (
    <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label={label} className="block h-auto w-full select-none rounded-media bg-surface-sunken">
      <defs>
        <clipPath id={clipId}>
          <rect width={WIDTH} height={HEIGHT} />
        </clipPath>
      </defs>
      <GraphGrid window={window} />
      <g clipPath={`url(#${clipId})`}>{children}</g>
    </svg>
  );
}

function coloredMatrixTex(columns: Coefficients[]): string {
  const rows = [0, 1, 2].map((row) => columns.map((col, index) => `\\textcolor{${BASIS_TEX_COLORS[index]}}{${texNumber(col[row])}}`).join(" & "));
  return `\\begin{bmatrix} ${rows.join(" \\\\ ")} \\end{bmatrix}`;
}

const plainColumnTex = (entries: number[], color?: string) => {
  const body = `\\begin{bmatrix} ${entries.map((value) => texNumber(value)).join(" \\\\ ")} \\end{bmatrix}`;
  return color ? `\\textcolor{${color}}{${body}}` : body;
};

function ColumnTab({ index, name, selected, done, onSelect }: { index: number; name: string; selected: boolean; done: boolean; onSelect: () => void }) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      aria-label={`Build column ${index + 1}, the image of ${name.replace("^2", " squared")}${done ? ", finished" : ""}`}
      onClick={onSelect}
      className={`relative rounded-lg px-3 py-2 text-meta transition-[background-color,box-shadow] duration-150 active:scale-[0.96] ${
        selected ? "bg-line ring-2 ring-[var(--palette-text)]" : "bg-surface-sunken hover:bg-line"
      }`}
    >
      <Tex>{`T(\\textcolor{${BASIS_TEX_COLORS[index]}}{${name}})`}</Tex>
      <span className={`absolute -right-1.5 -top-1.5 grid size-5 place-items-center rounded-full bg-[var(--palette-teal)] ${done ? "swap-shown" : "swap-hidden"}`} aria-hidden>
        <Check weight="bold" className="size-3 text-surface" />
      </span>
    </button>
  );
}

const BUILDER_WINDOW: Window = { tMin: -2, tMax: 1.5, yMin: -4, yMax: 8 };
const ZERO_COLUMNS: Coefficients[] = [[0, 0, 0], [0, 0, 0], [0, 0, 0]];

/** Build [T]_B one column at a time: for each basis polynomial, set a column whose polynomial matches the dashed image T(b_j). */
export function ColumnBuilder({ images, names = ["1", "t", "t^2"], mapTex }: { images: Coefficients[]; names?: string[]; mapTex: string }) {
  const [columns, setColumns] = useState<Coefficients[]>(ZERO_COLUMNS);
  const [active, setActive] = useState(0);
  const { settled, gesture } = useSettled(JSON.stringify(columns));
  const settledColumns = JSON.parse(settled) as Coefficients[];
  const done = images.map((image, index) => sameCoefficients(settledColumns[index], image));
  const solved = done.every(Boolean);
  const setEntry = (row: number) => (value: number) =>
    setColumns((current) => current.map((col, index) => (index === active ? (col.map((old, r) => (r === row ? value : old)) as Coefficients) : col)));
  const current = columns[active];

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Let <Tex>{mapTex}</Tex>. Pick each basis polynomial, then set its column so the solid curve lands on the dashed image.</>}
        success={<>All three columns are in. Each one lists the coefficients of <Tex>{"T(\\mathbf b_j)"}</Tex>, so this is <Tex>{"[T]_{\\mathcal B}"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Graph window={BUILDER_WINDOW} label={`Graph of the image of ${names[active]} as a dashed curve, and the polynomial ${polynomialTex(current)} built from column ${active + 1}`}>
            <Curve window={BUILDER_WINDOW} coeffs={images[active]} color="text" width={2.5} dashed />
            <Curve window={BUILDER_WINDOW} coeffs={current} color={BASIS_HUES[active]} width={done[active] ? 5 : 3.5} />
          </Graph>
        }
        readout={
          <>
            <div className="flex flex-wrap gap-2" role="group" aria-label="Choose a column to build">
              {names.map((name, index) => (
                <ColumnTab key={name} index={index} name={name} selected={index === active} done={done[index]} onSelect={() => setActive(index)} />
              ))}
            </div>
            {["a_0", "a_1", "a_2"].map((name, row) => (
              <Slider key={name} label={name} value={current[row]} onChange={setEntry(row)} min={-3} max={3} step={1} color={BASIS_TEX_COLORS[active]} />
            ))}
            <Readout tex={`[T]_{\\mathcal B} = ${coloredMatrixTex(columns)}`} />
          </>
        }
      />
    </Panel>
  );
}

const ROUTES_WINDOW: Window = { tMin: -1.5, tMax: 1.5, yMin: -10, yMax: 10 };
const DERIVATIVE_MATRIX_TEX = `\\begin{bmatrix} \\textcolor{${palette.i_hat}}{0} & \\textcolor{${palette.j_hat}}{1} & \\textcolor{${palette.blue}}{0} \\\\ \\textcolor{${palette.i_hat}}{0} & \\textcolor{${palette.j_hat}}{0} & \\textcolor{${palette.blue}}{2} \\\\ \\textcolor{${palette.i_hat}}{0} & \\textcolor{${palette.j_hat}}{0} & \\textcolor{${palette.blue}}{0} \\end{bmatrix}`;

/** Choose p with sliders; [T]_B times [p]_B gives the coordinates of p'. The goal is a prescribed derivative, which fixes a1 and a2 but not a0. */
export function DerivativeRoutes({ target, start = [1, 1, 1] }: { target: Coefficients; start?: Coefficients }) {
  const [p, setP] = useState<Coefficients>(start);
  const slope = derivative(p);
  const { settled: solved, gesture } = useSettled(sameCoefficients(slope, target));
  const setEntry = (index: number) => (value: number) => setP((current) => current.map((old, i) => (i === index ? value : old)) as Coefficients);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Choose <Tex>{"\\mathbf p"}</Tex> so that its derivative, the teal curve, lands on the dashed target <Tex>{`${polynomialTex(target)}`}</Tex>.</>}
        success={<>That works. Now move <Tex>{"a_0"}</Tex>: the teal curve stays put, because column 1 of <Tex>{"[T]_{\\mathcal B}"}</Tex> is all zeros.</>}
      />
      <Workbench
        plane={
          <Graph window={ROUTES_WINDOW} label={`Graph of p, which is ${polynomialTex(p)}, its derivative ${polynomialTex(slope)}, and the dashed target`}>
            <Curve window={ROUTES_WINDOW} coeffs={target} color={solved ? "teal" : "text"} width={2.5} dashed />
            <Curve window={ROUTES_WINDOW} coeffs={p} color="yellow" width={2.5} />
            <Curve window={ROUTES_WINDOW} coeffs={slope} color="teal" width={solved ? 5 : 3.5} />
          </Graph>
        }
        readout={
          <>
            {["a_0", "a_1", "a_2"].map((name, index) => (
              <Slider key={name} label={name} value={p[index]} onChange={setEntry(index)} min={-5} max={5} step={1} color={palette.yellow} />
            ))}
            <Readout tex={`\\textcolor{${palette.yellow}}{\\mathbf p(t)} = \\textcolor{${palette.yellow}}{${polynomialTex(p)}}`} />
            <Readout tex={`${DERIVATIVE_MATRIX_TEX}${plainColumnTex(p, palette.yellow)} = ${plainColumnTex(slope, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}

function twoColumnTex(first: Vec, second: Vec): string {
  const g = (value: number) => `\\textcolor{${palette.i_hat}}{${texNumber(value)}}`;
  const r = (value: number) => `\\textcolor{${palette.j_hat}}{${texNumber(value)}}`;
  return `\\begin{bmatrix} ${g(first[0])} & ${r(second[0])} \\\\ ${g(first[1])} & ${r(second[1])} \\end{bmatrix}`;
}

function StepPath({ images, x }: { images: [Vec, Vec]; x: Vec }) {
  const firstLeg = scale(x[0], images[0]);
  return (
    <>
      <Arrow to={firstLeg} color="green" width={2.5} dashed />
      <Arrow from={firstLeg} to={add(firstLeg, scale(x[1], images[1]))} color="red" width={2.5} dashed />
    </>
  );
}

/** T is known only through T(e1) and T(e2). Drag the teal point to where T(x) must land; once it does, the column path appears. */
export function LandingPredict({ images, x }: { images: [Vec, Vec]; x: Vec }) {
  const [guess, setGuess] = useState<Vec>([0, 0]);
  const landing = add(scale(x[0], images[0]), scale(x[1], images[1]));
  const { settled: solved, gesture } = useSettled(nearlyEqual(guess, landing));
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The green and red arrows are <Tex>{"T(\\mathbf e_1)"}</Tex> and <Tex>{"T(\\mathbf e_2)"}</Tex>. Drag the teal point to <Tex>{`T${columnTex(x)}`}</Tex>.</>}
        success={<>Right. The dashed path is <Tex>{`${texNumber(x[0])}\\,T(\\mathbf e_1) + ${texNumber(x[1])}\\,T(\\mathbf e_2)`}</Tex>, which is <Tex>{"A"}</Tex> times <Tex>{columnTex(x)}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={{ xMin: -6, xMax: 6, yMin: -4, yMax: 5 }} label="Plane showing T of e1 in green and T of e2 in red, with a draggable teal point">
            {solved ? <StepPath images={images} x={x} /> : null}
            <Arrow to={images[0]} color="green" />
            <Arrow to={images[1]} color="red" />
            <Label at={images[0]} color="green">T(e₁)</Label>
            <Label at={images[1]} color="red" dx={-58}>T(e₂)</Label>
            {solved ? <Marker at={landing} color="teal" ring /> : null}
            <Handle at={guess} onMove={setGuess} color="teal" label={`Guess for T of x, at ${describeVector(guess)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`A = ${twoColumnTex(images[0], images[1])}`} />
            <Readout tex={`\\text{your point} = ${columnTex(guess, palette.teal)}`} />
          </>
        }
      />
    </Panel>
  );
}

const DEGREE = Math.PI / 180;
const roundTo = (value: number) => Math.round(value * 100) / 100 + 0;

function rotated(angle: number, v: Vec): Vec {
  const [c, s] = [Math.cos(angle * DEGREE), Math.sin(angle * DEGREE)];
  return [roundTo(c * v[0] - s * v[1]), roundTo(s * v[0] + c * v[1])];
}

const rotationMatrixTex = (angle: number) => twoColumnTex(rotated(angle, [1, 0]), rotated(angle, [0, 1]));

function UnitCircle() {
  const points = Array.from({ length: 73 }, (_, i) => rotated(i * 5, [1, 0]));
  return (
    <g opacity={0.45}>
      {points.slice(1).map((point, i) => (
        <Segment key={i} from={points[i]} to={point} color="text" dashed={false} />
      ))}
    </g>
  );
}

function RingMark({ at, color, filled }: { at: Vec; color: Hue; filled: boolean }) {
  const { toSvg } = usePlane();
  const [x, y] = toSvg(at);
  return (
    <circle
      cx={x}
      cy={y}
      r={8}
      fill={hue(color)}
      fillOpacity={filled ? 0.35 : 0}
      stroke={hue(color)}
      strokeWidth={1.5}
      strokeDasharray={filled ? undefined : "3 3"}
      className="transition-[fill-opacity]"
    />
  );
}

/** Turn the plane with a slider; the columns of the rotation matrix are the tips of the turned e1 and e2. */
export function RotationColumns({ target }: { target: number }) {
  const [angle, setAngle] = useState(0);
  const { settled: solved, gesture } = useSettled(angle === target);
  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Turn the plane counterclockwise by <Tex>{"\\varphi"}</Tex> degrees until its standard matrix is <Tex>{rotationMatrixTex(target)}</Tex>. The rings mark where those columns say the arrows end.</>}
        success={<>A turn of {target}° does it. The first column is where <Tex>{"\\mathbf e_1"}</Tex> ends and the second is where <Tex>{"\\mathbf e_2"}</Tex> ends.</>}
      />
      <Workbench
        plane={
          <Plane bounds={{ xMin: -2, xMax: 2, yMin: -2, yMax: 2 }} label={`Unit circle with e1 and e2 turned by ${angle} degrees`}>
            <UnitCircle />
            <RingMark at={rotated(target, [1, 0])} color="green" filled={solved} />
            <RingMark at={rotated(target, [0, 1])} color="red" filled={solved} />
            <Arrow to={rotated(angle, [1, 0])} color="green" width={2} />
            <Arrow to={rotated(angle, [0, 1])} color="red" width={2} />
          </Plane>
        }
        readout={
          <>
            <Slider label="\varphi" value={angle} onChange={setAngle} min={0} max={345} step={15} color={palette.teal} />
            <Readout tex={`A = ${rotationMatrixTex(angle)}`} />
          </>
        }
      />
    </Panel>
  );
}
