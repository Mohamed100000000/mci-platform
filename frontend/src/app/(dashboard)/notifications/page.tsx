"use client";
import { Bell } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { BackendPendingState } from "@/components/shared/backend-pending-state";

export default function NotificationsPage() {
  return (
    <>
      <PageHeader title="Notifications" description="System and activity notifications." />
      <BackendPendingState
        icon={Bell}
        title="Notification center"
        description="Real-time notifications for certificate expiry, assessment completion, and system activity."
        endpoints={["GET /api/notifications", "POST /api/notifications/mark-read", "WS /ws/notifications"]}
      />
    </>
  );
}
