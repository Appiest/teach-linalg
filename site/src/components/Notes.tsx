import { Children } from "react";
import { CaretRight } from "@phosphor-icons/react/dist/ssr";
import { MDXRemote } from "next-mdx-remote-client/rsc";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";
import { VectorAnswer } from "@/components/interactive/answers";
import { TransformExplorer } from "@/components/interactive/transform";
import { EntryHunt, SpanPainter } from "@/components/interactive/span";
import { RowReduceExplorer, SolutionCountExplorer } from "@/components/interactive/systems";
import { ColumnSpanCheck, MatrixVectorExplorer } from "@/components/interactive/matrix";
import { AdditionExplorer, CombinationTarget, ScaleExplorer, VectorExplorer } from "@/components/interactive/vectors";
import { ElementaryMoves, InverseBuilder } from "@/components/interactive/elementary";
import { assetPath, getNotesSource, type Lesson } from "@/lib/course";
import { katexMacros } from "@/lib/katex-macros";

type FigureProps = { src: string; alt: string; wide?: boolean; children?: React.ReactNode };

function makeFigure(lesson: Lesson) {
  return function Figure({ src, alt, wide = false, children }: FigureProps) {
    return (
      <figure className={wide ? "lg:-mx-24" : ""}>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={assetPath(lesson, `figures/${src}.png`)}
          alt={alt}
          loading="lazy"
          className="w-full rounded-media bg-surface-sunken shadow-lift"
        />
        {children ? <figcaption className="mt-3 text-meta text-text-muted">{children}</figcaption> : null}
      </figure>
    );
  };
}

function Pair({ children }: { children: React.ReactNode }) {
  const [visual, ...explanation] = Children.toArray(children);
  return (
    <div className="grid items-center gap-x-10 gap-y-6 lg:-mx-24 lg:grid-cols-[1.15fr_1fr] [&>*+*]:mt-0">
      <div className="min-w-0">{visual}</div>
      <div className="min-w-0 [&_.katex-display_.katex]:text-[1.2em] [&>*+*]:mt-4">{explanation}</div>
    </div>
  );
}

function Definition({ term, children }: { term: string; children: React.ReactNode }) {
  return (
    <section className="rounded-card bg-surface-raised p-6 shadow-lift sm:p-8 [&>*+*]:mt-4">
      <h3 className="text-section text-accent">{term}</h3>
      {children}
    </section>
  );
}

function Check({ children }: { children: React.ReactNode }) {
  return <div className="rounded-card bg-surface-raised p-6 shadow-lift [&>*+*]:mt-4">{children}</div>;
}

function Answer({ children }: { children: React.ReactNode }) {
  return (
    <details className="group">
      <summary className="inline-flex cursor-pointer list-none items-center gap-1.5 rounded-md py-1 text-meta font-semibold text-accent [&::-webkit-details-marker]:hidden">
        <CaretRight weight="bold" className="size-3.5 transition-transform duration-200 group-open:rotate-90" />
        <span className="group-open:hidden">Show the solution</span>
        <span className="hidden group-open:inline">Hide the solution</span>
      </summary>
      <div className="mt-3 [&>*+*]:mt-3">{children}</div>
    </details>
  );
}

export function Notes({ lesson }: { lesson: Lesson }) {
  const components = {
    Figure: makeFigure(lesson),
    Pair,
    Definition,
    Check,
    Answer,
    VectorExplorer,
    AdditionExplorer,
    ScaleExplorer,
    CombinationTarget,
    TransformExplorer,
    VectorAnswer,
    SpanPainter,
    EntryHunt,
    RowReduceExplorer,
    SolutionCountExplorer,
    MatrixVectorExplorer,
    ColumnSpanCheck,
    ElementaryMoves,
    InverseBuilder,
  };
  return (
    <div className="notes">
      <MDXRemote
        source={getNotesSource(lesson)}
        components={components}
        options={{
          mdxOptions: {
            remarkPlugins: [remarkMath],
            rehypePlugins: [[rehypeKatex, { macros: katexMacros(), strict: false }]],
          },
        }}
      />
    </div>
  );
}
