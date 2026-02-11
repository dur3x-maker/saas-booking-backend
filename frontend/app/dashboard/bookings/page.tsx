"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import Table from "@/components/Table";
import Button from "@/components/Button";

interface Booking {
  id: number;
  business_id: number;
  staff_id: number;
  staff_service_id: number;
  customer_id: number;
  start_at: string;
  end_at: string;
  price: number;
  duration_min: number;
  status: string;
  expires_at: string | null;
  customer_name: string | null;
  comment: string | null;
  is_active: boolean;
  created_at: string;
  [key: string]: unknown;
}

export default function BookingsPage() {
  const [rows, setRows] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const data = await api<Booking[]>("/bookings", { needsBusiness: true });
      setRows(data);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCancel(id: number) {
    try {
      await api(`/bookings/${id}/cancel`, {
        method: "POST",
        needsBusiness: true,
      });
      load();
    } catch {
      /* ignore */
    }
  }

  async function handleConfirm(id: number) {
    try {
      await api(`/bookings/${id}/confirm`, {
        method: "POST",
        needsBusiness: true,
      });
      load();
    } catch {
      /* ignore */
    }
  }

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-brand-800">Bookings</h1>
        <p className="text-sm text-brand-500">
          Create bookings from the Calendar page
        </p>
      </div>

      <Table
        loading={loading}
        rows={rows}
        columns={[
          { key: "id", header: "ID" },
          {
            key: "customer_name",
            header: "Customer",
            render: (r) => r.customer_name ?? "—",
          },
          {
            key: "start_at",
            header: "Start",
            render: (r) => new Date(r.start_at).toLocaleString(),
          },
          {
            key: "duration_min",
            header: "Duration",
            render: (r) => `${r.duration_min} min`,
          },
          {
            key: "price",
            header: "Price",
            render: (r) => `${r.price}₽`,
          },
          {
            key: "status",
            header: "Status",
            render: (r) => (
              <span
                className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                  r.status === "CONFIRMED"
                    ? "bg-green-100 text-green-700"
                    : r.status === "HOLD"
                      ? "bg-yellow-100 text-yellow-700"
                      : r.status === "CANCELLED"
                        ? "bg-red-100 text-red-600"
                        : "bg-brand-100 text-brand-600"
                }`}
              >
                {r.status}
              </span>
            ),
          },
          {
            key: "_actions",
            header: "",
            render: (r) => (
              <div className="flex gap-1">
                {r.status === "HOLD" && (
                  <Button
                    variant="ghost"
                    onClick={() => handleConfirm(r.id)}
                    className="text-xs text-green-600"
                  >
                    Confirm
                  </Button>
                )}
                {(r.status === "CONFIRMED" || r.status === "HOLD") && (
                  <Button
                    variant="ghost"
                    onClick={() => handleCancel(r.id)}
                    className="text-xs text-red-500"
                  >
                    Cancel
                  </Button>
                )}
              </div>
            ),
          },
        ]}
      />
    </div>
  );
}
