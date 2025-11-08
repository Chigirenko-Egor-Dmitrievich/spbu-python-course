"""
Thread-safe hash table based on a Binary Search Tree (BST) per bucket.

This module provides:
- BST: a simple binary search tree storing (key, value) pairs.
- HashTable: a hash table using BST objects as buckets.
- ThreadSafeHashTable: a thread-safe wrapper around HashTable using per-bucket locks.

Important notes:
- ThreadSafeHashTable does not use multiprocessing.Manager and is intended for
  multithreaded use (shared-memory threads).
- Single-key operations use one per-bucket RLock to avoid race conditions while minimizing contention.
- Global operations that need a consistent view (e.g. snapshot of keys, computing length)
  acquire all bucket locks in a fixed order to avoid deadlocks.
"""

from collections.abc import MutableMapping
from typing import Optional, Generator, Iterator, Tuple, List, Any
import threading


class BSTNode:
    """Node for Binary Search Tree storing key-value pairs."""

    slots = ("key", "value", "left", "right")

    def __init__(self, key: Any, value: Any) -> None:
        """
        Initialize a BST node with given key and value.

        Args:
            key: Key stored in the node.
            value: Value associated with the key.
        """

        self.key: Any = key
        self.value: Any = value
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None


class BST:
    """Binary Search Tree implementation with dictionary interface."""

    def __init__(self) -> None:
        """Create an empty BST."""

        self._root: Optional[BSTNode] = None
        self._size: int = 0
        self._lock = threading.RLock()

    def __len__(self) -> int:
        """
        Return the number of nodes (key-value pairs) stored in the tree.

        Returns:
            int: size of the tree
        """

        return self._size

    def _insert_(self, key: Any, value: Any) -> bool:
        """
        Insert or update the value for 'key'.

        If the key is new, it increases the tree size and returns True.
        If the key existed, update the value and return False.

        Args:
            key: Key to insert or update.
            value: Value to associate with the key.

        Returns:
            bool: True if a new key was inserted, False if an existing key was updated.
        """

        with self._lock:
            if self._root is None:
                self._root = BSTNode(key, value)
                self._size = 1
                return True

            node = self._root
            while True:
                if key == node.key:
                    node.value = value
                    return False
                elif key < node.key:
                    if node.left is None:
                        node.left = BSTNode(key, value)
                        self._size += 1
                        return True
                    node = node.left
                else:
                    if node.right is None:
                        node.right = BSTNode(key, value)
                        self._size += 1
                        return True
                    node = node.right

    def _find_(self, key: Any) -> Any:
        """
        Find and return the value associated with 'key'.

        Args:
            key: Key to search for.

        Returns:
            The value associated with 'key'.

        Raises:
            KeyError: if key is not present.
        """

        with self._lock:
            node = self._root
            while node is not None:
                if key == node.key:
                    return node.value
                elif key < node.key:
                    node = node.left
                else:
                    node = node.right
            raise KeyError(key)

    def __contains__(self, key: Any) -> bool:
        """
        Check whether 'key' exists in the tree.

        Args:
            key: Key to check.

        Returns:
            True if key exists, False otherwise.
        """

        with self._lock:
            node = self._root
            while node is not None:
                if key == node.key:
                    return True
                elif key < node.key:
                    node = node.left
                else:
                    node = node.right
            return False

    def _delete_(self, key: Any) -> None:
        """
        Delete the node with 'key' from the tree.

        Args:
            key: Key to delete.

        Raises:
            KeyError: if key does not exist.
        """

        with self._lock:
            self._root, deleted = self._delete_rec_(self._root, key)
            if not deleted:
                raise KeyError(key)
            self._size -= 1

    def _delete_rec_(
        self, node: Optional[BSTNode], key: Any
    ) -> Tuple[Optional[BSTNode], bool]:
        """
        Recursive helper for delete.

        Args:
            node: Current subtree root.
            key: Key to delete.

        Returns:
            (new_node, deleted_flag): new subtree root and whether deletion happened.
        """

        if node is None:
            return None, False
        if key < node.key:
            node.left, deleted = self._delete_rec_(node.left, key)
            return node, deleted
        elif key > node.key:
            node.right, deleted = self._delete_rec_(node.right, key)
            return node, deleted
        else:
            # Node to delete found
            if node.left is None and node.right is None:
                return None, True
            if node.left is None:
                return node.right, True
            if node.right is None:
                return node.left, True
            # Both children exist: find successor (smallest in right subtree)
            succ_parent = node
            succ = node.right
            while succ.left:
                succ_parent = succ
                succ = succ.left
            node.key, node.value = succ.key, succ.value
            # Delete succ node
            if succ_parent is node:
                node.right, _ = self._delete_rec_(node.right, succ.key)
            else:
                succ_parent.left, _ = self._delete_rec_(succ_parent.left, succ.key)
            return node, True

    def keys(self) -> List[Any]:
        """
        Return a list of keys in ascending order.

        Returns:
            A list of keys (in-order traversal).
        """

        res: List[Any] = []
        with self._lock:
            self._in_order_(self._root, res)
        return res

    def _in_order_(self, node: Optional[BSTNode], out: List[Any]) -> None:
        """In-order traversal pushing keys into 'out'."""

        if node is None:
            return
        self._in_order_(node.left, out)
        out.append(node.key)
        self._in_order_(node.right, out)

    def __iter__(self) -> Iterator[Any]:
        """
        Iterate over keys in ascending order.

        Returns:
            An iterator over keys (snapshot).
        """

        return iter(self.keys())

    def items(self) -> List[Tuple[Any, Any]]:
        """
        Return a list of (key, value) pairs in ascending key order.

        Returns:
            List of tuples (key, value).
        """

        out: List[Tuple[Any, Any]] = []
        with self._lock:
            self._items_inorder_(self._root, out)
        return out

    def _items_inorder_(
        self, node: Optional[BSTNode], out: List[Tuple[Any, Any]]
    ) -> None:
        """In-order traversal pushing (key, value) pairs into 'out'."""

        if node is None:
            return
        self._items_inorder_(node.left, out)
        out.append((node.key, node.value))
        self._items_inorder_(node.right, out)

    def get(self, key: Any, default: Any = None) -> Any:
        """
        Get the value for 'key' or return default if not present.

        Args:
            key: Key to search.
            default: Value to return if key not found.

        Returns:
            Associated value or default.
        """

        try:
            return self._find_(key)
        except KeyError:
            return default


