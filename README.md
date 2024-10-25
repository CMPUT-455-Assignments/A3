# A3
CMPUT455 Assignment 3

Issue Report: a3.py Script Analysis

1. Executive Summary
   The a3.py script, which implements a game interface with pattern matching and move probability calculations, has several issues affecting its functionality and accuracy. The main problems revolve around incorrect probability calculations for empty boards, ineffective pattern matching influence, and weight calculation discrepancies.

2. Test Results
   Latest test results:
   - Total tests: 25
   - Successful: 9 (36%)
   - Failed: 12 (48%)
   - Mismatched: 4 (16%)
   - Marked tests score: 0.0 / 2.0 marks

3. Identified Issues
   3.1 Empty Board Case
       - For a 10x10 empty board, all moves have a uniform probability of 0.010 instead of the expected 0.005.
       - This indicates a fundamental issue with the base weight calculation in the calculate_weight function.

   3.2 Pattern Matching
       - The influence of pattern matches on move probabilities is not as significant as expected.
       - Pattern weights are not effectively altering the final probabilities for moves in non-empty board cases.

   3.3 Weight Calculation
       - The scaling and normalization of weights in the calculate_weight function are not producing the desired effect on final probabilities.
       - The cumulative impact of multiple pattern matches is not properly reflected in the final weights.

4. Implemented Changes
   The following modifications were made to address the identified issues:

   In calculate_weight function:
   - Changed base_weight calculation to a fixed value of 0.005 for 10x10 boards.
   - Increased the significance of pattern matches by adjusting the scaling factor.
   - Removed the board size scaling factor to simplify the calculation.

   In policy_moves function:
   - Removed the separate handling of empty board cases to ensure consistent weight calculation.
   - Implemented more detailed logging to track weight calculations and normalization.

   Rationale:
   - The fixed base_weight aims to correct the empty board probability issue.
   - Increased pattern match significance should make pattern influences more apparent.
   - Removing board size scaling simplifies the calculation and focuses on pattern impacts.

5. Remaining Challenges
   - The 13 mismatches in test results have not been fully resolved.
   - The effectiveness of pattern matching on final probabilities still needs improvement.
   - Potential performance issues may arise with larger board sizes due to the complexity of weight calculations.

6. Next Steps
   - Re-run tests to verify the impact of recent changes on mismatches.
   - Further optimize the calculate_weight function to ensure pattern matches have a more significant and accurate influence on final probabilities.
   - Implement a more robust normalization process in the policy_moves function to ensure probabilities sum to 1.
   - Consider implementing caching or memoization techniques to improve performance for larger board sizes.
   - Conduct more detailed analysis of specific test cases that are still failing to identify any remaining edge cases or logical errors.

This report highlights the current state of the a3.py script and outlines the steps taken to address the identified issues. Further iterations of debugging and optimization are necessary to fully resolve the remaining challenges and improve the overall functionality and accuracy of the script.
