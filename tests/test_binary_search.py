import unittest
from binary_search import binary_search

class TestBinarySearch(unittest.TestCase):
    def test_binary_search(self):
        arr = [1, 3, 5, 7, 9]
        self.assertEqual(binary_search(arr, 3), 1)
        self.assertEqual(binary_search(arr, 9), 4)
        self.assertEqual(binary_search(arr, 0), -1)

if __name__ == '__main__':
    unittest.main()