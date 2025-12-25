from __future__ import annotations
import argparse, json, webbrowser
from pathlib import Path
from typing import Literal
from .service import build_company_intel

def _render_table(data: dict) -> str:
    rows = data.get("drugs_approved", [])
    if not rows:
        return "No results found."
    keys = rows[0].keys()
    header = " | ".join(keys)
    out = [header, "-" * len(header)]
    for r in rows:
        out.append(" | ".join(str(r.get(k, "")) for k in keys))
    return "\n".join(out)
'''
def _render_table(data: dict) -> str:
    out = []
    out.append(f"Company: {data.get('company','')}")
    out.append("\nApproved Drugs (OpenFDA):")
    if data.get("drugs_approved"):
        for d in data["drugs_approved"]:
            out.append(
                f"  - {d.get('brand_name') or ''} "
                f"({d.get('active_ingredient') or ''}) | "
                f"App: {d.get('application') or ''} | "
                f"Approval: {d.get('approval_date') or ''}"
            )
    else:
        out.append("  (none)")
    return "\n".join(out)
'''
def _render_html(data: dict) -> str:
    # Minimal standalone HTML (no server). Style kept compact.
    def esc(s): return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    def td(x): return f"<td>{esc(str(x))}</td>"
    def row(cells): return f"<tr>{''.join(cells)}</tr>"

    drugs_rows = "\n".join(
        row([
            td(d.get("brand_name","")),
            td(d.get("active_ingredient","")),
            td(d.get("dosage_form","")),
            td(d.get("route","")),
            td(d.get("marketing_status","")),
            td(d.get("application","")),
            td(d.get("product_no","")),
        ])
        for d in (data.get("drugs_approved") or [])
    ) or "<tr><td colspan=4>(none)</td></tr>"

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{esc(data.get('company','IND Intelligence'))}</title>
<style>
:root {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; }}
body {{ margin:0; background:#0b1220; color:#e6edf3; }}
header {{ padding:16px 24px; border-bottom:1px solid #1f2a44; position:sticky; top:0; background:#0b1220; }}
.container {{ padding:24px; display:grid; gap:16px; }}
.card {{ background:#0f172a; border:1px solid #1f2a44; border-radius:14px; padding:16px; }}
.title {{ font-size:20px; margin:0 0 8px; }}
table {{ width:100%; border-collapse: collapse; }}
th, td {{ text-align:left; border-bottom:1px solid #1f2a44; padding:8px; }}
th {{ font-weight:600; }}
.muted {{ color:#a4b1c6; }}
</style></head>
<body>
<header><strong>Investigation New Drug Application</strong></header>
<div class="container">
  <div class="card">
    <h2 class="title">Company</h2>
    <div style="font-size:24px; margin-bottom:8px;">{esc(data.get('company',''))}</div>
  </div>

  <div class="card">
    <h3 class="title">Approved Drugs (OpenFDA)</h3>
    <table><thead><tr><th>Brand</th><th>Ingredient</th><th>Dosage Form</th><th>Route</th><th>Marketing Status</th><th>Application</th><th>Product No</th></tr></thead>
    <tbody>{drugs_rows}</tbody></table>
  </div>
</div>
</body></html>"""

def add_subparser(subparsers: argparse._SubParsersAction, formatter_class: type[argparse.HelpFormatter]=argparse.HelpFormatter) -> None:
    p = subparsers.add_parser(
        "intel",
        help="Retrieve FDA-approved drugs for a company (OpenFDA)",
        description="Search OpenFDA for a company's FDA-approved drugs.",
        formatter_class=formatter_class
    )
    p.add_argument("company", help="Company or sponsor name")
    p.add_argument("--format", choices=["json","table","html"], default="table", help="Output format")
    p.add_argument("-o","--output", type=Path, help="Output file (required for --format html)")
    p.add_argument("--open", dest="auto_open", action="store_true", help="Open HTML output in browser")
    p.set_defaults(func=_run)

def _run(**kwargs) -> None:
    args = argparse.Namespace(**kwargs)
    intel = build_company_intel(args.company).dict()

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