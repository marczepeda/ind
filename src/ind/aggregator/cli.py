from __future__ import annotations
import argparse, json, webbrowser, re
from pathlib import Path
import shutil
import importlib.resources as pkg_resources

# Within package
import ind.resources.icon as icon_pkg
from ..utils import mkdir
from ..gen.html import make_html_index

# Within module
from .orchrestator import build_company_intel

## Render
from .render.csv import (_write_drugs_csv, _write_ndc_csv, _write_adverse_events_csv, _write_enforcements_csv, _write_labels_csv, _write_shortages_csv, 
                         _write_devices_csv, _write_device_events_csv, _write_device_enforcements_csv, _write_device_recalls_csv, _write_device_registrationlisting_csv, _write_transparency_crl_csv)
from .render.html import _render_html

def _safe_company(name: str) -> str:
    s = (name or "").strip()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^A-Za-z0-9_\-]+", "", s)
    return s or "company"

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

    # Create company directory and subdirectories
    ## Company level
    data_dir = out_dir / company_dirname

    ## Category level
    drug_dir = data_dir / "Drug"
    device_dir = data_dir / "Device"
    transparency_dir = data_dir / "Transparency"
    
    ## Endpoint level
    drug_approved_dir = drug_dir / "Approved"
    drug_ndc_dir = drug_dir / "NDC Directory"
    drug_adverse_dir = drug_dir / "Adverse Events"
    drug_enforcement_dir = drug_dir / "Enforcement"
    drug_labeling_dir = drug_dir / "Labeling"
    drug_shortages_dir = drug_dir / "Shortages"

    device_approved_dir = device_dir / "Approved"
    device_adverse_dir = device_dir / "Adverse Events"
    device_enforcement_dir = device_dir / "Enforcement"
    device_recalls_dir = device_dir / "Recalls"
    device_registrationlisting_dir = device_dir / "Registration Listing"

    crl_dir = transparency_dir / "Complete Response Letters"
    
    mkdir(drug_approved_dir)
    mkdir(drug_ndc_dir)
    mkdir(drug_adverse_dir)
    mkdir(drug_enforcement_dir)
    mkdir(drug_labeling_dir)
    mkdir(drug_shortages_dir)

    mkdir(device_approved_dir)
    mkdir(device_adverse_dir)
    mkdir(device_enforcement_dir)
    mkdir(device_recalls_dir)
    mkdir(device_registrationlisting_dir)

    mkdir(crl_dir)

    # File paths
    ## Company level
    html_filename = args.html_name or f"{company_dirname}.html"
    
    ## Category/endpoint levels
    drug_approved_html_path = drug_dir / "Approved.html"
    drug_approved_csv_path = drug_approved_dir / f"Approved.csv"
    drug_approved_json_path = drug_approved_dir / f"Approved.json"

    drug_ndc_html_path = drug_dir / "NDC Directory.html"
    drug_ndc_csv_path = drug_ndc_dir / "NDC Directory.csv"
    drug_ndc_json_path = drug_ndc_dir / "NDC Directory.json"

    drug_adverse_html_path = drug_dir / "Adverse Events.html"
    drug_adverse_csv_path = drug_adverse_dir / "Adverse Events.csv"
    drug_adverse_json_path = drug_adverse_dir / "Adverse Events.json"

    drug_enforcement_html_path = drug_dir / "Enforcement.html"
    drug_enforcement_csv_path = drug_enforcement_dir / "Enforcement.csv"
    drug_enforcement_json_path = drug_enforcement_dir / "Enforcement.json"

    drug_labeling_html_path = drug_dir / "Labeling.html"
    drug_labeling_csv_path = drug_labeling_dir / "Labeling.csv"
    drug_labeling_json_path = drug_labeling_dir / "Labeling.json"
    
    drug_shortages_html_path = drug_dir / "Shortages.html"
    drug_shortages_csv_path = drug_shortages_dir / "Shortages.csv"
    drug_shortages_json_path = drug_shortages_dir / "Shortages.json"

    device_approved_html_path = device_dir / "Approved.html"
    device_approved_csv_path = device_approved_dir / f"Approved.csv"
    device_approved_json_path = device_approved_dir / f"Approved.json"
    
    device_adverse_html_path = device_dir / "Adverse Events.html"
    device_adverse_csv_path = device_adverse_dir / "Adverse Events.csv"
    device_adverse_json_path = device_adverse_dir / "Adverse Events.json"

    device_enforcement_html_path = device_dir / "Enforcement.html"
    device_enforcement_csv_path = device_enforcement_dir / "Enforcement.csv"
    device_enforcement_json_path = device_enforcement_dir / "Enforcement.json"

    device_recalls_html_path = device_dir / "Recalls.html"
    device_recalls_csv_path = device_recalls_dir / "Recalls.csv"
    device_recalls_json_path = device_recalls_dir / "Recalls.json"

    device_registrationlisting_html_path = device_dir / "Registration Listing.html"
    device_registrationlisting_csv_path = device_registrationlisting_dir / "Registration Listing.csv"
    device_registrationlisting_json_path = device_registrationlisting_dir / "Registration Listing.json"

    crl_html_path = transparency_dir / "Complete Response Letters.html"
    crl_csv_path = crl_dir / "Complete Response Letters.csv"
    crl_json_path = crl_dir / "Complete Response Letters.json"
    
    # Ensure the icon exists in both drug/device subfolders and link to it from the HTML
    with pkg_resources.path(icon_pkg, "fda.svg") as svg_path:
        shutil.copy(svg_path, drug_approved_dir / "fda.svg")
        shutil.copy(svg_path, drug_ndc_dir / "fda.svg")
        shutil.copy(svg_path, drug_adverse_dir / "fda.svg")
        shutil.copy(svg_path, drug_enforcement_dir / "fda.svg")
        shutil.copy(svg_path, drug_labeling_dir / "fda.svg")
        shutil.copy(svg_path, drug_shortages_dir / "fda.svg")
        shutil.copy(svg_path, device_approved_dir / "fda.svg")
        shutil.copy(svg_path, device_adverse_dir / "fda.svg")
        shutil.copy(svg_path, device_enforcement_dir / "fda.svg")
        shutil.copy(svg_path, device_recalls_dir / "fda.svg")
        shutil.copy(svg_path, device_registrationlisting_dir / "fda.svg")
        shutil.copy(svg_path, crl_dir / "fda.svg")

    # Write JSON, CSV, and HTML
    ## Drug
    ### Approved
    drug_approved_json = {
        "company": intel.get("company", args.company),
        "drugs_approved": intel.get("drugs_approved") or []
    }
    drug_approved_json_path.write_text(json.dumps(drug_approved_json, indent=2), encoding="utf-8")
    _write_drugs_csv(intel.get("drugs_approved") or [], drug_approved_csv_path)
    drug_approved_html = _render_html(intel, icon_href=str(drug_approved_dir / "fda.svg"), show_drug_approved=True)
    drug_approved_html_path.write_text(drug_approved_html, encoding="utf-8")

    ### NDC Directory
    drug_ndc_json = {
        "company": intel.get("company", args.company),
        "ndc_directory": intel.get("ndc_directory") or []
    }
    drug_ndc_json_path.write_text(json.dumps(drug_ndc_json, indent=2), encoding="utf-8")
    _write_ndc_csv(intel.get("ndc_directory") or [], drug_ndc_csv_path)
    drug_ndc_html = _render_html(intel, icon_href=str(drug_ndc_dir / "fda.svg"), show_drug_ndc=True)
    drug_ndc_html_path.write_text(drug_ndc_html, encoding="utf-8")

    ### Adverse Events
    drug_adverse_json = {
        "company": intel.get("company", args.company),
        "drug_adverse_events": intel.get("drug_adverse_events") or [],
    }
    drug_adverse_json_path.write_text(json.dumps(drug_adverse_json, indent=2), encoding="utf-8")
    _write_adverse_events_csv(intel.get("drug_adverse_events") or [], drug_adverse_csv_path)
    drug_adverse_html = _render_html(
        intel,
        icon_href=str(drug_adverse_dir / "fda.svg"),
        show_drug_adverse_events=True,
    )
    drug_adverse_html_path.write_text(drug_adverse_html, encoding="utf-8")

    ### Enforcement
    drug_enforcement_json = {
        "company": intel.get("company", args.company),
        "drug_enforcements": intel.get("drug_enforcements") or [],
    }
    drug_enforcement_json_path.write_text(json.dumps(drug_enforcement_json, indent=2), encoding="utf-8")
    _write_enforcements_csv(intel.get("drug_enforcements") or [], drug_enforcement_csv_path)
    drug_enforcement_html = _render_html(
        intel,
        icon_href=str(drug_enforcement_dir / "fda.svg"),
        show_drug_enforcements=True,
    )
    drug_enforcement_html_path.write_text(drug_enforcement_html, encoding="utf-8")

    ### Labels
    drug_labeling_json = {
        "company": intel.get("company", args.company),
        "drug_labels": intel.get("drug_labels") or [],
    }
    drug_labeling_json_path.write_text(json.dumps(drug_labeling_json, indent=2), encoding="utf-8")
    _write_labels_csv(intel.get("drug_labels") or [], drug_labeling_csv_path)
    drug_labeling_html = _render_html(
        intel,
        icon_href=str(drug_labeling_dir / "fda.svg"),
        show_drug_labels=True,
    )
    drug_labeling_html_path.write_text(drug_labeling_html, encoding="utf-8")

    ### Shortages
    drug_shortages_json = {
        "company": intel.get("company", args.company),
        "drug_shortages": intel.get("drug_shortages") or [],
    }
    drug_shortages_json_path.write_text(json.dumps(drug_shortages_json, indent=2), encoding="utf-8")
    _write_shortages_csv(intel.get("drug_shortages") or [], drug_shortages_csv_path)
    drug_shortages_html = _render_html(
        intel,
        icon_href=str(drug_shortages_dir / "fda.svg"),
        show_drug_shortages=True,
    )
    drug_shortages_html_path.write_text(drug_shortages_html, encoding="utf-8")

    ## Device
    ### Approved
    device_json = {
        "company": intel.get("company", args.company),
        "devices_510k": intel.get("devices_510k") or [],
        "devices_pma": intel.get("devices_pma") or [],
    }
    device_approved_json_path.write_text(json.dumps(device_json, indent=2), encoding="utf-8")

    device_combined: list[dict] = []
    for d in (intel.get("devices_510k") or []):
        dd = dict(d)
        dd.setdefault("device_type", "510k")
        device_combined.append(dd)
    for d in (intel.get("devices_pma") or []):
        dd = dict(d)
        dd.setdefault("device_type", "PMA")
        device_combined.append(dd)

    _write_devices_csv(device_combined, device_approved_csv_path)
    device_approved_html = _render_html(intel, icon_href=str(device_approved_dir / "fda.svg"), show_device_approved=True)
    device_approved_html_path.write_text(device_approved_html, encoding="utf-8")

    ### Adverse Events
    device_adverse_json = {
        "company": intel.get("company", args.company),
        "device_adverse_events": intel.get("device_adverse_events") or [],
    }
    device_adverse_json_path.write_text(json.dumps(device_adverse_json, indent=2), encoding="utf-8")
    _write_device_events_csv(intel.get("device_adverse_events") or [], device_adverse_csv_path)
    device_adverse_html = _render_html(
        intel,
        icon_href=str(device_adverse_dir / "fda.svg"),
        show_device_adverse_events=True,
    )
    device_adverse_html_path.write_text(device_adverse_html, encoding="utf-8")

    ### Enforcement
    device_enforcement_json = {
        "company": intel.get("company", args.company),
        "device_enforcements": intel.get("device_enforcements") or [],
    }
    device_enforcement_json_path.write_text(json.dumps(device_enforcement_json, indent=2), encoding="utf-8")
    _write_device_enforcements_csv(intel.get("device_enforcements") or [], device_enforcement_csv_path)
    device_enforcement_html = _render_html(
        intel,
        icon_href=str(device_enforcement_dir / "fda.svg"),
        show_device_enforcements=True,
    )
    device_enforcement_html_path.write_text(device_enforcement_html, encoding="utf-8")  

    ### Recalls
    device_recalls_json = {
        "company": intel.get("company", args.company),
        "device_recalls": intel.get("device_recalls") or [],
    }
    device_recalls_json_path.write_text(json.dumps(device_recalls_json, indent=2), encoding="utf-8")
    _write_device_recalls_csv(intel.get("device_recalls") or [], device_recalls_csv_path)
    device_recalls_html = _render_html(
        intel,
        icon_href=str(device_recalls_dir / "fda.svg"),
        show_device_recalls=True,
    )
    device_recalls_html_path.write_text(device_recalls_html, encoding="utf-8")

    ### Registration Listing
    device_registrationlisting_json = {
        "company": intel.get("company", args.company),
        "device_registration_listing": intel.get("device_registration_listing") or [],
    }
    device_registrationlisting_json_path.write_text(json.dumps(device_registrationlisting_json, indent=2), encoding="utf-8")
    _write_device_registrationlisting_csv(intel.get("device_registration_listing") or [], device_registrationlisting_csv_path)
    device_registrationlisting_html = _render_html(
        intel,
        icon_href=str(device_registrationlisting_dir / "fda.svg"),
        show_device_registrationlisting=True,
    )
    device_registrationlisting_html_path.write_text(device_registrationlisting_html, encoding="utf-8")

    ## Transparency CRL
    crl_json = {
        "company": intel.get("company", args.company),
        "transparency_crl": intel.get("transparency_crl") or [],
    }
    crl_json_path.write_text(json.dumps(crl_json, indent=2), encoding="utf-8")
    _write_transparency_crl_csv(intel.get("transparency_crl") or [], crl_csv_path)

    crl_html = _render_html(
        intel,
        icon_href=str(crl_dir / "fda.svg"),
        show_transparency_crl=True,
    )
    crl_html_path.write_text(crl_html, encoding="utf-8")

    # Create a per-company HTML index that previews all generated HTML in subdirectories
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

    # Print summary
    print(f"Wrote {drug_approved_csv_path}")
    print(f"Wrote {drug_approved_json_path}")
    print(f"Wrote {drug_approved_html_path}")

    print(f"Wrote {drug_ndc_csv_path}")
    print(f"Wrote {drug_ndc_json_path}")
    print(f"Wrote {drug_ndc_html_path}")

    print(f"Wrote {drug_adverse_csv_path}")
    print(f"Wrote {drug_adverse_json_path}")
    print(f"Wrote {drug_adverse_html_path}")

    print(f"Wrote {drug_enforcement_csv_path}")
    print(f"Wrote {drug_enforcement_json_path}")
    print(f"Wrote {drug_enforcement_html_path}")

    print(f"Wrote {drug_labeling_csv_path}")
    print(f"Wrote {drug_labeling_json_path}")
    print(f"Wrote {drug_labeling_html_path}")

    print(f"Wrote {drug_shortages_csv_path}")
    print(f"Wrote {drug_shortages_json_path}")
    print(f"Wrote {drug_shortages_html_path}")

    print(f"Wrote {device_approved_csv_path}")
    print(f"Wrote {device_approved_json_path}")
    print(f"Wrote {device_approved_html_path}")

    print(f"Wrote {device_adverse_csv_path}")
    print(f"Wrote {device_adverse_json_path}")
    print(f"Wrote {device_adverse_html_path}")

    print(f"Wrote {device_enforcement_csv_path}")
    print(f"Wrote {device_enforcement_json_path}")
    print(f"Wrote {device_enforcement_html_path}")

    print(f"Wrote {device_recalls_csv_path}")
    print(f"Wrote {device_recalls_json_path}")
    print(f"Wrote {device_recalls_html_path}")

    print(f"Wrote {device_registrationlisting_csv_path}")
    print(f"Wrote {device_registrationlisting_json_path}")
    print(f"Wrote {device_registrationlisting_html_path}")

    print(f"Wrote {crl_csv_path}")
    print(f"Wrote {crl_json_path}")
    print(f"Wrote {crl_html_path}")

    print(f"Wrote {company_index_path}")

    if args.auto_open:
        webbrowser.open(company_index_path.resolve().as_uri())