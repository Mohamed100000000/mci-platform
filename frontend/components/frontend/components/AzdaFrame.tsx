import { ReactNode } from "react";

interface AzdaFrameProps {
  logoSrc: string;
  title: string;
  subtitle: string;
  onHome?: () => void;
  lang: "ar" | "en";
  onToggleLang: () => void;
  children: ReactNode;
}

/**
 * The outer shell every AZDA exam screen sits inside — matches the
 * `.frame` / top-row / logo / lang-toggle markup in the original game 1:1.
 */
export function AzdaFrame({
  logoSrc,
  title,
  subtitle,
  onHome,
  lang,
  onToggleLang,
  children,
}: AzdaFrameProps) {
  const dir = lang === "ar" ? "rtl" : "ltr";

  return (
    <div
      dir={dir}
      className="min-h-screen flex items-center justify-center p-6 font-azda-body text-azda-off-white"
      style={{
        background:
          "radial-gradient(circle at 20% 10%, rgba(200,149,47,0.08), transparent 40%), radial-gradient(circle at 85% 85%, rgba(47,143,124,0.10), transparent 45%), linear-gradient(180deg, #0a1c30 0%, #123252 100%)",
      }}
    >
      <div className="w-full max-w-[600px]">
        <div className="relative rounded-[18px] border border-azda-brass/35 bg-white/[0.04] p-6 shadow-2xl">
          <div className="absolute inset-1.5 rounded-xl border border-dashed border-azda-brass/20 pointer-events-none" />

          <div className="flex items-center justify-between mb-2.5">
            <button
              onClick={onHome}
              aria-label={lang === "ar" ? "الرئيسية" : "Home"}
              className="rounded-2xl border border-azda-brass/40 bg-azda-brass/10 px-3 py-1.5 text-xs font-bold text-azda-brass-light hover:bg-azda-brass/20 transition-colors"
            >
              🏠
            </button>
            <div className="flex-1 flex justify-center">
              <img
                src={logoSrc}
                alt="AZDA Marine Training Institute"
                className="h-[50px] rounded-lg bg-azda-off-white/90 px-3 py-1.5 drop-shadow-lg"
              />
            </div>
            <button
              onClick={onToggleLang}
              className="rounded-2xl border border-azda-brass/40 bg-azda-brass/10 px-3 py-1.5 text-xs font-bold text-azda-brass-light hover:bg-azda-brass/20 transition-colors"
            >
              {lang === "ar" ? "EN" : "AR"}
            </button>
          </div>

          <h1 className="font-azda-display text-center text-[26px] tracking-wide mb-1">{title}</h1>
          <p className="text-center text-azda-off-white/55 text-[12.5px] mb-4">{subtitle}</p>

          {children}
        </div>
      </div>
    </div>
  );
}
