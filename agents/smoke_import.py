# Import-only smoke test for CI; no network calls, no key required
# This simply imports the agents bootstrap module to ensure imports succeed.
# No secrets are used or printed.

import importlib

importlib.import_module("agents.crew.bootstrap")  # noqa: F401
print("Agents import OK")
