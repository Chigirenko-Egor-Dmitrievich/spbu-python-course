import pytest
from project.assignment_3.curry_uncurry import curry_explicit, uncurry_explicit


def test_curry_multiple_arity():
    """The multi-arity function currying test"""

    def sumi(a, b, c, d):
        return a + b + c + d

    curried = curry_explicit(sumi, 4)
    assert curried(1)(2)(3)(4) == 10


def test_curry_single_arity():
    """The single-arity function currying test"""

    def squaring(x):
        return x**2

    curried = curry_explicit(squaring, 1)
    assert curried(10) == 100


def test_curry_zero_arity():
    """The non-arity function currying test"""

    def the_Ultimate_Question_of_Life__the_Universe__and_Everything():
        return "The Answer is: 42"

    curried = curry_explicit(
        the_Ultimate_Question_of_Life__the_Universe__and_Everything, 0
    )
    assert curried() == "The Answer is: 42"


def test_check_curry_one_at_the_time():
    "The test for checking whether more than one at the time argument giving for currying is possible"

    f = curry_explicit((lambda x, y, z: f"<{x},{y},{z}>"), 3)
    assert f(123)(456)(789) == "<123,456,789>"

    with pytest.raises(TypeError, match="takes 1 positional argument but 2 were given"):
        f(123, 456)(789)

    with pytest.raises(TypeError, match="takes 1 positional argument but 2 were given"):
        f(123)(456, 789)

    with pytest.raises(TypeError, match="takes 1 positional argument but 3 were given"):
        f(123, 456, 789)


def test_error_check_curry_negative_arity():
    """The error test for checking whether the negative arity for currying is possible"""

    def func(x):
        return x

    with pytest.raises(ValueError, match="Arity must be a non-negative number"):
        curry_explicit(func, -1)


def test_error_check_curry_too_many_arguments():
    """The error test for checking whether more than number of arity arguments for currying is possible"""

    def multi(a, b, c, d):
        return a * b * c * d

    curried = curry_explicit(multi, 4)
    with pytest.raises(TypeError, match="'int' object is not callable"):
        curried(1)(2)(3)(4)(5)


def test_curry_builtin_functions():
    """The built-in functions currying test"""

    curried_len = curry_explicit(len, 1)
    assert curried_len("Hi") == 2
    assert curried_len("Hello") == 5
    assert curried_len("Greetings!") == 10

    curried_join = curry_explicit(" ".join, 1)
    assert curried_join(["Hi", "Marry"]) == "Hi Marry"
    assert curried_join(["Hello", "Mr.", "Jeorge"]) == "Hello Mr. Jeorge"
    assert curried_join(["Greetings", "Mrs.", "Penny", "!"]) == "Greetings Mrs. Penny !"

    curried_map = curry_explicit(map, 2)
    assert list(curried_map(lambda x: x**2)(range(1, 6))) == [1, 4, 9, 16, 25]
    assert list(curried_map(lambda x: x[0])([(1, 2), (3, 4), (5, 6)])) == [1, 3, 5]


def test_curry_arbitrary_arity():
    """The arbitrary arity function currying test"""

    curried_max = curry_explicit(max, 4)
    assert curried_max(1)(5)(10)(50) == 50
    assert curried_max(-20)(10)(20)(-10) == 20

    curried_min = curry_explicit(min, 5)
    assert curried_min(-2)(2)(0)(1)(-1) == -2
    assert curried_min(1)(2)(0)(1)(2) == 0


def test_curry_uncurry():
    """The function currying and uncurrying test"""

    def original(a, b, c):
        return a + b * c

    curried = curry_explicit(original, 3)
    uncurried = uncurry_explicit(curried, 3)

    assert uncurried(1, 2, 3) == original(1, 2, 3)

    curried_abs = curry_explicit(abs, 1)
    uncurried_abs = uncurry_explicit(curried_abs, 1)

    assert uncurried_abs(-2) == abs(-2)
    assert uncurried_abs(2) == abs(-2)


def test_uncurry_multiple_arity():
    """The multi-arity function uncurrying test"""

    def curried_multiply(a):
        return lambda b: lambda c: a * b * c

    uncurried = uncurry_explicit(curried_multiply, 3)
    assert uncurried(1, 2, 3) == 6


def test_uncurry_single_arity():
    """The single-arity function uncurrying test"""

    def curried_cubing(x):
        return x**3

    uncurried = uncurry_explicit(curried_cubing, 1)
    assert uncurried(10) == 1000


def test_uncurry_zero_arity():
    """The non-arity function uncurrying test"""

    def curried_What_is_Power__Brother():
        return "Truth to Power, Brother"

    uncurried = uncurry_explicit(curried_What_is_Power__Brother, 0)
    assert uncurried() == "Truth to Power, Brother"


def test_error_check_uncurry_negative_arity():
    """The error test for checking whether the negative arity for uncurrying is possible"""

    def curried_func(x):
        return x

    with pytest.raises(ValueError, match="Arity must be a non-negative number"):
        uncurry_explicit(curried_func, -1)


def test_error_check_uncurry_wrong_arity():
    """The error test for checking whether the wrong arity for uncurrying is possible"""

    def curried_add(a):
        return lambda b: a + b

    uncurried = uncurry_explicit(curried_add, 2)
    with pytest.raises(
        ValueError,
        match="The curried function expects 2 arguments, but 1 argument is given",
    ):
        uncurried(1)
