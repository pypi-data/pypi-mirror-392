from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Union

Env = Union[str, "PROD" "HMG" "DEV"]


@dataclass
class SdkMetric:
    ts: int
    method: str
    route: str
    status: int
    dur_ms: int
    req_bytes: Optional[int] = None
    res_bytes: Optional[int] = None
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    service: Optional[str] = None
    env: Optional[Env] = None
    release: Optional[str] = None


@dataclass
class Config:
    remoteUrl: str
    apiKey: str
    protectedRoutes: Optional[List[str]] = None
    debug: bool = False
    service: Optional[str] = None
    env: Optional[Env] = None
    release: Optional[str] = None
    batchSize: int = 100
    flushIntervalMs: int = 60000
    requestTimeoutMs: int = 10000
    measureBodyBytes: bool = False
