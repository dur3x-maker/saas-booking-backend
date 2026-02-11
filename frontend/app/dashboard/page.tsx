"use client";

import { FormEvent, useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { getBusinessId, setBusinessId } from "@/lib/business-context";
import Card from "@/components/Card";
import Button from "@/components/Button";
import Input from "@/components/Input";

interface Business {
  id: number;
  name: string;
  role: string;
}

interface MeData {
  user: { id: number; email: string; is_active: boolean; created_at: string };
  businesses: Business[];
}

interface BusinessReadResponse {
  id: number;
  name: string;
  timezone: string;
  is_active: boolean;
}

function CreateBusinessCard({ onCreated }: { onCreated: () => void }) {
  const [name, setName] = useState("");
  const [timezone, setTimezone] = useState("UTC");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      const biz = await api<BusinessReadResponse>("/businesses", {
        method: "POST",
        body: { name, timezone: timezone || "UTC" },
      });
      setBusinessId(biz.id);
      onCreated();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create business");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <Card className="w-full max-w-md">
        <h2 className="mb-1 text-lg font-semibold text-brand-800">
          Create Your First Business
        </h2>
        <p className="mb-5 text-sm text-brand-500">
          To get started, give your business a name.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            label="Business Name"
            placeholder="My Salon"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <Input
            label="Timezone (optional)"
            placeholder="UTC"
            value={timezone}
            onChange={(e) => setTimezone(e.target.value)}
          />

          {error && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
              {error}
            </p>
          )}

          <Button type="submit" loading={saving} disabled={!name.trim()}>
            Create Business
          </Button>
        </form>
      </Card>
    </div>
  );
}

export default function DashboardPage() {
  const [me, setMe] = useState<MeData | null>(null);
  const [selected, setSelected] = useState<string | null>(null);

  function loadMe() {
    api<MeData>("/me").then(setMe).catch(() => {});
  }

  useEffect(() => {
    setSelected(getBusinessId());
    loadMe();
  }, []);

  function selectBusiness(biz: Business) {
    setBusinessId(biz.id);
    setSelected(String(biz.id));
  }

  if (!me) {
    return (
      <div className="flex items-center justify-center py-20 text-brand-400">
        Loading...
      </div>
    );
  }

  if (me.businesses.length === 0) {
    return <CreateBusinessCard onCreated={loadMe} />;
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-6 text-lg font-semibold text-brand-800">
        Select Business
      </h1>

      <div className="flex flex-col gap-3">
        {me.businesses.map((biz) => (
          <Card
            key={biz.id}
            className={`flex items-center justify-between ${selected === String(biz.id) ? "ring-2 ring-brand-500" : ""}`}
          >
            <div>
              <p className="font-medium text-brand-800">{biz.name}</p>
              <p className="text-xs text-brand-500">
                Role: {biz.role} &middot; ID: {biz.id}
              </p>
            </div>
            <Button
              variant={selected === String(biz.id) ? "primary" : "secondary"}
              onClick={() => selectBusiness(biz)}
            >
              {selected === String(biz.id) ? "Selected" : "Select"}
            </Button>
          </Card>
        ))}
      </div>

      {selected && (
        <p className="mt-6 text-center text-sm text-brand-500">
          Business <strong>{selected}</strong> is active. Use the sidebar to
          navigate.
        </p>
      )}
    </div>
  );
}
