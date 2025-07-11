import os, sys, types
from unittest.mock import MagicMock

# 1) Make sure your project root is on PYTHONPATH
repo_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../..")
)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)


# 2) Stub out all the airflow bits (including DAG) in one shot
for name in (
    "airflow",
    "airflow.models",
    "airflow.models.baseoperator",
    "airflow.models.dag",            # ← include the dag module here
    "airflow.operators",
    "airflow.operators.python",
    "airflow.operators.python_operator",
):
    m = types.ModuleType(name)
    # make the top-level package “airflow” look like a package
    if name == "airflow":
        m.__path__ = []

    # if we're in the dag‐module, give it a DAG symbol
    if name == "airflow.models.dag":
        m.DAG = MagicMock(name="DAG")

    sys.modules[name] = m

# 3) Expose DAG at the top level so `from airflow import DAG` works
#    (sys.modules["airflow"] is the ModuleType("airflow") we just inserted)
sys.modules["airflow"].DAG = sys.modules["airflow.models.dag"].DAG


# 4) Stub the Moogsoft leaf module just as before
leaf = "cli.src.airflow_resources.PLATFORM.moogsoft_alerts.moogsoft_alert_v1_0"
moog = types.ModuleType(leaf)
moog.alert = MagicMock()
moog.close_alert = MagicMock()
sys.modules[leaf] = moog


# 5) Now import the thing under test
import cli.src.airflow_resources.PLATFORM.collibra_adaptor as collibra_adaptor


def test_something():
    # …your assertions here…
    assert hasattr(collibra_adaptor, "some_function")




import os
import sys
import types
import pytest
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def stub_airflow_and_moogsoft():
    # 1) Make sure your package is importable
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    # 2) Stub out all the airflow bits (including DAG) in one loop
    for name in (
        "airflow",
        "airflow.models",
        "airflow.models.baseoperator",
        "airflow.models.dag",            # ← DAG lives here
        "airflow.operators",
        "airflow.operators.python",
        "airflow.operators.python_operator",
    ):
        m = types.ModuleType(name)
        # make the top‐level airflow act like a package
        if name == "airflow":
            m.__path__ = []
        # inject a fake DAG class
        if name == "airflow.models.dag":
            m.DAG = MagicMock(name="DAG")
        sys.modules[name] = m

    # 3) Expose DAG on airflow itself so 'from airflow import DAG' works
    sys.modules["airflow"].DAG = sys.modules["airflow.models.dag"].DAG

    # 4) Stub the Moogsoft leaf module
    leaf = "cli.src.airflow_resources.PLATFORM.moogsoft_alerts.moogsoft_alert_v1_0"
    moog = types.ModuleType(leaf)
    moog.alert = MagicMock()
    moog.close_alert = MagicMock()
    sys.modules[leaf] = moog

    # yield back to pytest so your tests now see these stubs
    yield