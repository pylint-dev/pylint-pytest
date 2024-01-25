from __future__ import annotations

from typing import Any, Dict, List

from _pytest.fixtures import FixtureDef

FixtureDict = Dict[str, List[FixtureDef[Any]]]
