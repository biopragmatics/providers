"""Generate static sites for resources with none."""

from pathlib import Path
from typing import List

import bioregistry
import click
import pyobo
from bioregistry import manager
from more_click import verbose_option
from pyobo import Obo
from pyobo.sources import ontology_resolver
from pyobo.ssg import make_site
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

HERE = Path(__file__).parent.resolve()
BASE_URL = "https://biopragmatics.github.io/providers"
REPOSITORY_NAME = "providers"
SKIP = {"gexo", "reto", "rexo"}
SHOW_MANIFEST = {"cemo"}


@click.command()
@click.option("--extra", multiple=True)
@verbose_option
def main(extra: List[str]):
    """Generate static sites for resources with none."""
    ontologies = []
    with logging_redirect_tqdm():
        for resource in manager.registry.values():
            if resource.prefix in SKIP:
                continue
            if extra and resource.prefix not in extra:
                continue

            downloads = [
                ("obo", resource.get_download_obo()),
                ("owl", resource.get_download_owl()),
            ]
            for download_format, download in downloads:
                # there's a ton of junk in aber-owl
                if download is None or "aber-owl" in download:
                    continue
                uri_format = resource.get_uri_format()
                if (
                    uri_format is None
                    or uri_format.startswith(BASE_URL)
                    or resource.prefix in extra
                ):
                    try:
                        obo = pyobo.get_ontology(resource.prefix)
                        make_site(
                            obo, HERE.joinpath(obo.ontology), manifest=obo.ontology in SHOW_MANIFEST
                        )
                        ontologies.append(obo)
                        if resource.uri_format is None and resource.prefix:
                            resource.uri_format = f"{BASE_URL}/{resource.prefix}/$1"
                    except Exception as e:
                        tqdm.write(f"failed on {resource.prefix}: {e}")
                        continue
                    break

        for cls in ontology_resolver:
            if extra and cls.ontology not in extra:
                continue

            resource = bioregistry.get_resource(cls.ontology)
            assert resource is not None
            uri_format = resource.get_uri_format()
            if uri_format is None or uri_format.startswith(BASE_URL):
                try:
                    obo: Obo = cls()
                except ValueError as e:
                    tqdm.write(f"failed to get {cls.ontology}: {e}")
                    continue
                make_site(obo, HERE.joinpath(obo.ontology))
                ontologies.append(obo)
                if resource.uri_format is None:
                    resource.uri_format = f"{BASE_URL}/{resource.prefix}/$1"

    manager.write_registry()

    link_list = "\n".join(
        f"- [{bioregistry.get_name(obo.ontology)} (`{obo.ontology}`)]({obo.ontology})"
        for obo in sorted(ontologies, key=lambda o: o.ontology)
    )
    HERE.joinpath("README.md").write_text(
        f"""\
# Biopragmatics Sites

This repository contains static sites generated for resources
that do not have their own providers, but are implemented in PyOBO.

{link_list}

## Update

The sites can be updated with the following:

```shell
$ pip install tox
$ tox
```
"""
    )


if __name__ == "__main__":
    main()
