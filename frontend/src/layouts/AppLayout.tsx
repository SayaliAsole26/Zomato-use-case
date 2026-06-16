import { Footer } from "../components/layout/Footer";
import { Navbar } from "../components/Navbar/Navbar";

interface AppLayoutProps {
  children: React.ReactNode;
  onOpenFilters?: () => void;
  footerMeta?: string;
}

export function AppLayout({ children, onOpenFilters, footerMeta }: AppLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar onOpenFilters={onOpenFilters} />
      {children}
      <Footer metaText={footerMeta} />
    </div>
  );
}
