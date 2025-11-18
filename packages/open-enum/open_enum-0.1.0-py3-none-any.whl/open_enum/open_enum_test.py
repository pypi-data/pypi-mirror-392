from typing import assert_never
import pytest
from open_enum import OpenEnum


class Status(OpenEnum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"

    UNKNOWN = None


# Known values
new = Status.NEW
done = Status.DONE

# Unknown values
blocked = Status("blocked")
cancelled = Status("cancelled")


def test_member_list():
    assert list(Status) == [Status.NEW, Status.IN_PROGRESS, Status.DONE]


def test_basic_equality():
    assert Status("new") == new
    assert Status("new") != done


def test_subtyping():
    assert isinstance(blocked, Status)


def test_value_equality():
    assert blocked == Status("blocked")
    assert blocked != new
    assert blocked != cancelled


def test_unknown_subtyping():
    assert not isinstance(Status.UNKNOWN, Status)


def test_unknown_equality():
    assert Status.UNKNOWN == Status("blocked")
    assert Status.UNKNOWN == Status("cancelled")
    assert Status.UNKNOWN != Status("new")
    assert Status.UNKNOWN != Status("in_progress")


@pytest.mark.parametrize(
    "input,output",
    [
        ("new", "new"),
        ("in_progress", "in progress"),
        ("done", "done and done"),
        ("cancelled", "unknown: cancelled"),
        ("closed", "unknown: closed"),
    ],
)
def test_pattern_matching_simple(input, output):
    status = Status(input)

    match status:
        case Status.NEW:
            result = "new"
        case Status.IN_PROGRESS:
            result = "in progress"
        case Status.DONE:
            result = "done and done"
        case Status.UNKNOWN:
            result = f"unknown: {status._value_}"
        case _:
            assert_never(status)

    assert result == output


@pytest.mark.parametrize(
    "input,output",
    [
        ("new", "known value"),
        ("in_progress", "known value"),
        ("done", "known value"),
        ("cancelled", "custom value"),
        ("blocked", "custom value"),
        ("cursed", "unknown value"),
    ],
)
def test_pattern_matching_multiple(input, output):
    status = Status(input)

    match status:
        case Status.NEW | Status("in_progress") | Status.DONE:
            result = "known value"
        case Status("blocked") | Status("cancelled"):
            result = "custom value"
        case Status.UNKNOWN:
            result = "unknown value"
        case _:
            assert_never(status)

    assert result == output


def test_unknown_only_matches_own_type():
    class Color(OpenEnum):
        RED = "red"
        GREEN = "green"

        UNKNOWN = None

    mauve = Color("mauve")
    assert mauve == Color.UNKNOWN
    assert mauve != Status.UNKNOWN

    assert blocked == Status.UNKNOWN
    assert blocked != Color.UNKNOWN

    assert Color.UNKNOWN != Status.UNKNOWN


def test_custom_name_for_undefined():
    class Color(OpenEnum):
        RED = "red"
        NOT_RED = None

    mauve = Color("mauve")
    assert mauve != Color.RED
    assert mauve == Color.NOT_RED
