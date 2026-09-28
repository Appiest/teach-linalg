"use client";

import { createContext, useContext, useMemo, useState } from "react";

type Gesture = { begin: () => void };

const GestureContext = createContext<Gesture>({ begin: () => {} });

export const GestureProvider = GestureContext.Provider;

export function useGesture(): Gesture {
  return useContext(GestureContext);
}

/** Follows `value`, but holds its last reading while a pointer drag is in progress. */
export function useSettled<T>(value: T): { settled: T; gesture: Gesture } {
  const [dragging, setDragging] = useState(false);
  const [settled, setSettled] = useState(value);
  if (!dragging && !Object.is(settled, value)) setSettled(value);

  const gesture = useMemo<Gesture>(
    () => ({
      begin: () => {
        setDragging(true);
        const end = () => {
          setDragging(false);
          window.removeEventListener("pointerup", end);
          window.removeEventListener("pointercancel", end);
        };
        window.addEventListener("pointerup", end);
        window.addEventListener("pointercancel", end);
      },
    }),
    [],
  );

  return { settled, gesture };
}
