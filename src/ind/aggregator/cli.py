# src/ind/aggregator/cli.py
from __future__ import annotations
import argparse, json, webbrowser
from pathlib import Path
from typing import Literal
from .service import build_company_intel

def _render_table(data: dict) -> str:
    from textwrap import indent
    out = []
    out.append(f"Company: {data['company']}")
    out.append("\nApproved Drugs:")
    if data["drugs_approved"]:
        for d in data["drugs_approved"]:
            out.append(f"  - {d.get('brand_name') or ''} "
                       f"({d.get('active_ingredient') or ''}) | "
                       f"Indications: {', '.join(d.get('indications') or [])} | "
                       f"App: {d.get('application') or ''} | "
                       f"Approval: {d.get('approval_date') or ''}")
    else:
        out.append("  (none)")

    out.append("\nClinical Trials:")
    if data["in_trials"]:
        for t in data["in_trials"]:
            out.append(f"  - {t.get('nct_id')} | {t.get('title')} "
                       f"| Phase: {t.get('phase') or ''} | Status: {t.get('status') or ''}")
    else:
        out.append("  (none)")

    out.append("\nPatents:")
    if data["patents"]:
        for p in data["patents"]:
            out.append(f"  - {p.get('number')} | {p.get('title')} "
                       f"| Filed: {p.get('filing_date') or ''} | Issued: {p.get('issue_date') or ''}")
    else:
        out.append("  (none)")

    out.append("\nPatient Population (US):")
    if data["populations"]:
        for p in data["populations"]:
            out.append(f"  - {p.get('disease')} | Incidence/yr: {p.get('incidence_per_year') or ''} "
                       f"| Source: {p.get('source') or ''}")
    else:
        out.append("  (none)")

    out.append("\nCompetitors (inferred):")
    if data["competitors"]:
        for c in data["competitors"]:
            out.append(f"  - {c}")
    else:
        out.append("  (none)")
    return "\n".join(out)

def _render_html(data: dict) -> str:
    # Minimal standalone HTML (no server). Style kept compact.
    def esc(s): return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    def td(x): return f"<td>{esc(str(x))}</td>"
    def row(cells): return f"<tr>{''.join(cells)}</tr>"

    drugs_rows = "\n".join(
        row([td(d.get("brand_name","")), td(d.get("active_ingredient","")),
             td("; ".join(d.get("indications") or [])), td(d.get("application","")), td(d.get("approval_date",""))])
        for d in (data.get("drugs_approved") or [])
    ) or "<tr><td colspan=5>(none)</td></tr>"

    trials_rows = "\n".join(
        row([td(t.get("nct_id","")), td(t.get("title","")), td(t.get("phase","")), td(t.get("status",""))])
        for t in (data.get("in_trials") or [])
    ) or "<tr><td colspan=4>(none)</td></tr>"

    patents_rows = "\n".join(
        row([td(p.get("number","")), td(p.get("title","")), td(p.get("filing_date","")), td(p.get("issue_date",""))])
        for p in (data.get("patents") or [])
    ) or "<tr><td colspan=4>(none)</td></tr>"

    pops_rows = "\n".join(
        row([td(p.get("disease","")), td(p.get("incidence_per_year","")), td(p.get("source",""))])
        for p in (data.get("populations") or [])
    ) or "<tr><td colspan=3>(none)</td></tr>"

    comps_html = "".join(f"<span class='pill'>{esc(c)}</span>" for c in (data.get("competitors") or [])) or "<span class='muted'>(none)</span>"

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{esc(data.get('company','IND Intelligence'))}</title>
<style>
:root {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; }}
body {{ margin:0; background:#0b1220; color:#e6edf3; }}
header {{ padding:16px 24px; border-bottom:1px solid #1f2a44; position:sticky; top:0; background:#0b1220; }}
.container {{ padding:24px; display:grid; gap:16px; }}
.card {{ background:#0f172a; border:1px solid #1f2a44; border-radius:14px; padding:16px; }}
.title {{ font-size:20px; margin:0 0 8px; }}
.grid {{ display:grid; gap:12px; }}
.grid.cols-2 {{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
.pill {{ display:inline-block; padding:4px 8px; border-radius:999px; border:1px solid #32456b; margin:2px; font-size:12px; }}
table {{ width:100%; border-collapse: collapse; }}
th, td {{ text-align:left; border-bottom:1px solid #1f2a44; padding:8px; }}
th {{ font-weight:600; }}
.muted {{ color:#a4b1c6; }}
</style></head>
<body>
<header><strong>IND Intelligence</strong></header>
<div class="container">
  <div class="card">
    <h2 class="title">Summary</h2>
    <div class="muted">Company</div>
    <div style="font-size:24px; margin-bottom:8px;">{esc(data.get('company',''))}</div>
    <div class="muted" style="margin-top:6px;">Competitors (inferred)</div>
    <div>{comps_html}</div>
  </div>

  <div class="grid cols-2">
    <div class="card">
      <h3 class="title">Approved Drugs</h3>
      <table><thead><tr><th>Brand</th><th>Ingredient</th><th>Indications</th><th>Application</th><th>Approval</th></tr></thead>
      <tbody>{drugs_rows}</tbody></table>
    </div>

    <div class="card">
      <h3 class="title">Clinical Trials</h3>
      <table><thead><tr><th>NCT</th><th>Title</th><th>Phase</th><th>Status</th></tr></thead>
      <tbody>{trials_rows}</tbody></table>
    </div>

    <div class="card">
      <h3 class="title">Patent Portfolio</h3>
      <table><thead><tr><th>Number</th><th>Title</th><th>Filed</th><th>Issued</th></tr></thead>
      <tbody>{patents_rows}</tbody></table>
    </div>

    <div class="card">
      <h3 class="title">Patient Population (US)</h3>
      <table><thead><tr><th>Disease</th><th>Incidence / yr</th><th>Source</th></tr></thead>
      <tbody>{pops_rows}</tbody></table>
    </div>
  </div>
</div>
</body></html>"""

def add_subparser(subparsers: argparse._SubParsersAction, formatter_class: type[argparse.HelpFormatter]=argparse.HelpFormatter) -> None:
    p = subparsers.add_parser(
        "intel",
        help="Aggregate company information from OpenFDA, ClinicalTrials, USPTO, NAACCR, PubChem",
        description="Search a company and aggregate drugs, trials, patents, population, and competitors.",
        formatter_class=formatter_class
    )
    p.add_argument("company", help="Company or sponsor name")
    p.add_argument("--trial-limit", type=int, default=50, help="Max trials to fetch")
    p.add_argument("--format", choices=["json","table","html"], default="table", help="Output format")
    p.add_argument("-o","--output", type=Path, help="Output file (required for --format html)")
    p.add_argument("--open", dest="auto_open", action="store_true", help="Open HTML output in browser")
    p.set_defaults(func=_run)

def _run(**kwargs) -> None:
    args = argparse.Namespace(**kwargs)
    intel = build_company_intel(args.company, trial_limit=args.trial_limit).dict()

    fmt: Literal["json","table","html"] = args.format
    if fmt == "json":
        print(json.dumps(intel, indent=2))
        return

    if fmt == "table":
        print(_render_table(intel))
        return

    # html
    if not args.output:
        raise SystemExit("Please provide -o/--output for --format html")
    html = _render_html(intel)
    args.output.write_text(html, encoding="utf-8")
    print(f"Wrote {args.output}")
    if args.auto_open:
        webbrowser.open(args.output.resolve().as_uri())