from exam_mode.constraint_checker import check_constraints_multilang, is_precise_language

c_code = """
#include <stdio.h>

int main() {
    int arr[5] = {5, 2, 4, 1, 3};
    qsort(arr, 5, sizeof(int), compare);
    return 0;
}
"""

print("Is 'c' a precise language?", is_precise_language("c"))
violations = check_constraints_multilang(c_code, banned_names=["qsort"], language="c")
for v in violations:
    print(v)