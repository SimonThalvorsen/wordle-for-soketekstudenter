from context import in3120
from solver.wordlesolver import WordleSolver
import time


def main():
    st = time.time()
    solver = WordleSolver()
    solver.solve()
    print("----%.2f----" % (time.time() - st))


if __name__ == "__main__":
    main()
