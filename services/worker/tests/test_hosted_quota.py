from __future__ import annotations

import asyncio
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal

import pytest
from caragent_core.models import utc_now

from caragent_worker.quotas import (
    HostedQuotaExceeded,
    HostedQuotaReserveRequest,
    InMemoryHostedQuotaStore,
    RedisHostedQuotaStore,
)


def test_hosted_quota_store_reserves_atomically_and_settles_usage() -> None:
    store = InMemoryHostedQuotaStore()
    now = utc_now()
    request = HostedQuotaReserveRequest(
        daily_limit=1,
        estimated_cost=Decimal("0.0300"),
        job_id="job-1",
        max_estimated_cost_per_job=Decimal("1.0000"),
        minute_limit=1,
        model_run_id="run-1",
        now=now,
        provider="bfl",
    )

    reservation = asyncio.run(store.reserve(request))

    with pytest.raises(HostedQuotaExceeded, match="daily"):
        asyncio.run(
            store.reserve(
                replace(
                    request,
                    job_id="job-2",
                    model_run_id="run-2",
                    now=now + timedelta(seconds=1),
                ),
            ),
        )

    settled = asyncio.run(
        store.settle(
            reservation.reservation_id,
            actual_cost=Decimal("0.0200"),
            status="succeeded",
        ),
    )

    assert reservation.status == "reserved"
    assert settled.actual_cost == Decimal("0.0200")
    assert settled.status == "succeeded"


def test_hosted_quota_store_rejects_estimated_cost_before_reserving() -> None:
    store = InMemoryHostedQuotaStore()

    with pytest.raises(HostedQuotaExceeded, match="estimated cost"):
        asyncio.run(
            store.reserve(
                HostedQuotaReserveRequest(
                    daily_limit=10,
                    estimated_cost=Decimal("2.0000"),
                    job_id="job-1",
                    max_estimated_cost_per_job=Decimal("1.0000"),
                    minute_limit=10,
                    model_run_id="run-1",
                    now=utc_now(),
                    provider="bfl",
                ),
            ),
        )



def test_redis_hosted_quota_store_reserves_with_eval_and_settles_usage() -> None:
    fake = FakeRedisClient()
    store = RedisHostedQuotaStore(fake)
    now = utc_now()

    reservation = asyncio.run(
        store.reserve(
            HostedQuotaReserveRequest(
                daily_limit=10,
                estimated_cost=Decimal("0.0300"),
                job_id="job-1",
                max_estimated_cost_per_job=Decimal("1.0000"),
                minute_limit=10,
                model_run_id="run-1",
                now=now,
                provider="bfl",
            ),
        ),
    )
    settled = asyncio.run(
        store.settle(
            reservation.reservation_id,
            actual_cost=Decimal("0.0200"),
            status="succeeded",
        ),
    )

    assert fake.eval_calls == 1
    assert reservation.status == "reserved"
    assert settled.status == "succeeded"
    assert settled.actual_cost == Decimal("0.0200")
    assert settled.provider == "bfl"


class FakeRedisClient:
    def __init__(self) -> None:
        self.eval_calls = 0
        self.hashes: dict[str, dict[object, object]] = {}

    async def eval(self, _script: str, _numkeys: int, *keys_and_args: object) -> object:
        self.eval_calls += 1
        reservation_key = str(keys_and_args[2])
        reservation_id = str(keys_and_args[8])
        self.hashes[reservation_key] = {
            "actual_cost": "",
            "estimated_cost": str(keys_and_args[12]),
            "job_id": str(keys_and_args[9]),
            "model_run_id": str(keys_and_args[10]),
            "provider": str(keys_and_args[11]),
            "reserved_at": str(keys_and_args[13]),
            "status": "reserved",
        }
        return ["reserved", reservation_id]

    async def expire(self, _name: str, _time: int) -> object:
        return 1

    async def hgetall(self, name: str) -> dict[object, object]:
        return self.hashes[name]

    async def hset(self, name: str, mapping: dict[str, str]) -> object:
        self.hashes[name].update(mapping)
        return len(mapping)