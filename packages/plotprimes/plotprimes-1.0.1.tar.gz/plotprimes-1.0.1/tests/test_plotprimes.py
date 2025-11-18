from plotprimes import plotprimes
import unittest

HIGH_N = 100_000
HIGH_PRIME = 1_299_709

LOW_N = 1
LOW_PRIME = 2


class TestGetUpperLimit(unittest.TestCase):
    def test_low(self):
        for i in range(-1, 7):
            self.assertEqual(
                plotprimes.get_upper_limit(i), 15, f"get_upper_limit({i}) != 15"
            )

    def test_high(self):
        self.assertGreaterEqual(plotprimes.get_upper_limit(HIGH_N), HIGH_PRIME)


class TestGetPrimes(unittest.TestCase):
    def test_enough_primes(self):
        self.assertGreaterEqual(len(list(plotprimes.get_primes(HIGH_N))), HIGH_N)

    def test_low_correct_prime(self):
        primes = list(plotprimes.get_primes(LOW_N))[:LOW_N]
        self.assertEqual(primes[-1], LOW_PRIME)

    def test_high_correct_prime(self):
        primes = list(plotprimes.get_primes(HIGH_N))[:HIGH_N]
        self.assertEqual(primes[-1], HIGH_PRIME)


if __name__ == "__main__":
    unittest.main()
