from exam_mode.sandbox_executor_java import run_java_in_sandbox

code = """
public class Simple {
    public static void main(String[] args) {
        System.out.println("hello from java");
    }
}
"""

result = run_java_in_sandbox(code, stdin_input="", timeout=25)
print(result)