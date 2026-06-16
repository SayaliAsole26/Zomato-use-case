from src.data.repository import build_repository_from_records
from src.models.preferences import Budget, UserPreferences
from src.models.restaurant import CostTier, RestaurantRecord


def _record(name: str, location: str) -> RestaurantRecord:
    return RestaurantRecord(
        id=f"id-{name}",
        name=name,
        location=location,
        cuisines=["italian"],
        rating=4.0,
        cost_for_two=600,
        cost_tier=CostTier.MEDIUM,
    )


def test_repository_get_all_and_locations():
    records = [
        _record("A", "Bangalore"),
        _record("B", "New Delhi"),
        _record("C", "Bangalore"),
    ]
    repo = build_repository_from_records(records)

    assert repo.count() == 3
    assert len(repo.get_all()) == 3
    assert repo.get_locations() == ["Bangalore", "New Delhi"]
    assert repo.get_by_id("id-A") == records[0]


def test_repository_get_by_filters_stub():
    repo = build_repository_from_records([_record("X", "Mumbai")])
    filtered = repo.get_by_filters(location="Mumbai")
    assert len(filtered) == 1
    assert filtered[0].location == "Mumbai"


def test_repository_query_delegates_to_filter():
    records = [
        RestaurantRecord(
            id="1",
            name="Italian Place",
            location="Bangalore",
            cuisines=["italian"],
            rating=4.5,
            cost_for_two=800,
            cost_tier=CostTier.MEDIUM,
            votes=100,
        ),
        RestaurantRecord(
            id="2",
            name="Other",
            location="Bangalore",
            cuisines=["chinese"],
            rating=4.0,
            cost_for_two=600,
            cost_tier=CostTier.MEDIUM,
            votes=50,
        ),
    ]
    repo = build_repository_from_records(records)
    prefs = UserPreferences(
        location="Bangalore",
        budget=Budget.MEDIUM,
        cuisine="italian",
        min_rating=4.0,
    )

    result = repo.query(prefs)

    assert len(result) == 1
    assert result[0].name == "Italian Place"


def test_repository_query_empty_when_no_match():
    repo = build_repository_from_records([_record("X", "Mumbai")])
    prefs = UserPreferences(location="Chennai", budget=Budget.LOW)
    assert repo.query(prefs) == []
