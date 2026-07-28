import { Mail, Shield, Calendar } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

export default function ProfilePage() {
  return (
    <>
      <PageHeader title="Profile" description="Your MCI Platform account details." />
      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardContent className="flex flex-col items-center pt-6 text-center">
            <Avatar className="h-20 w-20 border border-border">
              <AvatarFallback className="bg-primary text-primary-foreground text-xl">MC</AvatarFallback>
            </Avatar>
            <h2 className="mt-4 text-lg font-semibold">Institute Admin</h2>
            <p className="text-sm text-muted-foreground">admin@mci-platform.com</p>
            <Badge variant="accent" className="mt-3">Administrator</Badge>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Account details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3 text-sm">
              <Mail className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Email</span>
              <span className="ml-auto font-medium">admin@mci-platform.com</span>
            </div>
            <Separator />
            <div className="flex items-center gap-3 text-sm">
              <Shield className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Role</span>
              <span className="ml-auto font-medium">Administrator</span>
            </div>
            <Separator />
            <div className="flex items-center gap-3 text-sm">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-muted-foreground">Member since</span>
              <span className="ml-auto font-medium">—</span>
            </div>
            <Separator />
            <Badge variant="warning">
              Live profile data requires GET /api/auth/me (see README &ldquo;Backend Gaps&rdquo;)
            </Badge>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
