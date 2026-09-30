"use client";

import { CheckCircle, Circle } from "@phosphor-icons/react";
import { useId, useState } from "react";
import { palette } from "@/lib/palette.generated";
import { hue, type Hue } from "./colors";
import { columnTex, describeVector, Goal, Panel, Readout, Slider, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { add, scale, texNumber, type Vec } from "./math";
import { Arrow, boundsAround, Handle, Label, Marker, Plane, usePlane } from "./plane";
import { polynomialTex } from "./vector-spaces";

const cross = (a: Vec, b: Vec) => a[0] * b[1] - a[1] * b[0];
const isZero = (v: Vec) => v[0] === 0 && v[1] === 0;

function FullLine({ direction, through = [0, 0], color, width, opacity }: { direction: Vec; through?: Vec; color: Hue; width: number; opacity: number }) {
  const { toSvg, bounds } = usePlane();
  const reach = (bounds.xMax - bounds.xMin + bounds.yMax - bounds.yMin) / Math.max(Math.hypot(...direction), 1e-9);
  const [x1, y1] = toSvg(add(through, scale(-reach, direction)));
  const [x2, y2] = toSvg(add(through, scale(reach, direction)));
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={width} strokeOpacity={opacity} strokeLinecap="round" />;
}

/** The lines a·u + t·v and t·u + b·v for whole-number a and b: the grid a basis draws on the plane. */
function BasisGrid({ u, v, reach = 14, opacity = 0.45 }: { u: Vec; v: Vec; reach?: number; opacity?: number }) {
  const weights = Array.from({ length: 2 * reach + 1 }, (_, i) => i - reach);
  return (
    <g aria-hidden>
      {weights.map((k) => <FullLine key={`u${k}`} through={scale(k, u)} direction={v} color="teal" width={1.2} opacity={opacity} />)}
      {weights.map((k) => <FullLine key={`v${k}`} through={scale(k, v)} direction={u} color="teal" width={1.2} opacity={opacity} />)}
    </g>
  );
}

type Member = { name: string; vector: Vec; color: Hue };

/** Rank of a set of plane vectors: 0, 1 or 2. */
function rank(vectors: Vec[]): number {
  const nonzero = vectors.filter((v) => !isZero(v));
  if (nonzero.length === 0) return 0;
  return nonzero.some((v) => cross(nonzero[0], v) !== 0) ? 2 : 1;
}

function independentPair(vectors: Vec[]): [Vec, Vec] | null {
  for (const first of vectors) {
    const partner = vectors.find((v) => cross(first, v) !== 0);
    if (partner) return [first, partner];
  }
  return null;
}

function SpanPicture({ kept }: { kept: Vec[] }) {
  const pair = independentPair(kept);
  if (pair) return <BasisGrid u={pair[0]} v={pair[1]} />;
  const direction = kept.find((v) => !isZero(v));
  return direction ? <FullLine direction={direction} color="teal" width={4} opacity={0.85} /> : null;
}

function Light({ on, children }: { on: boolean; children: React.ReactNode }) {
  return (
    <div className={`flex items-center gap-3 rounded-lg px-4 py-3 transition-colors duration-300 ${on ? "bg-[color-mix(in_oklab,var(--palette-teal)_16%,transparent)]" : "bg-surface-sunken"}`}>
      <span className="grid shrink-0">
        <CheckCircle weight="fill" aria-hidden className={`size-5 text-[var(--palette-teal)] [grid-area:1/1] ${on ? "swap-shown" : "swap-hidden"}`} />
        <Circle aria-hidden className={`size-5 text-text-muted [grid-area:1/1] ${on ? "swap-hidden" : "swap-shown"}`} />
      </span>
      <span className={on ? "text-text" : "text-text-muted"}>{children}</span>
      <span className="sr-only">{on ? "passes" : "fails"}</span>
    </div>
  );
}

const TEX_COLORS: Record<Hue, string> = {
  yellow: palette.yellow,
  blue: palette.blue,
  teal: palette.teal,
  pink: palette.pink,
  green: palette.i_hat,
  red: palette.j_hat,
  glow: palette.glow,
  text: palette.text,
};

function KeepToggle({ member, kept, onToggle }: { member: Member; kept: boolean; onToggle: () => void }) {
  return (
    <button
      type="button"
      aria-label={`${kept ? "Drop" : "Bring back"} vector ${member.name.replace("\\mathbf ", "")}`}
      onClick={onToggle}
      className={`whitespace-nowrap rounded-lg px-3 py-2 text-meta font-semibold transition-colors duration-200 ${
        kept ? "bg-surface-sunken text-text hover:bg-line" : "bg-text text-surface"
      }`}
    >
      {kept ? "Drop " : "Bring back "}
      <Tex>{`\\textcolor{${TEX_COLORS[member.color]}}{${member.name}}`}</Tex>
    </button>
  );
}

const TRIM_MEMBERS: Member[] = [
  { name: "\\mathbf a", vector: [2, 1], color: "yellow" },
  { name: "\\mathbf b", vector: [-1, 1], color: "blue" },
  { name: "\\mathbf c", vector: [4, 2], color: "pink" },
];

/** Three vectors that span the plane with one to spare. Dropping the right one leaves a basis; dropping the wrong one shrinks the span. */
export function TrimToBasis({ members = TRIM_MEMBERS }: { members?: Member[] }) {
  const [kept, setKept] = useState(members.map(() => true));
  const keptVectors = members.filter((_, index) => kept[index]).map((member) => member.vector);
  const spans = rank(keptVectors) === 2;
  const independent = keptVectors.length > 0 && rank(keptVectors) === keptVectors.length;
  const { settled: solved, gesture } = useSettled(spans && independent);
  const toggle = (index: number) => setKept((current) => current.map((value, i) => (i === index ? !value : value)));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>These three vectors span the plane, but one of them is spare. Drop vectors until both lights are on.</>}
        success={<>That set is a basis. It still spans the plane, and none of its vectors is a combination of the others.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround(members.map((member) => member.vector))} label="Plane with the kept vectors and the teal span they cover.">
            <SpanPicture kept={keptVectors} />
            {members.map((member, index) => (
              <g key={member.name} opacity={kept[index] ? 1 : 0.25}>
                <Arrow to={member.vector} color={member.color} dashed={!kept[index]} />
                <Label at={member.vector} color={member.color} dx={member.vector[0] < 0 ? -18 : 10}>{member.name.replace("\\mathbf ", "")}</Label>
              </g>
            ))}
          </Plane>
        }
        readout={
          <>
            <div className="flex flex-wrap gap-2">
              {members.map((member, index) => (
                <KeepToggle key={member.name} member={member} kept={kept[index]} onToggle={() => toggle(index)} />
              ))}
            </div>
            <Light on={spans}>
              Spans <Tex>{"\\mathbb{R}^2"}</Tex>
            </Light>
            <Light on={independent}>Linearly independent</Light>
            <Readout tex={`\\textcolor{${palette.pink}}{\\mathbf c} = 2\\,\\textcolor{${palette.yellow}}{\\mathbf a} + 0\\,\\textcolor{${palette.blue}}{\\mathbf b}`} />
          </>
        }
      />
    </Panel>
  );
}

