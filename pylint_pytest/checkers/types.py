from __future__ import annotations

from typing import Any

from _pytest.fixtures import FixtureDef

FixtureDict = dict[str, list[FixtureDef[Any]]]
