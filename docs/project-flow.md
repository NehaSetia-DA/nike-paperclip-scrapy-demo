# Nike Paperclip Scrapy Demo Flow

This diagram captures the decisions we made while building the demo: Paperclip
as control plane, Zyte Claude skills as the build workflow, Scrapy as extraction
engine, Zyte API as access/rendering layer, Spidermon as runtime guardrail, and
cost analysis as the optimization lane.

Editable dark-mode Excalidraw version:
`docs/project-flow-dark.excalidraw`

```mermaid
%%{init: {
  "theme": "base",
  "flowchart": {
    "htmlLabels": true,
    "curve": "basis",
    "nodeSpacing": 58,
    "rankSpacing": 78
  },
  "themeVariables": {
    "fontFamily": "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
    "fontSize": "20px",
    "primaryTextColor": "#f8fafc",
    "lineColor": "#94a3b8",
    "background": "#0b1020",
    "mainBkg": "#0f172a",
    "clusterBkg": "#111827",
    "clusterBorder": "#475569",
    "edgeLabelBackground": "#0b1020"
  }
}}%%
flowchart LR
    subgraph CP["<b>Company + Control Plane</b>"]
        A["<b>Nike Product Intelligence</b><br/>Paperclip company"]
        B["<b>Goal</b><br/>Generate and monitor Nike product catalog extraction"]
        C["<b>Workspace</b><br/>nike-paperclip-scrapy-demo<br/>nike_catalog"]
        D["<b>Local Environment</b><br/>ANTHROPIC_API_KEY<br/>ZYTE_API_KEY"]
    end

    subgraph AG["<b>Five Agents</b>"]
        E["<b>Coordinator</b><br/>Routes build, run, QA, cost<br/>Owns approvals and escalation"]
        F["<b>ScrapyBuilder</b><br/>Builds or rebuilds spider<br/>Runs Zyte Claude skills"]
        G["<b>QAReviewer</b><br/>Validates output quality<br/>Diagnoses drift vs local fix"]
        H["<b>Monitor</b><br/>Runs existing spider<br/>Owns health checks"]
        I["<b>CostAnalyst</b><br/>Reviews Zyte API spend<br/>Finds high-impact reductions"]
    end

    subgraph BUILD["<b>Build Mode: First Site Or Rebuild</b>"]
        J["<b>Zyte Claude Skill Flow</b><br/>/scrape-zyte-login<br/>/scrape-define<br/>/scrape-review-schema"]
        K{"<b>Schema Approved?</b>"}
        J4["<b>Generate Spec + Project</b><br/>/scrape-spec<br/>/scrape-ensure-project"]
        J6["<b>Codegen + Spider</b><br/>/scrape-codegen<br/>/scrape-create-spider"]
        L["<b>Generated Scrapy Project</b><br/>nike_catalog"]
        M["<b>Extraction Strategy</b><br/>Nike JSON-LD<br/>ProductGroup / Product"]
        N["<b>Access Layer</b><br/>scrapy-zyte-api<br/>browserHtml for reliability"]
        O["<b>Fixtures + Sample Crawl</b>"]
    end

    subgraph RUN["<b>Run Mode: Daily Existing Spider Loop</b>"]
        T["<b>Run Mode Begins</b><br/>No ScrapyBuilder in normal runs"]
        U["<b>Monitor Command</b><br/>scripts/monitor-nike-crawl.sh"]
        V["<b>Scrapy Output</b><br/>products.jsonl<br/>crawl.log"]
        W["<b>Spidermon Close Monitors</b><br/>minimum items<br/>required fields<br/>duplicate URLs<br/>Zyte API processed<br/>no fatal Zyte errors"]
        X["<b>Paperclip Health Report</b><br/>health.json"]
        Y{"<b>Healthy Run?</b>"}
        Z["<b>Record Healthy Latest Run</b>"]
    end

    subgraph QA["<b>QA + Repair Loop</b>"]
        P{"<b>Healthy Sample?</b>"}
        Q["<b>QA Repair Issue</b>"]
        R{"<b>Structural Drift?</b>"}
        S["<b>Local Parser / Settings Repair</b>"]
    end

    subgraph COST["<b>Cost Optimization Loop</b>"]
        AA["<b>Cost Review</b><br/>/scrapy-cost-analysis<br/>or local analyzer"]
        AB["<b>Signals Reviewed</b><br/>browserHtml, automap, retries,<br/>duplicates, request/item ratio"]
        AC{"<b>Highest-impact Change?</b>"}
        AD["<b>Keep Reliability-first Settings</b>"]
        AE["<b>Test Cheaper Path</b><br/>non-browser JSON-LD<br/>or reduce duplicates/retries"]
    end

    A --> B --> C --> D --> E
    E --> F
    E --> G
    E --> H
    E --> I

    F --> J --> K
    K -->|"revise"| J
    K -->|"approved"| J4 --> J6 --> L --> M --> N --> O --> G

    G --> P
    P -->|"yes"| T
    P -->|"no"| Q --> R
    R -->|"yes: rebuild"| E
    R -->|"no: local fix"| S --> G

    H --> U
    T --> U --> V --> W --> X --> Y
    Y -->|"yes"| Z
    Y -->|"no"| Q

    I --> AA --> AB --> AC
    AC -->|"none"| AD
    AC -->|"yes"| AE --> G

    classDef company fill:#1e3a8a,stroke:#60a5fa,color:#f8fafc,stroke-width:2px,font-size:20px;
    classDef coordinator fill:#4c1d95,stroke:#c4b5fd,color:#faf5ff,stroke-width:3px,font-size:22px;
    classDef agent fill:#111827,stroke:#a78bfa,color:#f8fafc,stroke-width:2px,font-size:20px;
    classDef build fill:#064e3b,stroke:#34d399,color:#ecfdf5,stroke-width:2px,font-size:20px;
    classDef run fill:#0f766e,stroke:#5eead4,color:#f0fdfa,stroke-width:2px,font-size:20px;
    classDef qa fill:#581c87,stroke:#d8b4fe,color:#faf5ff,stroke-width:2px,font-size:20px;
    classDef cost fill:#7c2d12,stroke:#fb923c,color:#fff7ed,stroke-width:2px,font-size:20px;
    classDef decision fill:#713f12,stroke:#facc15,color:#fefce8,stroke-width:3px,font-size:21px;
    classDef success fill:#14532d,stroke:#86efac,color:#f0fdf4,stroke-width:2px,font-size:20px;

    class A,B,C,D company;
    class E coordinator;
    class F,G,H,I agent;
    class J,J4,J6,L,M,N,O build;
    class T,U,V,W,X run;
    class P,Q,R,S qa;
    class AA,AB,AD,AE cost;
    class K,Y,AC decision;
    class Z success;
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
