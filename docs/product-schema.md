# Nike Product Schema

The approved product item should include these fields:

| Field | Type | Required | Notes |
|---|---:|---:|---|
| `name` | string | yes | Product display name. |
| `brand` | string | yes | Brand or Nike sub-brand visible on the page. |
| `product_url` | string | yes | Absolute product detail URL. |
| `category` | string | no | Category or collection page context. |
| `gender_or_department` | string | no | Men, women, kids, unisex, or visible department label. |
| `price` | number | yes | Current selling price. |
| `currency` | string | yes | Currency code visible or inferable from page locale. |
| `sale_price` | number | no | Discounted price if separate from regular price. |
| `color` | string | no | Visible colorway. |
| `sizes` | array | no | Available sizes when visible. |
| `availability` | string | no | In stock, sold out, limited, or page-visible equivalent. |
| `image_url` | string | no | Primary product image. |
| `description` | string | no | Product detail text. |
| `sku` | string | no | Product SKU/style code if visible. |
| `source_url` | string | yes | Page URL used as evidence. |
| `fetched_at` | string | yes | ISO timestamp for traceability. |

Acceptance criteria:

- At least 10 product records in the sample output.
- Required fields present on every sample item.
- No duplicate `product_url` values.
- Zyte API usage is visible in crawl logs or summary.
