import { ArrowLeft, ArrowRight } from "@phosphor-icons/react/dist/ssr";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Notes } from "@/components/Notes";
import { OriginMark } from "@/components/OriginMark";
import { assetPath, formatDuration, getPublishedLessons, type Lesson } from "@/lib/course";

type Params = { params: Promise<{ day: string }> };

export function generateStaticParams() {
  return getPublishedLessons().map((lesson) => ({ day: String(lesson.day) }));
}

function findLesson(day: string) {
  const lessons = getPublishedLessons();
  const index = lessons.findIndex((lesson) => String(lesson.day) === day);
  return { lesson: lessons[index], previous: lessons[index - 1], next: lessons[index + 1] };
}

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { lesson } = findLesson((await params).day);
  return { title: lesson ? `Day ${lesson.day}: ${lesson.title}` : "Lesson" };
}

function syllabusFact(lesson: Lesson): string {
  if (lesson.syllabus_lesson) return `UM51A Lesson ${lesson.syllabus_lesson}`;
  return lesson.syllabus_note ?? "Groundwork before Lesson 10";
}

function Facts({ lesson }: { lesson: Lesson }) {
  const facts = [
    ["Day", `${lesson.day} of 40`],
    ["Length", formatDuration(lesson.published?.duration_seconds ?? 0)],
    ["Textbook", `Lay §${lesson.lay}`],
    ["Syllabus", syllabusFact(lesson)],
  ];
  return (
    <dl className="mt-6 grid grid-cols-2 gap-x-8 gap-y-3 sm:grid-cols-4">
      {facts.map(([label, value]) => (
        <div key={label}>
          <dt className="text-meta text-text-muted">{label}</dt>
          <dd className="text-meta font-semibold">{value}</dd>
        </div>
      ))}
    </dl>
  );
}

function Pager({ previous, next }: { previous?: Lesson; next?: Lesson }) {
  return (
    <nav aria-label="More lessons" className="mt-20 grid gap-3 sm:grid-cols-2">
      {previous ? (
        <Link href={`/day/${previous.day}/`} className="group rounded-card bg-surface-raised p-5 shadow-lift transition-colors hover:bg-line">
          <span className="inline-flex items-center gap-1.5 text-meta text-text-muted">
            <ArrowLeft className="size-4 transition-transform group-hover:-translate-x-0.5" /> Day {previous.day}
          </span>
          <span className="mt-1 block font-semibold">{previous.title}</span>
        </Link>
      ) : <span />}
      {next ? (
        <Link href={`/day/${next.day}/`} className="group rounded-card bg-surface-raised p-5 text-right shadow-lift transition-colors hover:bg-line">
          <span className="inline-flex items-center gap-1.5 text-meta text-text-muted">
            Day {next.day} <ArrowRight className="size-4 transition-transform group-hover:translate-x-0.5" />
          </span>
          <span className="mt-1 block font-semibold">{next.title}</span>
        </Link>
      ) : null}
    </nav>
  );
}

export default async function LessonPage({ params }: Params) {
  const { lesson, previous, next } = findLesson((await params).day);
  if (!lesson) notFound();

  return (
    <main className="mx-auto max-w-5xl px-4 pb-24 pt-8 sm:px-8">
      <Link href="/" className="inline-flex items-center gap-2 rounded-md py-2 text-meta font-semibold text-text-muted transition-colors hover:text-text">
        <OriginMark />
        All lessons
      </Link>

      <video
        controls
        playsInline
        preload="metadata"
        poster={assetPath(lesson, "poster.jpg")}
        className="mt-4 aspect-video w-full rounded-card bg-surface-sunken shadow-lift"
      >
        <source src={assetPath(lesson, "lesson.mp4")} type="video/mp4" />
      </video>

      <article className="mx-auto mt-10 max-w-[68ch]">
        <h1 className="text-title">{lesson.title}</h1>
        <Facts lesson={lesson} />
        <p className="mt-10 text-lead text-accent">{lesson.big_idea}</p>
        <div className="mt-10">
          <Notes lesson={lesson} />
        </div>
      </article>

      <Pager previous={previous} next={next} />
    </main>
  );
}
