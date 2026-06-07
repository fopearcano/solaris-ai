"""
Best-effort, stdlib-only sampling of the resources Solaris_Ai is
using while it runs.

The Solaris process *is* the running Conscience, so process-level
CPU / RAM / disk / fds / threads are exactly "what Solaris_Ai is
taking". Network and load average are system-wide context, and GPU
is read from nvidia-smi if present.

Everything here is best-effort: each reader is wrapped so that on a
platform where a source is unavailable (e.g. /proc on macOS) the
metric is simply omitted rather than raising. No third-party deps.
"""

from __future__ import annotations

import os
import subprocess
import time


class ResourceMonitor:
    def __init__(self) -> None:
        self.ncpu = os.cpu_count() or 1
        try:
            self.page = os.sysconf("SC_PAGE_SIZE")
        except (ValueError, OSError, AttributeError):
            self.page = 4096
        self.mem_total = self._mem_total()
        self._prev: dict | None = None
        self._gpu_ok = True
        self._gpu_cache: dict | None = None
        self._gpu_ts = 0.0
        self._rss_cache: int | None = None
        self._rss_ts = 0.0

    # ---- public -------------------------------------------------------

    def sample(self) -> dict:
        """Return a dict of currently-available metrics.

        Rate metrics (cpu, net, disk) need two samples, so they are
        absent on the very first call and appear from the second.
        """
        now = time.monotonic()
        cpu_t = os.times()
        proc_cpu = cpu_t[0] + cpu_t[1]
        net = self._net()
        io = self._proc_io()
        out: dict = {}

        rss = self._rss(now)
        if rss is not None:
            out["ram"] = {"mb": round(rss / 1048576, 1)}
            if self.mem_total:
                out["ram"]["pct"] = round(rss / self.mem_total * 100, 1)

        if self._prev is not None:
            dt = max(1e-6, now - self._prev["now"])
            pct = max(0.0, (proc_cpu - self._prev["cpu"]) / dt * 100.0)
            out["cpu"] = {
                "pct": round(pct, 1),
                "per_core": round(pct / self.ncpu, 1),
                "cores": self.ncpu,
            }
            if net and self._prev.get("net"):
                drx = max(0, net[0] - self._prev["net"][0])
                dtx = max(0, net[1] - self._prev["net"][1])
                out["net"] = {
                    "down_kbps": round(drx / dt / 1024, 1),
                    "up_kbps": round(dtx / dt / 1024, 1),
                }
            if io and self._prev.get("io"):
                dr = max(0, io[0] - self._prev["io"][0])
                dw = max(0, io[1] - self._prev["io"][1])
                out["disk"] = {
                    "read_kbps": round(dr / dt / 1024, 1),
                    "write_kbps": round(dw / dt / 1024, 1),
                }

        thr = self._threads()
        if thr is not None:
            out["threads"] = thr
        fds = self._fds()
        if fds is not None:
            out["fds"] = fds
        try:
            la = os.getloadavg()
            out["load"] = {"1": round(la[0], 2), "5": round(la[1], 2), "15": round(la[2], 2)}
        except (OSError, AttributeError):
            pass
        gpu = self._gpu(now)
        if gpu is not None:
            out["gpu"] = gpu

        self._prev = {"now": now, "cpu": proc_cpu, "net": net, "io": io}
        return out

    # ---- readers (each best-effort) -----------------------------------

    def _mem_total(self) -> int | None:
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        return int(line.split()[1]) * 1024
        except OSError:
            pass
        try:
            return os.sysconf("SC_PHYS_PAGES") * self.page
        except (ValueError, OSError, AttributeError):
            return None

    def _rss(self, now: float) -> int | None:
        if self._rss_cache is not None and now - self._rss_ts < 0.8:
            return self._rss_cache
        val: int | None = None
        try:
            with open("/proc/self/statm") as f:
                val = int(f.read().split()[1]) * self.page  # resident pages
        except OSError:
            try:
                r = subprocess.run(
                    ["ps", "-o", "rss=", "-p", str(os.getpid())],
                    capture_output=True, text=True, timeout=0.6,
                )
                val = int(r.stdout.strip() or 0) * 1024
            except Exception:  # noqa: BLE001
                val = None
        self._rss_cache = val
        self._rss_ts = now
        return val

    @staticmethod
    def _net() -> tuple[int, int] | None:
        try:
            rx = tx = 0
            with open("/proc/net/dev") as f:
                for line in f.read().splitlines()[2:]:
                    name, _, rest = line.partition(":")
                    if name.strip() == "lo":
                        continue
                    cols = rest.split()
                    if len(cols) >= 9:
                        rx += int(cols[0])
                        tx += int(cols[8])
            return (rx, tx)
        except OSError:
            return None

    @staticmethod
    def _proc_io() -> tuple[int, int] | None:
        try:
            read = write = 0
            with open("/proc/self/io") as f:
                for line in f:
                    if line.startswith("read_bytes:"):
                        read = int(line.split()[1])
                    elif line.startswith("write_bytes:"):
                        write = int(line.split()[1])
            return (read, write)
        except OSError:
            return None

    @staticmethod
    def _threads() -> int | None:
        try:
            with open("/proc/self/status") as f:
                for line in f:
                    if line.startswith("Threads:"):
                        return int(line.split()[1])
        except OSError:
            pass
        return None

    @staticmethod
    def _fds() -> int | None:
        try:
            return len(os.listdir("/proc/self/fd"))
        except OSError:
            return None

    def _gpu(self, now: float) -> dict | None:
        if not self._gpu_ok:
            return None
        if self._gpu_cache is not None and now - self._gpu_ts < 2.0:
            return self._gpu_cache
        self._gpu_ts = now
        try:
            r = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=0.6,
            )
            if r.returncode != 0 or not r.stdout.strip():
                self._gpu_ok = False
                return None
            util, mem = [x.strip() for x in r.stdout.strip().splitlines()[0].split(",")[:2]]
            self._gpu_cache = {"pct": float(util), "mem_mb": float(mem)}
        except FileNotFoundError:
            self._gpu_ok = False
            self._gpu_cache = None
        except Exception:  # noqa: BLE001
            self._gpu_cache = None
        return self._gpu_cache
