"""Locate the local Apache Jena / Fuseki installs (fail loud when absent)."""

import os
import subprocess
from pathlib import Path

JENA_VERSION = "5.6.0"
_ROOT = Path.home() / ".golden-chain" / "jena"
# Single place that names the fallback install paths.
DEFAULT_HOMES = {
    "GOLDEN_CHAIN_JENA_HOME": _ROOT / f"jena-{JENA_VERSION}" / f"apache-jena-{JENA_VERSION}",
    "GOLDEN_CHAIN_FUSEKI_HOME": _ROOT / f"fuseki-{JENA_VERSION}" / f"apache-jena-fuseki-{JENA_VERSION}",
}


class JenaMissing(RuntimeError):
    pass


def _home(var: str, probe: str) -> Path:
    p = Path(os.environ.get(var) or DEFAULT_HOMES[var])
    if not (p / probe).exists():
        raise JenaMissing(
            f"{var}: no Jena install at {p} (expected {probe} inside). "
            f"Set {var} or install Jena {JENA_VERSION} to {DEFAULT_HOMES[var]}."
        )
    return p


def jena_home() -> Path:
    return _home("GOLDEN_CHAIN_JENA_HOME", "lib")


def fuseki_home() -> Path:
    return _home("GOLDEN_CHAIN_FUSEKI_HOME", "fuseki-server.jar")


def jena_version() -> str:
    jars = sorted((jena_home() / "lib").glob("jena-core-*.jar"))
    if not jars:
        raise JenaMissing(f"no jena-core jar under {jena_home() / 'lib'}")
    return jars[0].stem.removeprefix("jena-core-")


def run_tool(main_class: str, args: list[str], cwd: Path, log: Path) -> None:
    """Run a Jena command-line class (e.g. tdb2.tdbloader); raise with the log tail on failure."""
    cmd = ["java", "-cp", str(jena_home() / "lib") + os.sep + "*", main_class, *args]
    with open(log, "ab") as f:
        f.write(("\n$ " + " ".join(cmd) + "\n").encode())
        r = subprocess.run(cmd, cwd=cwd, stdout=f, stderr=subprocess.STDOUT)
    if r.returncode:
        tail = log.read_text(errors="replace")[-1500:]
        raise RuntimeError(f"{main_class} failed ({r.returncode}); log {log}:\n{tail}")
