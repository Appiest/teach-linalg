"use client";

import { ArrowCounterClockwise, CaretDown, CheckCircle, XCircle } from "@phosphor-icons/react";
import { Children, isValidElement, useState } from "react";
import { RichText } from "./controls";

export function Step({ children }: { children: React.ReactNode }) {
  return <div className="[&>*+*]:mt-3">{children}</div>;
}

const secondaryButton = "inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-meta font-semibold text-text-muted transition-colors hover:text-text";
const primaryButton = "inline-flex items-center gap-1.5 rounded-lg bg-text px-4 py-2 text-meta font-semibold text-surface transition-opacity hover:opacity-90";

/** Reveals one step at a time. Hidden steps keep their space so the buttons never move under the pointer. */
export function Steps({ children }: { children: React.ReactNode }) {
  const steps = Children.toArray(children).filter(isValidElement);
  const [shown, setShown] = useState(1);
  const finished = shown >= steps.length;

  return (
    <div className="not-prose rounded-card bg-surface-raised p-5 shadow-lift sm:p-6 in-[.problem]:bg-surface-sunken in-[.problem]:shadow-none">
      <ol className="space-y-5">
        {steps.map((step, index) => (
          <li key={index} className="grid grid-cols-[1.75rem_1fr] gap-3">
            <span
              className={`mt-0.5 grid size-7 place-items-center rounded-full text-meta font-semibold tabular-nums transition-colors ${
                index < shown ? "bg-line text-text" : "bg-surface-sunken text-text-muted/60"
              }`}
            >
              {index + 1}
            </span>
            <div aria-hidden={index >= shown} className={`min-w-0 ${index < shown ? "swap-shown" : "swap-hidden"}`}>
              {step}
            </div>
          </li>
        ))}
      </ol>
      <div className="mt-5 flex flex-wrap items-center gap-2">
        {finished ? (
          <button type="button" className={secondaryButton} onClick={() => setShown(1)}>
            <ArrowCounterClockwise className="size-4" aria-hidden /> Start over
          </button>
        ) : (
          <>
            <button type="button" className={primaryButton} onClick={() => setShown(shown + 1)}>
              <CaretDown weight="bold" className="size-4" aria-hidden /> Show step {shown + 1}
            </button>
            <button type="button" className={secondaryButton} onClick={() => setShown(steps.length)}>
              Show every step
            </button>
          </>
        )}
      </div>
    </div>
  );
}

type OptionState = "open" | "right" | "wrong";

function optionClass(state: OptionState): string {
  const base = "flex w-full items-center gap-3 rounded-lg px-4 py-3 text-left text-body transition-colors";
  if (state === "right") return `${base} bg-[color-mix(in_oklab,var(--color-correct)_18%,transparent)] ring-2 ring-correct`;
  if (state === "wrong") return `${base} bg-surface-sunken text-text-muted ring-2 ring-wrong/60`;
  return `${base} bg-surface-sunken hover:bg-line`;
}

function OptionMark({ state }: { state: OptionState }) {
  if (state === "right") return <CheckCircle weight="fill" className="size-5 shrink-0 text-correct" aria-label="Correct" />;
  if (state === "wrong") return <XCircle weight="fill" className="size-5 shrink-0 text-wrong" aria-label="Not this one" />;
  return <span aria-hidden className="size-5 shrink-0 rounded-full bg-line" />;
}

/** A quick multiple-choice check. Wrong picks stay marked so the learner can try again; the explanation appears once they find the answer. */
export function Choice({ question, options, answer, children }: { question: string; options: string[]; answer: number; children?: React.ReactNode }) {
  const [tried, setTried] = useState<number[]>([]);
  const solved = tried.includes(answer);
  const stateOf = (index: number): OptionState => {
    if (!tried.includes(index)) return "open";
    return index === answer ? "right" : "wrong";
  };

  return (
    <div className="not-prose rounded-card bg-surface-raised p-5 shadow-lift sm:p-6 in-[.check]:p-0 in-[.check]:shadow-none sm:in-[.check]:p-0">
      <p className="font-semibold">
        <RichText>{question}</RichText>
      </p>
      <div className="mt-4 grid gap-2" role="group" aria-label="Answer choices">
        {options.map((option, index) => (
          <button
            key={index}
            type="button"
            disabled={solved}
            aria-pressed={tried.includes(index)}
            onClick={() => setTried((current) => (current.includes(index) ? current : [...current, index]))}
            className={optionClass(stateOf(index))}
          >
            <OptionMark state={stateOf(index)} />
            <span className="min-w-0">
              <RichText>{option}</RichText>
            </span>
          </button>
        ))}
      </div>
      <div aria-live="polite">
        {solved && children ? <div className="mt-4 [&>*+*]:mt-3">{children}</div> : null}
        {!solved && tried.length > 0 ? <p className="mt-4 text-meta text-text-muted">Not that one. Give it another try.</p> : null}
      </div>
    </div>
  );
}
