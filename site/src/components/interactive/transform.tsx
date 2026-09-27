"use client";

import { useState } from "react";
import { palette } from "@/lib/palette.generated";
import { describeVector, Goal, Panel, Readout, RichText, Workbench } from "./controls";
import { apply, det, texNumber, type Matrix2, type Vec } from "./math";
import { Arrow, DEFAULT_BOUNDS, Handle, Plane, usePlane } from "./plane";

const GRID_REACH = 12;

function TransformedGrid({ matrix }: { matrix: Matrix2 }) {
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

function UnitSquare({ matrix }: { matrix: Matrix2 }) {
  const { toSvg } = usePlane();
  const corners: Vec[] = [[0, 0], [1, 0], [1, 1], [0, 1]];
  const points = corners.map((corner) => toSvg(apply(matrix, corner)).join(",")).join(" ");
  const flipped = det(matrix) < 0;
  return <polygon points={points} fill={flipped ? "var(--palette-pink)" : "var(--palette-yellow)"} fillOpacity={0.22} />;
}

function matrixTex(matrix: Matrix2): string {
  const [[a, b], [c, d]] = matrix;
  return `\\begin{bmatrix} \\textcolor{${palette.i_hat}}{${texNumber(a)}} & \\textcolor{${palette.j_hat}}{${texNumber(b)}} \\\\ \\textcolor{${palette.i_hat}}{${texNumber(c)}} & \\textcolor{${palette.j_hat}}{${texNumber(d)}} \\end{bmatrix}`;
}

type TransformGoal = { determinant?: number; matrix?: Matrix2; prompt: string; success: string };

function isSolved(matrix: Matrix2, goal?: TransformGoal): boolean {
  if (!goal) return false;
  if (goal.matrix) return goal.matrix.every((row, i) => row.every((value, j) => Math.abs(value - matrix[i][j]) < 1e-6));
  if (goal.determinant !== undefined) return Math.abs(det(matrix) - goal.determinant) < 1e-6;
  return false;
}

export function TransformExplorer({ matrix: start = [[1, 1], [0, 1]], showArea = false, goal }: { matrix?: Matrix2; showArea?: boolean; goal?: TransformGoal }) {
  const [matrix, setMatrix] = useState<Matrix2>(start);
  const iHat: Vec = [matrix[0][0], matrix[1][0]];
  const jHat: Vec = [matrix[0][1], matrix[1][1]];
  const solved = isSolved(matrix, goal);
  const setColumn = (column: 0 | 1) => (point: Vec) =>
    setMatrix((current) => current.map((row, i) => row.map((value, j) => (j === column ? point[i] : value))) as Matrix2);
  const readout = showArea ? `${matrixTex(matrix)} \\qquad \\det = ${texNumber(det(matrix))}` : matrixTex(matrix);

  return (
    <Panel>
      {goal ? <Goal solved={solved} prompt={<RichText>{goal.prompt}</RichText>} success={<RichText>{goal.success}</RichText>} /> : null}
      <Workbench
        plane={
          <Plane bounds={DEFAULT_BOUNDS} label="Grid transformed by a 2 by 2 matrix. Drag the green and red basis tips.">
            <TransformedGrid matrix={matrix} />
            {showArea ? <UnitSquare matrix={matrix} /> : null}
            <Arrow to={iHat} color="green" />
            <Arrow to={jHat} color="red" />
            <Handle at={iHat} onMove={setColumn(0)} color="green" label={`Where i-hat lands, at ${describeVector(iHat)}`} />
            <Handle at={jHat} onMove={setColumn(1)} color="red" label={`Where j-hat lands, at ${describeVector(jHat)}`} />
          </Plane>
        }
        readout={<Readout tex={readout} />}
      />
    </Panel>
  );
}
