"use client";

import { CheckCircle, Crosshair } from "@phosphor-icons/react";
import katex from "katex";
import { useMemo } from "react";
import { GestureProvider, useGesture } from "./gesture";
import { formatNumber, texNumber, type Vec } from "./math";

export function Tex({ children, display = false }: { children: string; display?: boolean }) {
  const html = useMemo(() => katex.renderToString(children, { displayMode: display, throwOnError: false }), [children, display]);
  return <span className="[&_.katex]:text-[1.1em]" dangerouslySetInnerHTML={{ __html: html }} />;
}

/** Plain text with $…$ math segments, for goal strings passed as props from MDX. */
export function RichText({ children }: { children: string }) {
  return (
    <>
      {children.split("$").map((part, index) => (index % 2 === 1 ? <Tex key={index}>{part}</Tex> : <span key={index}>{part}</span>))}
    </>
  );
}

export function columnTex(entries: number[], color?: string): string {
  const body = `\\begin{bmatrix} ${entries.map((entry) => texNumber(entry)).join(" \\\\ ")} \\end{bmatrix}`;
  return color ? `\\textcolor{${color}}{${body}}` : body;
}

export function Panel({ children, gesture }: { children: React.ReactNode; gesture?: { begin: () => void } }) {
  const panel = <div className="not-prose my-8 rounded-card bg-surface-raised p-4 shadow-lift sm:p-6 lg:-mx-12">{children}</div>;
  return gesture ? <GestureProvider value={gesture}>{panel}</GestureProvider> : panel;
}

export function Workbench({ plane, readout }: { plane: React.ReactNode; readout: React.ReactNode }) {
  return (
    <div className="grid items-center gap-5 md:grid-cols-[1.35fr_1fr]">
      <div className="min-w-0">{plane}</div>
      <div className="min-w-0 space-y-4">{readout}</div>
    </div>
  );
}

export function Goal({ solved, prompt, success }: { solved: boolean; prompt: React.ReactNode; success: React.ReactNode }) {
  return (
    <div
      aria-live="polite"
      className={`mb-4 flex items-start gap-3 rounded-lg px-4 py-3 text-body transition-colors duration-300 ${
        solved ? "bg-[color-mix(in_oklab,var(--palette-teal)_16%,transparent)]" : "bg-surface-sunken"
      }`}
    >
      {solved ? (
        <CheckCircle weight="fill" className="mt-1 size-5 shrink-0 text-[var(--palette-teal)]" aria-hidden />
      ) : (
        <Crosshair className="mt-1 size-5 shrink-0 text-text-muted" aria-hidden />
      )}
      <div>{solved ? success : prompt}</div>
    </div>
  );
}

export function Slider({ label, value, onChange, min, max, step, color }: {
  label: string; value: number; onChange: (value: number) => void; min: number; max: number; step: number; color: string;
}) {
  const gesture = useGesture();
  return (
    <label className="flex items-center gap-3">
      <span className="w-24 shrink-0 tabular-nums" style={{ color }}>
        <Tex>{`${label} = ${texNumber(value)}`}</Tex>
      </span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        aria-label={label}
        aria-valuetext={formatNumber(value)}
        onPointerDown={gesture.begin}
        onChange={(event) => onChange(Number(event.target.value))}
        className="h-2 w-full cursor-pointer appearance-none rounded-full bg-line"
        style={{ accentColor: color }}
      />
    </label>
  );
}

export function Readout({ tex }: { tex: string }) {
  return (
    <div className="overflow-x-auto rounded-lg bg-surface-sunken px-4 py-3 text-center">
      <Tex display>{tex}</Tex>
    </div>
  );
}

export const describeVector = (v: Vec) => `(${formatNumber(v[0])}, ${formatNumber(v[1])})`;
