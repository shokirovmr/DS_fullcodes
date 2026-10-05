# Source: https://github.com/khamidovvv/COSC-3100-Challenges/blob/main/Challenge2/two_sum_via_hash_map
# Original author: khamidovvv (copied for reference)

def two_sum(nums: list[int], target: int) -> tuple[int, int]:
    seen = {}
    for i, x in enumerate(nums):
        complement = target - x
        if complement in seen:
            return (seen[complement], i)
        seen[x] = i
    raise ValueError("no valid pair found")


if __name__ == "__main__":
    assert two_sum([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum([3, 2, 4], 6) == (1, 2)
    assert two_sum([-3, 4, 3, 90], 0) == (0, 2)
    print("All tests passed.")