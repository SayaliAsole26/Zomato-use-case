import { AppLayout } from "../../layouts/AppLayout";
import { RestaurantCard, summaryToCardProps } from "../../components/RestaurantCard/RestaurantCard";
import { useFavoritesStore } from "../../store/favoritesStore";

export function SavedPage() {
  const saved = useFavoritesStore((s) => s.saved);
  const remove = useFavoritesStore((s) => s.remove);

  return (
    <AppLayout>
      <main className="flex-1 p-6 lg:p-10 max-w-container-max mx-auto w-full">
        <h1 className="text-3xl font-bold mb-6">Saved Restaurants</h1>
        {saved.length === 0 ? (
          <p className="text-on-surface-variant">
            No saved restaurants yet. Save picks from search results to see them here.
          </p>
        ) : (
          <div className="flex flex-col gap-8">
            {saved.map((item, index) => (
              <RestaurantCard
                key={item.id}
                {...summaryToCardProps(item, index)}
                saved
                onSave={() => remove(item.id)}
              />
            ))}
          </div>
        )}
      </main>
    </AppLayout>
  );
}