/** A number of thirds as TeX, e.g. 5/3 becomes \tfrac{5}{3}. */
function thirdsTex(numerator: number): string {
  if (numerator % 3 === 0) return texNumber(numerator / 3);
  const sign = numerator < 0 ? "-" : "";
  return `${sign}\\tfrac{${Math.abs(numerator)}}{3}`;
}

const ADDRESS_B1: Vec = [2, 1];
const ADDRESS_B2: Vec = [-1, 1];

/** Weights times 3 for x in the basis {(2, 1), (-1, 1)}, whose matrix has determinant 3. */
const tripledAddress = (x: Vec): Vec => [x[0] + x[1], -x[0] + 2 * x[1]];

/** Drag a point and read its address on the standard grid and on the skewed grid of b1 and b2. */
export function AddressHunt({ start = [1, 5], target = [-1, 2] }: { start?: Vec; target?: Vec }) {
  const [x, setX] = useState<Vec>(start);
  const tripled = tripledAddress(x);
  const weights: Vec = [tripled[0] / 3, tripled[1] / 3];
  const { settled: solved, gesture } = useSettled(tripled[0] === 3 * target[0] && tripled[1] === 3 * target[1]);
  const corner = scale(weights[0], ADDRESS_B1);
  const goalPoint = add(scale(target[0], ADDRESS_B1), scale(target[1], ADDRESS_B2));
  const b1 = `\\textcolor{${palette.yellow}}{\\mathbf b_1}`;
  const b2 = `\\textcolor{${palette.blue}}{\\mathbf b_2}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf x"}</Tex> to the point whose address in the basis <Tex>{`\\{${b1}, ${b2}\\}`}</Tex> is <Tex>{`(${texNumber(target[0])}, ${texNumber(target[1])})`}</Tex>, meaning <Tex>{`${texNumber(target[0])}\\,${b1} + ${texNumber(target[1])}\\,${b2}`}</Tex>.</>}
        success={<>Found it. On the standard grid the same point has the address <Tex>{`(${texNumber(x[0])}, ${texNumber(x[1])})`}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([start, goalPoint, [-5, -2]])} label="Standard grid with the teal grid of b1 and b2 on top, the draggable point x and the path of its b-address.">
            <BasisGrid u={ADDRESS_B1} v={ADDRESS_B2} opacity={0.4} />
            <Arrow to={corner} color="yellow" width={2.5} />
            <Arrow from={corner} to={x} color="blue" width={2.5} />
            <Arrow to={ADDRESS_B1} color="yellow" />
            <Arrow to={ADDRESS_B2} color="blue" />
            <Label at={ADDRESS_B1} color="yellow" dy={18}>b1</Label>
            <Label at={ADDRESS_B2} color="blue" dx={-24} dy={18}>b2</Label>
            {solved ? <Marker at={x} color="teal" ring /> : null}
            <Label at={x} color="teal">x</Label>
            <Handle at={x} onMove={setX} color="teal" label={`Point x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={`\\mathbf x = ${texNumber(x[0])}\\,\\textcolor{${palette.i_hat}}{\\mathbf e_1} + ${texNumber(x[1])}\\,\\textcolor{${palette.j_hat}}{\\mathbf e_2}`} />
            <Readout tex={`\\mathbf x = ${thirdsTex(tripled[0])}\\,${b1} + ${thirdsTex(tripled[1])}\\,${b2}`} />
          </>
        }
      />
    </Panel>
  );
}

