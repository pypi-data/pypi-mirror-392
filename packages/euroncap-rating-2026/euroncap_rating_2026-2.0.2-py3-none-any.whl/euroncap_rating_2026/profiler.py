import cProfile
import sys
import os

from euroncap_rating_2026.crash_avoidance import preprocess
from euroncap_rating_2026.crash_avoidance import compute_score


def run_preprocess():
    # Provide the actual paths you want to test
    if len(sys.argv) < 3:
        print("Usage: python profile.py <input_file> <output_path>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_path = sys.argv[2]
    # Call the Click command as a regular function
    preprocess.callback(input_file, output_path)


def run_compute_score():
    # Provide the actual paths you want to test
    if len(sys.argv) < 3:
        print("Usage: python profile.py <input_file> <output_path>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_path = sys.argv[2]
    # Import compute_score only when needed to avoid circular imports
    compute_score.callback(input_file, output_path)


if __name__ == "__main__":
    # Uncomment the function you want to profile
    cProfile.run("run_preprocess()", sort="cumtime")
    # cProfile.run("run_compute_score()", sort="cumtime")
