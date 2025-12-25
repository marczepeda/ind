from __future__ import annotations
import argparse, json, webbrowser, csv, re
from pathlib import Path
from typing import Literal
import shutil
from .service import build_company_intel
from ind.gen.html import make_html_index
import importlib.resources as pkg_resources
import ind.resources.icon as icon_pkg
from ind.utils import mkdir


def _safe_company(name: str) -> str:
    s = (name or "").strip()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^A-Za-z0-9_\-]+", "", s)
    return s or "company"

def _write_csv_rows(rows: list[dict], output_csv: Path, preferred: list[str]) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    keys: list[str] = []
    seen = set()
    for k in preferred:
        if any(k in (d or {}) for d in rows):
            keys.append(k)
            seen.add(k)
    for d in rows:
        for k in (d or {}).keys():
            if k not in seen:
                keys.append(k)
                seen.add(k)

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for d in rows:
            w.writerow({k: (d.get(k, "") if isinstance(d, dict) else "") for k in keys})


def _write_drugs_csv(drugs: list[dict], output_csv: Path) -> None:
    preferred = [
        "brand_name",
        "active_ingredient",
        "dosage_form",
        "route",
        "marketing_status",
        "application",
        "product_no",
        "approval_date",
        "sponsor",
    ]
    _write_csv_rows(drugs, output_csv, preferred)


def _write_devices_csv(devices: list[dict], output_csv: Path) -> None:
    preferred = [
        "device_type",
        "k_number",
        "pma_number",
        "device_name",
        "trade_name",
        "generic_name",
        "applicant",
        "manufacturer_name",
        "product_code",
        "advisory_committee",
        "clearance_type",
        "decision_code",
        "decision_date",
    ]
    _write_csv_rows(devices, output_csv, preferred)