class HashTable(MutableMapping):
    """
    Hash table that uses BST objects as buckets.

    Each bucket is a separate BST. This class is not thread-safe by itself.
    Use ThreadSafeHashTable for concurrent access.
    """

    def __init__(self, size: int = 100) -> None:
        """
        Initialize HashTable with a specific number of buckets.

        Args:
            size: Number of buckets (must be positive).
        """

        if size <= 0:
            raise ValueError("size must be positive")
        self.size: int = int(size)
        self.buckets: List[BST] = [BST() for _ in range(self.size)]
        self._count_: int = 0  # total number of keys across all buckets

    def _get_bucket_index_(self, key: Any) -> int:
        """
        Calculate the bucket index for a given key.

        Args:
            key: The key to calculate index for

        Returns:
            The bucket index (from 0 to size-1)
        """

        return hash(key) % self.size

    def _get_bucket_(self, key: Any, default: Any = None) -> Any:
        """
        Get the value for key or return default if not present.

        Args:
            key: Key to search.
            default: Default value if key absent.

        Returns:
            Associated value or default.
        """

        try:
            return self.buckets[self._get_bucket_index_(key)]
        except KeyError:
            return default

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Insert or update a (key, value) pair in the hash table.

        Args:
            key: Key to set.
            value: Value to associate.
        """

        idx = self._get_bucket_index_(key)
        bucket = self.buckets[idx]
        was_new = bucket._insert_(key, value)
        if was_new:
            self._count_ += 1

    def __getitem__(self, key: Any) -> Any:
        """
        Retrieve value associated with key.

        Args:
            key: Key to retrieve.

        Returns:
            Associated value.

        Raises:
            KeyError: if key not present.
        """

        idx = self._get_bucket_index_(key)
        bucket = self.buckets[idx]
        return bucket._find_(key)

    def __delitem__(self, key: Any) -> None:
        """
        Delete a key from the hash table.

        Args:
            key: Key to delete.

        Raises:
            KeyError: if key not present.
        """

        idx = self._get_bucket_index_(key)
        bucket = self.buckets[idx]
        bucket._delete_(key)
        self._count_ -= 1

    def __iter__(self) -> Generator[Any, None, None]:
        """
        Iterate over all keys in the hash table.

        Keys are yielded bucket by bucket, with keys in each bucket
        yielded in ascending order.

        Yields:
            All keys in the hash table
        """

        for bucket in self.buckets:
            for i in bucket:
                yield i

    def __contains__(self, key: Any) -> bool:
        """
        Check if key exists in the table.

        Args:
            key: Key to check.

        Returns:
            True if present, False otherwise.
        """
        idx = self._get_bucket_index_(key)
        bucket = self.buckets[idx]
        return key in bucket

    def __len__(self) -> int:
        """
        Return the number of keys stored in the table.

        Returns:
            int: total key count
        """

        return self._count_

    def __repr__(self) -> str:
        """
        Return a short string representation of the table.

        Returns:
            str: representation.
        """

        return f"<HashTable size={self.size} count={len(self)}>"


class ThreadSafeHashTable(HashTable):
    """
    Thread-safe hash table wrapper using per-bucket locks.

    - Single-key operations (get/set/delete/contains) lock only the corresponding bucket.
    - Global operations (keys_snapshot, len) acquire all bucket locks in a fixed order
      to produce a consistent view without deadlocks.
    """

    def __init__(self, size: int = 100) -> None:
        """
        Initialize the thread-safe hash table.

        Args:
            size: Number of buckets (passed to HashTable).
        """
        super().__init__(size=size)
        self._locks: List[threading.RLock] = [
            threading.RLock() for _ in range(self.size)
        ]

    def _get_lock_for_key_(self, key: Any) -> threading.RLock:
        """
        Return the RLock object corresponding to the bucket for 'key'.

        Args:
            key: Key to locate bucket lock.

        Returns:
            threading.RLock for that bucket.
        """

        return self._locks[self._get_bucket_index_(key)]

    def _acquire_all_locks_in_order_(self) -> List[threading.RLock]:
        """
        Acquire all bucket locks in ascending bucket index order.

        Returns:
            List of locks that were acquired (in the order acquired).

        Note:
            Caller must release them (in reverse order) after use.
        """

        acquired: List[threading.RLock] = []
        try:
            for lock in self._locks:
                lock.acquire()
                acquired.append(lock)
            return acquired
        except Exception:
            # If acquiring fails for some reason, release acquired locks
            for l in reversed(acquired):
                l.release()
            raise

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Thread-safe insertion or update for a key.

        Locks only the corresponding bucket to allow parallel operations on other buckets.

        Args:
            key: Key to set.
            value: Value to associate.
        """

        lock = self._get_lock_for_key_(key)
        with lock:
            super().__setitem__(key, value)

    def __getitem__(self, key: Any) -> Any:
        """
        Thread-safe retrieval for a key.

        Args:
            key: Key to retrieve.

        Returns:
            Associated value.

        Raises:
            KeyError: if key not present.
        """

        lock = self._get_lock_for_key_(key)
        with lock:
            return super().__getitem__(key)

    def __delitem__(self, key: Any) -> None:
        """
        Thread-safe deletion for a key.

        Args:
            key: Key to delete.

        Raises:
            KeyError: if key not present.
        """

        lock = self._get_lock_for_key_(key)
        with lock:
            super().__delitem__(key)

    def __contains__(self, key: Any) -> bool:
        """
        Thread-safe membership test for a key.

        Args:
            key: Key to test.

        Returns:
            True if present, False otherwise.
        """

        lock = self._get_lock_for_key_(key)
        with lock:
            return super().__contains__(key)

    def __len__(self) -> int:
        """
        Thread-safe computation of the total number of keys.

        This method acquires all bucket locks in a fixed order and sums individual bucket sizes
        to return a consistent result.

        Returns:
            int: total key count
        """

        acquired = self._acquire_all_locks_in_order_()
        try:
            # Sum sizes of each bucket to avoid races with updates.
            total: int = sum(len(bucket) for bucket in self.buckets)
            return total
        finally:
            for l in reversed(acquired):
                l.release()

    def keys_snapshot(self) -> List[Any]:
        """
        Return a consistent snapshot (list) of all keys in the table.

        All bucket locks are acquired (in fixed order) to prevent concurrent modifications
        during snapshot creation.

        Returns:
            List of keys (order: buckets in index order, within bucket ascending by key).
        """

        acquired = self._acquire_all_locks_in_order_()
        try:
            keys: List[Any] = []
            for bucket in self.buckets:
                keys.extend(list(bucket))
            return keys
        finally:
            for l in reversed(acquired):
                l.release()
