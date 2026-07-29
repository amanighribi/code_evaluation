import pytest
from exam_mode.sandbox_executor_java import run_java_in_sandbox


@pytest.mark.docker
def test_runs_simple_code_successfully():
    code = """
public class Hello {
    public static void main(String[] args) {
        System.out.println("hello");
    }
}
"""
    result = run_java_in_sandbox(code, timeout=25)
    assert result["stdout"].strip() == "hello"
    assert result["exit_code"] == 0


@pytest.mark.docker
def test_captures_compile_error():
    code = """
public class Broken {
    public static void main(String[] args) {
        int x = ;
    }
}
"""
    result = run_java_in_sandbox(code, timeout=25)
    assert result["compile_error"] is not None
    assert "error" in result["compile_error"].lower()


@pytest.mark.docker
def test_infinite_loop_times_out():
    code = """
public class Infinite {
    public static void main(String[] args) {
        while (true) {}
    }
}


"""
    result = run_java_in_sandbox(code, timeout=8)
    assert result["timed_out"] is True


@pytest.mark.docker
def test_handles_non_public_class():
    code = """
class Solution {
    public static void main(String[] args) {
        System.out.println("works without public modifier");
    }
}
"""
    result = run_java_in_sandbox(code, timeout=25)
    assert result["stdout"].strip() == "works without public modifier"
    assert result["compile_error"] is None