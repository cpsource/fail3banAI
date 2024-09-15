# Custom exception class
class MyCustomException(Exception):
    pass

def risky_division(x, y):
    """Performs division but raises custom exceptions for specific cases."""
    if y == 0:
        raise ValueError("Division by zero is not allowed.")
    if y == 1:
        raise MyCustomException("Division by 1 is discouraged.")
    return x / y

def test_exceptions():
    # Define test cases with expected output and exception
    test_cases = [
        (10,  2,    5.0,                None),               # Expected result 5.0 (no exception)
        (10,  0,    None,               ValueError),         # Expect ValueError for division by 0
        (10,  1,    None,               MyCustomException),  # Expect MyCustomException for division by 1
        (10,  "a",  None,               TypeError)           # Expect TypeError for invalid input
    ]

    passed = 0
    failed = 0

    for idx, (x, y, expected_output, expected_exception) in enumerate(test_cases, 1):
        try:
            print(f"Test {idx}: Trying to divide {x} by {y}...")
            result = risky_division(x, y)
            # If no exception is raised, check if the result matches the expected output
            if result == expected_output:
                print(f"Test {idx} - PASS: {x} / {y} = {result}")
                passed += 1
            else:
                print(f"Test {idx} - FAIL: Unexpected result {result}")
                failed += 1
        except ValueError as ve:
            if expected_exception == ValueError:
                print(f"Test {idx} - PASS: Caught expected ValueError")
                passed += 1
            else:
                print(f"Test {idx} - FAIL: Caught unexpected ValueError")
                failed += 1
        except MyCustomException as me:
            if expected_exception == MyCustomException:
                print(f"Test {idx} - PASS: Caught expected MyCustomException")
                passed += 1
            else:
                print(f"Test {idx} - FAIL: Caught unexpected MyCustomException")
                failed += 1
        except TypeError as te:
            if expected_exception == TypeError:
                print(f"Test {idx} - PASS: Caught expected TypeError")
                passed += 1
            else:
                print(f"Test {idx} - FAIL: Caught unexpected TypeError")
                failed += 1
        except Exception as e:
            print(f"Test {idx} - FAIL: Caught unexpected general exception {e}")
            failed += 1
        finally:
            print("Execution of this test case is complete.\n")

    # Summarize the results
    print(f"Summary of Results: {passed} tests passed, {failed} tests failed.")
    if failed == 0:
        print("All tests passed!")
    else:
        print("Some tests failed.")

if __name__ == "__main__":
    test_exceptions()

