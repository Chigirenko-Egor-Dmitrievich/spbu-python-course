from project.assignment_5.hash_table_bst import HashTable, BST
import pytest


@pytest.fixture
def some_hashtable():
    """Initializing the hash table for tests."""
    ht = HashTable(size=1)  # Use size=1 to ensure all keys go to same bucket
    ht[0] = "1"
    ht[-1] = "2"
    ht[1] = "3"
    ht[-2] = "4"
    ht[-0.5] = "5"
    return ht


@pytest.fixture
def empty_hashtable():
    """Initialize empty hash table."""
    return HashTable()


@pytest.mark.parametrize(
    "key,value",
    [
        (0, "1"),
        (-1, "2"),
        (1, "3"),
        (-2, "4"),
        (-0.5, "5"),
    ],
)
def test_getitem(some_hashtable, key, value):
    """Test that the value is returned by the key through square brackets."""
    assert some_hashtable[key] == value


def test_getitem_key_error(empty_hashtable):
    """Test that KeyError is raised for non-existent key."""
    with pytest.raises(KeyError):
        empty_hashtable["nonexistent"]


@pytest.mark.parametrize(
    "key,value",
    [
        (-10, "A"),
        (10, "B"),
        (-20, "C"),
        (-5, "D"),
    ],
)
def test_setitem(some_hashtable, key, value):
    """Test that the values are correctly assigned by the key."""
    some_hashtable[key] = value
    assert some_hashtable[key] == value


def test_update_key():
    """Test that when the value is set again, the previous one is replaced."""
    ht = HashTable()
    ht[5] = "value1"
    ht[5] = "value2"
    assert ht[5] == "value2"
    assert len(ht) == 1


def test_delete(some_hashtable):
    """Test that the elements are removed from the hash table."""
    assert len(some_hashtable) == 5
    del some_hashtable[-0.5]
    assert len(some_hashtable) == 4

    with pytest.raises(KeyError):
        some_hashtable[-0.5]


def test_delete_key_error(some_hashtable):
    """Test that KeyError is raised when deleting non-existent key."""
    with pytest.raises(KeyError):
        del some_hashtable[2]


def test_in_operator(some_hashtable):
    """Test that the in operator works correctly."""
    assert 1 in some_hashtable
    assert 3 not in some_hashtable


def test_empty_hashtable(empty_hashtable):
    """Test that an empty hash table has zero elements."""
    assert len(empty_hashtable) == 0


def test_iteration(some_hashtable):
    """Test that the iteration is working correctly."""
    # With size=1, keys should be in BST order
    expected_keys = [-2, -1, -0.5, 0, 1]
    actual_keys = list(some_hashtable)
    assert actual_keys == expected_keys


def test_reversed_iteration(some_hashtable):
    """Test that the reversed iteration is working correctly."""
    # With size=1, reversed keys should be in reverse BST order
    expected_keys = [1, 0, -0.5, -1, -2]
    actual_keys = list(reversed(some_hashtable))
    assert actual_keys == expected_keys


def test_str_hashtable(some_hashtable):
    """Test that the hash table is correctly represented as a string."""
    result = str(some_hashtable)
    assert "HashTable:" in result
    assert "Key: 0, Value: 1" in result
    assert "Key: 1, Value: 3" in result


def test_items(some_hashtable):
    """Test items() method returns key-value pairs."""
    items = list(some_hashtable.items())
    expected_items = [(-2, "4"), (-1, "2"), (-0.5, "5"), (0, "1"), (1, "3")]
    assert items == expected_items


def test_collision_resolution():
    """Test that collisions are properly handled using BST."""
    ht = HashTable(size=2)  # Small size to force collisions

    # Add keys that will likely cause collisions
    ht[1] = "1"
    ht[2] = "2"
    ht[3] = "3"
    ht[4] = "4"

    assert len(ht) == 4
    assert ht[1] == "1"
    assert ht[2] == "2"
    assert ht[3] == "3"
    assert ht[4] == "4"


def test_large_hashtable():
    """Test hash table with many elements."""
    ht = HashTable(size=10)

    # Add 100 elements
    for i in range(100):
        ht[f"key_{i}"] = f"value_{i}"

    assert len(ht) == 100

    # Verify all elements can be retrieved
    for i in range(100):
        assert ht[f"key_{i}"] == f"value_{i}"


def test_bst_operations():
    """Test BST operations directly."""
    bst = BST()

    # Test basic operations
    bst[5] = "five"
    bst[3] = "three"
    bst[7] = "seven"

    assert bst[5] == "five"
    assert bst[3] == "three"
    assert bst[7] == "seven"
    assert len(bst) == 3

    # Test deletion
    del bst[3]
    assert len(bst) == 2
    assert 3 not in bst

    # Test iteration
    keys = list(bst)
    assert keys == [5, 7]


def test_hash_table_bucket_distribution():
    """Test that keys are distributed across buckets."""
    ht = HashTable(size=5)

    # Add multiple keys
    for i in range(20):
        ht[f"key_{i}"] = i

    # Count non-empty buckets
    non_empty_buckets = sum(1 for bucket in ht.buckets if len(bucket) > 0)
    assert non_empty_buckets > 1  # Should have keys in multiple buckets


def test_repeated_operations():
    """Test repeated insertions and deletions."""
    ht = HashTable()

    # Repeatedly insert and delete
    for i in range(10):
        ht["key"] = f"value_{i}"
        assert ht["key"] == f"value_{i}"
        del ht["key"]
        assert "key" not in ht

    assert len(ht) == 0
