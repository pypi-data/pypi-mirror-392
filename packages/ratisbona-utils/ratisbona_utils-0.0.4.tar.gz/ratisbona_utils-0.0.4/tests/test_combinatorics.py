import unittest

from ratisbona_utils.combinatorics import perm_sign


class CombinartoricsTest(unittest.TestCase):
    
    def test_sign(self):
        # given
        permutations = [ (1,2,3), (1,3,2), (2,1,3), (2,3,1), (3,1,2), (3,2,1) ]

        # when
        signs = [perm_sign(perm) for perm in permutations]

        # then
        expect = [1, -1, -1, +1, +1, -1]

        self.assertEqual(expect, signs)



if __name__ == '__main__':
    unittest.main()
