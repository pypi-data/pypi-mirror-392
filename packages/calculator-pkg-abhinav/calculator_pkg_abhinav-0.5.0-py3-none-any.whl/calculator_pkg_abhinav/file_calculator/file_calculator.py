# built in
from pathlib import Path

# pip installed
from tqdm import tqdm

# our package
# from ..calculator import Calculator
from calculator_pkg_abhinav.calculator import Calculator


class FileCalculator(Calculator):
    def sum_file(self, path=None) -> int:
        if path is None:
            path = Path(__file__).parent / "nums.csv"
        with tqdm(total=100_000_000, desc="summing file") as pbar:
            total = 0
            with path.open() as f:
                for line in f:
                    total += int(line)
                    pbar.update()
            return total
