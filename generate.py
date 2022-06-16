"""Generate static sites for resources with none."""

from pathlib import Path

import bioregistry
from pyobo import Obo
from pyobo.sources import ontology_resolver
from pyobo.ssg import make_site
import click
from tqdm.contrib.logging import logging_redirect_tqdm

HERE = Path(__file__).parent.resolve()
REPOSITORY_NAME = "providers"

@click.command()
def main():
    """Generate static sites for resources with none."""
    ontologies = []
    with logging_redirect_tqdm():
        for cls in ontology_resolver:
            uri_format = bioregistry.get_uri_format(cls.ontology)
            if uri_format is None or "biopragmatics.github.io" in uri_format:
                obo: Obo = cls()
                make_site(obo, HERE.joinpath(obo.ontology))
                ontologies.append(obo)

    link_list = "\n".join(
        f"- [{bioregistry.get_name(obo.ontology)} (`{obo.ontology}`)]({obo.ontology})"
        for obo in ontologies
    )
    HERE.joinpath("README.md").write_text(f"""\
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
""")


if __name__ == '__main__':
    main()
