"""
Hash Table implementation with Binary Search Tree collision resolution.

This module provides a hash table implementation that uses separate chaining
with Binary Search Trees (BST) to handle key collisions. The implementation
conforms to the MutableMapping ABC, providing dictionary-like interface.

Classes:
    BSTNode: Node for Binary Search Tree storing key-value pairs.
    BST: Binary Search Tree implementation with dictionary interface.
    HashTable: Hash table using BSTs for collision resolution.
"""

from collections.abc import MutableMapping
from typing import Generator, Any, Optional, Iterator, Tuple, List


class BSTNode:
    """Node for Binary Search Tree storing key-value pairs."""

    def __init__(self, key: Any, value: Any) -> None:
        """
        Initialize an empty Binary Search Tree node.

        Args:
            key: The key used for ordering in the BST
            value: The value associated with the key"""

        self.key: Any = key
        self.value: Any = value
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None


class BST(MutableMapping):
    """Binary Search Tree implementation with dictionary interface."""

    def __init__(self) -> None:
        """
        Initialize an empty Binary Search Tree.
        """

        self.root: Optional[BSTNode] = None
        self._count_: int = 0

    def __getitem__(self, key: Any) -> Any:
        """
        Get the value associated with the given key.

        Args:
            key: The key to search for

        Returns:
            The value associated with the key

        Raises:
            KeyError: If the key is not found in the BST
        """

        return self._find_(self.root, key).value

    def _find_(self, node: Optional[BSTNode], key: Any) -> BSTNode:
        """
        Recursively find the node containing the given key.

        Args:
            node: Current node in the recursion
            key: The key to search for

        Returns:
            The node containing the key

        Raises:
            KeyError: If the key is not found in the BST
        """

        if node is None:
            raise KeyError(f"Key {key} is not found")

        if key < node.key:
            return self._find_(node.left, key)
        elif key > node.key:
            return self._find_(node.right, key)
        else:
            return node

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set the value for the given key, inserting if not present.

        Args:
            key: The key to set or insert
            value: The value to associate with the key
        """

        self.root = self._insert_(self.root, key, value)

    def _insert_(self, node: Optional[BSTNode], key: Any, value: Any) -> BSTNode:
        """
        Recursively insert or update a key-value pair in the BST.

        Args:
            node: Current node in the recursion
            key: The key to insert or update
            value: The value to associate with the key

        Returns:
            The root node of the (sub)tree after insertion
        """

        if node is None:
            self._count_ += 1
            return BSTNode(key, value)

        if key < node.key:
            node.left = self._insert_(node.left, key, value)
        elif key > node.key:
            node.right = self._insert_(node.right, key, value)
        else:
            node.value = value

        return node

    def __delitem__(self, key: Any) -> None:
        """
        Remove the key-value pair for the given key.

        Args:
            key: The key to remove

        Raises:
            KeyError: If the key is not found in the BST
        """

        self.root = self._delete_(self.root, key)
        self._count_ -= 1

    def _delete_(self, node: Optional[BSTNode], key: Any) -> Optional[BSTNode]:
        """
        Recursively delete the node with the given key.

        Args:
            node: Current node in the recursion
            key: The key to delete

        Returns:
            The root node of the (sub)tree after deletion

        Raises:
            KeyError: If the key is not found in the BST
        """

        if node is None:
            raise KeyError(f"Key {key} is not found")

        if key < node.key:
            node.left = self._delete_(node.left, key)
        elif key > node.key:
            node.right = self._delete_(node.right, key)
        else:
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            else:
                min_node = self._find_min_(node.right)
                node.key = min_node.key
                node.value = min_node.value
                node.right = self._delete_(node.right, min_node.key)

        return node

    def _find_min_(self, node: BSTNode) -> BSTNode:
        """
        Find the node with the minimum key in the given subtree.

        Args:
            node: The root node of the subtree to search

        Returns:
            The node with the minimum key in the subtree
        """

        while node.left is not None:
            node = node.left
        return node

    def __iter__(self) -> Generator[Any, None, None]:
        """
        Iterate over keys in ascending order (in-order traversal).

        Yields:
            Keys in ascending order
        """

        yield from self._in_order_(self.root)

    def _in_order_(self, node: Optional[BSTNode]) -> Generator[Any, None, None]:
        """
        Generate keys using in-order traversal.

        Args:
            node: Current node in the recursion

        Yields:
            Keys in ascending order
        """

        if node is not None:
            yield from self._in_order_(node.left)
            yield node.key
            yield from self._in_order_(node.right)

    def __reversed__(self) -> Generator[Any, None, None]:
        """
        Iterate over keys in descending order (reverse in-order traversal).

        Yields:
            Keys in descending order
        """

        yield from self._reverse_order_(self.root)

    def _reverse_order_(self, node: Optional[BSTNode]) -> Generator[Any, None, None]:
        """
        Generate keys using reverse in-order traversal.

        Args:
            node: Current node in the recursion

        Yields:
            Keys in descending order
        """

        if node is not None:
            yield from self._reverse_order_(node.right)
            yield node.key
            yield from self._reverse_order_(node.left)

    def __contains__(self, key: Any) -> bool:
        """
        Check if the key exists in the BST.

        Args:
            key: The key to check for existence

        Returns:
            True if key exists, False otherwise
        """

        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def __len__(self) -> int:
        """
        Get the number of elements in the BST.

        Returns:
            The number of key-value pairs in the BST
        """

        return self._count_


class HashTable(MutableMapping):
    """Hash table implementation using BST for collision resolution."""

    def __init__(self, size: int = 100) -> None:
        """
        Initialize the hash table with specified number of buckets.

        Args:
            size: The number of buckets in the hash table. Defaults to 100.
                  Larger sizes reduce collisions but use more memory."""

        self.size: int = size
        self.buckets: List[BST] = [BST() for _ in range(size)]
        self._count_: int = 0

    def _get_bucket_index_(self, key: Any) -> int:
        """
        Calculate the bucket index for a given key.

        Args:
            key: The key to calculate index for

        Returns:
            The bucket index (from 0 to size-1)
        """

        return hash(key) % self.size

    def _get_bucket_(self, key: Any) -> BST:
        """
        Get the bucket (BST) for a given key.

        Args:
            key: The key to get bucket for

        Returns:
            The BST bucket for the key
        """

        index = self._get_bucket_index_(key)
        return self.buckets[index]

    def __getitem__(self, key: Any) -> Any:
        """
        Get the value associated with the given key.

        Args:
            key: The key to search for

        Returns:
            The value associated with the key

        Raises:
            KeyError: If the key is not found in the hash table
        """

        bucket = self._get_bucket_(key)
        return bucket[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set the value for the given key, inserting if not present.

        Args:
            key: The key to set or insert
            value: The value to associate with the key
        """

        bucket = self._get_bucket_(key)
        old_len = len(bucket)
        bucket[key] = value
        if len(bucket) > old_len:
            self._count_ += 1

    def __delitem__(self, key: Any) -> None:
        """
        Remove the key-value pair for the given key.

        Args:
            key: The key to remove

        Raises:
            KeyError: If the key is not found in the hash table
        """

        bucket = self._get_bucket_(key)
        del bucket[key]
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
            yield from bucket

    def __reversed__(self) -> Generator[Any, None, None]:
        """
        Iterate over all keys in reverse order.

        Keys are yielded bucket by bucket in reverse order, with keys
        in each bucket yielded in descending order.

        Yields:
            All keys in the hash table in reverse order
        """

        for bucket in reversed(self.buckets):
            yield from reversed(bucket)

    def __contains__(self, key: Any) -> bool:
        """
        Check if the key exists in the hash table.

        Args:
            key: The key to check for existence

        Returns:
            True if key exists, False otherwise
        """

        bucket = self._get_bucket_(key)
        return key in bucket

    def __len__(self) -> int:
        """
        Get the number of elements in the hash table.

        Returns:
            The number of key-value pairs in the hash table
        """

        return self._count_

    def __str__(self) -> str:
        """
        Get a string representation of the hash table contents.

        Returns:
            A formatted string showing all key-value pairs
        """

        result = "HashTable:\n"
        for key in self:
            result += f"Key: {key}, Value: {self[key]}\n"
        return result
