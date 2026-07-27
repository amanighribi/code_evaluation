from exam_mode.full_exam_pipeline import run_full_exam_evaluation
import json

instructions = """
Write a Java program that reads an integer n, then n integers, and prints them
sorted in ascending order using the bubble sort algorithm. Do not use
Collections.sort() or Arrays.sort().

For example, given n=5 and the list 5 2 4 1 3, the output should be:
1 2 3 4 5
"""

lazy_java_code = """
import java.util.Arrays;
import java.util.Scanner;

public class Sorter {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = Integer.parseInt(sc.nextLine());
        String[] parts = sc.nextLine().split(" ");
        int[] arr = new int[n];
        for (int i = 0; i < n; i++) arr[i] = Integer.parseInt(parts[i]);
        Arrays.sort(arr);
        StringBuilder sb = new StringBuilder();
        for (int x : arr) sb.append(x).append(" ");
        System.out.println(sb.toString().trim());
    }
}
"""

result = run_full_exam_evaluation(instructions, lazy_java_code, language="java")
print(json.dumps(result, indent=2, ensure_ascii=False))