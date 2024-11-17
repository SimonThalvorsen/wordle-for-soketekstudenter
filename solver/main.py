import random
import time

from wordlesolver import WordleSolver


def main():
    st = time.time()

    results = []
    successful_solves = 0
    total_attempts = 0
    unsolved_words = []
    f = open("answer-words.txt", "r")
    word_list = list(f.readlines())
    max_attempts = 6
    solver = WordleSolver()
    num_iterations = 100

    # for word in word_list:
    for _ in range(num_iterations):
        x = random.randint(0, len(word_list) - 1)
        word = word_list[x]
        solver.reset(word)
        result = solver.solve(max_attempts=max_attempts)

        if result["success"]:
            successful_solves += 1
            total_attempts += result["attempts"]
            print(f"Solved '{word.strip()}' in {result['attempts']} attempts.")
        else:
            unsolved_words.append(word)
            print(f"Failed to solve '{word.strip()}'.")

        results.append(result)

    # Calculate and display summary
    print("\n=== Summary ===")
    print(f"Total words attempted: {num_iterations}")
    print(f"Total successful solves: {successful_solves}")
    print(
        f"Average attempts for successful solves: "
        f"{total_attempts / successful_solves if successful_solves > 0 else 'N/A'}"
    )
    if unsolved_words:
        print(
            f"Words not solved within {max_attempts} attempts:\n{''.join(unsolved_words)}"
        )

    print("----%.2f----" % (time.time() - st))
    return results


if __name__ == "__main__":
    # WordleSolver().solve()
    main()
    # WordleSolver()
