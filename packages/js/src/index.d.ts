export type Category = "public_holiday" | "school_days" | "exam_days" | "term_holidays" | "other";
export type Status = "final" | "current" | "tentative";

export interface CalendarEvent {
  /** Stable across updates; only changes if the name or start date changes. */
  readonly id: string;
  /** First day, "YYYY-MM-DD". */
  readonly start: string;
  /** Last day, inclusive. Always set (equals `start` for a single day). */
  readonly end: string;
  readonly name: string;
  readonly category: Category;
  /** The year the calendar starts in. */
  readonly calendar: number;
  /** The calendar's file name: "2026" or "2023-2024". */
  readonly file: string;
  readonly status: Status;
}

export interface CalendarInfo {
  file: string;
  year: number;
  status: Status;
  events: number;
  /** When this calendar was last checked, "YYYY-MM-DD". */
  retrieved: string;
}

export interface EventFilter {
  file?: string | string[];
  year?: number;
  category?: Category | Category[];
  status?: Status | Status[];
  from?: string | Date;
  to?: string | Date;
  text?: string;
}

export const attribution: string;
export const updated: string;
export function toDate(d: string | Date): string;
export function calendars(): CalendarInfo[];
export function events(filter?: EventFilter): CalendarEvent[];
export function eventsOn(date: string | Date): CalendarEvent[];
export function isPublicHoliday(date: string | Date): boolean;
export function nextEvent(date: string | Date, filter?: EventFilter): CalendarEvent | undefined;
