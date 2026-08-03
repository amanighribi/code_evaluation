import io
import zipfile
from project_utils.zip_extractor import extract_zip_safely, cleanup_project_dir
from exam_mode.sandbox_executor_java import run_java_project_in_sandbox

buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as zf:
    zf.writestr("Main.java", """
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = Integer.parseInt(sc.nextLine());
        int b = Integer.parseInt(sc.nextLine());
        System.out.println(Helper.add(a, b));
    }
}
""")
    zf.writestr("Helper.java", """
public class Helper {
    public static int add(int a, int b) {
        return a + b;
    }
}
""")

project_dir = extract_zip_safely(buf.getvalue())
try:
    result = run_java_project_in_sandbox(project_dir, "Main.java", stdin_input="3\n4\n", timeout=25)
    print(result)
finally:
    cleanup_project_dir(project_dir)