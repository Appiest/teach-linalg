"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { columnTex, describeVector, Goal, Panel, Readout, RichText, Tex, Workbench } from "./controls";
import { useSettled } from "./gesture";
import { apply, det, nearlyEqual, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, boundsAround, type Bounds, Handle, Label, Marker, Plane, usePlane } from "./plane";

const GRID_REACH = 14;
const CLOSE_UP: Bounds = { xMin: -3, xMax: 4, yMin: -3, yMax: 4 };

const columnsOf = (matrix: Matrix2): [Vec, Vec] => [
  [matrix[0][0], matrix[1][0]],
  [matrix[0][1], matrix[1][1]],
];

const sameMatrix = (a: Matrix2, b: Matrix2) => a.every((row, i) => row.every((value, j) => Math.abs(value - b[i][j]) < 1e-6));

function basisMatrixTex(matrix: Matrix2): string {
  const entry = (value: number, color: string) => `\\textcolor{${color}}{${texNumber(value)}}`;
  const rows = matrix.map((row) => `${entry(row[0], palette.i_hat)} & ${entry(row[1], palette.j_hat)}`);
  return `\\begin{bmatrix} ${rows.join(" \\\\ ")} \\end{bmatrix}`;
}

/** The integer grid after the map, drawn in blue over the fixed grid, with the images of the axes brighter. */
function MovedGrid({ matrix }: { matrix: Matrix2 }) {
  const { toSvg } = usePlane();
  const lines: { from: Vec; to: Vec; axis: boolean }[] = [];
  for (let k = -GRID_REACH; k <= GRID_REACH; k++) {
    lines.push({ from: apply(matrix, [k, -GRID_REACH]), to: apply(matrix, [k, GRID_REACH]), axis: k === 0 });
    lines.push({ from: apply(matrix, [-GRID_REACH, k]), to: apply(matrix, [GRID_REACH, k]), axis: k === 0 });
  }
  return (
    <g aria-hidden>
      {lines.map(({ from, to, axis }, index) => {
        const [x1, y1] = toSvg(from);
        const [x2, y2] = toSvg(to);
        return (
          <line
            key={index}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            stroke={axis ? "var(--palette-axis)" : "var(--palette-blue)"}
            strokeOpacity={axis ? 0.85 : 0.5}
            strokeWidth={axis ? 1.8 : 1.2}
          />
        );
      })}
    </g>
  );
}

/** Drag x in the original plane until its image A x lands on b. The moved grid shows how many steps of each column b needs. */
export function PreimageHunt({ matrix, target, start = [1, 0], success }: { matrix: Matrix2; target: Vec; start?: Vec; success?: string }) {
  const [x, setX] = useState<Vec>(start);
  const image = apply(matrix, x);
  const [iImage, jImage] = columnsOf(matrix);
  const { settled: solved, gesture } = useSettled(nearlyEqual(image, target));
  const product = `${basisMatrixTex(matrix)}${columnTex(x, palette.yellow)} = ${columnTex(image, palette.teal)}`;

  return (
    <Panel gesture={gesture}>
      <Goal
        solved={solved}
        prompt={<>Drag <Tex>{"\\mathbf x"}</Tex> until its image <Tex>{"T(\\mathbf x) = A\\mathbf x"}</Tex> lands on the ringed point <Tex>{`\\mathbf b = (${texNumber(target[0])}, ${texNumber(target[1])})`}</Tex>. Count steps along the blue grid.</>}
        success={success ? <RichText>{success}</RichText> : <>You found <Tex>{`\\mathbf x = ${columnTex(x)}`}</Tex>, so <Tex>{"\\mathbf b"}</Tex> is in the range of <Tex>{"T"}</Tex>.</>}
      />
      <Workbench
        plane={
          <Plane bounds={boundsAround([target, iImage, jImage])} label="A fixed grid and the same grid moved by A. Drag the yellow tip of x; the teal arrow is its image.">
            <MovedGrid matrix={matrix} />
            {!solved ? <Marker at={target} ring /> : null}
            <Arrow to={iImage} color="green" width={2} />
            <Arrow to={jImage} color="red" width={2} />
            <Arrow to={image} color="teal" />
            <Arrow to={x} color="yellow" />
            <Label at={x} color="yellow">x</Label>
            <Label at={image} color="teal">T(x)</Label>
            {solved ? <Marker at={target} color="teal" /> : null}
            <Handle at={x} onMove={setX} color="yellow" label={`Tip of x, at ${describeVector(x)}`} />
          </Plane>
        }
        readout={
          <>
            <Readout tex={product} />
            <Readout tex={`= ${texNumber(x[0])}${columnTex(iImage, palette.i_hat)} + ${texNumber(x[1])}${columnTex(jImage, palette.j_hat)}`} />
          </>
        }
      />
    </Panel>
  );
}

const F_SHAPE: Vec[] = [
  [0, 0], [0.5, 0], [0.5, 1], [1.2, 1], [1.2, 1.5], [0.5, 1.5], [0.5, 2], [1.5, 2], [1.5, 2.5], [0, 2.5],
];

function MovedShape({ matrix, ghost = false }: { matrix: Matrix2; ghost?: boolean }) {
  const { toSvg } = usePlane();
  const points = F_SHAPE.map((corner) => toSvg(apply(matrix, corner)).join(",")).join(" ");
  if (ghost) return <polygon points={points} fill="none" stroke="var(--palette-glow)" strokeWidth={2} strokeDasharray="5 5" />;
  const flipped = det(matrix) < 0;
  return <polygon points={points} fill={flipped ? "var(--palette-pink)" : "var(--palette-yellow)"} fillOpacity={0.35} />;
}

/** Drag where e1 and e2 land until the letter F matches the dashed outline of its image under a hidden matrix. */
export function ShapeMatch({ target, prompt, success }: { target: Matrix2; prompt: string; success: string }) {
  const [matrix, setMatrix] = useState<Matrix2>([[1, 0], [0, 1]]);
  const [iImage, jImage] = columnsOf(matrix);
  const { settled: solved, gesture } = useSettled(sameMatrix(matrix, target));
  const setColumn = (column: 0 | 1) => (point: Vec) =>
    setMatrix((current) => current.map((row, i) => row.map((value, j) => (j === column ? point[i] : value))) as Matrix2);
  const [targetI, targetJ] = columnsOf(target);
  const ghostCorners = F_SHAPE.map((corner) => apply(target, corner));

  return (
    <Panel gesture={gesture}>
      <Goal solved={solved} prompt={<RichText>{prompt}</RichText>} success={<RichText>{success}</RichText>} />
      <Workbench
        plane={
          <Plane bounds={boundsAround([...ghostCorners, targetI, targetJ], CLOSE_UP)} label="A letter F moved by a matrix and a dashed outline to match. Drag the green and red basis tips.">
            <MovedGrid matrix={matrix} />
            {!solved ? <MovedShape matrix={target} ghost /> : null}
            <MovedShape matrix={matrix} />
            <Arrow to={iImage} color="green" />
            <Arrow to={jImage} color="red" />
            <Handle at={iImage} onMove={setColumn(0)} color="green" label={`Where e1 lands, at ${describeVector(iImage)}`} />
            <Handle at={jImage} onMove={setColumn(1)} color="red" label={`Where e2 lands, at ${describeVector(jImage)}`} />
          </Plane>
        }
        readout={<Readout tex={`A = ${basisMatrixTex(matrix)}`} />}
      />
    </Panel>
  );
}
