interface FooterProps {
  metaText?: string;
}

export function Footer({ metaText }: FooterProps) {
  return (
    <footer className="w-full py-10 px-6 lg:px-10 flex flex-col md:flex-row justify-between items-center gap-4 bg-surface-container-highest border-t border-outline-variant mt-10">
      <div className="flex flex-col items-center md:items-start gap-1">
        <span className="text-sm font-bold text-on-surface">CulinaAI</span>
        <p className="text-xs text-on-surface-variant">
          © 2024 CulinaAI. Powered by real Zomato dataset + AI
        </p>
        {metaText && (
          <p className="text-xs text-primary font-bold italic">{metaText}</p>
        )}
      </div>
      <div className="flex gap-6 flex-wrap justify-center text-on-surface-variant text-sm opacity-60">
        <span>Terms of Service</span>
        <span>Privacy Policy</span>
        <span>Contact Support</span>
      </div>
    </footer>
  );
}
