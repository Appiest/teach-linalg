"use client";

import { ArrowCounterClockwise, CheckCircle, WarningCircle } from "@phosphor-icons/react";
import { useRef, useState } from "react";
import { Tex } from "./controls";

type Status = "idle" | "correct" | "wrong";

function parseEntry(text: string): number | null {
  const cleaned = text.trim().replaceAll("−", "-");
  if (cleaned === "") return null;
  if (/^-?\d+\/\d+$/.test(cleaned)) {
    const [top, bottom] = cleaned.split("/").map(Number);
    return bottom === 0 ? null : top / bottom;
  }
  const value = Number(cleaned);
  return Number.isFinite(value) ? value : null;
}

function wrongEntries(values: string[], answer: number[]): number[] {
  return answer.flatMap((expected, index) => {
    const given = parseEntry(values[index]);
    return given === null || Math.abs(given - expected) > 1e-6 ? [index] : [];
  });
}

function Feedback({ status, wrong, labels }: { status: Status; wrong: number[]; labels: string[] }) {
  if (status === "correct") {
    return (
      <p className="flex items-center gap-2 font-semibold text-correct">
        <CheckCircle weight="fill" className="size-5" aria-hidden /> Correct.
      </p>
    );
  }
  if (status === "wrong") {
    const names = wrong.map((index) => labels[index]).join(" and ");
    return (
      <p className="flex items-center gap-2 text-wrong">
        <WarningCircle weight="fill" className="size-5 shrink-0" aria-hidden /> Not quite. Check {names}.
      </p>
    );
  }
  return null;
}

function flipSign(text: string): string {
  return text.startsWith("-") ? text.slice(1) : `-${text}`;
}

/** Keys the iPhone number pad lacks. Pointer-down is cancelled so the tapped field keeps focus and the pad stays open. */
function TouchKeys({ onFlipSign, onFractionBar }: { onFlipSign: () => void; onFractionBar: () => void }) {
  const key = "min-w-11 rounded-lg bg-surface-sunken px-3 py-2 text-base tabular-nums text-text shadow-[inset_0_0_0_1px_var(--color-line)]";
  return (
    <div className="hidden gap-2 pointer-coarse:flex">
      <button type="button" aria-label="Flip the sign" className={key} onPointerDown={(event) => event.preventDefault()} onClick={onFlipSign}>
        ±
      </button>
      <button type="button" aria-label="Type a fraction bar" className={key} onPointerDown={(event) => event.preventDefault()} onClick={onFractionBar}>
        /
      </button>
    </div>
  );
}

function defaultNames(count: number, columns: number): string[] {
  if (columns === 1) return Array.from({ length: count }, (_, index) => `entry ${index + 1}`);
  return Array.from({ length: count }, (_, index) => `row ${Math.floor(index / columns) + 1}, column ${(index % columns) + 1}`);
}

/** Typed answer checked entry by entry. With `columns`, the entries are a matrix listed row by row. */
export function VectorAnswer({ answer, labels, prefix, columns = 1 }: { answer: number[]; labels?: string[]; prefix?: string; columns?: number }) {
  const names = labels ?? defaultNames(answer.length, columns);
  const [values, setValues] = useState<string[]>(answer.map(() => ""));
  const [status, setStatus] = useState<Status>("idle");
  const [wrong, setWrong] = useState<number[]>([]);
  const [activeIndex, setActiveIndex] = useState(0);
  const inputs = useRef<(HTMLInputElement | null)[]>([]);

  const check = () => {
    const misses = wrongEntries(values, answer);
    setWrong(misses);
    setStatus(misses.length === 0 ? "correct" : "wrong");
  };
  const update = (index: number, text: string) => {
    setValues((current) => current.map((value, i) => (i === index ? text : value)));
    setStatus("idle");
  };
  const editActive = (edit: (text: string) => string) => {
    update(activeIndex, edit(values[activeIndex]));
    inputs.current[activeIndex]?.focus();
  };

  return (
    <form
      className="flex flex-wrap items-center gap-4"
      onSubmit={(event) => {
        event.preventDefault();
        check();
      }}
    >
      {prefix ? <Tex>{prefix}</Tex> : null}
      <div className="flex items-stretch gap-1.5">
        <span aria-hidden className="w-2 border-y-2 border-l-2 border-text-muted" />
        <div className="grid gap-1.5 py-1" style={{ gridTemplateColumns: `repeat(${columns}, auto)` }}>
          {answer.map((_, index) => (
            <input
              key={index}
              ref={(element) => {
                inputs.current[index] = element;
              }}
              inputMode="decimal"
              onFocus={() => setActiveIndex(index)}
              aria-label={names[index]}
              placeholder={labels ? labels[index] : undefined}
              value={values[index]}
              onChange={(event) => update(index, event.target.value)}
              className={`${columns > 2 ? "w-14 sm:w-20" : "w-20"} rounded-md border bg-surface-sunken px-2 py-1.5 text-center text-base tabular-nums outline-none focus-visible:border-accent ${
                status === "wrong" && wrong.includes(index) ? "border-wrong" : "border-line"
              } ${status === "correct" ? "border-correct" : ""}`}
            />
          ))}
        </div>
        <span aria-hidden className="w-2 border-y-2 border-r-2 border-text-muted" />
      </div>
      <div className="flex items-center gap-3">
        <TouchKeys onFlipSign={() => editActive(flipSign)} onFractionBar={() => editActive((text) => `${text}/`)} />
        <button type="submit" className="rounded-lg bg-text px-4 py-2 text-meta font-semibold text-surface transition-opacity hover:opacity-90">
          Check
        </button>
        {status !== "idle" ? (
          <button
            type="button"
            aria-label="Clear answer"
            onClick={() => {
              setValues(answer.map(() => ""));
              setStatus("idle");
            }}
            className="rounded-lg p-2 text-text-muted transition-colors hover:text-text"
          >
            <ArrowCounterClockwise className="size-4" />
          </button>
        ) : null}
      </div>
      <div aria-live="polite" className="basis-full">
        <Feedback status={status} wrong={wrong} labels={names} />
      </div>
    </form>
  );
}
