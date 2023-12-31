# A/B Testing Automation
NOTE***: Certain information has been redacted/changed to protect proprietary information

Object-oriented Python program I made to automate the A/B testing process on the Mint website at Intuit.

## File Guide


### module_creation.py
This module abstracts away some of the manual, repetitve work involved in A/B testing such as connecting to the AWS datalake, writing a query, and changing scripts for new tests and/or metrics. By importing the module, the user can create a QueryConnection object, which has two methods:
1. run_query()
- This method takes the user's AWS parameters & relevant test information as arguments, connects to the lake, creates queries based on the test info provided, and sends the output to a csv
2. analyze()
- Once the output has been created, this method is called which will run a two-tailed z-test, along with other info such as:
- Estimate of number users required to reach statistical significance
- Conversion rate for each metric
- If the test has reached statistical significance, which variant won. If stat sig has not been reached, how many more days it will take given current conversion rate difference

### execute_test.py
This is an example of how an analyst would use the above module. The analyst is asked to provide relevant (non-sensitive) information such as their AWS directory, test number, and when the test started. They are also asked to provide the expected (or desired) conversion rate difference between the control & variant, as well as the metrics they would like to test. With this info, they can call run_query() and analyze() and voila! An A/B test is executed
