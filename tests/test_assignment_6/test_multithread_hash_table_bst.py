import os
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytest

from project.assignment_6.multithread_hash_table_bst import ThreadSafeHashTable


# Configuration constants for tests
DEFAULT_THREADS = 8


@pytest.fixture
def empty_table():
    """Return a fresh empty ThreadSafeHashTable for a test."""
    return ThreadSafeHashTable(size=64)


@pytest.fixture
def preloaded_table():
    """Return a ThreadSafeHashTable preloaded with deterministic data."""
    t = ThreadSafeHashTable(size=64)
    for i in range(1000):
        t[i] = i * 10
    return t


def test_concurrent_unique_inserts_no_data_loss(empty_table):
    """Insert many unique keys concurrently; verify no keys are lost."""
    threads = DEFAULT_THREADS
    per_thread = 2000
    total = threads * per_thread

    def worker(seed: int) -> None:
        base = seed * per_thread
        for i in range(per_thread):
            k = base + i
            empty_table[k] = k + 1

    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = [ex.submit(worker, s) for s in range(threads)]
        for f in as_completed(futures):
            # re-raise if exceptions occurred in worker
            f.result()

    # Validate count and values
    assert len(empty_table) == total

    # check random sample of values
    rng = random.Random(0)
    for _ in range(100):
        k = rng.randint(0, total - 1)
        assert empty_table[k] == k + 1


def test_concurrent_mixed_operations_no_crash_and_consistency(preloaded_table):
    """Run mixed operations (reads/writes/deletes) concurrently and check consistency."""
    table = preloaded_table
    threads = DEFAULT_THREADS
    ops_per_thread = 5000

    def worker(seed: int) -> None:
        rng = random.Random(seed)
        for _ in range(ops_per_thread):
            r = rng.random()
            k = rng.randint(0, 1500)
            if r < 0.70:
                # read
                try:
                    _ = table[k]
                except KeyError:
                    pass
            elif r < 0.95:
                # write
                table[k] = seed + k
            else:
                # delete
                try:
                    del table[k]
                except KeyError:
                    pass

    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = [ex.submit(worker, s) for s in range(threads)]
        for f in as_completed(futures):
            f.result()

    # After concurrent ops, check that reported length equals snapshot length
    snap = table.keys_snapshot()
    assert len(snap) == len(
        table
    )  # Snapshot length and table length must match after concurrent ops


def test_concurrent_same_key_inserts(empty_table):
    """Multiple threads set the same key concurrently; verify there is only one entry and no duplicate counts."""
    key = "shared-key"
    initial_len = len(empty_table)
    threads = DEFAULT_THREADS
    values_to_write = [f"value-{i}" for i in range(threads)]

    def worker_write(val: str) -> None:
        # each thread writes a different value to the same key
        empty_table[key] = val

    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = [ex.submit(worker_write, v) for v in values_to_write]
        for f in as_completed(futures):
            f.result()

    # length should have increased by exactly 1
    assert len(empty_table) == initial_len + 1
    assert key in empty_table
    # final value must be one of the written values
    assert empty_table[key] in set(values_to_write)


def test_keys_items_values_views_or_snapshots(empty_table: ThreadSafeHashTable) -> None:
    """Ensure keys/items/values return usable collections."""
    table = empty_table
    for i in range(10):
        table[i] = i

    # Try to introspect expected view types; fall back to list if not provided.
    try:
        from collections.abc import KeysView, ItemsView, ValuesView  # type: ignore

        keys_obj = table.keys()
        items_obj = table.items()
        values_obj = table.values()
        # If view objects present, they should be iterable and have correct lengths
        assert len(keys_obj) == len(table)
        assert len(items_obj) == len(table)
        assert len(values_obj) == len(table)
    except Exception:
        # Fallback: ensure snapshot lists behave sensibly
        keys_list = list(table.keys())
        items_list = list(table.items())
        values_list = list(table.values())
        assert len(keys_list) == len(table)
        assert len(items_list) == len(table)
        assert len(values_list) == len(table)


# @pytest.mark.skipif(os.getenv("RUN_STRESS", "0") != "1", reason="Stress test skipped unless RUN_STRESS=1")
def test_full_stress_5m_operations():
    """
    Optional stress test: 5,000,000 operations with a high read ratio.
    Enabled by setting environment variable RUN_STRESS=1.
    """
    threads = 16
    n_ops = 5_000_000
    table = ThreadSafeHashTable(size=512)

    # preload some keys
    for k in range(20000):
        table[k] = k
    ops_per_thread = n_ops // threads

    def worker(seed: int) -> tuple[int, int, int]:
        rng = random.Random(seed)
        reads = writes = deletes = 0
        for _ in range(ops_per_thread):
            r = rng.random()
            k = rng.randint(0, 30000)
            if r < 0.75:
                reads += 1
                try:
                    _ = table[k]
                except KeyError:
                    pass
            elif r < 0.95:
                writes += 1
                table[k] = k + seed
            else:
                deletes += 1
                try:
                    del table[k]
                except KeyError:
                    pass
        return reads, writes, deletes

    start = time.time()
    with ThreadPoolExecutor(max_workers=threads) as ex:
        futures = [ex.submit(worker, i) for i in range(threads)]
        for f in as_completed(futures):
            f.result()
    duration = time.time() - start
    print(f"Stress test completed in {duration:.2f}s")
