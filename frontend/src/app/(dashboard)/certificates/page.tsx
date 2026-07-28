"use client";
import { Award } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { BackendPendingState } from "@/components/shared/backend-pending-state";

export default function CertificatesPage() {
  return (
    <>
      <PageHeader title="Certificates" description="Issue and verify digital competency certificates." />
      <BackendPendingState
        icon={Award}
        title="Digital certificates"
        description="QR-verifiable digital certificates with PDF download and public verification pages, per the Certification Authority module in the architecture document."
        endpoints={["POST /api/certificates", "GET /api/certificates/{id}", "GET /verify/{certificate_number}"]}
      />
    </>
  );
}
