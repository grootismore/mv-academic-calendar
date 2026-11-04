// The iCalendar files. Kept in its own entry point so apps that only need the data stay small.
import ICS from "../data/ics.json";

/** The iCalendar text for a calendar, such as "2026" or "2023-2024". Throws if there is no such calendar. */
export function ics(file) {
  const text = ICS[String(file)];
  if (!text) throw new RangeError(`No calendar named "${file}". Available: ${Object.keys(ICS).join(", ")}`);
  return text;
}
export const files = () => Object.keys(ICS);
