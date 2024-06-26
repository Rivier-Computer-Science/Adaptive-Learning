import unittest

def solve_equation():
    # Solve the equation 2x + 5 = 11
    return (11 - 5) / 2

class TestEquationSolver(unittest.TestCase):

    def test_equation_solution(self):
        # Expected solution
        expected_solution = 3

        # Call the function to solve the equation
        actual_solution = solve_equation()

        # Assert that the actual solution matches the expected solution
        self.assertEqual(actual_solution, expected_solution)

if __name__ == '__main__':
    unittest.main()
