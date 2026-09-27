import Link from "next/link";
import { assetPath, formatDuration, type Lesson } from "@/lib/course";

function Thumbnail({ lesson }: { lesson: Lesson }) {
  if (!lesson.published) {
    return (
      <div
        aria-hidden
        className="aspect-video w-28 shrink-0 rounded-md bg-surface-sunken bg-[repeating-linear-gradient(135deg,transparent_0_6px,var(--color-line)_6px_7px)] sm:w-36"
      />
    );
  }
  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={assetPath(lesson, "poster.jpg")}
      alt=""
      className="aspect-video w-28 shrink-0 rounded-md object-cover shadow-lift transition-transform duration-300 ease-spring group-hover:scale-[1.03] sm:w-36"
    />
  );
}

function RowBody({ lesson }: { lesson: Lesson }) {
  return (
    <div className="min-w-0">
      <p className="text-meta text-text-muted">
        Day {lesson.day}
        {lesson.published ? <span className="text-text-muted/80">, {formatDuration(lesson.published.duration_seconds)}</span> : null}
      </p>
      <h3 className="mt-0.5 text-body font-semibold leading-snug text-pretty">{lesson.title}</h3>
      <p className="mt-1 line-clamp-2 text-meta text-text-muted">{lesson.big_idea}</p>
    </div>
  );
}

export function LessonRow({ lesson }: { lesson: Lesson }) {
  const content = (
    <>
      <Thumbnail lesson={lesson} />
      <RowBody lesson={lesson} />
    </>
  );
  if (!lesson.published) {
    return <li className="flex items-center gap-4 rounded-card p-3 opacity-55">{content}</li>;
  }
  return (
    <li>
      <Link
        href={`/day/${lesson.day}/`}
        className="group flex items-center gap-4 rounded-card p-3 transition-colors hover:bg-surface-raised"
      >
        {content}
      </Link>
    </li>
  );
}
