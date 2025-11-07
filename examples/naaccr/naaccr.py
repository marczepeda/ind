from __future__ import annotations

"""
Comprehensive NAACCR API examples

Run me directly, e.g.:

  python examples/naaccr/naaccr.py --version 22 --q cancer --pages 2 --minimize

What this script demonstrates:
  1) Listing NAACCR versions
  2) Searching data items (with paging + optional minimize_results)
  3) Fetching a full data item by ItemNumber or XmlNaaccrId
  4) Fetching attribute history for an item (e.g., Description)
  5) Fetching operation history for an item

The `NAACCRClient` already forces JSON responses and supports the special
`minimize_results="true"` query parameter when requested from endpoints.
"""

from typing import Any, Dict, List, Optional
import argparse
import sys

from ind.naaccr import (
    NAACCRClient,
    list_versions,
    search_data_items,
    get_data_item,
    get_attribute_history,
    get_operation_history,
)

try:
    # Pretty output if available (it's in the project deps)
    from rich.console import Console
    from rich.table import Table
    from rich import print as rprint
except Exception:  # pragma: no cover
    Console = None  # type: ignore
    Table = None  # type: ignore
    def rprint(*args, **kwargs):  # fallback
        print(*args, **kwargs)


def _print_versions(versions: List[Dict[str, Any]]) -> None:
    if Console and Table:
        table = Table(title="NAACCR Versions")
        table.add_column("Version")
        table.add_column("YearImplemented", justify="right")
        table.add_column("DateOfPublication")
        for v in versions:
            table.add_row(
                str(v.get("Version", "")),
                str(v.get("YearImplemented", "")),
                str(v.get("DateOfPublication", "")),
            )
        Console().print(table)
    else:
        rprint("NAACCR Versions:")
        for v in versions:
            rprint(v)


def _print_items(title: str, items: List[Dict[str, Any]], limit: int = 10) -> None:
    rprint(f"[bold]{title}[/bold] (showing up to {limit}): {len(items)} found")
    for i, it in enumerate(items[:limit], start=1):
        rprint(
            f"{i:>3}. ItemNumber={it.get('ItemNumber')}  "
            f"ItemName={it.get('ItemName')}  XmlNaaccrId={it.get('XmlNaaccrId')}"
        )


def _select_id(item: Dict[str, Any]) -> Optional[str]:
    # Prefer ItemNumber if present; otherwise use XmlNaaccrId
    return str(item.get("ItemNumber") or item.get("XmlNaaccrId") or "") or None


def run(
    *,
    naaccr_version: str,
    query: Optional[str],
    minimize: bool,
    pages: int,
    delay: float,
    item_id: Optional[str],
) -> int:
    client = NAACCRClient()

    # 1) Versions
    versions = list_versions(client)
    _print_versions(versions)

    # 2) Search (paged)
    items = search_data_items(
        client,
        naaccr_version,
        q=query,
        minimize_results=minimize,
        pages=pages,
        delay=delay,
    )
    _print_items(
        title=f"Search results for version={naaccr_version!r}, q={query!r}, minimize={minimize}",
        items=items,
        limit=15,
    )

    if not items and not item_id:
        rprint("[yellow]No items returned by search and no explicit item id provided. Exiting.[/yellow]")
        return 0

    # 3) Pick an item (either explicit --item or first search hit) and fetch full record
    chosen_id = item_id or _select_id(items[0])
    if not chosen_id:
        rprint("[red]Could not determine an item identifier (ItemNumber/XmlNaaccrId). Exiting.[/red]")
        return 1

    rprint(f"\n[bold]Fetching full item[/bold] id={chosen_id!r} (version {naaccr_version}) ...")
    full = get_data_item(client, naaccr_version, chosen_id)
    # Print a compact subset
    summary_keys = [
        "ItemNumber",
        "ItemName",
        "ItemLength",
        "YearImplemented",
        "VersionImplemented",
        "XmlNaaccrId",
        "Section",
        "SourceOfStandard",
    ]
    rprint({k: full.get(k) for k in summary_keys})

    # 4) Attribute history (Description is usually present across versions)
    rprint("\n[bold]Attribute history[/bold] (Description):")
    try:
        hist = get_attribute_history(client, chosen_id, attribute="Description")
        for row in hist:
            rprint(f"  - v{row.get('NaaccrVersion')}: {row.get('Value')}")
    except Exception as e:
        rprint(f"[yellow]Attribute history not available: {e}[/yellow]")

    # 5) Operation history for this item in the selected version
    rprint("\n[bold]Operation history[/bold]:")
    try:
        ops = get_operation_history(client, naaccr_version, chosen_id)
        if not ops:
            rprint("  (no operations returned)")
        for op in ops[:25]:
            rprint(
                f"  - {op.get('Operation')} | {op.get('ModifiedAttribute')}: "
                f"{op.get('OldValue')} -> {op.get('NewValue')}"
            )
    except Exception as e:
        rprint(f"[yellow]Operation history not available: {e}[/yellow]")

    rprint("\n[green]Done.[/green]")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Comprehensive NAACCR API examples")
    p.add_argument("--version", default="22", help="NAACCR version to query (e.g., 22)")
    p.add_argument("--q", dest="query", default="cancer", help="Search query (optional)")
    p.add_argument("--pages", type=int, default=1, help="Max number of pages to fetch for search")
    p.add_argument("--minimize", action="store_true", help="Request minimized search results")
    p.add_argument("--delay", type=float, default=0.25, help="Delay between page requests (seconds)")
    p.add_argument("--item", dest="item_id", help="Explicit ItemNumber or XmlNaaccrId to fetch")

    args = p.parse_args(argv)
    return run(
        naaccr_version=str(args.version),
        query=args.query,
        minimize=bool(args.minimize),
        pages=int(args.pages),
        delay=float(args.delay),
        item_id=args.item_id,
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())