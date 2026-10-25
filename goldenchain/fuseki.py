"""Start/stop the read-only Fuseki server over fuseki/config.ttl."""

import json
import os
import socket
import subprocess
import time
import urllib.parse
import urllib.request
from contextlib import contextmanager

from goldenchain import jena
from goldenchain.ingest import FUSEKI, ROOT


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Server:
    def __init__(self, port: int):
        self.port = port
        self.base = f"http://127.0.0.1:{port}"

    def select(self, sparql: str, endpoint: str = "/gc/sparql") -> list[dict]:
        req = urllib.request.Request(
            self.base + endpoint,
            urllib.parse.urlencode({"query": sparql}).encode(),
            {"Accept": "application/sparql-results+json"},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)["results"]["bindings"]


@contextmanager
def serve(timeout: float = 60.0):
    """Run fuseki-server with fuseki/config.ttl (cwd = repo root); stop on exit."""
    home = jena.fuseki_home()
    port = free_port()
    (FUSEKI / "run").mkdir(parents=True, exist_ok=True)
    log = open(FUSEKI / "run" / "fuseki.log", "wb")
    proc = subprocess.Popen(
        [
            "java",
            "-cp",
            str(home / "fuseki-server.jar"),
            "org.apache.jena.fuseki.main.cmds.FusekiServerCmd",
            f"--config={FUSEKI / 'config.ttl'}",
            f"--port={port}",
            "--localhost",
        ],
        cwd=ROOT,
        env={**os.environ, "FUSEKI_BASE": str(FUSEKI / "run" / "base")},  # keep ./run out of the repo root
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    try:
        deadline = time.time() + timeout
        while True:
            if proc.poll() is not None:
                raise RuntimeError(f"fuseki exited ({proc.returncode}); see {log.name}")
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/$/ping", timeout=2):
                    break
            except OSError:
                if time.time() > deadline:
                    raise RuntimeError(f"fuseki did not answer /$/ping in {timeout}s; see {log.name}")
                time.sleep(0.3)
        yield Server(port)
    finally:
        proc.terminate()
        try:
            proc.wait(10)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()
