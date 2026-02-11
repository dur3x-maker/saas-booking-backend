import { getToken } from "./auth";
import { getBusinessId } from "./business-context";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
const BASE = `${API_URL}/api/v1`;

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(status: number, body: unknown) {
    super(typeof body === "object" && body && "detail" in body ? String((body as Record<string, unknown>).detail) : `HTTP ${status}`);
    this.status = status;
    this.body = body;
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  needsBusiness?: boolean;
}

export async function api<T = unknown>(
  path: string,
  opts: RequestOptions = {},
): Promise<T> {
  const { method = "GET", body, needsBusiness = false } = opts;

  const headers: Record<string, string> = {};

  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (needsBusiness) {
    const bizId = getBusinessId();
    if (bizId) {
      headers["X-Business-ID"] = bizId;
    }
  }

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return undefined as T;

  const json = await res.json().catch(() => null);

  if (!res.ok) {
    throw new ApiError(res.status, json);
  }

  return json as T;
}
