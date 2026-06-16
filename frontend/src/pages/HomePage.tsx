import { Link } from "react-router-dom";
import { PopularRestaurants } from "../components/PopularRestaurants/PopularRestaurants";
import { AppLayout } from "../layouts/AppLayout";
import { DEMO_LOCATION } from "../lib/constants";

const STEPS = [
  { icon: "tune", title: "1. Set preferences", text: "Location, budget, cuisine, rating, and more." },
  { icon: "filter_alt", title: "2. AI filters & ranks", text: "We scan 12k+ real Zomato data points." },
  { icon: "forum", title: "3. Get explained picks", text: "Clear reasons for every suggestion." },
];

export function HomePage() {
  return (
    <AppLayout>
      <main className="flex-1">
        <section className="relative min-h-[70vh] flex flex-col items-center justify-center text-center px-6 py-16 bg-surface-container-low/40">
          <div className="max-w-3xl z-10">
            <span className="bg-primary-fixed text-on-surface px-4 py-1 rounded-full mb-6 inline-block text-sm font-semibold">
              Powered by Zomato Intelligence
            </span>
            <h1 className="text-4xl md:text-5xl font-extrabold text-on-surface mb-4 tracking-tight">
              Smart picks, explained for you.
            </h1>
            <p className="text-lg text-on-surface-variant mb-8 max-w-xl mx-auto leading-relaxed">
              Your AI food guide for Bangalore. We don&apos;t just show lists; we give you the
              &ldquo;why&rdquo; behind every recommendation.
            </p>
            <Link
              to="/search"
              className="inline-flex items-center justify-center gap-2 h-14 px-10 btn-primary text-xl shadow-lg hover:scale-105"
            >
              <span className="material-symbols-outlined filled">auto_awesome</span>
              Search restaurants
            </Link>
          </div>
        </section>

        <section className="max-w-container-max mx-auto px-6">
          <PopularRestaurants location={DEMO_LOCATION} />
        </section>

        <section className="bg-surface-container-highest py-12 px-6 border-y border-outline-variant">
          <div className="max-w-container-max mx-auto grid grid-cols-1 md:grid-cols-3 gap-10 text-center">
            {STEPS.map((step) => (
              <div key={step.title} className="flex flex-col items-center">
                <div className="w-16 h-16 rounded-full bg-primary-fixed flex items-center justify-center mb-4">
                  <span className="material-symbols-outlined text-primary text-3xl">{step.icon}</span>
                </div>
                <h4 className="text-xl font-semibold mb-2">{step.title}</h4>
                <p className="text-base text-on-surface-variant">{step.text}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="py-16 px-6 bg-inverse-surface text-inverse-on-surface text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to eat smarter?</h2>
          <p className="text-lg opacity-90 mb-8 max-w-lg mx-auto">
            Stop scrolling endlessly. Let CulinaAI do the heavy lifting for your next meal.
          </p>
          <Link to="/search" className="inline-block btn-primary px-10 py-4 text-xl">
            Get Started Now
          </Link>
        </section>
      </main>
    </AppLayout>
  );
}
