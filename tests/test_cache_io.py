from src.data.cache_io import load_processed_cache, save_processed_cache
from src.models.restaurant import CostTier, RestaurantRecord


def test_processed_cache_roundtrip(tmp_path):
    records = [
        RestaurantRecord(
            id="abc123",
            name="Cache Test",
            location="Bangalore",
            cuisines=["italian", "cafe"],
            rating=4.2,
            cost_for_two=500,
            cost_tier=CostTier.LOW,
            votes=10,
        )
    ]
    path = tmp_path / "restaurants.parquet"

    save_processed_cache(records, path)
    loaded = load_processed_cache(path)

    assert loaded is not None
    assert len(loaded) == 1
    assert loaded[0].name == "Cache Test"
    assert loaded[0].cuisines == ["italian", "cafe"]
    assert loaded[0].cost_tier == CostTier.LOW
    assert loaded[0].raw is None
