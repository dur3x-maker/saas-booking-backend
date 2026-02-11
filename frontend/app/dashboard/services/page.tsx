"use client";

import { useEffect, useState, FormEvent } from "react";
import { api, ApiError } from "@/lib/api";
import Table from "@/components/Table";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Card from "@/components/Card";

interface Service {
  id: number;
  name: string;
  description: string | null;
  duration_minutes: number;
  price: number;
  is_active: boolean;
  [key: string]: unknown;
}

interface StaffItem {
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

export default function ServicesPage() {
  const [rows, setRows] = useState<Service[]>([]);
  const [staffList, setStaffList] = useState<StaffItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Create form
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [duration, setDuration] = useState("30");
  const [price, setPrice] = useState("0");
  const [selectedStaff, setSelectedStaff] = useState<number[]>([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  // Staff links panel
  const [expandedServiceId, setExpandedServiceId] = useState<number | null>(null);
  const [linkedStaff, setLinkedStaff] = useState<StaffItem[]>([]);
  const [loadingLinks, setLoadingLinks] = useState(false);
  const [linkError, setLinkError] = useState("");

  async function load() {
    setLoading(true);
    try {
      const [services, staff] = await Promise.all([
        api<Service[]>("/services", { needsBusiness: true }),
        api<StaffItem[]>("/staff", { needsBusiness: true }),
      ]);
      setRows(services);
      setStaffList(staff);
    } catch {
      /* ignore */
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function toggleStaff(id: number) {
    setSelectedStaff((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id],
    );
  }

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      const created = await api<Service>("/services", {
        method: "POST",
        needsBusiness: true,
        body: {
          name,
          duration_minutes: Number(duration),
          price: Number(price),
        },
      });

      // Attach selected staff
      for (const staffId of selectedStaff) {
        await api(
          `/staff/${staffId}/services/${created.id}?price=${Number(price)}&duration=${Number(duration)}`,
          { method: "POST", needsBusiness: true },
        );
      }

      setName("");
      setDuration("30");
      setPrice("0");
      setSelectedStaff([]);
      setShowForm(false);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error");
    } finally {
      setSaving(false);
    }
  }

  async function loadLinkedStaff(serviceId: number) {
    if (expandedServiceId === serviceId) {
      setExpandedServiceId(null);
      return;
    }
    setExpandedServiceId(serviceId);
    setLoadingLinks(true);
    setLinkError("");
    try {
      const staff = await api<StaffItem[]>(
        `/services/${serviceId}/staff`,
        { needsBusiness: true },
      );
      setLinkedStaff(staff);
    } catch {
      setLinkedStaff([]);
    } finally {
      setLoadingLinks(false);
    }
  }

  async function attachStaff(serviceId: number, staffId: number) {
    setLinkError("");
    const svc = rows.find((r) => r.id === serviceId);
    try {
      await api(
        `/staff/${staffId}/services/${serviceId}?price=${svc?.price ?? 0}&duration=${svc?.duration_minutes ?? 30}`,
        { method: "POST", needsBusiness: true },
      );
      loadLinkedStaff(serviceId);
      setExpandedServiceId(serviceId);
    } catch (err) {
      setLinkError(err instanceof ApiError ? err.message : "Error");
    }
  }

  async function detachStaff(serviceId: number, staffId: number) {
    setLinkError("");
    try {
      await api(`/staff/${staffId}/services/${serviceId}`, {
        method: "DELETE",
        needsBusiness: true,
      });
      loadLinkedStaff(serviceId);
      setExpandedServiceId(serviceId);
    } catch (err) {
      setLinkError(err instanceof ApiError ? err.message : "Error");
    }
  }

  const linkedStaffIds = linkedStaff.map((s) => s.id);

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-brand-800">Services</h1>
        <Button onClick={() => setShowForm((v) => !v)} variant="secondary">
          {showForm ? "Cancel" : "+ Add Service"}
        </Button>
      </div>

      {showForm && (
        <Card className="mb-4">
          <form onSubmit={handleCreate} className="flex flex-col gap-3">
            <div className="grid grid-cols-3 gap-3">
              <Input
                label="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
              <Input
                label="Duration (min)"
                type="number"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                required
                min={5}
              />
              <Input
                label="Price"
                type="number"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                required
                min={0}
              />
            </div>

            {staffList.length > 0 && (
              <div>
                <p className="mb-1 text-sm font-medium text-brand-700">
                  Assign to Staff
                </p>
                <div className="flex flex-wrap gap-2">
                  {staffList.map((s) => (
                    <label
                      key={s.id}
                      className={`flex cursor-pointer items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm transition-colors ${
                        selectedStaff.includes(s.id)
                          ? "border-brand-500 bg-brand-50 text-brand-800"
                          : "border-brand-200 text-brand-600 hover:border-brand-300"
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedStaff.includes(s.id)}
                        onChange={() => toggleStaff(s.id)}
                        className="accent-brand-600"
                      />
                      {s.first_name} {s.last_name ?? ""}
                    </label>
                  ))}
                </div>
              </div>
            )}

            {error && <p className="text-sm text-red-500">{error}</p>}
            <Button type="submit" loading={saving} className="self-start">
              Create
            </Button>
          </form>
        </Card>
      )}

      <Table
        loading={loading}
        rows={rows}
        columns={[
          { key: "id", header: "ID" },
          { key: "name", header: "Name" },
          { key: "duration_minutes", header: "Duration" },
          { key: "price", header: "Price" },
          {
            key: "is_active",
            header: "Active",
            render: (r) => (r.is_active ? "Yes" : "No"),
          },
          {
            key: "_staff",
            header: "Staff",
            render: (r) => (
              <Button
                variant="ghost"
                className="text-xs"
                onClick={() => loadLinkedStaff(r.id)}
              >
                {expandedServiceId === r.id ? "Hide" : "Manage"}
              </Button>
            ),
          },
        ]}
      />

      {/* Staff links panel */}
      {expandedServiceId && (
        <Card className="mt-4">
          <h3 className="mb-2 text-sm font-semibold text-brand-800">
            Staff for: {rows.find((r) => r.id === expandedServiceId)?.name}
          </h3>

          {loadingLinks && (
            <p className="text-sm text-brand-400">Loading...</p>
          )}

          {linkError && (
            <p className="mb-2 text-sm text-red-500">{linkError}</p>
          )}

          {!loadingLinks && (
            <div className="flex flex-wrap gap-2">
              {staffList.map((s) => {
                const isLinked = linkedStaffIds.includes(s.id);
                return (
                  <button
                    key={s.id}
                    onClick={() =>
                      isLinked
                        ? detachStaff(expandedServiceId, s.id)
                        : attachStaff(expandedServiceId, s.id)
                    }
                    className={`rounded-lg border px-3 py-1.5 text-sm transition-colors ${
                      isLinked
                        ? "border-brand-500 bg-brand-800 text-white"
                        : "border-brand-200 text-brand-600 hover:border-brand-400"
                    }`}
                  >
                    {s.first_name} {s.last_name ?? ""}
                    {isLinked ? " ✓" : ""}
                  </button>
                );
              })}
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
