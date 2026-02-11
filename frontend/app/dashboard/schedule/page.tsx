"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import Button from "@/components/Button";
import Card from "@/components/Card";

interface StaffItem {
  id: number;
  first_name: string;
  last_name: string | null;
}

interface WorkingHoursEntry {
  id: number;
  staff_id: number;
  weekday: number;
  start_time: string;
  end_time: string;
  break_start: string | null;
  break_end: string | null;
  is_active: boolean;
}

interface DayRow {
  weekday: number;
  enabled: boolean;
  start_time: string;
  end_time: string;
  break_start: string;
  break_end: string;
}

const WEEKDAY_NAMES = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

function emptyWeek(): DayRow[] {
  return WEEKDAY_NAMES.map((_, i) => ({
    weekday: i,
    enabled: i < 5,
    start_time: "09:00",
    end_time: "18:00",
    break_start: "",
    break_end: "",
  }));
}

export default function SchedulePage() {
  const [staffList, setStaffList] = useState<StaffItem[]>([]);
  const [staffId, setStaffId] = useState("");
  const [days, setDays] = useState<DayRow[]>(emptyWeek);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    api<StaffItem[]>("/staff", { needsBusiness: true })
      .then(setStaffList)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!staffId) return;
    setLoading(true);
    setError("");
    setSuccess("");
    api<WorkingHoursEntry[]>(`/working-hours?staff_id=${staffId}`, {
      needsBusiness: true,
    })
      .then((entries) => {
        const week = emptyWeek();
        // Reset all to disabled first
        week.forEach((d) => (d.enabled = false));
        for (const e of entries) {
          if (e.weekday >= 0 && e.weekday <= 6) {
            week[e.weekday] = {
              weekday: e.weekday,
              enabled: e.is_active,
              start_time: e.start_time.slice(0, 5),
              end_time: e.end_time.slice(0, 5),
              break_start: e.break_start ? e.break_start.slice(0, 5) : "",
              break_end: e.break_end ? e.break_end.slice(0, 5) : "",
            };
          }
        }
        setDays(week);
      })
      .catch(() => {
        setDays(emptyWeek());
      })
      .finally(() => setLoading(false));
  }, [staffId]);

  function updateDay(weekday: number, patch: Partial<DayRow>) {
    setDays((prev) =>
      prev.map((d) => (d.weekday === weekday ? { ...d, ...patch } : d)),
    );
  }

  async function handleSave() {
    if (!staffId) return;
    setSaving(true);
    setError("");
    setSuccess("");

    try {
      // Create new working hours for each enabled day
      const enabledDays = days.filter((d) => d.enabled);

      for (const d of enabledDays) {
        await api("/working-hours", {
          method: "POST",
          needsBusiness: true,
          body: {
            staff_id: Number(staffId),
            weekday: d.weekday,
            start_time: d.start_time + ":00",
            end_time: d.end_time + ":00",
            break_start: d.break_start ? d.break_start + ":00" : null,
            break_end: d.break_end ? d.break_end + ":00" : null,
            is_active: true,
          },
        });
      }

      setSuccess("Schedule saved successfully");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to save schedule");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-4 text-lg font-semibold text-brand-800">
        Working Hours
      </h1>

      {/* Staff selector */}
      <Card className="mb-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-brand-700">
            Select Staff
          </label>
          <select
            className="rounded-lg border border-brand-300 bg-white px-3 py-2 text-sm text-brand-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            value={staffId}
            onChange={(e) => setStaffId(e.target.value)}
          >
            <option value="">Choose a staff member</option>
            {staffList.map((s) => (
              <option key={s.id} value={s.id}>
                {s.first_name} {s.last_name ?? ""}
              </option>
            ))}
          </select>
        </div>
      </Card>

      {loading && (
        <p className="py-8 text-center text-brand-400">Loading schedule...</p>
      )}

      {/* Schedule grid */}
      {staffId && !loading && (
        <Card>
          <div className="flex flex-col gap-3">
            {days.map((d) => (
              <div
                key={d.weekday}
                className={`flex items-center gap-3 rounded-lg border px-3 py-2 transition-colors ${
                  d.enabled
                    ? "border-brand-200 bg-white"
                    : "border-brand-100 bg-brand-50"
                }`}
              >
                {/* Toggle */}
                <label className="flex w-28 shrink-0 cursor-pointer items-center gap-2">
                  <input
                    type="checkbox"
                    checked={d.enabled}
                    onChange={(e) =>
                      updateDay(d.weekday, { enabled: e.target.checked })
                    }
                    className="accent-brand-600"
                  />
                  <span
                    className={`text-sm font-medium ${
                      d.enabled ? "text-brand-800" : "text-brand-400"
                    }`}
                  >
                    {WEEKDAY_NAMES[d.weekday]}
                  </span>
                </label>

                {d.enabled && (
                  <>
                    {/* Work time */}
                    <div className="flex items-center gap-1">
                      <input
                        type="time"
                        value={d.start_time}
                        onChange={(e) =>
                          updateDay(d.weekday, { start_time: e.target.value })
                        }
                        className="rounded border border-brand-300 px-2 py-1 text-sm text-brand-900"
                      />
                      <span className="text-brand-400">—</span>
                      <input
                        type="time"
                        value={d.end_time}
                        onChange={(e) =>
                          updateDay(d.weekday, { end_time: e.target.value })
                        }
                        className="rounded border border-brand-300 px-2 py-1 text-sm text-brand-900"
                      />
                    </div>

                    {/* Break */}
                    <div className="flex items-center gap-1 text-brand-500">
                      <span className="text-xs">Break:</span>
                      <input
                        type="time"
                        value={d.break_start}
                        onChange={(e) =>
                          updateDay(d.weekday, { break_start: e.target.value })
                        }
                        className="rounded border border-brand-200 px-2 py-1 text-xs text-brand-700"
                      />
                      <span className="text-brand-300">—</span>
                      <input
                        type="time"
                        value={d.break_end}
                        onChange={(e) =>
                          updateDay(d.weekday, { break_end: e.target.value })
                        }
                        className="rounded border border-brand-200 px-2 py-1 text-xs text-brand-700"
                      />
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>

          {error && (
            <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
              {error}
            </p>
          )}
          {success && (
            <p className="mt-3 rounded-lg bg-green-50 px-3 py-2 text-sm text-green-600">
              {success}
            </p>
          )}

          <div className="mt-4">
            <Button onClick={handleSave} loading={saving}>
              Save Schedule
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
