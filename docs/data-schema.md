# Data Schema Mapping

Dataset: [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)

Split: `train` (~51,717 rows)

## Raw columns (Hugging Face)

| Raw column | Type | Maps to |
|------------|------|---------|
| `name` | string | `RestaurantRecord.name` |
| `location` | string | `RestaurantRecord.location` (normalized + aliases) |
| `listed_in(city)` | string | Fallback for `location` when `location` is empty |
| `cuisines` | string | `RestaurantRecord.cuisines` (split on `,`, `\|`, `/`) |
| `rate` | string | `RestaurantRecord.rating` (parsed, e.g. `4.5/5`) |
| `approx_cost(for two people)` | string | `RestaurantRecord.cost_for_two` |
| — | derived | `RestaurantRecord.cost_tier` from cost thresholds |
| `address` | string | `RestaurantRecord.address` |
| `votes` | int64 | `RestaurantRecord.votes` |
| (all columns) | — | `RestaurantRecord.raw` (in-memory only, omitted from cache) |
| — | derived | `RestaurantRecord.id` (SHA-256 of name + location + address + index) |

Unused in v1 filtering (retained in `raw`): `url`, `online_order`, `book_table`, `phone`, `rest_type`, `dish_liked`, `reviews_list`, `menu_item`, `listed_in(type)`.

## Preprocessing rules

| Field | Rule |
|-------|------|
| Location | Trim; alias map (`bengaluru` → `Bangalore`); fallback to `listed_in(city)` |
| Rating | Parse `X/5`; `NEW`, `-`, out of range → `null` |
| Cost | Strip commas; ranges `300-400` → midpoint |
| Cost tier | `≤500` low, `501–1000` medium, `>1000` high (configurable via env) |
| Dedup | Keep first row per `(name, location)` case-insensitive |
| Drop row | Missing/blank `name` or unresolvable `location` |

## Cache file

| Path | Content |
|------|---------|
| `data/cache/restaurants.parquet` | Preprocessed records (gitignored) |

## Canonical model

See `src/models/restaurant.py` — `RestaurantRecord` and `CostTier`.
