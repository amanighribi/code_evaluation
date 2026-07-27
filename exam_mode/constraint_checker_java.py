import javalang


def check_constraints_java(source_code: str, banned_names: list[str]) -> list[dict]:
    """Checks Java source code against a list of banned method names, class names, or imports."""
    banned_set = set(banned_names)
    violations = []

    try:
        tree = javalang.parse.parse(source_code)
    except javalang.parser.JavaSyntaxError as e:
        return [{
            "type": "parse_error",
            "name": None,
            "line": None,
            "message": f"Could not parse Java code: {e}",
        }]

    # Method invocations, e.g. Collections.sort(list) or list.sort()
    for path, node in tree.filter(javalang.tree.MethodInvocation):
        qualified_name = f"{node.qualifier}.{node.member}" if node.qualifier else node.member
        matched_name = None

        if node.member in banned_set:
            matched_name = node.member
        elif qualified_name in banned_set:
            matched_name = qualified_name

        if matched_name:
            violations.append({
                "type": "banned_call",
                "name": matched_name,
                "line": node.position.line if node.position else None,
                "message": f"Use of banned method '{matched_name}' at line {node.position.line if node.position else '?'}.",
            })

    # Imports, e.g. import java.util.Collections;
    for path, node in tree.filter(javalang.tree.Import):
        imported = node.path
        base_name = imported.split(".")[-1]
        if base_name in banned_set or imported in banned_set:
            violations.append({
                "type": "banned_import",
                "name": imported,
                "line": node.position.line if node.position else None,
                "message": f"Import of banned '{imported}' at line {node.position.line if node.position else '?'}.",
            })

    return violations


if __name__ == "__main__":
    test_code = """
import java.util.Collections;
import java.util.Arrays;
import java.util.List;

public class Sorter {
    public static void bubbleSort(int[] arr) {
        List<Integer> list = Arrays.asList(1, 2, 3);
        Collections.sort(list);
    }
}
"""
    violations = check_constraints_java(test_code, banned_names=["sort", "Collections"])
    for v in violations:
        print(v)