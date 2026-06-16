import { Link, useLocation } from "react-router-dom";

interface HeaderProps {
  onOpenFilters?: () => void;
}

export function Header({ onOpenFilters }: HeaderProps) {
  const { pathname } = useLocation();
  const onDiscover = pathname.startsWith("/discover");

  return (
    <header className="sticky top-0 z-50 bg-surface border-b border-outline-variant shadow-sm">
      <div className="max-w-container-max mx-auto flex justify-between items-center px-6 h-16">
        <Link to="/" className="text-2xl font-extrabold text-primary tracking-tight">
          CulinaAI
        </Link>

        <nav className="hidden md:flex items-center gap-6">
          <Link
            to="/"
            className={`py-1 transition-colors ${
              pathname === "/"
                ? "text-primary font-bold border-b-2 border-primary"
                : "text-on-surface-variant hover:text-primary"
            }`}
          >
            Home
          </Link>
          <Link
            to="/discover"
            className={`py-1 transition-colors ${
              onDiscover
                ? "text-primary font-bold border-b-2 border-primary"
                : "text-on-surface-variant hover:text-primary"
            }`}
          >
            Discover
          </Link>
        </nav>

        <div className="flex items-center gap-3">
          {onOpenFilters && (
            <button
              type="button"
              onClick={onOpenFilters}
              className="lg:hidden material-symbols-outlined text-on-surface-variant hover:text-primary p-2"
              aria-label="Open filters"
            >
              tune
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
