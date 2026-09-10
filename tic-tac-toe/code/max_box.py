from typing import List

class Solution:
    def maxHeight(self, cuboids: List[List[int]]) -> int:
        sorted_cuboids = sorted([sorted(dimensions) for dimensions in cuboids])
        N = len(cuboids)
        dp = [[0] * (N + 1) for _ in range(N + 1)]
        def find_max_height_rec(base, n):
            if n == 0:
                return 0
            if base != 0 and dp[n][base] != 0:
                return dp[n][base]
            ml, mb, mh = float('inf'), float('inf'), float('inf')
            if base != 0:
                ml, mb, mh = sorted_cuboids[base - 1][0], sorted_cuboids[base - 1][1], sorted_cuboids[base - 1][2]
            l, b, h = sorted_cuboids[n - 1][0], sorted_cuboids[n - 1][1], sorted_cuboids[n - 1][2]
            
            mx_height = find_max_height_rec(base, n - 1)
            print((n - 1, base), mx_height)
            if ml >= l and mb >= b and mh >= h:
                mx_height = max(h + find_max_height_rec(n, n - 1), mx_height)
                print((n - 1,n), mx_height)
            print((n, base), mx_height, "S")
            dp[n][base] = mx_height
            return mx_height

        # result = find_max_height_rec(0, len(cuboids))

        # return result
