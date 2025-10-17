import copy
from collections import OrderedDict
import pytest
from project.assignment_3.decorators import (
    cache_function,
    smart_args,
    Evaluated,
    Isolated,
)


def _get_cache_from_wrapped(wrapped):
    """Helper: извлечь OrderedDict cache из closure wrapped-функции."""
    if wrapped.__closure__ is None:
        return None
    for cell in wrapped.__closure__:
        try:
            val = cell.cell_contents
        except ValueError:
            continue
        if isinstance(val, OrderedDict):
            return val
    return None


def test_cache_function_adds_and_removes_oldest_and_counts_calls(capsys):
    """Проверяем, что cache_function добавляет элементы, удаляет самый старый
    и что декорируемая функция вызывается только при промахе кэша."""
    calls = {"n": 0}

    def base_fn(x):
        calls["n"] += 1
        return x * 10

    wrapped = cache_function(limit=2)(base_fn)

    # нет кэша до первого вызова
    assert _get_cache_from_wrapped(wrapped) is not None

    # первый вызов — промах
    assert wrapped(1) == 10
    assert calls["n"] == 1
    cache = _get_cache_from_wrapped(wrapped)
    assert len(cache) == 1
    # ключ должен соответствовать (args_tuple, frozenset(kwargs.items()))
    keys = list(cache.keys())
    assert keys[0][0] == (1,)
    assert keys[0][1] == frozenset()

    # второй вызов с другим аргументом — добавится
    assert wrapped(2) == 20
    assert calls["n"] == 2
    assert len(cache) == 2
    keys = list(cache.keys())
    assert keys[0][0] == (1,)
    assert keys[1][0] == (2,)

    # обращение к уже кешированному ключу — не увеличивает calls, и перемещает в конец
    assert wrapped(1) == 10
    assert calls["n"] == 2  # не вызов функции — использован кэш
    keys_after_hit = list(cache.keys())
    # теперь порядок: 2 (старый) , 1 (после move_to_end)
    assert keys_after_hit[0][0] == (2,)
    assert keys_after_hit[1][0] == (1,)

    # добавление третьего элемента — должен удалиться самый старый (2)
    assert wrapped(3) == 30
    # при добавлении будет печататься удаление — проверим наличие сообщения
    captured = capsys.readouterr()
    assert "Removing the oldest element" in captured.out
    keys_after = list(cache.keys())
    assert len(keys_after) == 2
    # ожидаемые ключи: (1,) и (3,)
    assert keys_after[0][0] == (1,)
    assert keys_after[1][0] == (3,)


def test_cache_function_counts_separately_for_unhashable_args():
    """Проверяем, что не-хэшируемые аргументы (list, dict, set, bytearray)
    корректно конвертируются в ключи и кэш работает (т.е. повторный вызов — cache hit)."""
    counters = {"list": 0, "dict": 0, "set": 0, "ba": 0}

    def fn_list(x):
        counters["list"] += 1
        return tuple(x)

    def fn_dict(d):
        counters["dict"] += 1
        return "".join(sorted(d.keys()))

    def fn_set(s):
        counters["set"] += 1
        return len(s)

    def fn_ba(b):
        counters["ba"] += 1
        return bytes(b)

    wrapped_list = cache_function(limit=5)(fn_list)
    wrapped_dict = cache_function(limit=5)(fn_dict)
    wrapped_set = cache_function(limit=5)(fn_set)
    wrapped_ba = cache_function(limit=5)(fn_ba)

    l = [1, 2]
    assert wrapped_list(l) == (1, 2)
    assert wrapped_list(l) == (1, 2)
    assert counters["list"] == 1  # второй вызов — из кэша

    d = {"b": 2, "a": 1}
    assert wrapped_dict(d) == "ab"
    assert wrapped_dict(d) == "ab"
    assert counters["dict"] == 1

    s = {1, 2, 3}
    assert wrapped_set(s) == 3
    assert wrapped_set(s) == 3
    assert counters["set"] == 1

    ba = bytearray(b"hi")
    assert wrapped_ba(ba) == b"hi"
    assert wrapped_ba(ba) == b"hi"
    assert counters["ba"] == 1


