"use client";

import { useEffect, useState, FormEvent } from "react";
import { api, ApiError } from "@/lib/api";
import Table from "@/components/Table";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Card from "@/components/Card";

interface Customer {
  id: number;
  name: string;
  phone: string;
  email: string | null;
  [key: string]: unknown;
}

export default function CustomersPage() {
  const [rows, setRows] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const data = await api<Customer[]>("/customers", { needsBusiness: true });
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
      await api("/customers", {
        method: "POST",
        needsBusiness: true,
        body: {
          name,
          phone,
          email: email || null,
        },
      });
      setName("");
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
        <h1 className="text-lg font-semibold text-brand-800">Customers</h1>
        <Button onClick={() => setShowForm((v) => !v)} variant="secondary">
          {showForm ? "Cancel" : "+ Add Customer"}
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
                label="Phone"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                required
              />
              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
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
          { key: "phone", header: "Phone" },
          { key: "email", header: "Email" },
        ]}
      />
    </div>
  );
}
