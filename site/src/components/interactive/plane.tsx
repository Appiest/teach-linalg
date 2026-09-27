"use client";

import { createContext, useCallback, useContext, useId, useMemo, useRef, useState } from "react";
import { hue, type Hue } from "./colors";
import type { Vec } from "./math";

export type Bounds = { xMin: number; xMax: number; yMin: number; yMax: number };

type PlaneApi = {
  bounds: Bounds;
  unit: number;
  toSvg: (point: Vec) => Vec;
  toMath: (clientX: number, clientY: number) => Vec;
  arrowheadId: (color: Hue) => string;
};

export const DEFAULT_BOUNDS: Bounds = { xMin: -6, xMax: 6, yMin: -4, yMax: 5 };

/** The default window, grown just enough to keep every given point one unit inside the edge. */
export function boundsAround(points: Vec[], base: Bounds = DEFAULT_BOUNDS): Bounds {
  const xs = points.map((point) => point[0]);
  const ys = points.map((point) => point[1]);
  return {
    xMin: Math.min(base.xMin, Math.floor(Math.min(...xs)) - 1),
    xMax: Math.max(base.xMax, Math.ceil(Math.max(...xs)) + 1),
    yMin: Math.min(base.yMin, Math.floor(Math.min(...ys)) - 1),
    yMax: Math.max(base.yMax, Math.ceil(Math.max(...ys)) + 1),
  };
}

const PlaneContext = createContext<PlaneApi | null>(null);

export function usePlane(): PlaneApi {
  const api = useContext(PlaneContext);
  if (!api) throw new Error("usePlane must be used inside <Plane>");
  return api;
}

const UNIT = 40;
const HUES: Hue[] = ["yellow", "blue", "teal", "pink", "green", "red", "glow", "text"];

function GridLines() {
  const { bounds, toSvg } = usePlane();
  const xs = Array.from({ length: bounds.xMax - bounds.xMin + 1 }, (_, i) => bounds.xMin + i);
  const ys = Array.from({ length: bounds.yMax - bounds.yMin + 1 }, (_, i) => bounds.yMin + i);
  const line = (from: Vec, to: Vec, key: string, axis: boolean) => {
    const [x1, y1] = toSvg(from);
    const [x2, y2] = toSvg(to);
    return (
      <line
        key={key}
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke={axis ? "var(--palette-axis)" : "var(--palette-grid)"}
        strokeOpacity={axis ? 0.9 : 0.45}
        strokeWidth={axis ? 1.6 : 1}
      />
    );
  };
  return (
    <g aria-hidden>
      {xs.map((x) => line([x, bounds.yMin], [x, bounds.yMax], `x${x}`, x === 0))}
      {ys.map((y) => line([bounds.xMin, y], [bounds.xMax, y], `y${y}`, y === 0))}
    </g>
  );
}

function Arrowheads({ prefix }: { prefix: string }) {
  return (
    <defs>
      {HUES.map((name) => (
        <marker
          key={name}
          id={`${prefix}-${name}`}
          viewBox="0 0 10 10"
          refX="8.5"
          refY="5"
          markerWidth="5"
          markerHeight="5"
          orient="auto-start-reverse"
        >
          <path d="M0,0 L10,5 L0,10 z" fill={hue(name)} />
        </marker>
      ))}
    </defs>
  );
}

export function Plane({ bounds, label, children }: { bounds: Bounds; label: string; children: React.ReactNode }) {
  const svgRef = useRef<SVGSVGElement>(null);
  const prefix = useId().replaceAll(":", "");
  const width = (bounds.xMax - bounds.xMin) * UNIT;
  const height = (bounds.yMax - bounds.yMin) * UNIT;

  const toSvg = useCallback((point: Vec): Vec => [(point[0] - bounds.xMin) * UNIT, (bounds.yMax - point[1]) * UNIT], [bounds]);
  const toMath = useCallback(
    (clientX: number, clientY: number): Vec => {
      const svg = svgRef.current;
      const matrix = svg?.getScreenCTM()?.inverse();
      if (!svg || !matrix) return [0, 0];
      const point = new DOMPoint(clientX, clientY).matrixTransform(matrix);
      return [point.x / UNIT + bounds.xMin, bounds.yMax - point.y / UNIT];
    },
    [bounds],
  );
  const api = useMemo(
    () => ({ bounds, unit: UNIT, toSvg, toMath, arrowheadId: (color: Hue) => `${prefix}-${color}` }),
    [bounds, toSvg, toMath, prefix],
  );

  return (
    <PlaneContext.Provider value={api}>
      <svg
        ref={svgRef}
        viewBox={`0 0 ${width} ${height}`}
        role="group"
        aria-label={label}
        className="block h-auto w-full touch-none select-none rounded-media bg-surface-sunken"
      >
        <Arrowheads prefix={prefix} />
        <GridLines />
        {children}
      </svg>
    </PlaneContext.Provider>
  );
}

