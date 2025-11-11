from __future__ import annotations

from typing import Any, Dict, Optional
import argparse

from .client import NAACCRClient
from .endpoints import (
    list_versions,
    search_data_items,
    get_data_item,
    get_attribute_history,
    get_operation_history,
)

try:
    from rich import print as rprint
    from rich.table import Table
    from rich.console import Console
except Exception:  # pragma: no cover
    def rprint(*args, **kwargs): print(*args, **kwargs)  # type: ignore
    Table = None  # type: ignore
    Console = None  # type: ignore


def _print_versions(rows):
    if Table and Console:
        t = Table(title="NAACCR Versions")
        t.add_column("Version")
        t.add_column("YearImplemented")
        t.add_column("DateOfPublication")
        for v in rows:
            t.add_row(
                str(v.get("Version", "")),
                str(v.get("YearImplemented", "")),
                str(v.get("DateOfPublication", "")),
            )
        Console().print(t)
    else:
        rprint(rows)


def _print_items(rows, limit: int = 25):
    rprint(f"[bold]Items[/bold] (showing up to {limit}; total {len(rows)}):")
    for i, it in enumerate(rows[:limit], start=1):
        rprint(
            f"{i:>3}. ItemNumber={it.get('ItemNumber')}  "
            f"ItemName={it.get('ItemName')}  XmlNaaccrId={it.get('XmlNaaccrId')}"
        )


def _choose_id(rec: Dict[str, Any]) -> Optional[str]:
    return (rec.get("ItemNumber") or rec.get("XmlNaaccrId") or None) and str(
        rec.get("ItemNumber") or rec.get("XmlNaaccrId")
    )


def add_subparser(subparsers: argparse._SubParsersAction, formatter_class) -> None:
    parser = subparsers.add_parser(
        "naaccr",
        help="NAACCR Data Dictionary tools",
        description="Interact with the NAACCR Data Dictionary API",
        formatter_class=formatter_class,
    )
    sub = parser.add_subparsers(dest="naaccr_cmd")

    # naaccr versions
    p_versions = sub.add_parser("versions", help="List NAACCR versions", formatter_class=formatter_class)
    p_versions.set_defaults(func=_cmd_versions)

    # naaccr search
    p_search = sub.add_parser("search", help="Search data items", formatter_class=formatter_class)
    p_search.add_argument("--version", required=True, help="NAACCR version (e.g., 22)")
    p_search.add_argument("--q", help="Search term (optional)")
    p_search.add_argument("--minimize", action="store_true", help='Use minimize_results="true"')
    p_search.add_argument("--pages", type=int, default=1, help="Max pages to fetch")
    p_search.add_argument("--delay", type=float, default=0.25, help="Delay between page requests (sec)")
    p_search.set_defaults(func=_cmd_search)

    # naaccr item
    p_item = sub.add_parser("item", help="Get a single data item", formatter_class=formatter_class)
    p_item.add_argument("--version", required=True, help="NAACCR version (e.g., 22)")
    p_item.add_argument("--id", required=True, help="ItemNumber or XmlNaaccrId")
    p_item.set_defaults(func=_cmd_item)

    # naaccr attr-history
    p_attr = sub.add_parser("attr-history", help="Get attribute history for an item", formatter_class=formatter_class)
    p_attr.add_argument("--id", required=True, help="ItemNumber or XmlNaaccrId")
    p_attr.add_argument("--attribute", required=True, help="Attribute to query (e.g., ItemLength)")
    p_attr.set_defaults(func=_cmd_attr_history)

    # naaccr op-history
    p_ops = sub.add_parser("op-history", help="Get operation history for an item in a version", formatter_class=formatter_class)
    p_ops.add_argument("--version", required=True, help="NAACCR version (e.g., 22)")
    p_ops.add_argument("--id", required=True, help="ItemNumber or XmlNaaccrId")
    p_ops.set_defaults(func=_cmd_op_history)

    parser.set_defaults(func=lambda _: parser.print_help())


def run(args: argparse.Namespace) -> int:
    # Dispatch to the chosen subcommand
    if hasattr(args, "func"):
        return args.func(args)
    rprint("[yellow]Choose a NAACCR subcommand (versions|search|item|attr-history|op-history).[/yellow]")
    return 1


# -------------------------
# Command implementations
# -------------------------

def _cmd_versions(args: argparse.Namespace) -> int:
    client = NAACCRClient()
    rows = list_versions(client)
    _print_versions(rows)
    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    client = NAACCRClient()
    rows = search_data_items(
        client,
        args.version,
        q=args.q,
        minimize_results=bool(args.minimize),
        pages=int(args.pages),
        delay=float(args.delay),
    )
    _print_items(rows)
    return 0


def _cmd_item(args: argparse.Namespace) -> int:
    client = NAACCRClient()
    rec = get_data_item(client, args.version, args.id)
    # print a compact subset, but keep full dict visible
    to_show = {k: rec.get(k) for k in [
        "ItemNumber", "ItemName", "ItemLength", "YearImplemented",
        "VersionImplemented", "XmlNaaccrId", "Section", "SourceOfStandard"
    ]}
    rprint(to_show)
    return 0


def _cmd_attr_history(args: argparse.Namespace) -> int:
    client = NAACCRClient()
    hist = get_attribute_history(client, args.id, attribute=args.attribute)
    if not hist:
        rprint("(no attribute history returned)")
        return 0
    for row in hist:
        rprint(f"v{row.get('NaaccrVersion')}: {row.get('Value')}")
    return 0


def _cmd_op_history(args: argparse.Namespace) -> int:
    client = NAACCRClient()
    ops = get_operation_history(client, args.version, args.id)
    if not ops:
        rprint("(no operation history returned)")
        return 0
    for op in ops:
        rprint(f"{op.get('Operation')} | {op.get('ModifiedAttribute')}: {op.get('OldValue')} -> {op.get('NewValue')}")
    return 0