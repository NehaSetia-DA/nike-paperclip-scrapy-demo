# Nike Paperclip Scrapy Demo Flow

This diagram captures the decisions we made while building the demo: Paperclip
as control plane, Zyte Claude skills as the build workflow, Scrapy as extraction
engine, Zyte API as access/rendering layer, Spidermon as runtime guardrail, and
cost analysis as the optimization lane.

Editable dark-mode Excalidraw version:
`docs/project-flow-dark.excalidraw`

```mermaid
flowchart TD
    A["Paperclip company: Nike Product Intelligence"] --> B["Goal: generate and monitor Nike product catalog extraction"]
    B --> C["Workspace: nike-paperclip-scrapy-demo / nike_catalog"]
    C --> D["Local environment: ANTHROPIC_API_KEY + ZYTE_API_KEY"]
    D --> E["Coordinator"]

    E --> F["ScrapyBuilder"]
    E --> G["QAReviewer"]
    E --> H["Monitor"]
    E --> I["CostAnalyst"]

    F --> J["Build mode: use Zyte Claude skill flow"]
    J --> J1["/scrape-zyte-login"]
    J1 --> J2["/scrape-define"]
    J2 --> J3["/scrape-review-schema"]
    J3 --> K{"Schema approved?"}
    K -->|"No"| J2
    K -->|"Yes"| J4["/scrape-spec"]
    J4 --> J5["/scrape-ensure-project"]
    J5 --> J6["/scrape-codegen"]
    J6 --> J7["/scrape-create-spider"]
    J7 --> L["Generated Scrapy project: nike_catalog"]

    L --> M["Extraction strategy: Nike JSON-LD ProductGroup/Product"]
    M --> N["Zyte API access through scrapy-zyte-api"]
    N --> O["Fixtures and sample crawl"]
    O --> G

    G --> P{"Healthy sample?"}
    P -->|"No"| Q["QA repair issue"]
    Q --> R{"Structural site/parser drift?"}
    R -->|"Yes"| E
    R -->|"No"| S["Local parser/settings repair"]
    S --> G
    P -->|"Yes"| T["Run mode begins"]

    H --> U["scripts/monitor-nike-crawl.sh"]
    T --> U
    U --> V["Scrapy writes products.jsonl + crawl.log"]
    V --> W["Spidermon close monitors"]
    W --> W1["minimum items"]
    W --> W2["required fields"]
    W --> W3["duplicate product URLs"]
    W --> W4["Zyte API processed requests"]
    W --> W5["no fatal Zyte errors"]
    W --> X["health.json"]
    X --> Y{"Healthy run?"}
    Y -->|"Yes"| Z["Monitor records healthy latest run"]
    Y -->|"No"| Q

    I --> AA["/scrapy-cost-analysis or local analyzer"]
    AA --> AB["Review browserHtml, automap, retries, duplicates, request/item ratio"]
    AB --> AC{"Highest-impact cost change?"}
    AC -->|"None"| AD["Keep reliability-first settings"]
    AC -->|"Yes"| AE["Test cheaper non-browser JSON-LD path or reduce duplicates/retries"]
    AE --> G
```

## Why Paperclip

Paperclip is the control plane because it keeps the human-visible state:
company, goal, agents, issues, approvals, routines, and repair ownership. The
important design decision is that Paperclip does not scrape by itself. It routes
work to the right specialist:

- `Coordinator` decides build mode vs run mode, owns approval gates, and routes rebuilds only when QA confirms structural drift.
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