export function Arrow({ from = [0, 0], to, color, width = 3.5, dashed = false }: { from?: Vec; to: Vec; color: Hue; width?: number; dashed?: boolean }) {
  const { toSvg, arrowheadId } = usePlane();
  const [x1, y1] = toSvg(from);
  const [x2, y2] = toSvg(to);
  if (Math.hypot(x2 - x1, y2 - y1) < 2) return null;
  return (
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke={hue(color)}
      strokeWidth={width}
      strokeLinecap="round"
      strokeDasharray={dashed ? "6 6" : undefined}
      markerEnd={dashed ? undefined : `url(#${arrowheadId(color)})`}
    />
  );
}

export function Segment({ from, to, color, dashed = true }: { from: Vec; to: Vec; color: Hue; dashed?: boolean }) {
  const { toSvg } = usePlane();
  const [x1, y1] = toSvg(from);
  const [x2, y2] = toSvg(to);
  return <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={hue(color)} strokeWidth={2} strokeDasharray={dashed ? "5 5" : undefined} />;
}

export function Marker({ at, color = "glow", ring = false }: { at: Vec; color?: Hue; ring?: boolean }) {
  const { toSvg } = usePlane();
  const [x, y] = toSvg(at);
  return (
    <g>
      {ring ? <circle cx={x} cy={y} r={13} fill="none" stroke={hue(color)} strokeWidth={2} strokeDasharray="4 4" /> : null}
      <circle cx={x} cy={y} r={5} fill={hue(color)} />
    </g>
  );
}

export function Label({ at, color, children, dx = 10, dy = -10 }: { at: Vec; color: Hue; children: string; dx?: number; dy?: number }) {
  const { toSvg } = usePlane();
  const [x, y] = toSvg(at);
  return (
    <text x={x + dx} y={y + dy} fill={hue(color)} fontSize={17} fontStyle="italic" fontFamily="KaTeX_Math, serif" paintOrder="stroke" stroke="var(--color-surface-sunken)" strokeWidth={4}>
      {children}
    </text>
  );
}

function clampToBounds(point: Vec, bounds: Bounds, step: number): Vec {
  const snap = (value: number, min: number, max: number) => Math.min(max, Math.max(min, Math.round(value / step) * step));
  return [snap(point[0], bounds.xMin, bounds.xMax), snap(point[1], bounds.yMin, bounds.yMax)];
}

const KEY_STEPS: Record<string, Vec> = { ArrowRight: [1, 0], ArrowLeft: [-1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] };

export function Handle({ at, onMove, color, label, step = 1 }: { at: Vec; onMove: (point: Vec) => void; color: Hue; label: string; step?: number }) {
  const { toSvg, toMath, bounds } = usePlane();
  const [dragging, setDragging] = useState(false);
  const [x, y] = toSvg(at);

  const moveTo = (clientX: number, clientY: number) => onMove(clampToBounds(toMath(clientX, clientY), bounds, step));
  const onKeyDown = (event: React.KeyboardEvent) => {
    const direction = KEY_STEPS[event.key];
    if (!direction) return;
    event.preventDefault();
    onMove(clampToBounds([at[0] + direction[0] * step, at[1] + direction[1] * step], bounds, step));
  };

  return (
    <g
      role="slider"
      tabIndex={0}
      aria-label={label}
      aria-valuetext={`(${at[0]}, ${at[1]})`}
      className="group cursor-grab outline-none active:cursor-grabbing"
      onKeyDown={onKeyDown}
      onPointerDown={(event) => {
        event.currentTarget.setPointerCapture(event.pointerId);
        setDragging(true);
        moveTo(event.clientX, event.clientY);
      }}
      onPointerMove={(event) => dragging && moveTo(event.clientX, event.clientY)}
      onPointerUp={() => setDragging(false)}
      onPointerCancel={() => setDragging(false)}
    >
      <circle cx={x} cy={y} r={22} fill="transparent" />
      <circle cx={x} cy={y} r={13} fill={hue(color)} fillOpacity={dragging ? 0.3 : 0.16} className="transition-[fill-opacity]" />
      <circle cx={x} cy={y} r={16} fill="none" stroke="var(--palette-yellow)" strokeWidth={2.5} className="opacity-0 group-focus-visible:opacity-100" />
      <circle cx={x} cy={y} r={6.5} fill={hue(color)} />
    </g>
  );
}
