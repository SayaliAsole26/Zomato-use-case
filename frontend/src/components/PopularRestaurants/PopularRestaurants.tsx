import { useQuery } from "@tanstack/react-query";
import { fetchPopularRestaurants } from "../../services/api";
import { RestaurantCard, summaryToCardProps } from "../RestaurantCard/RestaurantCard";

interface PopularRestaurantsProps {
  location?: string;
}

export function PopularRestaurants({ location }: PopularRestaurantsProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["popular", location],
    queryFn: () => fetchPopularRestaurants(location),
  });

  if (isLoading || !data) {
    return (
      <section className="py-8">
        <div className="animate-pulse h-8 w-48 bg-surface-container-high rounded mb-4" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-48 bg-surface-container-high rounded-xl" />
          ))}
        </div>
      </section>
    );
  }

  const sections = [
    { title: "Trending", items: data.trending, icon: "local_fire_department" },
    { title: "Highly Rated", items: data.highly_rated, icon: "star" },
    { title: "New Opening", items: data.new_opening, icon: "new_releases" },
  ] as const;

  return (
    <section className="py-8 space-y-10">
      {sections.map(({ title, items, icon }) => (
        <div key={title}>
          <div className="flex items-center gap-2 mb-4">
            <span className="material-symbols-outlined text-primary">{icon}</span>
            <h2 className="text-xl font-semibold">{title}</h2>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {items.slice(0, 4).map((item, index) => (
              <RestaurantCard key={item.id} {...summaryToCardProps(item, index)} />
            ))}
          </div>
        </div>
      ))}
    </section>
  );
}
