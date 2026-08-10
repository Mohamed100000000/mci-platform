import { ReactNode } from "react";

interface MciFrameProps {
  logoSrc: string;
  title: string;
  subtitle: string;
  onHome?: () => void;
  lang: "ar" | "en";
  onToggleLang: () => void;
  children: ReactNode;
}

/**
 * The outer shell every MCI Platform exam screen sits inside.
 * Navy + sky-blue identity, matching the lighthouse logo.
 */
export function AzdaFrame({
  logoSrc,
  title,
  subtitle,
  onHome,
  lang,
  onToggleLang,
  children,
}: MciFrameProps) {
  const dir = lang === "ar" ? "rtl" : "ltr";

  return (
    <div
      dir={dir}
      className="min-h-screen flex items-center justify-center p-6 font-mci-body text-mci-off-white"
      style={{
        background:
          "radial-gradient(circle at 20% 10%, rgba(74,144,217,0.10), transparent 40%), radial-gradient(circle at 85% 85%, rgba(47,143,124,0.10), transparent 45%), linear-gradient(180deg, #0b1f3a 0%, #12315a 100%)",
      }}
    >
      <div className="w-full max-w-[600px]">
        <div className="relative rounded-[18px] border border-mci-sky-blue/35 bg-white/[0.04] p-6 shadow-2xl">
          <div className="absolute inset-1.5 rounded-xl border border-dashed border-mci-sky-blue/20 pointer-events-none" />

          <div className="flex items-center justify-between mb-2.5">
            <button
              onClick={onHome}
              aria-label={lang === "ar" ? "الرئيسية" : "Home"}
              className="rounded-2xl border border-mci-sky-blue/40 bg-mci-sky-blue/10 px-3 py-1.5 text-xs font-bold text-mci-sky-blue-light hover:bg-mci-sky-blue/20 transition-colors"
            >
              🏠
            </button>
            <div className="flex-1 flex justify-center">
              <img
                src={logoSrc}
                alt="MCI Platform - Maritime Competency Index"
                className="h-[50px] rounded-lg bg-mci-off-white/90 px-3 py-1.5 drop-shadow-lg"
              />
            </div>
            <button
              onClick={onToggleLang}
              className="rounded-2xl border border-mci-sky-blue/40 bg-mci-sky-blue/10 px-3 py-1.5 text-xs font-bold text-mci-sky-blue-light hover:bg-mci-sky-blue/20 transition-colors"
            >
              {lang === "ar" ? "EN" : "AR"}
            </button>
          </div>

          <h1 className="font-mci-display text-center text-[26px] tracking-wide mb-1">{title}</h1>
          <p className="text-center text-mci-off-white/55 text-[12.5px] mb-4">{subtitle}</p>

          {children}
        </div>
      </div>
    </div>
  );
}