type Coefficients = [number, number, number];

const GRAPH = { tMin: -0.5, tMax: 2.5, yMin: -6, yMax: 12, width: 420, height: 360 };

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
  const horizontal = [-4, 0, 4, 8];
  const vertical = [0, 1, 2];
  const stroke = (axis: boolean) => ({ stroke: axis ? "var(--palette-axis)" : "var(--palette-grid)", strokeOpacity: axis ? 0.9 : 0.4, strokeWidth: axis ? 1.6 : 1 });
  return (
    <g aria-hidden>
      {horizontal.map((y) => <line key={`y${y}`} x1={0} x2={GRAPH.width} y1={toGraph(0, y)[1]} y2={toGraph(0, y)[1]} {...stroke(y === 0)} />)}
      {vertical.map((t) => <line key={`t${t}`} x1={toGraph(t, 0)[0]} x2={toGraph(t, 0)[0]} y1={0} y2={GRAPH.height} {...stroke(t === 0)} />)}
      {[1, 2].map((t) => <text key={`n${t}`} x={toGraph(t, 0)[0] + 4} y={toGraph(t, 0)[1] + 16} fill="var(--palette-text-muted)" fontSize={13}>{t}</text>)}
      {[4, 8].map((y) => <text key={`m${y}`} x={toGraph(0, y)[0] + 6} y={toGraph(0, y)[1] - 4} fill="var(--palette-text-muted)" fontSize={13}>{y}</text>)}
    </g>
  );
}

const STAIRCASE: Coefficients[] = [
  [1, 0, 0],
  [1, 1, 0],
  [1, 1, 1],
];
const STAIRCASE_TEX = ["1", "(1 + t)", "(1 + t + t^2)"];
const STAIRCASE_HUES = [palette.i_hat, palette.j_hat, palette.pink];

const combineStaircase = (weights: number[]): Coefficients =>
  [0, 1, 2].map((power) => weights.reduce((sum, weight, index) => sum + weight * STAIRCASE[index][power], 0)) as Coefficients;

const sameCoefficients = (p: Coefficients, q: Coefficients) => p.every((value, index) => value === q[index]);

function signedWeight(weight: number, index: number): string {
  const colored = (value: number) => `\\textcolor{${STAIRCASE_HUES[index]}}{${texNumber(value)}}`;
  if (index === 0) return `{${colored(weight)}}`;
  return weight < 0 ? `- ${colored(-weight)}` : `+ ${colored(weight)}`;
}

/** One line per basis polynomial, then the total, so the readout stays narrow. */
function combinationTex(weights: number[], result: Coefficients): string {
  const lines = weights.map((weight, index) => `& ${signedWeight(weight, index)}${index === 0 ? "" : `\\,${STAIRCASE_TEX[index]}`}`);
  return `\\begin{aligned} ${lines.join(" \\\\ ")} \\\\ &= \\textcolor{${palette.teal}}{${polynomialTex(result)}} \\end{aligned}`;
}

