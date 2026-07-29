import pytest
from exam_mode.extract_constraints import extract_exam_metadata


@pytest.mark.llm
def test_extraction_handles_no_constraints_or_examples():
    instructions = "Write a function factorial(n) that computes the factorial of a non-negative integer n."
    metadata = extract_exam_metadata(instructions)
    assert isinstance(metadata["banned_names"], list)
    assert isinstance(metadata["test_cases"], list)
    assert metadata["banned_names"] == []
    assert metadata["test_cases"] == []

@pytest.mark.llm
def test_extraction_handles_multiple_examples():
    instructions = """
    Write a program that reads an integer n, then a list of n integers, and prints
    them sorted in ascending order using the bubble sort algorithm. Do not use
    sort() or sorted().

    Examples:
    - Given n=5 and the list [5, 2, 4, 1, 3], the output should be: 1 2 3 4 5
    - Given n=3 and the list [10, -1, 4], the output should be: -1 4 10
    - Given n=1 and the list [42], the output should be: 42
    """
    metadata = extract_exam_metadata(instructions)
    assert len(metadata["test_cases"]) == 3
    assert metadata["banned_names"] == ["sort", "sorted"] or set(metadata["banned_names"]) == {"sort", "sorted"}