"use client";

import { ArrowCounterClockwise, CheckCircle, WarningCircle } from "@phosphor-icons/react";
import { useState } from "react";
import { Tex } from "./controls";

type Status = "idle" | "correct" | "wrong";

function parseEntry(text: string): number | null {
  const cleaned = text.trim().replace("−", "-");
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
      <p className="flex items-center gap-2 font-semibold text-[var(--palette-teal)]">
        <CheckCircle weight="fill" className="size-5" aria-hidden /> Correct.
      </p>
    );
  }
  if (status === "wrong") {
    const names = wrong.map((index) => labels[index]).join(" and ");
    return (
      <p className="flex items-center gap-2 text-[var(--palette-j-hat)]">
        <WarningCircle weight="fill" className="size-5 shrink-0" aria-hidden /> Not quite. Check {names}.
      </p>
    );
  }
  return null;
}

export function VectorAnswer({ answer, labels, prefix }: { answer: number[]; labels?: string[]; prefix?: string }) {
  const names = labels ?? answer.map((_, index) => `entry ${index + 1}`);
  const [values, setValues] = useState<string[]>(answer.map(() => ""));
  const [status, setStatus] = useState<Status>("idle");
  const [wrong, setWrong] = useState<number[]>([]);

  const check = () => {
    const misses = wrongEntries(values, answer);
    setWrong(misses);
    setStatus(misses.length === 0 ? "correct" : "wrong");
  };
  const update = (index: number, text: string) => {
    setValues((current) => current.map((value, i) => (i === index ? text : value)));
    setStatus("idle");
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
        <div className="flex flex-col gap-1.5 py-1">
          {answer.map((_, index) => (
            <input
              key={index}
              inputMode="decimal"
              aria-label={names[index]}
              placeholder={labels ? labels[index] : undefined}
              value={values[index]}
              onChange={(event) => update(index, event.target.value)}
              className={`w-20 rounded-md border bg-surface-sunken px-2 py-1.5 text-center text-base tabular-nums outline-none focus-visible:border-accent ${
                status === "wrong" && wrong.includes(index) ? "border-[var(--palette-j-hat)]" : "border-line"
              } ${status === "correct" ? "border-[var(--palette-teal)]" : ""}`}
            />
          ))}
        </div>
        <span aria-hidden className="w-2 border-y-2 border-r-2 border-text-muted" />
      </div>
      <div className="flex items-center gap-3">
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