/** Weights on the basis 1, 1 + t, 1 + t + t² of P₂, tuned until the teal curve lands on a dashed target. */
export function StaircaseBasis({ target = [2, 3, 1] }: { target?: Coefficients }) {
  const [weights, setWeights] = useState([0, 0, 0]);
  const result = combineStaircase(weights);
  const { settled: solved, gesture } = useSettled(sameCoefficients(result, target));
  const clipId = `${useId().replaceAll(":", "")}-clip`;
  const setWeight = (index: number) => (value: number) => setWeights((current) => current.map((w, i) => (i === index ? value : w)));

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The set <Tex>{"\\{1,\\ 1 + t,\\ 1 + t + t^2\\}"}</Tex> is also a basis for <Tex>{"\\mathbb P_2"}</Tex>. Find the weights that build the dashed target <Tex>{polynomialTex(target)}</Tex>.</>}
        success={<>These weights are the address of <Tex>{polynomialTex(target)}</Tex> in this basis. Because the set is a basis, no other weights build it.</>}
      />
      <Workbench
        plane={
          <svg viewBox={`0 0 ${GRAPH.width} ${GRAPH.height}`} role="img" aria-label={`Graph of the target ${polynomialTex(target)} and the current combination ${polynomialTex(result)}`} className="block h-auto w-full select-none rounded-media bg-surface-sunken">
            <defs>
              <clipPath id={clipId}>
                <rect width={GRAPH.width} height={GRAPH.height} />
              </clipPath>
            </defs>
            <GraphLines />
            <g clipPath={`url(#${clipId})`}>
              <path d={curvePath(target)} fill="none" stroke={hue(solved ? "teal" : "text")} strokeWidth={2.5} strokeDasharray="7 7" />
              <path d={curvePath(result)} fill="none" stroke={hue("teal")} strokeWidth={solved ? 5 : 3.5} strokeLinecap="round" />
            </g>
          </svg>
        }
        readout={
          <>
            <Slider label="c_1" value={weights[0]} onChange={setWeight(0)} min={-3} max={3} step={1} color={palette.i_hat} />
            <Slider label="c_2" value={weights[1]} onChange={setWeight(1)} min={-3} max={3} step={1} color={palette.j_hat} />
            <Slider label="c_3" value={weights[2]} onChange={setWeight(2)} min={-3} max={3} step={1} color={palette.pink} />
            <Readout tex={combinationTex(weights, result)} />
          </>
        }
      />
    </Panel>
  );
}

const RECIPE_BOUNDS = { xMin: -5, xMax: 5, yMin: -3, yMax: 7 };

/**
 * A basis b1, b2 plus a spare vector u = b1 + b2. The learner finds a recipe for x that uses u, which shows that a
 * spanning set with a spare vector gives more than one list of weights.
 */
export function SpareRecipe({ b1, b2, x }: { b1: Vec; b2: Vec; x: Vec }) {
  const [weights, setWeights] = useState([0, 0, 0]);
  const spare = add(b1, b2);
  const vectors = [b1, b2, spare];
  const tips = vectors.reduce<Vec[]>((list, vector, index) => [...list, add(list[index], scale(weights[index], vector))], [[0, 0]]);
  const end = tips[3];
  const reached = end[0] === x[0] && end[1] === x[1] && weights[2] !== 0;
  const { settled: solved, gesture } = useSettled(reached);
  const setWeight = (index: number) => (value: number) => setWeights((current) => current.map((old, i) => (i === index ? value : old)));
  const hues: Hue[] = ["yellow", "blue", "pink"];
  const colors = [palette.yellow, palette.blue, palette.pink];
  const names = ["\\mathbf b_1", "\\mathbf b_2", "\\mathbf u"];
  const sum = weights.map((weight, index) => `${index === 0 ? "" : "+"} ${texNumber(weight)}\\,\\textcolor{${colors[index]}}{${names[index]}}`).join(" ");

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The spare vector <Tex>{`\\textcolor{${palette.pink}}{\\mathbf u} = \\mathbf b_1 + \\mathbf b_2`}</Tex> joins the basis. Reach the ringed point <Tex>{"\\mathbf x"}</Tex> with a recipe that gives <Tex>{"\\mathbf u"}</Tex> a weight other than <Tex>0</Tex>.</>}
        success={<>That is a second recipe for the same point, next to <Tex>{"2\\,\\mathbf b_1 + 3\\,\\mathbf b_2"}</Tex>. With a spare vector the weights stop being unique, which is why a basis leaves spare vectors out.</>}
      />
      <Workbench
        plane={
          <Plane bounds={RECIPE_BOUNDS} label="The skewed grid of b1 and b2, the spare vector u, a ringed point x and the chain of weighted vectors.">
            <BasisGrid u={b1} v={b2} opacity={0.3} />
            <Marker at={x} color={solved ? "teal" : "glow"} ring />
            {tips.slice(1).map((tip, index) => (
              <Arrow key={index} from={tips[index]} to={tip} color={hues[index]} />
            ))}
            <Arrow to={spare} color="pink" width={2} dashed />
            <Label at={spare} color="pink">u</Label>
            <Label at={x} color="teal" dx={16}>x</Label>
          </Plane>
        }
        readout={
          <>
            {[0, 1, 2].map((index) => (
              <Slider key={index} label={`c_${index + 1}`} value={weights[index]} onChange={setWeight(index)} min={-3} max={4} step={1} color={colors[index]} />
            ))}
            <Readout tex={`${sum} = ${columnTex(end)}`} />
          </>
        }
      />
    </Panel>
  );
}


