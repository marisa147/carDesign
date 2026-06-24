from __future__ import annotations

import asyncio
import importlib
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal
from functools import lru_cache
from typing import Any, Protocol, cast
from uuid import UUID, uuid4

LOCAL_RUNTIME_MODES = {"local", "development", "test"}


class HostedQuotaExceeded(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class HostedQuotaReserveRequest:
    provider: str
    job_id: str
    model_run_id: str
    now: datetime
    daily_limit: int
    minute_limit: int
    estimated_cost: Decimal | None = None
    max_estimated_cost_per_job: Decimal | None = None


@dataclass(frozen=True, slots=True)
class HostedQuotaReservation:
    reservation_id: str
    provider: str
    job_id: str
    model_run_id: str
    reserved_at: datetime
    status: str
    actual_cost: Decimal | None = None
    estimated_cost: Decimal | None = None


class HostedQuotaStore(Protocol):
    async def reserve(self, request: HostedQuotaReserveRequest) -> HostedQuotaReservation:
        pass

    async def settle(
        self,
        reservation_id: str,
        *,
        actual_cost: Decimal | None,
        status: str,
    ) -> HostedQuotaReservation:
        pass


class RedisClient(Protocol):
    async def eval(self, script: str, numkeys: int, *keys_and_args: object) -> object:
        pass

    async def expire(self, name: str, time: int) -> object:
        pass

    async def hgetall(self, name: str) -> dict[object, object]:
        pass

    async def hset(self, name: str, mapping: dict[str, str]) -> object:
        pass


class InMemoryHostedQuotaStore:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._reservations: dict[str, HostedQuotaReservation] = {}

    async def reserve(self, request: HostedQuotaReserveRequest) -> HostedQuotaReservation:
        async with self._lock:
            existing = self._reservation_for_model_run(request.model_run_id)
            if existing is not None and existing.status == "reserved":
                return existing

            if (
                request.estimated_cost is not None
                and request.max_estimated_cost_per_job is not None
                and request.estimated_cost > request.max_estimated_cost_per_job
            ):
                raise HostedQuotaExceeded(
                    "Hosted provider estimated cost exceeds per-job limit.",
                )

            provider = request.provider.strip().lower()
            daily_count = self._count(provider, since=request.now - timedelta(days=1))
            if daily_count >= request.daily_limit:
                raise HostedQuotaExceeded("Hosted provider daily call limit reached.")

            minute_count = self._count(provider, since=request.now - timedelta(minutes=1))
            if minute_count >= request.minute_limit:
                raise HostedQuotaExceeded("Hosted provider per-minute rate limit reached.")

            reservation = HostedQuotaReservation(
                estimated_cost=request.estimated_cost,
                job_id=request.job_id,
                model_run_id=request.model_run_id,
                provider=provider,
                reservation_id=str(uuid4()),
                reserved_at=request.now,
                status="reserved",
            )
            self._reservations[reservation.reservation_id] = reservation
            return reservation

    async def settle(
        self,
        reservation_id: str,
        *,
        actual_cost: Decimal | None,
        status: str,
    ) -> HostedQuotaReservation:
        async with self._lock:
            reservation = self._reservations[reservation_id]
            settled = replace(
                reservation,
                actual_cost=actual_cost,
                status=status.strip().lower() or "settled",
            )
            self._reservations[reservation_id] = settled
            return settled

    def _reservation_for_model_run(self, model_run_id: str) -> HostedQuotaReservation | None:
        for reservation in self._reservations.values():
            if reservation.model_run_id == model_run_id:
                return reservation
        return None

    def _count(self, provider: str, *, since: datetime) -> int:
        return sum(
            1
            for reservation in self._reservations.values()
            if reservation.provider == provider
            and reservation.reserved_at >= since
            and reservation.status in {"reserved", "succeeded"}
        )


class RedisHostedQuotaStore:
    _RESERVE_SCRIPT = """
local existing = redis.call("GET", KEYS[4])
if existing then
  return {"existing", existing}
end
local daily_count = tonumber(redis.call("GET", KEYS[1]) or "0")
if daily_count >= tonumber(ARGV[1]) then
  return {"error", "Hosted provider daily call limit reached."}
end
local minute_count = tonumber(redis.call("GET", KEYS[2]) or "0")
if minute_count >= tonumber(ARGV[2]) then
  return {"error", "Hosted provider per-minute rate limit reached."}
end
redis.call("INCR", KEYS[1])
redis.call("EXPIRE", KEYS[1], tonumber(ARGV[3]))
redis.call("INCR", KEYS[2])
redis.call("EXPIRE", KEYS[2], tonumber(ARGV[4]))
redis.call(
  "HSET",
  KEYS[3],
  "actual_cost", "",
  "estimated_cost", ARGV[9],
  "job_id", ARGV[6],
  "model_run_id", ARGV[7],
  "provider", ARGV[8],
  "reserved_at", ARGV[10],
  "status", "reserved"
)
redis.call("EXPIRE", KEYS[3], tonumber(ARGV[3]))
redis.call("SET", KEYS[4], ARGV[5], "EX", tonumber(ARGV[3]))
return {"reserved", ARGV[5]}
"""

    def __init__(self, client: RedisClient, *, key_prefix: str = "caragent:hosted-quota"):
        self._client = client
        self._key_prefix = key_prefix.rstrip(":")

    @classmethod
    def from_url(cls, redis_url: str) -> RedisHostedQuotaStore:
        redis_module = importlib.import_module("redis.asyncio")
        from_url = cast(Any, redis_module.from_url)
        return cls(cast(RedisClient, from_url(redis_url)))

    async def reserve(self, request: HostedQuotaReserveRequest) -> HostedQuotaReservation:
        if (
            request.estimated_cost is not None
            and request.max_estimated_cost_per_job is not None
            and request.estimated_cost > request.max_estimated_cost_per_job
        ):
            raise HostedQuotaExceeded(
                "Hosted provider estimated cost exceeds per-job limit.",
            )

        provider = request.provider.strip().lower()
        reservation_id = str(uuid4())
        daily_key, minute_key, reservation_key, model_run_key = self._reservation_keys(
            provider=provider,
            reservation_id=reservation_id,
            model_run_id=request.model_run_id,
            now=request.now,
        )
        result = await self._client.eval(
            self._RESERVE_SCRIPT,
            4,
            daily_key,
            minute_key,
            reservation_key,
            model_run_key,
            request.daily_limit,
            request.minute_limit,
            60 * 60 * 27,
            120,
            reservation_id,
            request.job_id,
            request.model_run_id,
            provider,
            _decimal_text(request.estimated_cost),
            request.now.isoformat(),
        )
        status, value = _redis_pair(result)
        if status == "error":
            raise HostedQuotaExceeded(value)
        active_reservation_id = value if _looks_like_uuid(value) else reservation_id
        return HostedQuotaReservation(
            estimated_cost=request.estimated_cost,
            job_id=request.job_id,
            model_run_id=request.model_run_id,
            provider=provider,
            reservation_id=active_reservation_id,
            reserved_at=request.now,
            status="reserved",
        )

    async def settle(
        self,
        reservation_id: str,
        *,
        actual_cost: Decimal | None,
        status: str,
    ) -> HostedQuotaReservation:
        reservation_key = self._reservation_key(reservation_id)
        await self._client.hset(
            reservation_key,
            mapping={
                "actual_cost": _decimal_text(actual_cost),
                "status": status.strip().lower() or "settled",
            },
        )
        await self._client.expire(reservation_key, 60 * 60 * 27)
        values = {
            _redis_text(key): _redis_text(value)
            for key, value in (await self._client.hgetall(reservation_key)).items()
        }
        return HostedQuotaReservation(
            actual_cost=_decimal_or_none(values.get("actual_cost")),
            estimated_cost=_decimal_or_none(values.get("estimated_cost")),
            job_id=values.get("job_id", ""),
            model_run_id=values.get("model_run_id", ""),
            provider=values.get("provider", ""),
            reservation_id=reservation_id,
            reserved_at=_datetime_or_now(values.get("reserved_at")),
            status=values.get("status", status),
        )

    def _reservation_keys(
        self,
        *,
        provider: str,
        reservation_id: str,
        model_run_id: str,
        now: datetime,
    ) -> tuple[str, str, str, str]:
        day = now.strftime("%Y%m%d")
        minute = now.strftime("%Y%m%d%H%M")
        return (
            f"{self._key_prefix}:{provider}:daily:{day}",
            f"{self._key_prefix}:{provider}:minute:{minute}",
            self._reservation_key(reservation_id),
            f"{self._key_prefix}:model-run:{model_run_id}",
        )

    def _reservation_key(self, reservation_id: str) -> str:
        return f"{self._key_prefix}:reservation:{reservation_id}"


HOSTED_QUOTA_STORE = InMemoryHostedQuotaStore()


@lru_cache(maxsize=8)
def _redis_store(redis_url: str) -> RedisHostedQuotaStore:
    return RedisHostedQuotaStore.from_url(redis_url)


def hosted_quota_store_for_runtime(*, redis_url: str, runtime_mode: str) -> HostedQuotaStore:
    if runtime_mode in LOCAL_RUNTIME_MODES:
        return HOSTED_QUOTA_STORE
    return _redis_store(redis_url)


def _decimal_text(value: Decimal | None) -> str:
    return "" if value is None else str(value)


def _decimal_or_none(value: str | None) -> Decimal | None:
    if not value:
        return None
    return Decimal(value)


def _datetime_or_now(value: str | None) -> datetime:
    if not value:
        return datetime.now().astimezone()
    return datetime.fromisoformat(value)


def _redis_pair(value: object) -> tuple[str, str]:
    if isinstance(value, list) and len(value) >= 2:
        return _redis_text(value[0]), _redis_text(value[1])
    if isinstance(value, tuple) and len(value) >= 2:
        return _redis_text(value[0]), _redis_text(value[1])
    raise HostedQuotaExceeded("Hosted provider quota reserve failed.")


def _redis_text(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return str(value)


def _looks_like_uuid(value: str) -> bool:
    try:
        UUID(value)
    except ValueError:
        return False
    return True