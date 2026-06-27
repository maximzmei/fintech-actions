import sys
import os
import types

root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root)

# Map code-review/ (hyphen) as importable code_review package
_pkg = types.ModuleType("code_review")
_pkg.__path__ = [os.path.join(root, "code-review")]
_pkg.__package__ = "code_review"
sys.modules["code_review"] = _pkg

_sdd = types.ModuleType("spec_driven_dev")
_sdd.__path__ = [os.path.join(root, "spec-driven-dev")]
_sdd.__package__ = "spec_driven_dev"
sys.modules["spec_driven_dev"] = _sdd
