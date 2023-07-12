import ab_test_module_template as ab

test_number = '3284'
profile_name = 'analysy_group'
s3_staging_dir = 's3://data-analytics-athena/workgroups/analysts/'
region_name = 'us-west-2'
test_start_date = '2022-11-19'


# The expected and/or desired difference between the control and treatment conversion rates is used to calculate what sample size is
# needed for the test to reach statistical significance
expected_control_cvr = 0.0576
expected_treatment_cvr = 0.0566


# Create conversion rates with field names in query. First item in list is numerator, second item in list is denominator
conversion_rate_1 = ['sign_up', 'user_count']
conversion_rate_2 = ['sign_up_2', 'user_count_2']
conversion_rates = [conversion_rate_1, conversion_rate_2]

# Set up Connection
query = ab.QueryConnection(test_number, profile_name, s3_staging_dir, region_name, conversion_rates)

# Runs query and outputs to csv. Only need to run once per session before commenting out
query.run_query()

# Analyzes each metric and dimension combination
query.analyze(test_start_date, expected_control_cvr, expected_treatment_cvr, conversion_rates)