const ADDRESS_BOUNDS = { xMin: -4, xMax: 5, yMin: -3, yMax: 6 };

function addressOf(x: Vec, b1: Vec, b2: Vec): Vec | null {
  const determinant = cross(b1, b2);
  if (determinant === 0) return null;
  return [cross(x, b2) / determinant, cross(b1, x) / determinant];
}

function addressTex(address: Vec | null): string {
  if (!address) return "\\text{no basis, so no address}";
  return `[\\mathbf x]_{\\mathcal B} = \\begin{bmatrix} ${texNumber(address[0])} \\\\ ${texNumber(address[1])} \\end{bmatrix}`;
}

/** The point x stays fixed while the learner drags b2. The address of x changes with the basis, and vanishes when b2 lines up with b1. */
export function BasisForAddress({ b1, start, x, target }: { b1: Vec; start: Vec; x: Vec; target: Vec }) {
  const [b2, setB2] = useState<Vec>(start);
  const address = addressOf(x, b1, b2);
  const matches = address !== null && Math.abs(address[0] - target[0]) < 1e-9 && Math.abs(address[1] - target[1]) < 1e-9;
  const { settled: solved, gesture } = useSettled(matches);
  const corner = address ? scale(address[0], b1) : ([0, 0] as Vec);

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>The point <Tex>{"\\mathbf x"}</Tex> never moves. Drag <Tex>{"\\mathbf b_2"}</Tex> until the address of <Tex>{"\\mathbf x"}</Tex> in the basis <Tex>{"\\{\\mathbf b_1, \\mathbf b_2\\}"}</Tex> is <Tex>{`(${texNumber(target[0])}, ${texNumber(target[1])})`}</Tex>.</>}
        success={<>Now <Tex>{`\\mathbf x = ${texNumber(target[0])}\\,\\mathbf b_1 + ${texNumber(target[1])}\\,\\mathbf b_2`}</Tex>. The same point has a different address in every basis, and no address at all when <Tex>{"\\mathbf b_2"}</Tex> lies on the line of <Tex>{"\\mathbf b_1"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={ADDRESS_BOUNDS} label={`Fixed point x, fixed vector b1 and draggable vector b2 at ${describeVector(b2)}, with the grid they draw. Drag b2 or use the arrow keys.`}>
            {address ? <BasisGrid u={b1} v={b2} opacity={0.35} /> : <FullLine direction={b1} color="glow" width={3} opacity={0.6} />}
            {address ? <Arrow to={corner} color="yellow" width={2} dashed /> : null}
            {address ? <Arrow from={corner} to={x} color="blue" width={2} dashed /> : null}
            <Arrow to={b1} color="yellow" />
            <Arrow to={b2} color="blue" />
            <Marker at={x} color="teal" ring={solved} />
            <Label at={x} color="teal">x</Label>
            <Label at={b1} color="yellow" dy={20}>b₁</Label>
            <Label at={b2} color="blue">b₂</Label>
            <Handle at={b2} onMove={setB2} color="blue" label={`Tip of basis vector b2, at ${describeVector(b2)}`} />
          </Plane>
        }
        readout={<Readout tex={addressTex(address)} />}
      />
    </Panel>
  );
}
