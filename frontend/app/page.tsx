"use client";

import { useState } from "react";
import Link from "next/link";

/**
 * Landing page — structurally inspired by marlinstests.com (login sidebar +
 * 3-card grid: licence-code test / certificate verification / practice
 * tests + footer), rebuilt entirely in AZDA's navy/brass/parchment identity.
 * Nothing here is copied from Marlins — same *shape*, different everything
 * else (colors, copy, iconography, card content).
 */

const STRINGS = {
  ar: {
    welcome: "أهلاً بيك في منصة AZDA للاختبارات",
    signIn: "تسجيل الدخول",
    signInSub: "ادخل ببريدك الإلكتروني",
    email: "البريد الإلكتروني",
    password: "كلمة المرور",
    forgot: "نسيت كلمة المرور؟",
    noAccount: "معندكش حساب؟",
    register: "سجّل الآن",
    login: "دخول",
    licenceTitle: "عندك كود ترخيص؟",
    licenceBody: "لو معاك كود الترخيص بتاعك، تقدر تدخله وتبدأ الاختبار فورًا.",
    licencePlaceholder: "أدخل كود الترخيص",
    licenceBtn: "ابدأ الاختبار",
    verifyTitle: "تحقق من صحة الشهادة",
    verifyBody: "عايز تتأكد من صحة شهادة معينة؟ أدخل رمز التحقق واضغط تأكيد.",
    verifyPlaceholder: "رمز التحقق",
    verifyBtn: "تحقق",
    practiceTitle: "جرّب اختبار تدريبي",
    practiceBody: "تقدر تجرّب اختبار تدريبي هنا من غير ما تحتاج كود ترخيص.",
    footerContact: "التواصل",
    footerAbout: "عن المنصة",
    aboutLinks: ["عن AZDA", "الشروط والأحكام", "سياسة الخصوصية"],
    rights: "AZDA Marine Training Institute © 2026",
    partOf: "جزء من",
  },
  en: {
    welcome: "Welcome to the AZDA Test Platform",
    signIn: "Sign In",
    signInSub: "Sign in with your email address",
    email: "Email address",
    password: "Password",
    forgot: "Forgot password?",
    noAccount: "Don't have an account?",
    register: "Register now",
    login: "Login",
    licenceTitle: "Have a licence code?",
    licenceBody: "If you have your licence code, enter it below to start the test immediately.",
    licencePlaceholder: "Enter licence code",
    licenceBtn: "Start the test",
    verifyTitle: "Check certificate validity",
    verifyBody: "Need to check a certificate's validity? Enter the verification code and confirm.",
    verifyPlaceholder: "Verification code",
    verifyBtn: "Verify",
    practiceTitle: "Practise a test",
    practiceBody: "You can take a practice test here without needing a licence code.",
    footerContact: "Contact",
    footerAbout: "About",
    aboutLinks: ["About AZDA", "Terms & Conditions", "Privacy Policy"],
    rights: "AZDA Marine Training Institute © 2026",
    partOf: "Part of",
  },
};

const PRACTICE_SUBJECTS = [
  { code: "PST", ar: "تقنيات النجاة الشخصية", en: "Personal Survival Techniques" },
  { code: "FRB", ar: "قوارب الإنقاذ السريع", en: "Fast Rescue Boats" },
  { code: "GMDSS", ar: "نظام الاستغاثة العالمي", en: "Global Maritime Distress System" },
];

