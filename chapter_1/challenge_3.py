# Source: https://github.com/MahmudRustamov/Data-Structures-II/blob/main/chapter_1/challenge_3.py
# Original author: MahmudRustamov (copied for reference)

# Challenge 3 - All Subsets (Power Set)

def power_set(items):
    result = []

    def backtrack(index, current):
        if index == len(items):
            result.append(current.copy())
            return

        backtrack(index + 1, current)

        current.append(items[index])
        backtrack(index + 1, current)

        current.pop()

    backtrack(0, [])
    return result


items = [1, 2]

print(power_set(items))