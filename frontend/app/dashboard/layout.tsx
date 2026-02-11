"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { isAuthenticated, removeToken } from "@/lib/auth";
import { getBusinessId, removeBusinessId } from "@/lib/business-context";
import { api } from "@/lib/api";
import Link from "next/link";

interface MeData {
  user: { id: number; email: string; is_active: boolean; created_at: string };
  businesses: { id: number; name: string; role: string }[];
}

const NAV = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/staff", label: "Staff" },
  { href: "/dashboard/services", label: "Services" },
  { href: "/dashboard/schedule", label: "Schedule" },
  { href: "/dashboard/customers", label: "Customers" },
  { href: "/dashboard/bookings", label: "Bookings" },
  { href: "/dashboard/calendar", label: "Calendar" },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [me, setMe] = useState<MeData | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [bizId, setBizId] = useState<string | null>(null);

  useEffect(() => {
    setBizId(getBusinessId());
  }, []);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
    api<MeData>("/me").then(setMe).catch(() => {
      removeToken();
      router.push("/login");
    });
  }, [router]);

  useEffect(() => {
    if (me && !bizId && me.businesses.length > 0) {
      router.push("/dashboard");
    }
  }, [me, bizId, router]);

  function handleLogout() {
    removeToken();
    removeBusinessId();
    router.push("/login");
  }

  const currentBiz = me?.businesses.find((b) => String(b.id) === bizId);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside
        className={`flex flex-col border-r border-brand-200 bg-white transition-all ${sidebarOpen ? "w-56" : "w-0 overflow-hidden"}`}
      >
        <div className="flex h-14 items-center border-b border-brand-200 px-4">
          <span className="text-sm font-semibold text-brand-800 truncate">
            {currentBiz?.name ?? "SaaS Booking"}
          </span>
        </div>

        <nav className="flex-1 overflow-y-auto p-2">
          {NAV.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`block rounded-lg px-3 py-2 text-sm transition-colors ${active ? "bg-brand-100 font-medium text-brand-900" : "text-brand-600 hover:bg-brand-50 hover:text-brand-800"}`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        <header className="flex h-14 shrink-0 items-center justify-between border-b border-brand-200 bg-white px-4">
          <button
            onClick={() => setSidebarOpen((v) => !v)}
            className="rounded-lg p-1.5 text-brand-500 hover:bg-brand-100"
          >
            <svg
              className="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>

          <div className="flex items-center gap-3">
            {currentBiz && (
              <span className="rounded-md bg-brand-100 px-2 py-1 text-xs font-medium text-brand-700">
                {currentBiz.role}
              </span>
            )}
            <span className="text-sm text-brand-600">
              {me?.user.email ?? ""}
            </span>
            <button
              onClick={handleLogout}
              className="rounded-lg px-3 py-1.5 text-sm text-brand-500 hover:bg-brand-100 hover:text-brand-700"
            >
              Logout
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
