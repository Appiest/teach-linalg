import { CaretRight, Lightbulb, WarningDiamond } from "@phosphor-icons/react/dist/ssr";

function Disclosure({ closedLabel, openLabel, children }: { closedLabel: string; openLabel: string; children: React.ReactNode }) {
  return (
    <details className="group">
      <summary className="inline-flex cursor-pointer list-none items-center gap-1.5 rounded-md py-1 text-meta font-semibold text-accent [&::-webkit-details-marker]:hidden">
        <CaretRight weight="bold" className="size-3.5 transition-transform duration-200 group-open:rotate-90" />
        <span className="group-open:hidden">{closedLabel}</span>
        <span className="hidden group-open:inline">{openLabel}</span>
      </summary>
      <div className="mt-3 [&>*+*]:mt-3">{children}</div>
    </details>
  );
}

export function Problem({ children }: { children: React.ReactNode }) {
  return (
    <section className="problem rounded-card bg-surface-raised p-6 shadow-lift [&>*+*]:mt-4">
      <h3 className="problem-number text-meta font-semibold text-text-muted" />
      {children}
    </section>
  );
}

export function Solution({ children }: { children: React.ReactNode }) {
  return (
    <Disclosure closedLabel="Walk through the solution" openLabel="Hide the walkthrough">
      {children}
    </Disclosure>
  );
}

export function Answer({ children }: { children: React.ReactNode }) {
  return (
    <Disclosure closedLabel="Show the solution" openLabel="Hide the solution">
      {children}
    </Disclosure>
  );
}

export function Hint({ children }: { children: React.ReactNode }) {
  return (
    <Disclosure closedLabel="Show a hint" openLabel="Hide the hint">
      {children}
    </Disclosure>
  );
}

export function Check({ children }: { children: React.ReactNode }) {
  return (
    <div className="check rounded-card bg-surface-raised p-6 shadow-lift [&>*+*]:mt-4">
      {children}
    </div>
  );
}

export function Definition({ term, children }: { term: string; children: React.ReactNode }) {
  return (
    <section className="rounded-card bg-surface-raised p-6 shadow-lift sm:p-8 [&>*+*]:mt-4">
      <h3 className="text-section text-accent">{term}</h3>
      {children}
    </section>
  );
}

export function Concept({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-card bg-[color-mix(in_oklab,var(--color-accent)_9%,var(--color-surface-raised))] p-6 shadow-lift sm:p-8 [&>*+*]:mt-4">
      <h3 className="flex items-center gap-2.5 text-section text-accent">
        <Lightbulb weight="fill" className="size-6 shrink-0" aria-hidden />
        {title}
      </h3>
      {children}
    </section>
  );
}

export function Warning({ children }: { children: React.ReactNode }) {
  return (
    <aside className="flex gap-3 rounded-card bg-surface-sunken p-5 shadow-lift">
      <WarningDiamond weight="fill" className="mt-1 size-5 shrink-0 text-glow" aria-label="Common mistake" />
      <div className="min-w-0 [&>*+*]:mt-3">{children}</div>
    </aside>
  );
}