def _render_html(data: dict, icon_href: str, *, show_drugs: bool = True, show_devices: bool = True) -> str:
    # Minimal standalone HTML (no server). Style kept compact.
    def esc(s):
        return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Build rows with data attributes for client-side filtering
    drugs_rows = "\n".join(
        f"<tr>"
        f"<td data-col='brand_name'>{esc(str(d.get('brand_name','')))}</td>"
        f"<td data-col='active_ingredient'>{esc(str(d.get('active_ingredient','')))}</td>"
        f"<td data-col='dosage_form'>{esc(str(d.get('dosage_form','')))}</td>"
        f"<td data-col='route'>{esc(str(d.get('route','')))}</td>"
        f"<td data-col='marketing_status'>{esc(str(d.get('marketing_status','')))}</td>"
        f"<td data-col='application'>{esc(str(d.get('application','')))}</td>"
        f"<td data-col='product_no'>{esc(str(d.get('product_no','')))}</td>"
        f"</tr>"
        for d in (data.get("drugs_approved") or [])
    ) or "<tr><td colspan=7>(none)</td></tr>"

    devices_510k = data.get("devices_510k") or []
    devices_pma = data.get("devices_pma") or []

    devices_rows_510k = [
        (
            f"<tr>"
            f"<td data-col='device_type'>510k</td>"
            f"<td data-col='k_number'>{esc(str(d.get('k_number','')))}</td>"
            f"<td data-col='pma_number'></td>"
            f"<td data-col='device_name'>{esc(str(d.get('device_name','')))}</td>"
            f"<td data-col='trade_name'></td>"
            f"<td data-col='generic_name'></td>"
            f"<td data-col='applicant'>{esc(str(d.get('applicant','')))}</td>"
            f"<td data-col='manufacturer_name'>{esc(str(d.get('manufacturer_name','')))}</td>"
            f"<td data-col='product_code'>{esc(str(d.get('product_code','')))}</td>"
            f"<td data-col='advisory_committee'>{esc(str(d.get('advisory_committee','')))}</td>"
            f"<td data-col='clearance_type'>{esc(str(d.get('clearance_type','')))}</td>"
            f"<td data-col='decision_code'>{esc(str(d.get('decision_code','')))}</td>"
            f"<td data-col='decision_date'>{esc(str(d.get('decision_date','')))}</td>"
            f"</tr>"
        )
        for d in devices_510k
    ]

    devices_rows_pma = [
        (
            f"<tr>"
            f"<td data-col='device_type'>PMA</td>"
            f"<td data-col='k_number'></td>"
            f"<td data-col='pma_number'>{esc(str(d.get('pma_number','')))}</td>"
            f"<td data-col='device_name'></td>"
            f"<td data-col='trade_name'>{esc(str(d.get('trade_name','')))}</td>"
            f"<td data-col='generic_name'>{esc(str(d.get('generic_name','')))}</td>"
            f"<td data-col='applicant'>{esc(str(d.get('applicant','')))}</td>"
            f"<td data-col='manufacturer_name'>{esc(str(d.get('manufacturer_name','')))}</td>"
            f"<td data-col='product_code'>{esc(str(d.get('product_code','')))}</td>"
            f"<td data-col='advisory_committee'>{esc(str(d.get('advisory_committee','')))}</td>"
            f"<td data-col='clearance_type'></td>"
            f"<td data-col='decision_code'>{esc(str(d.get('decision_code','')))}</td>"
            f"<td data-col='decision_date'>{esc(str(d.get('decision_date','')))}</td>"
            f"</tr>"
        )
        for d in devices_pma
    ]

    devices_rows = "\n".join(devices_rows_510k + devices_rows_pma)
    if not devices_rows:
        devices_rows = "<tr><td colspan=13>(none)</td></tr>"

    company_esc = esc(data.get('company', ''))

    drug_card = """
  <div class="card">
    <h3 class="title">openFDA: Approved Drugs</h3>
    <table id="drugs-table">
      <thead>
        <tr>
          <th data-sort="brand_name" title="Click to sort">Brand</th>
          <th data-sort="active_ingredient" title="Click to sort">Ingredient</th>
          <th data-sort="dosage_form" title="Click to sort">Dosage Form</th>
          <th data-sort="route" title="Click to sort">Route</th>
          <th data-sort="marketing_status" title="Click to sort">Marketing Status</th>
          <th data-sort="application" title="Click to sort">Application</th>
          <th data-sort="product_no" title="Click to sort">Product No</th>
        </tr>
        <tr class="filters">
          <th><select data-filter="brand_name"><option value="">All</option></select></th>
          <th><select data-filter="active_ingredient"><option value="">All</option></select></th>
          <th><select data-filter="dosage_form"><option value="">All</option></select></th>
          <th><select data-filter="route"><option value="">All</option></select></th>
          <th><select data-filter="marketing_status"><option value="">All</option></select></th>
          <th><select data-filter="application"><option value="">All</option></select></th>
          <th><select data-filter="product_no"><option value="">All</option></select></th>
        </tr>
      </thead>
      <tbody>__DRUGS_ROWS__</tbody>
    </table>
  </div>
"""

    device_card = """
  <div class="card">
    <h3 class="title">openFDA: Approved / Cleared Medical Devices</h3>
    <table id="devices-table">
      <thead>
        <tr>
          <th data-sort="device_type" title="Click to sort">Type</th>
          <th data-sort="k_number" title="Click to sort">510(k)</th>
          <th data-sort="pma_number" title="Click to sort">PMA</th>
          <th data-sort="device_name" title="Click to sort">Device Name</th>
          <th data-sort="trade_name" title="Click to sort">Trade Name</th>
          <th data-sort="generic_name" title="Click to sort">Generic Name</th>
          <th data-sort="applicant" title="Click to sort">Applicant</th>
          <th data-sort="manufacturer_name" title="Click to sort">Manufacturer</th>
          <th data-sort="product_code" title="Click to sort">Product Code</th>
          <th data-sort="advisory_committee" title="Click to sort">Advisory</th>
          <th data-sort="clearance_type" title="Click to sort">Clearance</th>
          <th data-sort="decision_code" title="Click to sort">Decision</th>
          <th data-sort="decision_date" title="Click to sort">Decision Date</th>
        </tr>
        <tr class="filters">
          <th><select data-filter="device_type"><option value="">All</option></select></th>
          <th><select data-filter="k_number"><option value="">All</option></select></th>
          <th><select data-filter="pma_number"><option value="">All</option></select></th>
          <th><select data-filter="device_name"><option value="">All</option></select></th>
          <th><select data-filter="trade_name"><option value="">All</option></select></th>
          <th><select data-filter="generic_name"><option value="">All</option></select></th>
          <th><select data-filter="applicant"><option value="">All</option></select></th>
          <th><select data-filter="manufacturer_name"><option value="">All</option></select></th>
          <th><select data-filter="product_code"><option value="">All</option></select></th>
          <th><select data-filter="advisory_committee"><option value="">All</option></select></th>
          <th><select data-filter="clearance_type"><option value="">All</option></select></th>
          <th><select data-filter="decision_code"><option value="">All</option></select></th>
          <th><select data-filter="decision_date"><option value="">All</option></select></th>
        </tr>
      </thead>
      <tbody>__DEVICES_ROWS__</tbody>
    </table>
  </div>
"""

    init_calls = []
    if show_drugs:
        init_calls.append("  initTable('drugs-table');")
    if show_devices:
        init_calls.append("  initTable('devices-table');")

    html_tpl = """<!doctype html>
<html>
  <head>
  <meta charset="utf-8">
  <title>IND __COMPANY__</title>
  <link rel="icon" type="image/svg+xml" href="__ICON_HREF__">
<style>
:root { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; }
body { margin:0; background:#0b1220; color:#e6edf3; }
header { padding:16px 24px; border-bottom:1px solid #1f2a44; position:sticky; top:0; background:#0b1220; }
.container { padding:24px; display:grid; gap:16px; }
.card { background:#0f172a; border:1px solid #1f2a44; border-radius:14px; padding:16px; }
.title { font-size:20px; margin:0 0 8px; }
table { width:100%; border-collapse: collapse; }
th, td { text-align:left; border-bottom:1px solid #1f2a44; padding:8px; }
th { font-weight:600; }
th[data-sort] { cursor: pointer; user-select: none; }
th[data-sort]::after { content: ' ↕'; font-weight: 400; color: #a4b1c6; }
th.sorted-asc::after { content: ' ↑'; }
th.sorted-desc::after { content: ' ↓'; }
tr.filters th { padding-top: 6px; padding-bottom: 10px; }
tr.filters select {
  width: 100%;
  background: #0b1220;
  color: #e6edf3;
  border: 1px solid #1f2a44;
  border-radius: 10px;
  padding: 6px 8px;
}
</style></head>
<body>
<header><strong>IND __COMPANY__</strong></header>
<div class="container">
__DRUG_CARD____DEVICE_CARD__
</div>
<script>
(function() {
  function initTable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const tbody = table.querySelector('tbody');
    const filterSelects = Array.from(table.querySelectorAll('select[data-filter]'));
    const headers = Array.from(table.querySelectorAll('th[data-sort]'));

    function getCellText(row, col) {
      const cell = row.querySelector(`td[data-col="${col}"]`);
      return cell ? (cell.textContent || '').trim() : '';
    }

    function uniqueSorted(values) {
      const set = new Set(values.filter(v => v !== ''));
      return Array.from(set).sort((a,b) => a.localeCompare(b, undefined, {numeric:true, sensitivity:'base'}));
    }

    function getActiveFilters(uptoIndexExclusive) {
      const active = {};
      filterSelects.forEach((sel, idx) => {
        if (idx >= uptoIndexExclusive) return;
        const col = sel.getAttribute('data-filter');
        const val = (sel.value || '').trim();
        if (val !== '') active[col] = val;
      });
      return active;
    }

    function rowMatchesActive(row, active) {
      for (const [col, val] of Object.entries(active)) {
        if (getCellText(row, col) !== val) return false;
      }
      return true;
    }

    function applyFilters() {
      const active = {};
      filterSelects.forEach(sel => {
        const col = sel.getAttribute('data-filter');
        const val = (sel.value || '').trim();
        if (val !== '') active[col] = val;
      });

      const rows = Array.from(tbody.querySelectorAll('tr'));
      rows.forEach(row => {
        if (row.children.length === 1 && row.textContent.includes('(none)')) {
          row.style.display = '';
          return;
        }
        row.style.display = rowMatchesActive(row, active) ? '' : 'none';
      });
    }

    function updateCascadingFilters() {
      const allRows = Array.from(tbody.querySelectorAll('tr'));
      const dataRows = allRows.filter(r => !(r.children.length === 1 && r.textContent.includes('(none)')));

      filterSelects.forEach((sel, idx) => {
        const col = sel.getAttribute('data-filter');
        const prevActive = getActiveFilters(idx);
        const eligibleRows = dataRows.filter(r => rowMatchesActive(r, prevActive));
        const vals = eligibleRows.map(r => getCellText(r, col));
        const uniques = uniqueSorted(vals);

        const current = (sel.value || '').trim();
        while (sel.options.length > 1) sel.remove(1);
        uniques.forEach(v => {
          const opt = document.createElement('option');
          opt.value = v;
          opt.textContent = v;
          sel.appendChild(opt);
        });

        if (current !== '' && !uniques.includes(current)) {
          sel.value = '';
        } else {
          sel.value = current;
        }
      });

      applyFilters();
    }

    filterSelects.forEach(sel => {
      sel.addEventListener('change', () => {
        updateCascadingFilters();
      });
    });

    let sortState = { col: null, dir: 'asc' };

    function clearHeaderIndicators() {
      headers.forEach(h => h.classList.remove('sorted-asc', 'sorted-desc'));
    }

    function sortRows(col, dir) {
      const rows = Array.from(tbody.querySelectorAll('tr'))
        .filter(r => !(r.children.length === 1 && r.textContent.includes('(none)')));

      rows.sort((ra, rb) => {
        const a = getCellText(ra, col);
        const b = getCellText(rb, col);
        const cmp = a.localeCompare(b, undefined, {numeric:true, sensitivity:'base'});
        return dir === 'asc' ? cmp : -cmp;
      });

      rows.forEach(r => tbody.appendChild(r));
    }

    headers.forEach(h => {
      h.addEventListener('click', () => {
        const col = h.getAttribute('data-sort');
        if (!col) return;

        const nextDir = (sortState.col === col && sortState.dir === 'asc') ? 'desc' : 'asc';
        sortState = { col, dir: nextDir };

        clearHeaderIndicators();
        h.classList.add(nextDir === 'asc' ? 'sorted-asc' : 'sorted-desc');

        sortRows(col, nextDir);
        updateCascadingFilters();
      });
    });

    updateCascadingFilters();
  }

__INIT_CALLS__
})();
</script>
</body></html>
"""

    return (
        html_tpl
        .replace("__COMPANY__", company_esc)
        .replace("__ICON_HREF__", esc(icon_href))
        .replace("__DRUG_CARD__", drug_card if show_drugs else "")
        .replace("__DEVICE_CARD__", device_card if show_devices else "")
        .replace("__DRUGS_ROWS__", drugs_rows)
        .replace("__DEVICES_ROWS__", devices_rows)
        .replace("__INIT_CALLS__", "\n".join(init_calls))
    )

