import { Children } from "react";
import { MDXRemote } from "next-mdx-remote-client/rsc";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";
import { VectorAnswer } from "@/components/interactive/answers";
import { Choice, Step, Steps } from "@/components/interactive/walkthrough";
import { Answer, Check, Concept, Definition, Hint, Problem, Solution, Warning } from "@/components/Walkthrough";
import { widgets } from "@/components/widgets";
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

export function Notes({ lesson }: { lesson: Lesson }) {
  const components = {
    Figure: makeFigure(lesson),
    Pair,
    Definition,
    Check,
    Answer,
    Problem,
    Solution,
    Hint,
    Concept,
    Warning,
    Steps,
    Step,
    Choice,
    VectorAnswer,
    ...widgets,
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
