"use client";

import { useEffect, useState, FormEvent } from "react";
import { api, ApiError } from "@/lib/api";
import Table from "@/components/Table";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Card from "@/components/Card";

interface Staff {
  id: number;
  first_name: string;
  last_name: string | null;
  phone: string | null;
  email: string | null;
  is_active: boolean;
  [key: string]: unknown;
}

export default function StaffPage() {
  const [rows, setRows] = useState<Staff[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const data = await api<Staff[]>("/staff", { needsBusiness: true });
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

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      await api("/staff", {
        method: "POST",
        needsBusiness: true,
        body: {
          first_name: firstName,
          last_name: lastName || null,
          phone: phone || null,
          email: email || null,
        },
      });
      setFirstName("");
      setLastName("");
      setPhone("");
      setEmail("");
      setShowForm(false);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-brand-800">Staff</h1>
        <Button onClick={() => setShowForm((v) => !v)} variant="secondary">
          {showForm ? "Cancel" : "+ Add Staff"}
        </Button>
      </div>

      {showForm && (
        <Card className="mb-4">
          <form onSubmit={handleCreate} className="flex flex-col gap-3">
            <div className="grid grid-cols-2 gap-3">
              <Input
                label="First Name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                required
              />
              <Input
                label="Last Name"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
              />
              <Input
                label="Phone"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            {error && (
              <p className="text-sm text-red-500">{error}</p>
            )}
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
          { key: "first_name", header: "First Name" },
          { key: "last_name", header: "Last Name" },
          { key: "phone", header: "Phone" },
          { key: "email", header: "Email" },
          {
            key: "is_active",
            header: "Active",
            render: (r) => (r.is_active ? "Yes" : "No"),
          },
        ]}
      />
    </div>
  );
}
