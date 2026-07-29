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