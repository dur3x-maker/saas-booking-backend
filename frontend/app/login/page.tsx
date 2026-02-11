"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { setToken } from "@/lib/auth";
import Button from "@/components/Button";
import Input from "@/components/Input";
import Card from "@/components/Card";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"login" | "register">("login");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await api("/auth/register", {
          method: "POST",
          body: { email, password },
        });
      }
      const data = await api<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: { email, password },
      });
      setToken(data.access_token);
      router.push("/dashboard");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Something went wrong");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <Card className="w-full max-w-sm">
        <h1 className="mb-6 text-center text-xl font-semibold text-brand-800">
          {mode === "login" ? "Sign In" : "Create Account"}
        </h1>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            label="Email"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <Input
            label="Password"
            type="password"
            placeholder="********"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />

          {error && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
              {error}
            </p>
          )}

          <Button type="submit" loading={loading}>
            {mode === "login" ? "Sign In" : "Register"}
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-brand-500">
          {mode === "login" ? (
            <>
              No account?{" "}
              <button
                type="button"
                onClick={() => { setMode("register"); setError(""); }}
                className="font-medium text-brand-700 hover:underline"
              >
                Register
              </button>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <button
                type="button"
                onClick={() => { setMode("login"); setError(""); }}
                className="font-medium text-brand-700 hover:underline"
              >
                Sign In
              </button>
            </>
          )}
        </p>
      </Card>
    </div>
  );
}