def add_subparser(subparsers: argparse._SubParsersAction, formatter_class: type[argparse.HelpFormatter]=argparse.HelpFormatter) -> None:
    p = subparsers.add_parser(
        "intel",
        help="Retrieve FDA-approved drugs for a company (OpenFDA)",
        description="Search OpenFDA for a company's FDA-approved drugs.",
        formatter_class=formatter_class
    )
    p.add_argument("company", help="Company or sponsor name")
    p.add_argument(
        "-o",
        "--out_dir",
        type=Path,
        default=Path("."),
        help="Output directory (default: working directory)",
    )
    p.add_argument(
        "--html-name",
        type=str,
        default=None,
        help="HTML filename (default: <company>.html)",
    )
    p.add_argument("--open", dest="auto_open", action="store_true", help="Open HTML output in browser")
    p.set_defaults(func=_run)

def _run(**kwargs) -> None:
    args = argparse.Namespace(**kwargs)
    intel = build_company_intel(args.company).dict()

    company_dirname = _safe_company(intel.get("company") or args.company)
    out_dir: Path = (args.out_dir or Path(".")).resolve()

    # Data outputs go into a subfolder named after the company
    data_dir = out_dir / company_dirname

    drug_dir = data_dir / "Drug"
    device_dir = data_dir / "Device"

    approved_drug_dir = drug_dir / "Approved"
    approved_device_dir = device_dir / "Approved"
    mkdir(approved_drug_dir)
    mkdir(approved_device_dir)
    
    drugs_csv_path = approved_drug_dir / f"Approved.csv"
    drugs_json_path = approved_drug_dir / f"Approved.json"

    devices_csv_path = approved_device_dir / f"Approved.csv"
    devices_json_path = approved_device_dir / f"Approved.json"

    html_filename = args.html_name or f"{company_dirname}.html"
    drug_html_path = drug_dir / "Approved.html"
    device_html_path = device_dir / "Approved.html"

    # Ensure the icon exists in both drug/device subfolders and link to it from the HTML
    with pkg_resources.path(icon_pkg, "fda.svg") as svg_path:
        shutil.copy(svg_path, approved_drug_dir / "fda.svg")
        shutil.copy(svg_path, approved_device_dir / "fda.svg")
    

    # Always write JSON, CSV, and HTML
    drug_json = {"company": intel.get("company", args.company), "drugs_approved": intel.get("drugs_approved") or []}
    device_json = {
        "company": intel.get("company", args.company),
        "devices_510k": intel.get("devices_510k") or [],
        "devices_pma": intel.get("devices_pma") or [],
    }
    drugs_json_path.write_text(json.dumps(drug_json, indent=2), encoding="utf-8")
    devices_json_path.write_text(json.dumps(device_json, indent=2), encoding="utf-8")
    _write_drugs_csv(intel.get("drugs_approved") or [], drugs_csv_path)

    devices_combined: list[dict] = []
    for d in (intel.get("devices_510k") or []):
        dd = dict(d)
        dd.setdefault("device_type", "510k")
        devices_combined.append(dd)
    for d in (intel.get("devices_pma") or []):
        dd = dict(d)
        dd.setdefault("device_type", "PMA")
        devices_combined.append(dd)

    _write_devices_csv(devices_combined, devices_csv_path)

    drug_html = _render_html(intel, icon_href=str(approved_drug_dir / "fda.svg"), show_drugs=True, show_devices=False)
    device_html = _render_html(intel, icon_href=str(approved_device_dir / "fda.svg"), show_drugs=False, show_devices=True)
    drug_html_path.write_text(drug_html, encoding="utf-8")
    device_html_path.write_text(device_html, encoding="utf-8")

    # Create a per-company HTML index that previews all generated HTML in subfolders
    company_index_path = make_html_index(
        dir=data_dir,
        file=html_filename,
        recursive=True,
        exclude=(html_filename,),
        sort="title",
        label="stem",
        preview=True,
        grid_cols=5,
        icon="python",
    )

    print(f"Wrote {drugs_csv_path}")
    print(f"Wrote {drugs_json_path}")
    print(f"Wrote {drug_html_path}")

    print(f"Wrote {devices_csv_path}")
    print(f"Wrote {devices_json_path}")
    print(f"Wrote {device_html_path}")
    print(f"Wrote {company_index_path}")

    if args.auto_open:
        webbrowser.open(company_index_path.resolve().as_uri())