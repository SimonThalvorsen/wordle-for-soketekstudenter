from wordlesolver import WordleSolver
import time


def main():
    st = time.time()

    results = []
    successful_solves = 0
    total_attempts = 0
    unsolved_words = []
    f = open("answer-words.txt", "r")
    word_list = list(f.readlines())
    max_attempts = 6

    for word in word_list:
        solver = WordleSolver()
        solver.target_word = word  # Set the target word for each run
        result = solver.solve(max_attempts=max_attempts)

        if result["success"]:
            successful_solves += 1
            total_attempts += result["attempts"]
            # print(f"Solved '{word}' in {result['attempts']} attempts.")
        else:
            unsolved_words.append(word)
            # print(f"Failed to solve '{word}'.")

        results.append(result)

    # Calculate and display summary
    print("\n=== Summary ===")
    print(f"Total words attempted: {len(word_list)}")
    print(f"Total successful solves: {successful_solves}")
    print(
        f"Average attempts for successful solves: "
        f"{total_attempts / successful_solves if successful_solves > 0 else 'N/A'}"
    )
    if unsolved_words:
        print(
            f"Words not solved within {max_attempts} attempts: {', '.join(unsolved_words)}"
        )

    print("----%.2f----" % (time.time() - st))
    return results


if __name__ == "__main__":
    main()
