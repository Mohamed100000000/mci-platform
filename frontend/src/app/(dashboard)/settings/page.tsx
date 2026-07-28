"use client";
import { useTheme } from "next-themes";
import { Moon, Sun, Monitor, Bell, Shield } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();

  const themeOptions = [
    { value: "light", label: "Light", icon: Sun },
    { value: "dark", label: "Dark", icon: Moon },
    { value: "system", label: "System", icon: Monitor },
  ];

  return (
    <>
      <PageHeader title="Settings" description="Manage your workspace preferences." />

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
            <CardDescription>Customize how MCI Platform looks on your device.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-3">
              {themeOptions.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setTheme(opt.value)}
                  className={cn(
                    "flex flex-col items-center gap-2 rounded-xl border-2 p-4 transition-colors",
                    theme === opt.value ? "border-primary bg-primary/5" : "border-border hover:bg-muted"
                  )}
                >
                  <opt.icon className="h-5 w-5" />
                  <span className="text-sm font-medium">{opt.label}</span>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-4 w-4" /> Notifications
            </CardTitle>
            <CardDescription>Email &amp; in-app alert preferences.</CardDescription>
          </CardHeader>
          <CardContent>
            <Badge variant="warning">Backend pending — POST /api/settings/notifications</Badge>
          </CardContent>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-4 w-4" /> Security &amp; Access
            </CardTitle>
            <CardDescription>Password, two-factor authentication, and API keys.</CardDescription>
          </CardHeader>
          <CardContent>
            <Badge variant="warning">
              Backend pending — requires /api/auth/* endpoints (see README &ldquo;Backend Gaps&rdquo;)
            </Badge>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
