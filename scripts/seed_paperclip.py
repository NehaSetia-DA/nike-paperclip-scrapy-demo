#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.request


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
API_URL = os.environ.get("PAPERCLIP_API_URL", "http://localhost:3100").rstrip("/")
API_KEY = os.environ.get("PAPERCLIP_API_KEY", "")


def request(method, path, payload=None):
    data = None
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"{API_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} failed: HTTP {exc.code}\n{detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Cannot reach Paperclip at {API_URL}: {exc}") from exc


def find_by_name(items, name):
    for item in items:
        if item.get("name") == name or item.get("title") == name:
            return item
    return None


def agent_instructions(agent):
    return f"""# {agent["title"]}

You are {agent["name"]} in the Nike Product Intelligence demo.

Work inside:

`/Users/nehasetianagpal/nike-paperclip-scrapy-demo`

Mission:

Coordinate a local Paperclip + Claude + Zyte Web Data + Scrapy demo for public Nike product/catalog extraction.

Rules:

- The Paperclip server process must be started with `ANTHROPIC_API_KEY` and `ZYTE_API_KEY` in its environment.
- Use Zyte Claude skills for scraper generation. Do not handwrite selectors from scratch.
- Respect the safety boundary in `README.md`.
- Do not bypass login walls, checkout flows, account pages, private pages, or restricted content.
- If robots, terms, credentials, or access constraints block the intended crawl, stop and report the blocker instead of working around it.

Capabilities:

{agent["capabilities"]}
"""


def main():
    with open(os.path.join(ROOT, "paperclip", "company-plan.json"), "r", encoding="utf-8") as f:
        plan = json.load(f)

    existing_companies = request("GET", "/api/companies")
    company = find_by_name(existing_companies if isinstance(existing_companies, list) else existing_companies.get("companies", []), plan["company"]["name"])
    if company:
        print(f"Using existing company: {company['name']} ({company['id']})")
    else:
        company = request("POST", "/api/companies", plan["company"])
        print(f"Created company: {company['name']} ({company['id']})")
    company_id = company["id"]

    goal_title = "Generate and monitor Nike product catalog extraction"
    existing_goals_response = request("GET", f"/api/companies/{company_id}/goals")
    existing_goals = existing_goals_response if isinstance(existing_goals_response, list) else existing_goals_response.get("goals", [])
    goal = find_by_name(existing_goals, goal_title)
    if goal:
        print(f"Using existing goal: {goal['title']} ({goal['id']})")
    else:
        goal = request("POST", f"/api/companies/{company_id}/goals", {
            "title": goal_title,
            "description": "Use Paperclip to coordinate Claude/Zyte skills, Scrapy, and Zyte API for a safe local Nike product intelligence demo.",
            "level": "company",
            "status": "active"
        })
        print(f"Created goal: {goal['title']} ({goal['id']})")

    project_name = "Nike Scrapy Demo"
    existing_projects_response = request("GET", f"/api/companies/{company_id}/projects")
    existing_projects = existing_projects_response if isinstance(existing_projects_response, list) else existing_projects_response.get("projects", [])
    project = find_by_name(existing_projects, project_name)
    if project:
        print(f"Using existing project: {project['name']} ({project['id']})")
    else:
        project = request("POST", f"/api/companies/{company_id}/projects", {
            "name": project_name,
            "description": "Workspace for the generated Scrapy + Zyte API product scraper.",
            "goalIds": [goal["id"]],
            "status": "in_progress",
            "workspace": {
            "name": "nike-paperclip-scrapy-demo",
                "cwd": ROOT,
                "isPrimary": True
            }
        })
        print(f"Created project: {project['name']} ({project['id']})")

    agent_ids = {}
    workspace = ROOT
    existing_agents_response = request("GET", f"/api/companies/{company_id}/agents")
    existing_agents = existing_agents_response if isinstance(existing_agents_response, list) else existing_agents_response.get("agents", [])
    for agent in plan["agents"]:
        existing_agent = find_by_name(existing_agents, agent["name"])
        if existing_agent:
            agent_ids[agent["name"]] = existing_agent["id"]
            print(f"Using existing agent: {agent['name']} ({existing_agent['id']})")
            continue
        payload = {
            "name": agent["name"],
            "role": agent["role"],
            "title": agent["title"],
            "capabilities": agent["capabilities"],
            "adapterType": agent["adapterType"],
            "adapterConfig": {
                "cwd": workspace,
                "env": {},
                "timeoutSec": 0,
                "dangerouslySkipPermissions": False
            },
            "instructionsBundle": {
                "files": {
                    "AGENTS.md": agent_instructions(agent)
                }
            },
            "budgetMonthlyCents": 800
        }
        reports_to = agent.get("reportsTo")
        if reports_to:
            payload["reportsTo"] = agent_ids[reports_to]
        created = request("POST", f"/api/companies/{company_id}/agents", payload)
        agent_ids[agent["name"]] = created["id"]
        print(f"Created agent: {agent['name']} ({created['id']})")

    for issue in plan["issues"]:
        payload = {
            "title": issue["title"],
            "description": issue["description"],
            "priority": issue["priority"],
            "status": "todo",
            "assigneeAgentId": agent_ids[issue["assignee"]],
            "projectId": project["id"],
            "goalId": goal["id"]
        }
        created = request("POST", f"/api/companies/{company_id}/issues", payload)
        print(f"Created issue: {created['title']} ({created['id']})")

    routine = plan["routine"]
    routine_payload = {
        "title": routine["title"],
        "description": routine["description"],
        "assigneeAgentId": agent_ids[routine["assignee"]],
        "projectId": project["id"],
        "goalId": goal["id"],
        "priority": "medium",
        "status": "active",
        "concurrencyPolicy": "coalesce_if_active",
        "catchUpPolicy": "skip_missed"
    }
    created_routine = request("POST", f"/api/companies/{company_id}/routines", routine_payload)
    print(f"Created routine: {created_routine['title']} ({created_routine['id']})")

    trigger_payload = {
        "kind": "schedule",
        "cronExpression": routine["cronExpression"],
        "timezone": routine["timezone"]
    }
    request("POST", f"/api/routines/{created_routine['id']}/triggers", trigger_payload)
    print("Added daily schedule trigger.")

    state = {
        "companyId": company_id,
        "goalId": goal["id"],
        "projectId": project["id"],
        "agentIds": agent_ids,
        "routineId": created_routine["id"]
    }
    os.makedirs(os.path.join(ROOT, "outputs"), exist_ok=True)
    with open(os.path.join(ROOT, "outputs", "paperclip-seed-state.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    print("Saved outputs/paperclip-seed-state.json")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
