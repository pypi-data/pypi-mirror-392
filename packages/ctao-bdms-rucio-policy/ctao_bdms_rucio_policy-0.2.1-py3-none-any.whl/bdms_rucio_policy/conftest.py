import os
from importlib.resources import files

config = files("bdms_rucio_policy") / "tests/resources/rucio.cfg"
os.environ["RUCIO_CONFIG"] = str(config)
