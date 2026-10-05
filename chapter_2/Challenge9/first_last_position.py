# Source: https://github.com/khamidovvv/COSC-3100-Challenges/blob/main/Challenge9/first_last_position
# Original author: khamidovvv (copied for reference)

def search_range(nums: list[int], target: int) -> tuple[int, int]:
    def find_bound(is_first: bool) -> int:
        lo, hi = 0, len(nums) - 1
        result = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if nums[mid] == target:
                result = mid
                if is_first:
                    hi = mid - 1
                else:
                    lo = mid + 1
            elif nums[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return result

    first = find_bound(True)
    if first == -1:
        return (-1, -1)
    last = find_bound(False)
    return (first, last)


if __name__ == "__main__":
    assert search_range([5, 7, 7, 8, 8, 8, 10], 8) == (3, 5)
    assert search_range([5, 7, 7, 8, 8, 8, 10], 6) == (-1, -1)
    assert search_range([1], 1) == (0, 0)
    print("All tests passed.")