import { Children } from "react";
import { MDXRemote } from "next-mdx-remote-client/rsc";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";
import { VectorAnswer } from "@/components/interactive/answers";
import { Choice, Step, Steps } from "@/components/interactive/walkthrough";
import { Answer, Check, Concept, Definition, Hint, Problem, Solution, Warning } from "@/components/Walkthrough";
import { TransformExplorer } from "@/components/interactive/transform";
import { EntryHunt, SpanPainter } from "@/components/interactive/span";
import { RowReduceExplorer, SolutionCountExplorer } from "@/components/interactive/systems";
import { ColumnSpanCheck, MatrixVectorExplorer } from "@/components/interactive/matrix";
import { PreimageHunt, ShapeMatch } from "@/components/interactive/transformations";
import { ClosureHunt, NegativeFinder, PolynomialCombiner, ScalingEscape } from "@/components/interactive/vector-spaces";
import { CostCompare, LUBuilder, PivotFlattener, SubstitutionSolver, TwoTriangleSolve } from "@/components/interactive/lu";
import { AdditionExplorer, CombinationTarget, DifferenceExplorer, GridWeights, ScaleExplorer, VectorExplorer } from "@/components/interactive/vectors";
import { ColumnWeights, CommuteHunt, CompositionExplorer, ProductColumns, ZeroProductHunt } from "@/components/interactive/product";
import { BuildFromSteps, ElementaryMoves, InverseBuilder, RowRecipe } from "@/components/interactive/elementary";
import { DeterminantSlider, InverseColumnsHunt, SameLanding, SingularHunt, UndoOrder } from "@/components/interactive/inverse";
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
import { DotShadowHunt, RowPerpendicularHunt, UnitCircleScale } from "@/components/interactive/inner-products";
import { LongestStretchHunt, RankCopyBudget, SvdEllipseMatch } from "@/components/interactive/singular-value-decomposition";
import { LineFootHunt, NearestPlanePoint, ShadowSumBasis } from "@/components/interactive/orthogonal-projection";
import { QrWeightSliders, ShadowSubtractSlider, StraightenedTargetHunt } from "@/components/interactive/gram-schmidt";
import { ProjectionRightAngle, ResidualSquaresFit } from "@/components/interactive/least-squares";
import { QuadraticAxisTurner, QuadraticCircleMax, QuadraticSurfaceShaper } from "@/components/interactive/quadratic-forms";
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
    VectorExplorer,
    AdditionExplorer,
    ScaleExplorer,
    CombinationTarget,
    DifferenceExplorer,
    GridWeights,
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
    ColumnWeights,
    ZeroProductHunt,
    PolynomialCombiner,
    ClosureHunt,
    NegativeFinder,
    ScalingEscape,
    LUBuilder,
    SubstitutionSolver,
    CostCompare,
    TwoTriangleSolve,
    PivotFlattener,
    ElementaryMoves,
    InverseBuilder,
    RowRecipe,
    BuildFromSteps,
    InverseColumnsHunt,
    SingularHunt,
    UndoOrder,
    SameLanding,
    DeterminantSlider,
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
    DotShadowHunt,
    UnitCircleScale,
    RowPerpendicularHunt,
    LongestStretchHunt,
    SvdEllipseMatch,
    RankCopyBudget,
    LineFootHunt,
    ShadowSumBasis,
    NearestPlanePoint,
    ShadowSubtractSlider,
    StraightenedTargetHunt,
    QrWeightSliders,
    ResidualSquaresFit,
    ProjectionRightAngle,
    QuadraticAxisTurner,
    QuadraticSurfaceShaper,
    QuadraticCircleMax,
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
