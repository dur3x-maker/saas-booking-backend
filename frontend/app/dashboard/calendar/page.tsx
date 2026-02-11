"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import Button from "@/components/Button";
import Card from "@/components/Card";
import Input from "@/components/Input";

interface Staff {
  id: number;
  first_name: string;
  last_name: string | null;
}

interface StaffServiceLink {
  service_id: number;
  service_name: string;
  price: number;
  duration: number | null;
  is_active: boolean;
}

interface Slot {
  start: string;
  end: string;
}

export default function CalendarPage() {
  const [staffList, setStaffList] = useState<Staff[]>([]);
  const [staffServices, setStaffServices] = useState<StaffServiceLink[]>([]);
  const [staffId, setStaffId] = useState("");
  const [serviceId, setServiceId] = useState("");
  const [day, setDay] = useState("");
  const [slots, setSlots] = useState<Slot[]>([]);
  const [loadingSlots, setLoadingSlots] = useState(false);

  // Booking modal
  const [selectedSlot, setSelectedSlot] = useState<Slot | null>(null);
  const [custName, setCustName] = useState("");
  const [custPhone, setCustPhone] = useState("");
  const [custEmail, setCustEmail] = useState("");
  const [booking, setBooking] = useState(false);
  const [bookError, setBookError] = useState("");
  const [bookSuccess, setBookSuccess] = useState("");

  useEffect(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    setDay(d.toISOString().slice(0, 10));
    api<Staff[]>("/staff", { needsBusiness: true })
      .then(setStaffList)
      .catch(() => {});
  }, []);

  // When staff changes, load their linked services
  useEffect(() => {
    setServiceId("");
    setStaffServices([]);
    setSlots([]);
    setSelectedSlot(null);
    if (!staffId) return;
    api<StaffServiceLink[]>(`/staff/${staffId}/services`, {
      needsBusiness: true,
    })
      .then(setStaffServices)
      .catch(() => {});
  }, [staffId]);

  async function loadSlots() {
    if (!staffId || !serviceId || !day) return;
    setLoadingSlots(true);
    setSlots([]);
    setSelectedSlot(null);
    try {
      const data = await api<Slot[]>(
        `/schedule/staff/${staffId}/slots?service_id=${serviceId}&day=${day}`,
        { needsBusiness: true },
      );
      setSlots(data);
    } catch {
      setSlots([]);
    } finally {
      setLoadingSlots(false);
    }
  }

  useEffect(() => {
    if (staffId && serviceId && day) loadSlots();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [staffId, serviceId, day]);

  async function handleBook() {
    if (!selectedSlot || !staffId || !serviceId) return;
    setBooking(true);
    setBookError("");
    setBookSuccess("");
    try {
      await api("/bookings", {
        method: "POST",
        needsBusiness: true,
        body: {
          staff_id: Number(staffId),
          service_id: Number(serviceId),
          start_at: selectedSlot.start,
          confirm: true,
          customer: {
            name: custName,
            phone: custPhone,
            email: custEmail || null,
          },
        },
      });
      setBookSuccess("Booking created!");
      setSelectedSlot(null);
      setCustName("");
      setCustPhone("");
      setCustEmail("");
      loadSlots();
    } catch (err) {
      setBookError(err instanceof ApiError ? err.message : "Booking failed");
    } finally {
      setBooking(false);
    }
  }

  function formatTime(iso: string) {
    return new Date(iso).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="mb-4 text-lg font-semibold text-brand-800">Calendar</h1>

      {/* Filters */}
      <Card className="mb-4">
        <div className="grid grid-cols-3 gap-3">
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-brand-700">Staff</label>
            <select
              className="rounded-lg border border-brand-300 bg-white px-3 py-2 text-sm text-brand-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={staffId}
              onChange={(e) => setStaffId(e.target.value)}
            >
              <option value="">Select staff</option>
              {staffList.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.first_name} {s.last_name ?? ""}
                </option>
              ))}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-brand-700">
              Service
            </label>
            <select
              className="rounded-lg border border-brand-300 bg-white px-3 py-2 text-sm text-brand-900 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
              value={serviceId}
              onChange={(e) => setServiceId(e.target.value)}
              disabled={!staffId}
            >
              <option value="">
                {!staffId
                  ? "Select staff first"
                  : staffServices.length === 0
                    ? "No services linked"
                    : "Select service"}
              </option>
              {staffServices.map((ss) => (
                <option key={ss.service_id} value={ss.service_id}>
                  {ss.service_name} ({ss.duration ?? "?"} min, {ss.price}₽)
                </option>
              ))}
            </select>
          </div>

          <Input
            label="Date"
            type="date"
            value={day}
            onChange={(e) => setDay(e.target.value)}
          />
        </div>

        {staffId && staffServices.length === 0 && (
          <p className="mt-2 text-xs text-brand-400">
            No services linked to this staff member. Go to Services → Manage to
            link them.
          </p>
        )}
      </Card>

      {/* Slots */}
      {loadingSlots && (
        <p className="py-8 text-center text-brand-400">Loading slots...</p>
      )}

      {!loadingSlots && staffId && serviceId && day && slots.length === 0 && (
        <p className="py-8 text-center text-brand-400">
          No available slots for this date
        </p>
      )}

      {slots.length > 0 && (
        <div className="grid grid-cols-4 gap-2 sm:grid-cols-6">
          {slots.map((slot) => (
            <button
              key={slot.start}
              onClick={() => {
                setSelectedSlot(slot);
                setBookError("");
                setBookSuccess("");
              }}
              className={`rounded-lg border px-3 py-2 text-sm transition-colors ${
                selectedSlot?.start === slot.start
                  ? "border-brand-500 bg-brand-800 text-white"
                  : "border-brand-200 bg-white text-brand-700 hover:border-brand-400"
              }`}
            >
              {formatTime(slot.start)}
            </button>
          ))}
        </div>
      )}

      {/* Booking modal */}
      {selectedSlot && (
        <Card className="mt-4">
          <h2 className="mb-3 font-medium text-brand-800">
            Book: {formatTime(selectedSlot.start)} &mdash;{" "}
            {formatTime(selectedSlot.end)}
          </h2>
          <div className="grid grid-cols-3 gap-3">
            <Input
              label="Customer Name"
              value={custName}
              onChange={(e) => setCustName(e.target.value)}
              required
            />
            <Input
              label="Customer Phone"
              value={custPhone}
              onChange={(e) => setCustPhone(e.target.value)}
              placeholder="+79001234567"
              required
            />
            <Input
              label="Email (optional)"
              type="email"
              value={custEmail}
              onChange={(e) => setCustEmail(e.target.value)}
            />
          </div>

          {bookError && (
            <p className="mt-2 text-sm text-red-500">{bookError}</p>
          )}
          {bookSuccess && (
            <p className="mt-2 text-sm text-green-600">{bookSuccess}</p>
          )}

          <div className="mt-3 flex gap-2">
            <Button
              onClick={handleBook}
              loading={booking}
              disabled={!custName || !custPhone}
            >
              Confirm Booking
            </Button>
            <Button variant="ghost" onClick={() => setSelectedSlot(null)}>
              Cancel
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
