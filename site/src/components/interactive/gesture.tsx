"use client";

import { createContext, useContext, useMemo, useState } from "react";

type Gesture = { begin: () => void; dragging: boolean };

const GestureContext = createContext<Gesture>({ begin: () => {}, dragging: false });

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
      dragging,
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
    [dragging],
  );

  return { settled, gesture };
}

/** The value from just before the current drag began, held until the drag ends, so layout can't shift under the pointer. */
export function useHeldWhileDragging<T>(value: T): T {
  const { dragging } = useGesture();
  const [held, setHeld] = useState({ value, dragging });
  if (held.dragging !== dragging) setHeld({ value, dragging });
  return dragging ? held.value : value;
}
