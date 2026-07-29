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