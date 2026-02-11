"use client";

import { ReactNode } from "react";

interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => ReactNode;
}

interface TableProps<T> {
  columns: Column<T>[];
  rows: T[];
  loading?: boolean;
  onRowClick?: (row: T) => void;
}

export default function Table<T extends Record<string, unknown>>({
  columns,
  rows,
  loading,
  onRowClick,
}: TableProps<T>) {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12 text-brand-400">
        Loading...
      </div>
    );
  }

  if (rows.length === 0) {
    return (
      <div className="flex items-center justify-center py-12 text-brand-400">
        No data
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-brand-200">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-brand-200 bg-brand-50">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className="px-4 py-3 font-medium text-brand-600"
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={i}
              onClick={() => onRowClick?.(row)}
              className={`border-b border-brand-100 last:border-0 ${onRowClick ? "cursor-pointer hover:bg-brand-50" : ""}`}
            >
              {columns.map((col) => (
                <td key={col.key} className="px-4 py-3 text-brand-800">
                  {col.render
                    ? col.render(row)
                    : (row[col.key] as ReactNode) ?? "—"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
