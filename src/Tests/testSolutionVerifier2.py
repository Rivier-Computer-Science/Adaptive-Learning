import unittest
import sys
import os

# 2 Define the functions that solve each question
def solve_dquestion_1():
    return 5 * 8  # Solves "What is the value of 5 multiplied by 8?"

def solve_dquestion_2():
    return 20 / 4  # Solves "What is the result of dividing 20 by 4?"

def solve_dquestion_3():
    return 7 * 9  # Solves "Calculate the product of 7 and 9."

def solve_dquestion_4():
    return 30 - 15  # Solves "What is the result of subtracting 15 from 30?"

def solve_dquestion_5():
    return 12 / 3
  # Define the unittest class
class TestSolutionVerifier(unittest.TestCase):
    
   
    def test_solve_dquestion_1(self):
        self.assertEqual(solve_dquestion_1(), 40, "The solution for Question 1 is incorrect.")
    
    def test_solve_dquestion_2(self):
        self.assertEqual(solve_dquestion_2(), 5, "The solution for Question 2 is incorrect.")
    
    def test_solve_dquestion_3(self):
        self.assertEqual(solve_dquestion_3(), 63, "The solution for Question 3 is incorrect.")
    
    def test_solve_dquestion_4(self):
        self.assertEqual(solve_dquestion_4(), 15, "The solution for Question 4 is incorrect.")
    
    def test_solve_dquestion_5(self):
        self.assertEqual(solve_dquestion_5(), 4, "The solution for Question 5 is incorrect.")
if __name__ == '__main__':
    unittest.main()
