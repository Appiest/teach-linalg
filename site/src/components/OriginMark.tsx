export function OriginMark({ className = "" }: { className?: string }) {
  return (
    <span aria-hidden className={`relative inline-grid size-4 place-items-center ${className}`}>
      <span className="absolute inset-0 rounded-full bg-glow/20 blur-[3px]" />
      <span className="size-1.5 rounded-full bg-glow shadow-[0_0_12px_2px] shadow-glow/60" />
    </span>
  );
}
