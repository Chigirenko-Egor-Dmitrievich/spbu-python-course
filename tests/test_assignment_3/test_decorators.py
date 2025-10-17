import pytest
from project.assignment_3.decorators import (
    smart_args,
    cache_function,
    Evaluated,
    Isolated,
)


def test_cache():
    """The test for basic cache behavior test"""
    counter = 0

    @cache_function(limit=2)
    def multiply(x):
        nonlocal counter
        counter += 1
        return x * 2

    assert multiply(2) == 4
    assert counter == 1

    assert multiply(2) == 4
    assert counter == 1


def test_cache_limit():
    """The test for the cache limit"""
    counter = 0

    @cache_function(limit=2)
    def identity(x):
        nonlocal counter
        counter += 1
        return x

    identity(1)
    identity(2)
    identity(3)

    identity(1)
    assert counter == 4


def test_check_cache_history():
    """The test for checking whether the cache function deletes the oldest data upon exceeding limit"""
    counter = 0

    @cache_function(limit=2)
    def squaring(x):
        nonlocal counter
        counter += 1
        return x * x

    squaring(1)
    assert counter == 1
    squaring(2)
    assert counter == 2
    squaring(2)
    assert counter == 2
    squaring(3)
    assert counter == 3
    squaring(1)
    assert counter == 4


def test_cache_with_builtins():
    """The test for caching of builtin functions"""

    len_count = 0
    print_count = 0

    @cache_function(limit=2)
    def cach_len(x):
        nonlocal len_count
        len_count += 1
        return len(x)

    @cache_function(limit=2)
    def cach_print(x):
        nonlocal print_count
        print_count += 1
        return print(x)

    cach_len("MIN")
    assert len_count == 1
    cach_len("MAX")
    assert len_count == 2
    cach_len("MIN")
    assert len_count == 2

    cach_print("Sentence")
    assert print_count == 1
    cach_print("Another sentence")
    assert print_count == 2
    cach_print("Sentence")
    assert print_count == 2


def test_evaluated_default_keywords():
    """The test for Evaluated default for keyword-only arguments"""
    gen = (i for i in range(2))

    def next_item():
        return next(gen)

    @smart_args(allow_pos_args=False)
    def check_eval(*, value=Evaluated(next_item)):
        return value

    assert check_eval() == 0
    assert check_eval() == 1
    assert check_eval(value=10) == 10


def test_isolated_default_keywords():
    """The test for Isolated default for keyword-only arguments"""

    @smart_args(allow_pos_args=False)
    def check_isolated(*, d=Isolated()):
        d["a"] = 0
        return d

    no_mutable = {"a": 10}
    assert check_isolated(d=no_mutable) == {"a": 0}


def test_evaluated_default_positional_args():
    """The test for Evaluated defaults for positional arguments when enabled"""
    counter = 0

    def to_count():
        nonlocal counter
        counter += 2
        return counter

    @smart_args()
    def func(a=Evaluated(to_count)):
        return a

    assert func() == 2
    assert func() == 4


def test_isolated_default_positional_args():
    """The test for Isolated default for positional arguments"""

    @smart_args()
    def func(a=Isolated()):
        a.append("4")
        return a

    lst = [1, 2, 3]

    assert func(lst) == [1, 2, 3, "4"]
    assert lst == [1, 2, 3]


def test_error_check_isolated_kwarg_requirement():
    """The error test for Isolated defaults for keyword args that must be explicitly provided"""

    @smart_args(allow_pos_args=False)
    def requires_isolated(*, data=Isolated()):
        return data

    with pytest.raises(
        ValueError,
        match="A keyword argument with default value Isolated has not been passed",
    ):
        requires_isolated()


def test_error_check_conflict_evaluated_isolated():
    """The error test for checking whether Evaluated and Isolated could be combined on the same parameter"""

    @smart_args(allow_pos_args=False)
    def conflict(*, data=Evaluated(Isolated)):
        return data

    with pytest.raises(
        AssertionError, match="It is forbidden to combine Evaluated and Isolated"
    ):
        conflict()


def test_mixed_args_cache_and_smart_args():
    """The complex test that mixing positional, keyword, caching, and smart args"""
    counter_a = 0
    counter_b = 0

    def count_a():
        nonlocal counter_a
        counter_a += 1
        return counter_a

    def count_b():
        nonlocal counter_b
        counter_b += 1
        return counter_b

    @cache_function(limit=5)
    @smart_args()
    def complex_fn(
        a=Isolated(), b=Evaluated(count_a), *, x=Evaluated(count_b), y=Isolated()
    ):
        a.append(f"changed_{b}")
        y["new"] = f"changed_{x}"
        return a, y

    seq = [1, 2]
    kwdict = {"a": 0}

    res_a, res_y = complex_fn(seq, y=kwdict)
    assert res_a == [1, 2, "changed_1"]
    assert res_y == {"a": 0, "new": "changed_1"}
    assert seq == [1, 2]
    assert kwdict == {"a": 0}

    res_a2, res_y2 = complex_fn(seq, y=kwdict)
    assert res_a2 == [1, 2, "changed_2"]
    assert res_y2 == {"a": 0, "new": "changed_2"}


def test_check_non_default_and_defaults_mix():
    """The test for checking whether args and defaulted args could be mixed"""

    @smart_args()
    def f(first, second=Isolated(), *, kw1, kw2=Evaluated(lambda: "Nothing!")):
        second.append(first)
        return {"1st": first, "2nd": second, "kw1": kw1, "kw2": kw2}

    isolated = ["a"]

    result = f(20, isolated, kw1=5)
    assert result["1st"] == 20
    assert result["2nd"] == ["a", 20]
    assert isolated == ["a"]
    assert result["kw1"] == 5
    assert result["kw2"] == "Nothing!"
