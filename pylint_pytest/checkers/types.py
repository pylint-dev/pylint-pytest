from __future__ import annotations

import sys
from pprint import pprint
from typing import Any, Dict, List

from _pytest.fixtures import FixtureDef

FixtureDict = Dict[str, List[FixtureDef[Any]]]


def replacement_add_message(*args, **kwargs):
    print("Called un-initialized _original_add_message with:", file=sys.stderr)
    pprint(args, sys.stderr)
    pprint(kwargs, sys.stderr)