def test_cache_function_with_builtin_function():
    """Проверка: кэширование декорирует и встроенные функции (например, len)."""
    wrapped_len = cache_function(limit=3)(len)
    assert wrapped_len("abc") == 3
    assert wrapped_len("abc") == 3  # hit
    assert wrapped_len("hello") == 5


def make_counter(start=0):
    state = {"n": start}

    def inc():
        state["n"] += 1
        return state["n"]

    return inc


def test_smart_args_evaluated_keyword_and_positional_defaults():
    """Evaluated() — вычисляется при каждом вызове (для kw-only и позиционных дефолтов)."""
    cnt1 = make_counter()
    cnt2 = make_counter()

    @smart_args
    def f_pos(a=Evaluated(cnt1)):
        return a

    @smart_args
    def f_kw(*, b=Evaluated(cnt2)):
        return b

    v1 = f_pos()
    v2 = f_pos()
    assert v1 != v2  # каждый вызов даёт новое значение

    w1 = f_kw()
    w2 = f_kw()
    assert w1 != w2


def test_smart_args_plain_default_evaluated_once_at_definition_time():
    """Обычное значение по умолчанию, вычисленное как вызов (not Evaluated), остаётся фиксированным."""
    cnt = make_counter()

    # обычный вызов функции при определении — выполнится один раз
    fixed_default = cnt()

    @smart_args
    def f(a=fixed_default):
        return a

    assert f() == fixed_default
    assert f() == fixed_default


def test_smart_args_isolated_deepcopy_and_no_change_original():
    """Isolated() должен заставить делать deepcopy перед передачей — оригинал не меняется."""

    @smart_args
    def mutate_kw(*, d=Isolated()):
        # функция изменяет переданный словарь
        d["changed"] = True
        return d

    original = {"changed": False, "x": 1}
    returned = mutate_kw(d=original)
    assert returned["changed"] is True
    # оригинальный объект не должен быть изменён
    assert original["changed"] is False


def test_smart_args_isolated_missing_kw_raises_and_positional_isolated_raises():
    """Если Isolated() стоит как kw-only default и не передали kw — ValueError;
    если Isolated() стоит как позиционный default и не передан — ValueError."""

    @smart_args
    def kw_only(*, d=Isolated()):
        return d

    with pytest.raises(ValueError, match="Isolated has not been passed"):
        kw_only()  # не передали d

    @smart_args
    def pos(a=Isolated()):
        return a

    # отсутствие переданного позиционного значения вызывает ту же ошибку
    with pytest.raises(
        ValueError,
        match="positional argument with default value Isolated has not been passed|Isolated has not been passed",
    ):
        pos()


def test_smart_args_evaluated_and_isolated_combination_asserts():
    """Комбинация Evaluated(Isolated) (и наоборот) запрещена — генерируется AssertionError."""
    # kw-only case
    @smart_args
    def f1(*, x=Evaluated(Isolated)):
        return x

    # positional case
    @smart_args
    def f2(a=Evaluated(Isolated)):
        return a

    with pytest.raises(AssertionError):
        f1()

    with pytest.raises(AssertionError):
        f2()


def test_smart_args_override_default_and_both_positional_and_kw_work():
    """Проверяем, что можно явно передавать значение вместо Evaluated default,
    и что одновременно работают позиционные и именованные Evaluated-значения."""
    cnt_a = make_counter()
    cnt_b = make_counter()

    @smart_args
    def mix(a=Evaluated(cnt_a), *, b=Evaluated(cnt_b)):
        return a, b

    # вызов по умолчанию — оба Evaluated вычисляются
    a1, b1 = mix()
    a2, b2 = mix()
    assert a1 != a2
    assert b1 != b2

    # можно подставить явно значение для позиции
    a_fixed, b_next = mix(999)
    assert a_fixed == 999
