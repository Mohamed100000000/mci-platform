"use client";

import * as React from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Mail, Lock, ArrowRight, ShieldCheck, Gauge, Award } from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const loginSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

type LoginValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const [submitting, setSubmitting] = React.useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginValues>({ resolver: zodResolver(loginSchema) });

  const onSubmit = async (values: LoginValues) => {
    setSubmitting(true);
    // NOTE: /api/auth/login does not exist on the backend yet (see README
    // "Backend Gaps"). Once implemented, replace this block with:
    //   const { data } = await apiClient.post("/api/auth/login", values);
    //   localStorage.setItem("mci_token", data.access_token);
    void values;
    await new Promise((r) => setTimeout(r, 600));
    toast.info("Authentication API not yet connected — continuing in demo mode.");
    setSubmitting(false);
    router.push("/dashboard");
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* Left: brand panel */}
      <div className="relative hidden overflow-hidden bg-brand-900 lg:flex lg:flex-col lg:justify-between lg:p-12">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(106,171,233,0.18),transparent_50%)]" />
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative z-10 flex items-center gap-3"
        >
          <div className="relative h-10 w-10 overflow-hidden rounded-lg">
            <Image src="/logo-mark-square.png" alt="MCI Platform" fill className="object-cover" />
          </div>
          <span className="text-lg font-semibold text-white">
            MCI <span className="text-brand-300">Platform</span>
          </span>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="relative z-10 max-w-md"
        >
          <div className="relative mx-auto mb-8 h-56 w-56">
            <Image src="/logo-mark-square.png" alt="" fill className="object-contain drop-shadow-2xl" />
          </div>
          <h1 className="text-3xl font-semibold leading-tight text-white">
            Assess. Measure. <span className="text-brand-300">Empower.</span>
          </h1>
          <p className="mt-3 text-sm leading-relaxed text-white/60">
            The world&rsquo;s standardized digital competency index for
            maritime and offshore professionals — guiding careers the way
            a lighthouse guides ships to safe harbor.
          </p>

          <div className="mt-8 space-y-3">
            {[
              { icon: Gauge, text: "0–1000 standardized competency scoring" },
              { icon: ShieldCheck, text: "Evidence-based, auditable methodology" },
              { icon: Award, text: "Verifiable digital certificates" },
            ].map((f, i) => (
              <motion.div
                key={f.text}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.25 + i * 0.08 }}
                className="flex items-center gap-3 text-sm text-white/80"
              >
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/10">
                  <f.icon className="h-4 w-4 text-brand-300" />
                </span>
                {f.text}
              </motion.div>
            ))}
          </div>
        </motion.div>

        <p className="relative z-10 text-xs text-white/40">
          &copy; {new Date().getFullYear()} MCI Platform. All rights reserved.
        </p>
      </div>

      {/* Right: form */}
      <div className="flex items-center justify-center p-6 sm:p-10">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-sm"
        >
          <div className="mb-8 flex flex-col items-center text-center lg:hidden">
            <div className="relative mb-4 h-14 w-14 overflow-hidden rounded-xl">
              <Image src="/logo-mark-square.png" alt="MCI Platform" fill className="object-cover" />
            </div>
            <span className="text-lg font-semibold">
              MCI <span className="text-brand-500 dark:text-brand-300">Platform</span>
            </span>
          </div>

          <h2 className="text-2xl font-semibold">Welcome back</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Sign in to your MCI Platform workspace.
          </p>

          <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  placeholder="you@company.com"
                  className="pl-9"
                  {...register("email")}
                />
              </div>
              {errors.email && <p className="text-xs text-danger">{errors.email.message}</p>}
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
                <a href="#" className="text-xs text-primary hover:underline">Forgot password?</a>
              </div>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  className="pl-9"
                  {...register("password")}
                />
              </div>
              {errors.password && <p className="text-xs text-danger">{errors.password.message}</p>}
            </div>

            <Button type="submit" className="w-full" size="lg" disabled={submitting}>
              {submitting ? "Signing in..." : "Sign in"}
              {!submitting && <ArrowRight className="h-4 w-4" />}
            </Button>
          </form>

          <p className="mt-6 text-center text-xs text-muted-foreground">
            Authentication API is not yet connected to the backend —
            this form will operate in demo mode until{" "}
            <code className="rounded bg-muted px-1 py-0.5">/api/auth/login</code> is implemented.
          </p>
        </motion.div>
      </div>
    </div>
  );
}
