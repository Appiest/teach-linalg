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
import { PreimageHunt, ShapeMatch } from "@/components/interactive/transformations";
import { ClosureHunt, PolynomialCombiner } from "@/components/interactive/vector-spaces";
import { CostCompare, LUBuilder, SubstitutionSolver } from "@/components/interactive/lu";
import { AdditionExplorer, CombinationTarget, ScaleExplorer, VectorExplorer } from "@/components/interactive/vectors";
import { CommuteHunt, CompositionExplorer, ProductColumns } from "@/components/interactive/product";
import { ElementaryMoves, InverseBuilder } from "@/components/interactive/elementary";
import { InverseColumnsHunt, SingularHunt, UndoOrder } from "@/components/interactive/inverse";
import { CoordinateFinder, PolynomialCoordinates } from "@/components/interactive/coordinates";
import { QuadrantEscape, ShiftedLineTest } from "@/components/interactive/subspaces";
import { AddressHunt, StaircaseBasis, TrimToBasis } from "@/components/interactive/basis";
import { LiftToPlane, LoopAnywhere, RelationFinder } from "@/components/interactive/independence";
import { OutputReach, PivotPicker, RowSlide } from "@/components/interactive/column-space";
import { PivotBudget, RankTally } from "@/components/interactive/rank-nullity";
import { ColumnBuilder, DerivativeRoutes } from "@/components/interactive/matrix-representations";
import { InvertibilityCalls, StatementBoard } from "@/components/interactive/invertible-matrix-theorem";
import { ChangeMatrixBuilder, SimilarityHunt, TwoAddresses } from "@/components/interactive/change-of-basis";
import { FreeWeights, LandingHunt } from "@/components/interactive/null-space";
import { DerivativeTarget, SharedDerivativeHunt, TranslationGap } from "@/components/interactive/linear-maps";
import { PivotHunt, PolynomialRecipe, ThirdVectorHunt } from "@/components/interactive/span-revisited";
import { DifferenceInKernel, EvaluationKernel } from "@/components/interactive/kernel";
import { ComplementLanding, RangeCollapse } from "@/components/interactive/image-range";
import { DiagonalZeroHunt, EigenDirectionHunt, EigenGapHunt } from "@/components/interactive/eigenvectors";
import { AreaShearSlide, CornerToOrigin } from "@/components/interactive/determinants-as-area";
import { CramerAreas, HeightStack, ProductAreaHunt } from "@/components/interactive/determinant-properties";
import { CofactorLinePicker, MultipleAreaScale, ReplacementShear } from "@/components/interactive/cofactor-expansion";
import { IterateSwing, ShiftToSingular, TraceCurveMatch } from "@/components/interactive/eigenvalue-properties";
import { JordanChainBuilder, MultiplicityGapSlider, NullPowerClimb } from "@/components/interactive/generalized-eigenvectors";
import { DiagonalBasisHunt, EigenOrbitSettle, EigenPolynomialHunt } from "@/components/interactive/diagonalizing-transformations";
import { DiagonalFactorSteps, EigenCoordinateTarget } from "@/components/interactive/diagonalization";
import { CharacteristicSweep, EigenpairHunt } from "@/components/interactive/characteristic-equation";
import { SpectralEllipseBuilder, SymmetricPerpendicularHunt } from "@/components/interactive/symmetric-matrices";
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
    PreimageHunt,
    ShapeMatch,
    CompositionExplorer,
    ProductColumns,
    CommuteHunt,
    PolynomialCombiner,
    ClosureHunt,
    LUBuilder,
    SubstitutionSolver,
    CostCompare,
    ElementaryMoves,
    InverseBuilder,
    InverseColumnsHunt,
    SingularHunt,
    UndoOrder,
    CoordinateFinder,
    PolynomialCoordinates,
    ShiftedLineTest,
    QuadrantEscape,
    TrimToBasis,
    AddressHunt,
    StaircaseBasis,
    RelationFinder,
    LiftToPlane,
    LoopAnywhere,
    OutputReach,
    PivotPicker,
    RowSlide,
    RankTally,
    PivotBudget,
    ColumnBuilder,
    DerivativeRoutes,
    StatementBoard,
    InvertibilityCalls,
    TwoAddresses,
    ChangeMatrixBuilder,
    SimilarityHunt,
    LandingHunt,
    FreeWeights,
    TranslationGap,
    DerivativeTarget,
    SharedDerivativeHunt,
    ThirdVectorHunt,
    PivotHunt,
    PolynomialRecipe,
    DifferenceInKernel,
    EvaluationKernel,
    RangeCollapse,
    ComplementLanding,
    EigenDirectionHunt,
    EigenGapHunt,
    DiagonalZeroHunt,
    AreaShearSlide,
    CornerToOrigin,
    HeightStack,
    ProductAreaHunt,
    CramerAreas,
    CofactorLinePicker,
    ReplacementShear,
    MultipleAreaScale,
    TraceCurveMatch,
    ShiftToSingular,
    IterateSwing,
    MultiplicityGapSlider,
    JordanChainBuilder,
    NullPowerClimb,
    DiagonalBasisHunt,
    EigenOrbitSettle,
    EigenPolynomialHunt,
    EigenCoordinateTarget,
    DiagonalFactorSteps,
    CharacteristicSweep,
    EigenpairHunt,
    SymmetricPerpendicularHunt,
    SpectralEllipseBuilder,
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
