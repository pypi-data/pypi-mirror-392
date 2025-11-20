import platform
import sys
from pathlib import Path


class Defaults:
    pillar = Path("/srv/pillar/defaults.sls")
    formatter = "yaml" if sys.stdout.isatty() else "expand"


class Darwin(Defaults):
    pillar = Path("/opt/pillar/defaults.sls")


if platform.system() == "Darwin":
    defaults = Darwin()
else:
    defaults = Defaults()
