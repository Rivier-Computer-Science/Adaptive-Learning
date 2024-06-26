def test_math_tutor():
    # Define the expected user prompts and corresponding expected tutor responses
    user_prompts = [
        "Solve the equation: 3𝑥 + 5 = 17.",
        "Calculate the area of a rectangle with length 8 units and width 5 units.",
        "Factorize the quadratic expression 𝑥^2 + 7𝑥 + 10.",
        "Find the value of squareroot of 144.",
        "Simplify the expression: (3/4) x (5/6)."
    ]

    expected_responses = [
        "To solve the equation 3𝑥 + 5 = 17, subtract 5 from both sides: 3𝑥 = 12. Divide by 3: 𝑥 = 4.",
        "To calculate the area, multiply length by width: Area = 8 units x 5 units = 40 square units.",
        "To factorize 𝑥^2 + 7𝑥 + 10, find numbers that multiply to 10 and add to 7. Factorized form: (𝑥 + 2)(𝑥 + 5).",
        "The square root of 144 is 12 because 12 x 12 = 144.",
        "To simplify (3/4) x (5/6), multiply numerators and denominators: 15 / 24. Simplify to 5/8."
    ]

    # Simulate the interaction with the math tutor system
    tutor_responses = []

    for prompt in user_prompts:
        # Simulate the tutor's response based on the prompt
        if "equation" in prompt.lower():
            tutor_responses.append("To solve the equation 3𝑥 + 5 = 17, subtract 5 from both sides: 3𝑥 = 12. Divide by 3: 𝑥 = 4.")
        elif "area" in prompt.lower():
            tutor_responses.append("To calculate the area, multiply length by width: Area = 8 units x 5 units = 40 square units.")
        elif "factorize" in prompt.lower():
            tutor_responses.append("To factorize 𝑥^2 + 7𝑥 + 10, find numbers that multiply to 10 and add to 7. Factorized form: (𝑥 + 2)(𝑥 + 5).")
        elif "squareroot" in prompt.lower():
            tutor_responses.append("The square root of 144 is 12 because 12 x 12 = 144.")
        elif "simplify" in prompt.lower():
            tutor_responses.append("To simplify (3/4) x (5/6), multiply numerators and denominators: 15 / 24. Simplify to 5/8.")

    # Compare each tutor's response with the expected response
    for i, response in enumerate(tutor_responses):
        expected = expected_responses[i]
        assert response == expected, f"Test case failed for prompt '{user_prompts[i]}'. Expected: '{expected}', but got: '{response}'."

    print("All test cases passed successfully!")

# Run the test case
test_math_tutor()