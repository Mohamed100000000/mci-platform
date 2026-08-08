"use client";

import { useState } from "react";

interface LoginPanelProps {
  lang: "ar" | "en";
  onSubmit: (data: { name: string; email: string; idNumber: string }) => void;
}

const STRINGS = {
  ar: {
    prompt: "أدخل بياناتك لبدء التحدي وإصدار شهادتك تلقائيًا بعد النجاح:",
    name: "الاسم الكامل",
    email: "البريد الإلكتروني",
    idNumber: "رقم الهوية / رقم الجواز",
    start: "ابدأ التحدي ⚓",
    errName: "من فضلك أدخل الاسم الكامل",
    errEmail: "من فضلك أدخل بريد إلكتروني صحيح",
    errId: "من فضلك أدخل رقم الهوية أو الجواز",
  },
  en: {
    prompt: "Enter your details to start the challenge and automatically receive your certificate after passing:",
    name: "Full Name",
    email: "Email",
    idNumber: "ID / Passport Number",
    start: "Start Challenge ⚓",
    errName: "Please enter your full name",
    errEmail: "Please enter a valid email",
    errId: "Please enter your ID or passport number",
  },
};

export function LoginPanel({ lang, onSubmit }: LoginPanelProps) {
  const s = STRINGS[lang];
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [idNumber, setIdNumber] = useState("");
  const [error, setError] = useState<string | null>(null);

  function handleSubmit() {
    if (!name.trim()) return setError(s.errName);
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return setError(s.errEmail);
    if (!idNumber.trim()) return setError(s.errId);
    setError(null);
    onSubmit({ name: name.trim(), email: email.trim(), idNumber: idNumber.trim() });
  }

  return (
    <div className="rounded-xl bg-mci-parchment text-mci-ink p-7 shadow-lg">
      <p className="text-sm leading-relaxed mb-4">{s.prompt}</p>

      <Field label={s.name} value={name} onChange={setName} placeholder="Mohamed Ahmed" />
      <Field label={s.email} value={email} onChange={setEmail} placeholder="example@email.com" type="email" />
      <Field label={s.idNumber} value={idNumber} onChange={setIdNumber} placeholder="1234567890" />

      {error && (
        <div className="mb-3 rounded-lg border border-mci-coral/35 bg-mci-coral/10 px-3 py-2 text-center text-xs text-[#7a2d1d]">
          {error}
        </div>
      )}

      <div className="flex justify-center mt-2">
        <button
          onClick={handleSubmit}
          className="rounded-full bg-gradient-to-b from-mci-sky-blue-light to-mci-sky-blue px-8 py-3 text-sm font-bold text-mci-navy-deep shadow-md hover:-translate-y-0.5 transition-transform"
        >
          {s.start}
        </button>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
  type?: string;
}) {
  return (
    <div className="mb-3">
      <label className="block text-[11.5px] font-bold text-mci-steel mb-1.5">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-lg border border-mci-parchment-dim bg-mci-off-white px-3.5 py-2.5 text-sm text-mci-ink focus:outline-none focus:border-mci-sky-blue focus:bg-white"
      />
    </div>
  );
}
