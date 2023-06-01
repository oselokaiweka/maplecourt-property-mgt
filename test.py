from typing import List

def solution(k: List[int], x: int, y: int, z: int) -> int:
    n = len(k)
    count = 0
    for i in range(n):
        for j in range(i+1, n):
            if abs(k[i] - k[j]) <= x:
                for m in range(j+1, n):
                    if abs(k[j] - k[m]) <= y and abs(k[i] - k[m]) <= z:
                        count += 1
    return count
k = [3, 0, 1, 1, 9, 7]
x = 7
y = 2
z = 3
print(solution(k, x, y, z))