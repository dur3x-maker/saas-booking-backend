const BIZ_KEY = "business_id";

export function getBusinessId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(BIZ_KEY);
}

export function setBusinessId(id: number | string): void {
  localStorage.setItem(BIZ_KEY, String(id));
}

export function removeBusinessId(): void {
  localStorage.removeItem(BIZ_KEY);
}
