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
