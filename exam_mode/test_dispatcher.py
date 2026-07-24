from exam_mode.constraint_checker import check_constraints_multilang

python_code = """
def bubble_sort(arr):
    return sorted(arr)
"""

java_code = """
import java.util.Collections;
public class Sorter {
    public static void sort(int[] arr) {
        Collections.sort(null);
    }
}
"""

print("Python check:")
for v in check_constraints_multilang(python_code, ["sort", "sorted"], language="python"):
    print(" ", v)

print("\nJava check:")
for v in check_constraints_multilang(java_code, ["sort"], language="java"):
    print(" ", v)