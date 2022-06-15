"""Generate static sites for resources with none."""

from pathlib import Path

from pyobo.sources import UniProtPtmGetter
from pyobo.ssg import make_site

HERE = Path(__file__).parent.resolve()


def main():
    for cls in [
        UniProtPtmGetter,
    ]:
        obo = cls()
        make_site(obo, HERE.joinpath(obo.ontology))


if __name__ == '__main__':
    main()
