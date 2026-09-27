import { Play } from "@phosphor-icons/react/dist/ssr";
import Link from "next/link";
import { LessonRow } from "@/components/LessonRow";
import { OriginMark } from "@/components/OriginMark";
import { assetPath, formatDuration, getPublishedLessons, getUnits, type Lesson } from "@/lib/course";

function LatestLesson({ lesson }: { lesson: Lesson }) {
  return (
    <Link href={`/day/${lesson.day}/`} className="group block">
      <div className="relative overflow-hidden rounded-card shadow-lift">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={assetPath(lesson, "poster.jpg")}
          alt=""
          className="aspect-video w-full object-cover transition-transform duration-500 ease-spring group-hover:scale-[1.02]"
        />
        <span className="absolute bottom-4 left-4 inline-flex items-center gap-2 rounded-lg bg-surface/90 px-4 py-2.5 text-meta font-semibold backdrop-blur transition-colors group-hover:bg-surface">
          <Play weight="fill" className="size-4 text-accent" />
          Watch day {lesson.day}
          <span className="font-normal text-text-muted">{formatDuration(lesson.published?.duration_seconds ?? 0)}</span>
        </span>
      </div>
      <h2 className="mt-5 text-title">{lesson.title}</h2>
      <p className="mt-2 max-w-2xl text-lead text-text-muted">{lesson.big_idea}</p>
    </Link>
  );
}

export default function Home() {
  const units = getUnits();
  const published = getPublishedLessons();
  const latest = published.at(-1);
  const total = units.reduce((sum, unit) => sum + unit.lessons.length, 0);

  return (
    <main className="relative">
      <div aria-hidden className="grid-paper pointer-events-none absolute inset-x-0 top-0 h-[42rem] [mask-image:radial-gradient(ellipse_at_top,black_20%,transparent_70%)]" />
      <div className="relative mx-auto max-w-5xl px-4 pb-24 pt-14 sm:px-8 sm:pt-20">
        <header className="flex items-start gap-3">
          <OriginMark className="mt-3 sm:mt-4" />
          <div>
            <h1 className="text-display">Linear algebra, one idea a morning</h1>
            <p className="mt-3 text-lead text-text-muted">
              {published.length} of {total} lessons out so far. A new one lands every morning by 8 am Pacific.
            </p>
          </div>
        </header>

        {latest ? (
          <section aria-label="Latest lesson" className="mt-12">
            <LatestLesson lesson={latest} />
          </section>
        ) : null}

        <div className="mt-20 space-y-14">
          {units.map((unit) => (
            <section key={unit.name}>
              <h2 className="text-section">{unit.name}</h2>
              <ol className="mt-4 grid gap-1 sm:grid-cols-2">
                {unit.lessons.map((lesson) => (
                  <LessonRow key={lesson.day} lesson={lesson} />
                ))}
              </ol>
            </section>
          ))}
        </div>
      </div>
    </main>
  );
}
