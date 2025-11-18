import unittest
from redenpy.core import RedenPy

class TestRedenPy(unittest.TestCase):
    
    def test_basic(self):
        r = RedenPy(3, rule={"round": "up"})
        result = r.redenomination("Rp.1000000")
        r = RedenPy(3, rule={"round":"up"})

        print(r.redenomination("1000000"))          # 1000
        print(r.redenomination("Rp.1000000"))       # 1000
        print(r.redenomination("1.000.000,50"))     # 1000
        print(r.redenomination("10000,00 Kr", fractional=True))  # 10,00
        print(r.redenomination("$ 1,000,000.75", fractional=True)) # 1000,00
        print(r.redenomination(1000000, output_type=int))          # 1000
        
        # Print the result
        print("Redenominated value:", result)
        
        # Example assertion (adjust to your expected value)
        self.assertEqual(result, "1000")

if __name__ == "__main__":
    unittest.main()
