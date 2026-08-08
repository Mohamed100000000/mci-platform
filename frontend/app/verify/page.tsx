"use client";

import { useEffect, useState } from "react";
import { examApi, type CertificateVerification } from "../../lib/examApi";

export default function VerifyPage() {
  const [code, setCode] = useState<string | null>(null);
  const [data, setData] = useState<CertificateVerification | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const parts = window.location.pathname.split("/");
    const c = parts[parts.length - 1];
    setCode(c);
    examApi
      .verifyCertificate(c)
      .then(setData)
      .catch(() => setData({ valid: false, revoked: false }))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div
      className="min-h-screen flex items-center justify-center p-6"
      style={{ background: "linear-gradient(180deg, #0b1f3a 0%, #12315a 100%)" }}
    >
      <div className="w-full max-w-md rounded-xl bg-mci-parchment p-8 text-center text-mci-ink shadow-2xl">
        <div className="text-4xl mb-3">👬</div>
        <h1 className="font-mci-display text-xl font-bold text-mci-navy-deep mb-4">
          MCI Platform Certificate Verification
        </h1>

        {loading && <p className="text-sm text-[#7a7260]">Checking certificate…</p>}

        {!loading && data?.valid && (
          <div className="rounded-lg border-2 border-mci-sea/50 bg-mci-sea/10 p-5">
            <div className="text-2xl mb-2">✅</div>
            <p className="font-bold text-mci-sea mb-3">Valid Certificate</p>
            <div className="text-sm space-y-1 text-start">
              <Row label="Trainee" value={data.trainee_name} />
              <Row label="Course" value={data.subject_name_en} />
              <Row label="Level" value={data.level_difficulty} />
              <Row label="Score" value={data.pct != null ? `${data.pct}%` : undefined} />
              <Row
                label="Issued"
                value={data.issued_at ? new Date(data.issued_at).toLocaleDateString() : undefined}
              />
              <Row label="Institute" value={data.institute_name} />
            </div>
          </div>
        )}

        {!loading && !data?.valid && (
          <div className="rounded-lg border-2 border-mci-coral/50 bg-mci-coral/10 p-5">
            <div className="text-2xl mb-2">❌</div>
            <p className="font-bold text-mci-coral">
              {data?.revoked ? "This certificate has been revoked" : "Certificate not found"}
            </p>
          </div>
        )}

        <p className="mt-5 text-[10px] text-[#8a8070]">Verification code: {code}</p>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value?: string }) {
  if (!value) return null;
  return (
    <div className="flex justify-between border-b border-mci-parchment-dim py-1">
      <span className="text-[#7a7260]">{label}</span>
      <span className="font-bold text-mci-navy-deep">{value}</span>
    </div>
  );
}
