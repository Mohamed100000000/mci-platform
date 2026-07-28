import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background p-6 text-center">
      <div className="relative h-16 w-16 overflow-hidden rounded-xl opacity-80">
        <Image src="/logo-mark-square.png" alt="" fill className="object-cover" />
      </div>
      <h1 className="text-4xl font-semibold">404</h1>
      <p className="max-w-sm text-sm text-muted-foreground">
        This page has drifted off the chart. Let&rsquo;s guide you back to safe harbor.
      </p>
      <Button asChild>
        <Link href="/dashboard">
          <ArrowLeft className="h-4 w-4" /> Back to dashboard
        </Link>
      </Button>
    </div>
  );
}
