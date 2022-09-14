"""Generate static sites for resources with none."""

from pathlib import Path

import bioregistry
import click
import pyobo
from pyobo import Obo
from pyobo.sources import ontology_resolver
from pyobo.ssg import make_site
from tqdm.contrib.logging import logging_redirect_tqdm
from tqdm import tqdm
HERE = Path(__file__).parent.resolve()
REPOSITORY_NAME = "providers"
SKIP = {"gexo", "reto", "rexo"}

@click.command()
def main():
    """Generate static sites for resources with none."""
    ontologies = []
    with logging_redirect_tqdm():
        for resource in bioregistry.resources():
            uri_format = resource.get_uri_format()
            obo_download = resource.get_download_obo()
            if uri_format is None and obo_download is not None and resource.prefix not in SKIP:
                obo = pyobo.get_ontology(resource.prefix)
                make_site(obo, HERE.joinpath(obo.ontology))
                ontologies.append(obo)

        for cls in ontology_resolver:
            uri_format = bioregistry.get_uri_format(cls.ontology)
            if uri_format is None or "biopragmatics.github.io" in uri_format:
                try:
                    obo: Obo = cls()
                except ValueError as e:
                    tqdm.write(f"failed to get {cls.ontology}: {e}")
                    continue
                make_site(obo, HERE.joinpath(obo.ontology))
                ontologies.append(obo)

    link_list = "\n".join(
        f"- [{bioregistry.get_name(obo.ontology)} (`{obo.ontology}`)]({obo.ontology})"
        for obo in ontologies
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
