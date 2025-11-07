from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import Dict, Iterable, Union, Optional
from rich import print as rprint
from .client import PubChemClient
from .http import pug_fetch

def _parse_keyvals(items: Iterable[str]) -> Dict[str, Union[str,int,float,bool]]:
    out: Dict[str, Union[str,int,float,bool]] = {}
    for raw in items or []:
        if "=" not in raw:
            raise argparse.ArgumentTypeError(f"Expected key=value, got: {raw}")
        k, v = raw.split("=", 1)
        out[k.strip()] = v.strip()
    return out

def _print_to_stdout(resp) -> None:
    ctype = (resp.headers.get("Content-Type") or "").lower()
    text_like = any(tok in ctype for tok in ("json","xml","csv","text","javascript"))
    if text_like:
        print(resp.text)
    else:
        sys.stdout.buffer.write(resp.content)

def run_pubchem(args: argparse.Namespace) -> int:
    client = PubChemClient(timeout=args.timeout, max_rps=args.max_rps, max_retries=args.retries)
    resp = pug_fetch(
        client,
        input_specification=args.input_spec,
        operation_specification=args.operation_spec,
        output_specification=args.output_spec,
        operation_options=_parse_keyvals(args.opt),
        method=args.method,
        accept=args.accept,
        post_params=_parse_keyvals(args.post),
        files=None,  # can add file support as needed
        content_type=args.content_type,
        data=None,
        output_file=args.output,
        quiet=args.quiet,
        raise_for_status=not args.no_raise,
    )
    if not args.output and not args.quiet:
        _print_to_stdout(resp)
    return 0

def add_subparser(subparsers: argparse._SubParsersAction, formatter_class: argparse.ArgumentParser) -> None:
    p = subparsers.add_parser(
        "pubchem",
        help="Query PubChem PUG REST",
        description="https://pubchem.ncbi.nlm.nih.gov/rest/pug/<input>/<operation>/<output>[?options]",
        formatter_class=formatter_class,
    )
    p.add_argument("input_spec", help="<input specification> = <domain>/<namespace>/<identifiers>; see details below")
    p.add_argument("operation_spec", nargs="?", default=None,help="<operation specification> = compound domain/substance domain/assay domain/gene domain/protein domain/pathway domain/taxonomy domain/cell domain; see details below")
    p.add_argument("output_spec", nargs="?", default=None, help="<output specification> = XML | ASNT | ASNB | JSON | JSONP [ ?callback=<callback name> ] | SDF | CSV | PNG | TXT")
    p.add_argument("--opt", action="append", default=[], metavar="key=value")
    p.add_argument("--method", default="GET", choices=["GET","POST"])
    p.add_argument("--accept")
    p.add_argument("--content-type")
    p.add_argument("--timeout", type=float, default=60.0)
    p.add_argument("--max-rps", type=float, default=5.0)
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("-o","--output")
    p.add_argument("-q","--quiet", action="store_true")
    p.add_argument("--no-raise", action="store_true")
    p.set_defaults(func=run_pubchem)

    # Help message for ind pe prime_designer because input file format can't be captured as block text by Myformatter(RichHelpFormatter):
    if any(["ind" in argv for argv in sys.argv]) and "pubchem" in sys.argv and ("--help" in sys.argv or "-h" in sys.argv):
        p.print_help()
        rprint("""[red]
Details:[/red]
  [cyan]--input_spec[/cyan] [dark_magenta]INPUT_SPEC[/dark_magenta]
  [blue]<input specification> = <domain>/<namespace>/<identifiers>
      <domain> = substance | compound | assay | gene | protein | pathway | taxonomy | cell | <other inputs>
          <other inputs> = sources / [substance, assay] | sourcetable | conformers | annotations/[sourcename/<source name> | heading/<heading>] | classification | standardize | periodictable
      compound domain <namespace> = cid | name | smiles | inchi | sdf | inchikey | formula | <structure search> | <xref> | <mass> | listkey | <fast search>
          <structure search> = { substructure | superstructure | similarity | identity } / { smiles | inchi | sdf | cid}
          <fast search> = { fastidentity | fastsimilarity_2d | fastsimilarity_3d | fastsubstructure | fastsuperstructure } / { smiles | smarts | inchi | sdf | cid } | fastformula
          <xref> = xref / { RegistryID | RN | PubMedID | MMDBID | ProteinGI | NucleotideGI | TaxonomyID | MIMID | GeneID | ProbeID | PatentID }
          <mass> = { molecular_weight | exact_mass | monoisotopic_mass } / { equals | range } / value_1 { / value 2 }
      substance domain <namespace> = sid | sourceid/<source id> | sourceall/<source name> | name | <xref> | listkey
          <source name> = any valid PubChem depositor name
          <xref> = xref / { RegistryID | RN | PubMedID | MMDBID | ProteinGI | NucleotideGI | TaxonomyID | MIMID | GeneID | ProbeID | PatentID }
      assay domain <namespace> = aid | listkey | type/<assay type> | sourceall/<source name> | target/<assay target> | activity/<activity column name>
          <assay type> = all | confirmatory | doseresponse | onhold | panel | rnai | screening | summary | cellbased | biochemical | invivo | invitro | activeconcentrationspecified
          <assay target> = gi | proteinname | geneid | genesymbol | accession
      gene domain <namespace> = geneid | genesymbol | synonym
      protein domain <namespace> = accession | gi | synonym
      pathway domain <namespace> = pwacc
      taxonomy domain <namespace> = taxid | synonym
      cell domain <namespace> = cellacc | synonym
  <identifiers> = comma-separated list of positive integers (e.g. cid, sid, aid) or identifier strings (source, inchikey, formula); in some cases only a single identifier string (name, smiles, xref; inchi, sdf by POST only)[/blue]
  [cyan]--operation_spec[/cyan] [dark_magenta]OPERATION_SPEC[/dark_magenta]
  [blue]compound domain <operation specification> = record | <compound property> | synonyms | sids | cids | aids | assaysummary | classification | <xrefs> | description | conformers
      <compound property> = property / [comma-separated list of property tags]
  substance domain <operation specification> = record | synonyms | sids | cids | aids | assaysummary | classification | <xrefs> | description
      <xrefs> = xrefs / [comma-separated list of xrefs tags]
  assay domain <operation specification> = record | concise | aids | sids | cids | description | targets/<target type> | <doseresponse> | summary | classification
      <target_type> = {ProteinGI, ProteinName, GeneID, GeneSymbol}
      <doseresponse> = doseresponse/sid
  gene domain <operation specification> = summary | aids | concise | pwaccs
  protein domain <operation specification> = summary | aids | concise | pwaccs
  pathway domain <operation specification> = summary | cids | geneids | accessions
  taxonomy domain <operation specification> = summary | aids
  cell domain <operation specification> = summary | aids[/blue]""")
        sys.exit()