export default function HomePage() {
  const [lang, setLang] = useState<"ar" | "en">("ar");
  const s = STRINGS[lang];
  const dir = lang === "ar" ? "rtl" : "ltr";

  return (
    <div
      dir={dir}
      className="min-h-screen font-azda-body text-azda-ink"
      style={{ background: "linear-gradient(180deg, #f6f1e4 0%, #efe6d0 100%)" }}
    >
      {/* Header */}
      <header className="flex items-center justify-between border-b border-azda-parchment-dim bg-azda-off-white px-6 py-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">⚓</span>
          <span className="font-azda-display text-lg font-bold text-azda-navy-deep">
            AZDA Test Platform
          </span>
        </div>
        <button
          onClick={() => setLang((l) => (l === "ar" ? "en" : "ar"))}
          className="rounded-full border border-azda-brass/50 px-3 py-1 text-xs font-bold text-azda-navy-deep hover:bg-azda-brass/10"
        >
          {lang === "ar" ? "EN" : "AR"}
        </button>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">
        <h1 className="font-azda-display text-center text-2xl font-bold text-azda-navy-deep mb-8">
          {s.welcome}
        </h1>

        <div className="grid gap-6 lg:grid-cols-[340px_1fr]">
          {/* Login sidebar */}
          <div className="rounded-xl border border-azda-parchment-dim bg-white p-6 shadow-sm h-fit">
            <h2 className="font-azda-display text-lg font-bold text-azda-navy-deep mb-1">
              {s.signIn}
            </h2>
            <p className="text-xs text-[#7a7260] mb-4">{s.signInSub}</p>

            <label className="block text-[11px] font-bold text-azda-steel mb-1">{s.email}</label>
            <input
              type="email"
              className="w-full rounded-lg border border-azda-parchment-dim px-3 py-2 text-sm mb-3 focus:outline-none focus:border-azda-brass"
            />
            <label className="block text-[11px] font-bold text-azda-steel mb-1">{s.password}</label>
            <input
              type="password"
              className="w-full rounded-lg border border-azda-parchment-dim px-3 py-2 text-sm mb-2 focus:outline-none focus:border-azda-brass"
            />
            <div className="text-end mb-4">
              <a href="#" className="text-[11px] text-azda-steel underline">
                {s.forgot}
              </a>
            </div>

            <button className="w-full rounded-full bg-gradient-to-b from-azda-brass-light to-azda-brass py-2.5 text-sm font-bold text-azda-navy-deep shadow-sm hover:-translate-y-0.5 transition-transform">
              {s.login}
            </button>

            <p className="mt-4 text-center text-xs text-[#7a7260]">
              {s.noAccount}{" "}
              <a href="#" className="font-bold text-azda-brass underline">
                {s.register}
              </a>
            </p>
          </div>

          {/* Card grid */}
          <div className="grid gap-5 sm:grid-cols-2">
            <Card icon="🎫" title={s.licenceTitle} body={s.licenceBody}>
              <div className="flex gap-2">
                <input
                  placeholder={s.licencePlaceholder}
                  className="flex-1 rounded-lg border border-azda-parchment-dim px-3 py-2 text-sm focus:outline-none focus:border-azda-brass"
                />
                <button className="shrink-0 rounded-lg bg-azda-navy-deep px-4 py-2 text-xs font-bold text-white hover:bg-azda-navy-mid">
                  {s.licenceBtn}
                </button>
              </div>
            </Card>

            <Card icon="✅" title={s.verifyTitle} body={s.verifyBody}>
              <div className="flex gap-2">
                <input
                  placeholder={s.verifyPlaceholder}
                  className="flex-1 rounded-lg border border-azda-parchment-dim px-3 py-2 text-sm focus:outline-none focus:border-azda-brass"
                />
                <Link
                  href="/verify"
                  className="shrink-0 rounded-lg border border-azda-brass px-4 py-2 text-xs font-bold text-azda-brass hover:bg-azda-brass/10"
                >
                  {s.verifyBtn}
                </Link>
              </div>
            </Card>

            <Card icon="🧭" title={s.practiceTitle} body={s.practiceBody} className="sm:col-span-2">
              <div className="flex flex-wrap gap-2">
                {PRACTICE_SUBJECTS.map((sub) => (
                  <Link
                    key={sub.code}
                    href={`/exam?practice=${sub.code}`}
                    className="rounded-full border border-azda-parchment-dim bg-azda-off-white px-3.5 py-1.5 text-xs font-bold text-azda-navy-deep hover:border-azda-brass"
                  >
                    {sub.code} · {lang === "ar" ? sub.ar : sub.en}
                  </Link>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-azda-parchment-dim bg-azda-navy-deep px-6 py-8 text-azda-off-white/80">
        <div className="mx-auto grid max-w-6xl gap-8 sm:grid-cols-3">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xl">⚓</span>
              <span className="font-azda-display font-bold text-azda-off-white">AZDA</span>
            </div>
            <p className="text-xs text-azda-off-white/50">{s.rights}</p>
          </div>
          <div>
            <div className="mb-2 text-xs font-bold uppercase tracking-wide text-azda-brass-light">
              {s.footerContact}
            </div>
            <p className="text-xs">admission@azdamarine.com</p>
            <p className="text-xs">WhatsApp: +966 53 592 4623</p>
          </div>
          <div>
            <div className="mb-2 text-xs font-bold uppercase tracking-wide text-azda-brass-light">
              {s.footerAbout}
            </div>
            {s.aboutLinks.map((link) => (
              <a key={link} href="#" className="block text-xs text-azda-off-white/70 hover:text-azda-off-white">
                {link}
              </a>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}

function Card({
  icon,
  title,
  body,
  children,
  className = "",
}: {
  icon: string;
  title: string;
  body: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`rounded-xl border border-azda-parchment-dim bg-white p-5 shadow-sm ${className}`}>
      <div className="mb-2 text-2xl">{icon}</div>
      <h3 className="font-azda-display text-base font-bold text-azda-navy-deep mb-1">{title}</h3>
      <p className="text-xs text-[#7a7260] mb-4">{body}</p>
      {children}
    </div>
  );
}
