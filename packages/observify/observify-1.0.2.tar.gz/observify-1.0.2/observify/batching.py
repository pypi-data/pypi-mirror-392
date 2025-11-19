from __future__ import annotations
import json
import threading
import atexit
import signal
from typing import Any, Dict, List, Optional
import requests
from .types import Config, SdkMetric


def _parse_int_safe(v: Any) -> Optional[int]:
    try:
        n = int(v)
        return n if n >= 0 else None
    except Exception:
        return None


def _sanitize(m: SdkMetric) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if m.ts:
        out["ts"] = m.ts
    if m.method:
        out["method"] = m.method
    if m.route:
        out["route"] = m.route
    if isinstance(m.status, int):
        out["status"] = m.status
    if isinstance(m.dur_ms, int):
        out["dur_ms"] = m.dur_ms
    if m.req_bytes is not None:
        out["req_bytes"] = m.req_bytes
    if m.res_bytes is not None:
        out["res_bytes"] = m.res_bytes
    if m.request_id:
        out["request_id"] = m.request_id
    if m.trace_id:
        out["trace_id"] = m.trace_id
    if m.service:
        out["service"] = m.service.strip()
    if m.env:
        out["env"] = str(m.env).upper()
    if m.release:
        out["release"] = m.release
    return out


class _BatchManager:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._buf: List[SdkMetric] = []
        self._lock = threading.Lock()
        self._flushing = False
        self._stop = False
        self._timer: Optional[threading.Timer] = None
        self._start_timer()
        self._install_exit_hooks()

    def _log(self, *args: Any):
        if self.cfg.debug:
            print("[observify]", *args)

    def _start_timer(self):
        def _tick():
            try:
                self.flush()
            finally:
                if not self._stop:
                    self._timer = threading.Timer(
                        self.cfg.flushIntervalMs / 1000.0, _tick)
                    self._timer.daemon = True
                    self._timer.start()
        _tick()

    def _install_exit_hooks(self):
        def _drain(*_a):
            try:
                self.flush()
            except Exception:
                pass
        atexit.register(_drain)
        try:
            signal.signal(signal.SIGINT, lambda *_: (_drain(), exit(0)))
            signal.signal(signal.SIGTERM, lambda *_: (_drain(), exit(0)))
        except Exception:
            pass

    def add(self, m: SdkMetric):
        with self._lock:
            self._buf.append(m)
            if len(self._buf) >= self.cfg.batchSize:
                threading.Thread(target=self.flush, daemon=True).start()

    def flush(self):
        with self._lock:
            if self._flushing or not self._buf:
                return
            self._flushing = True
            batch = self._buf
            self._buf = []

        try:
            payload = [_sanitize(x) for x in batch]
            self._log("sending", {"count": len(payload)})

            res = requests.post(
                self.cfg.remoteUrl,
                data=json.dumps(payload),
                headers={
                    "content-type": "application/json",
                    "x-api-key": self.cfg.apiKey,
                },
                timeout=self.cfg.requestTimeoutMs / 1000.0,
            )
            if res.status_code >= 400:
                txt = ""
                try:
                    txt = res.text
                except Exception:
                    pass
                self._log("server_error", res.status_code, txt)
                with self._lock:
                    self._buf = batch + self._buf

        except Exception as err:
            self._log("network_error", str(err))
            with self._lock:
                self._buf = batch + self._buf
        finally:
            with self._lock:
                self._flushing = False

    def stop(self):
        self._stop = True
        if self._timer:
            self._timer.cancel()
            self._timer = None
        self.flush()


_global_managers: Dict[str, _BatchManager] = {}


def get_manager(cfg: Config) -> _BatchManager:
    key = f"{cfg.remoteUrl}|{cfg.apiKey}"
    mgr = _global_managers.get(key)
    if not mgr:
        mgr = _BatchManager(cfg)
        _global_managers[key] = mgr
    return mgr


# reexports
parse_int_safe = _parse_int_safe
