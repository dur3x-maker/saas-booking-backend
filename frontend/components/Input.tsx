"use client";

import { InputHTMLAttributes, forwardRef } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = "", ...rest }, ref) => (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-sm font-medium text-brand-700">{label}</label>
      )}
      <input
        ref={ref}
        className={`rounded-lg border border-brand-300 bg-white px-3 py-2 text-sm text-brand-900 placeholder:text-brand-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 disabled:bg-brand-50 ${error ? "border-red-400" : ""} ${className}`}
        {...rest}
      />
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  ),
);

Input.displayName = "Input";
export default Input;
