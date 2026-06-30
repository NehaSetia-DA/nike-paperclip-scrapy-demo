# Nike Paperclip Scrapy Demo Flow

This diagram captures the decisions we made while building the demo: Paperclip
as control plane, Zyte Claude skills as the build workflow, Scrapy as extraction
engine, Zyte API as access/rendering layer, Spidermon as runtime guardrail, and
cost analysis as the optimization lane.

```mermaid
flowchart TD
    A["User goal: agentic ecommerce scraping demo"] --> B["Choose target site"]
    B --> C{"Foot Locker ID viable?"}
    C -->|"Difficult / blocked"| D["Switch to Nike public pages"]
    C -->|"Allowed and stable"| E["Continue Foot Locker plan"]
    D --> F["Preflight: tools, credentials, robots, terms boundary"]
    F --> G{"Allowed public target?"}
    G -->|"No"| H["Stop or choose compliant target"]
    G -->|"Yes"| I["Create Paperclip company: Nike Product Intelligence"]

    I --> J["Coordinator creates build issues and schema approval"]
    J --> K["ScrapyBuilder runs Zyte Claude skill flow"]
    K --> K1["/scrape-zyte-login"]
    K1 --> K2["/scrape-define"]
    K2 --> K3["/scrape-review-schema"]
    K3 --> L{"Schema approved?"}
    L -->|"No"| K2
    L -->|"Yes"| K4["/scrape-spec"]
    K4 --> K5["/scrape-ensure-project"]
    K5 --> K6["/scrape-codegen"]
    K6 --> K7["/scrape-create-spider"]

    K7 --> M["Generated Scrapy project: nike_catalog"]
    M --> N["Extraction strategy: Nike JSON-LD ProductGroup/Product"]
    N --> O["Zyte API access: scrapy-zyte-api with browserHtml for reliability"]
    O --> P["Fixtures and sample output"]
    P --> Q["QAReviewer validates schema completeness and duplicates"]
    Q --> R{"Sample crawl healthy?"}
    R -->|"No"| S["QA repair issue"]
    S --> T{"Structural site/parser drift?"}
    T -->|"Yes"| U["Coordinator sends rebuild to ScrapyBuilder"]
    T -->|"No"| V["Local parser/settings repair by QA"]
    R -->|"Yes"| W["Run mode begins"]

    W --> X["Monitor runs scripts/monitor-nike-crawl.sh"]
    X --> Y["Scrapy spider writes products.jsonl and crawl.log"]
    Y --> Z["Spidermon close monitors run"]
    Z --> Z1["Minimum item count"]
    Z --> Z2["Required field completeness"]
    Z --> Z3["Duplicate product URLs"]
    Z --> Z4["Zyte API processed requests"]
    Z --> Z5["Fatal Zyte API errors"]
    Z --> AA["Paperclip health JSON report"]
    AA --> AB{"Quality passed?"}
    AB -->|"Yes"| AC["Monitor records healthy run"]
    AB -->|"No"| AD["Monitor opens QA repair issue"]
    AD --> T

    W --> AE["CostAnalyst run: /scrapy-cost-analysis or local analyzer"]
    AE --> AF{"Cost issue confirmed?"}
    AF -->|"No"| AG["Keep current reliability-first settings"]
    AF -->|"Yes"| AH["Recommend highest-impact reduction"]
    AH --> AI{"Browser rendering needed?"}
    AI -->|"No"| AJ["Test cheaper non-browser PDP requests"]
    AI -->|"Yes"| AK["Keep rendering but reduce duplicates/retries/scope"]
    AJ --> Q
    AK --> Q
```

## Why Paperclip

Paperclip is the control plane because it keeps the human-visible state:
company, goal, agents, issues, approvals, routines, and repair ownership. The
important design decision is that Paperclip does not scrape by itself. It routes
work to the right specialist:

- `Coordinator` decides build mode vs run mode.
- `ScrapyBuilder` only runs for a new site, schema change, or structural drift.
- `Monitor` runs the existing spider and creates repair work when quality drops.
- `QAReviewer` diagnoses failures before escalating to a rebuild.
- `CostAnalyst` reviews Zyte API cost risks before deployment or when spend rises.

## Build Mode

Build mode is expensive and should be rare. It uses Zyte Claude skills to
discover the site, approve the schema, generate page objects, wire the spider,
and create fixtures.

## Run Mode

Run mode is the daily loop. It should not call ScrapyBuilder or regenerate code.
It runs the existing spider, captures artifacts, executes Spidermon, writes a
health report, and routes failures to QA.

## Cost Mode

Cost mode is an optimization loop. It reviews browser rendering, Zyte API
automation, retries, duplicate requests, pagination, job stats, and request/item
ratios. For this Nike demo, the first hypothesis is whether JSON-LD extraction
works without `browserHtml=True`.
