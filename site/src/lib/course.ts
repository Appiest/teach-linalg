import fs from "node:fs";
import path from "node:path";

const repoRoot = path.resolve(process.cwd(), "..");
const lessonsDir = path.join(repoRoot, "lessons");

type CurriculumDay = {
  day: number;
  slug: string;
  title: string;
  unit: string;
  lay: string;
  syllabus_lesson: number | null;
  syllabus_note?: string;
  big_idea: string;
};

type LessonMeta = {
  published_on: string;
  duration_seconds: number;
};

export type Lesson = CurriculumDay & {
  folder: string;
  published: LessonMeta | null;
};

export type Unit = { name: string; lessons: Lesson[] };

function readJson<T>(file: string): T {
  return JSON.parse(fs.readFileSync(file, "utf8")) as T;
}

function lessonFolder(day: CurriculumDay): string {
  return `day-${String(day.day).padStart(2, "0")}-${day.slug}`;
}

function readPublished(folder: string): LessonMeta | null {
  const metaPath = path.join(lessonsDir, folder, "meta.json");
  const hasVideo = fs.existsSync(path.join(lessonsDir, folder, "lesson.mp4"));
  if (!hasVideo || !fs.existsSync(metaPath)) return null;
  return readJson<LessonMeta>(metaPath);
}

export function getLessons(): Lesson[] {
  const curriculum = readJson<{ days: CurriculumDay[] }>(path.join(repoRoot, "curriculum.json"));
  return curriculum.days.map((day) => {
    const folder = lessonFolder(day);
    return { ...day, folder, published: readPublished(folder) };
  });
}

export function getPublishedLessons(): Lesson[] {
  return getLessons().filter((lesson) => lesson.published);
}

export function getUnits(): Unit[] {
  const units = new Map<string, Lesson[]>();
  for (const lesson of getLessons()) {
    units.set(lesson.unit, [...(units.get(lesson.unit) ?? []), lesson]);
  }
  return [...units].map(([name, lessons]) => ({ name, lessons }));
}

export function getNotesSource(lesson: Lesson): string {
  return fs.readFileSync(path.join(lessonsDir, lesson.folder, "notes.mdx"), "utf8");
}

export function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const rest = Math.round(seconds % 60);
  return `${minutes}:${String(rest).padStart(2, "0")}`;
}

export function assetPath(lesson: Lesson, file: string): string {
  return `${process.env.NEXT_PUBLIC_BASE_PATH ?? ""}/lessons/${lesson.folder}/${file}`;
}
