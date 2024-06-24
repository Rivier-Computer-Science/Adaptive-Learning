import unittest

# Define the functions that solve each question
def solve_question_1():
    return 5 * 8  # Solves "What is the value of 5 multiplied by 8?"

def solve_question_2():
    return 20 / 4  # Solves "What is the result of dividing 20 by 4?"

def solve_question_3():
    return 7 * 9  # Solves "Calculate the product of 7 and 9."

def solve_question_4():
    return 30 - 15  # Solves "What is the result of subtracting 15 from 30?"

def solve_question_5():
    return 12 / 3  # Solves "Calculate the result of 12 divided by 3."

# Define the unittest class
class TestSolutionVerifier(unittest.TestCase):

    
    def test_solve_question_1(self):
        self.assertEqual(solve_question_1(), 40, "The solution for Question 1 is incorrect.")
    
    def test_solve_question_2(self):
        self.assertEqual(solve_question_2(), 5, "The solution for Question 2 is incorrect.")
    
    def test_solve_question_3(self):
        self.assertEqual(solve_question_3(), 63, "The solution for Question 3 is incorrect.")
    
    def test_solve_question_4(self):
        self.assertEqual(solve_question_4(), 15, "The solution for Question 4 is incorrect.")
    
    def test_solve_question_5(self):
        self.assertEqual(solve_question_5(), 4, "The solution for Question 5 is incorrect.")


    def test_problem_1(self):
        # Problem 1: Solve the equation 2x + 5 = 11
        # Expected answer: x = 3
        expected_x = 3
        provided_x = (11 - 5) / 2
        self.assertEqual(provided_x, expected_x)

    def test_problem_2(self):
        # Problem 2: Solve the equation 3y - 7 = 8
        # Expected answer: y = 5
        expected_y = 5
        provided_y = (8 + 7) / 3
        self.assertEqual(provided_y, expected_y)

    def test_problem_3(self):
        # Problem 3: Solve the equation 4x - 9 = 7
        # Expected answer: x = 4
        expected_x = 4
        provided_x = (7 + 9) / 4
        self.assertEqual(provided_x, expected_x)

    def test_problem_4(self):
        # Problem 4: Solve the equation 2z + 3 = 11
        # Expected answer: z = 4
        expected_z = 4
        provided_z = (11 - 3) / 2
        self.assertEqual(provided_z, expected_z)

    def test_problem_5(self):
        # Problem 5: Solve the equation 3w - 5 = 16
        # Expected answer: w = 7
        expected_w = 7
        provided_w = (16 + 5) / 3
        self.assertEqual(provided_w, expected_w)

if __name__ == '__main__':
    unittest.main()
