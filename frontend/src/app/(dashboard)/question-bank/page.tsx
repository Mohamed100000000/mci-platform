"use client";
import { Database } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { BackendPendingState } from "@/components/shared/backend-pending-state";

export default function QuestionBankPage() {
  return (
    <>
      <PageHeader title="Question Bank" description="Author, tag, and organize assessment questions." />
      <BackendPendingState
        icon={Database}
        title="Question bank"
        description="A rich question editor with image/video support, tagging, bulk import, and live preview."
        endpoints={["POST /api/questions", "GET /api/questions", "POST /api/questions/bulk-import"]}
      />
    </>
  );
}
