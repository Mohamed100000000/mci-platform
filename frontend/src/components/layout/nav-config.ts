import {
  LayoutDashboard, Users, Building2, ClipboardList, Database, PlayCircle,
  Award, FileBarChart, BarChart3, Gauge, Bell, Settings, User,
} from "lucide-react";

export interface NavItem {
  label: string;
  href: string;
  icon: typeof LayoutDashboard;
  backendReady: boolean;
}

export const navSections: { title: string; items: NavItem[] }[] = [
  {
    title: "Overview",
    items: [
      { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard, backendReady: true },
      { label: "MCI Score", href: "/mci-score", icon: Gauge, backendReady: true },
    ],
  },
  {
    title: "People",
    items: [
      { label: "Candidates", href: "/candidates", icon: Users, backendReady: true },
      { label: "Companies", href: "/companies", icon: Building2, backendReady: false },
    ],
  },
  {
    title: "Assessment",
    items: [
      { label: "Assessments", href: "/assessments", icon: ClipboardList, backendReady: false },
      { label: "Question Bank", href: "/question-bank", icon: Database, backendReady: false },
      { label: "Assessment Sessions", href: "/sessions", icon: PlayCircle, backendReady: false },
    ],
  },
  {
    title: "Credentials",
    items: [
      { label: "Certificates", href: "/certificates", icon: Award, backendReady: false },
    ],
  },
  {
    title: "Insights",
    items: [
      { label: "Reports", href: "/reports", icon: FileBarChart, backendReady: false },
      { label: "Analytics", href: "/analytics", icon: BarChart3, backendReady: false },
    ],
  },
  {
    title: "Account",
    items: [
      { label: "Notifications", href: "/notifications", icon: Bell, backendReady: false },
      { label: "Settings", href: "/settings", icon: Settings, backendReady: false },
      { label: "Profile", href: "/profile", icon: User, backendReady: false },
    ],
  },
];
