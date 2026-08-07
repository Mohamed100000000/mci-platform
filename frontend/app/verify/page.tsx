"use client";

import { useEffect, useState } from "react";
import { examApi, type CertificateVerification } from "../../lib/examApi";

/**
 * Route: /verify/[code]
 * This page has NO auth — it's the public landing target for the QR code
 * printed on every certificate, so an employer or auditor can confirm a
 * certificate is genuine without logging in.
 *
 * Wire this file to your actual dynamic route, e.g.
 *   app/verify/[code]/page.tsx  with  params: { code: string }
 * (shown here as a client component reading the code from window.location
 * for portability outside a specific Next.js routing setup).
 */
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
      style={{ background: "linear-gradient(180deg, #0a1c30 0%, #123252 100%)" }}
    >
      <div className="w-full max-w-md rounded-xl bg-azda-parchment p-8 text-center text-azda-ink shadow-2xl">
        <div className="text-4xl mb-3">⚓</div>
        <h1 className="font-azda-display text-xl font-bold text-azda-navy-deep mb-4">
          AZDA Certificate Verification
        </h1>

        {loading && <p className="text-sm text-[#7a7260]">Checking certificate…</p>}

        {!loading && data?.valid && (
          <div className="rounded-lg border-2 border-azda-sea/50 bg-azda-sea/10 p-5">
            <div className="text-2xl mb-2">✅</div>
            <p className="font-bold text-azda-sea mb-3">Valid Certificate</p>
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
          <div className="rounded-lg border-2 border-azda-coral/50 bg-azda-coral/10 p-5">
            <div className="text-2xl mb-2">❌</div>
            <p className="font-bold text-azda-coral">
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
    <div className="flex justify-between border-b border-azda-parchment-dim py-1">
      <span className="text-[#7a7260]">{label}</span>
      <span className="font-bold text-azda-navy-deep">{value}</span>
    </div>
  );
}
