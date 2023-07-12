import scipy.stats as stats
import numpy as np
import pandas as pd
import statsmodels.stats.api as sms
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from math import ceil
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
import pyathena
from datetime import timedelta, date, datetime


class QueryConnection:

    def __init__(self, test_number, profile_name, s3_staging_dir, region_name):
        self.test_number = test_number
        self.profile_name = profile_name
        self.s3_staging_dir = s3_staging_dir
        self.region_name = region_name

    def run_query(self):

        connection_Athena = pyathena.connect(profile_name=self.profile_name,
                                         s3_staging_dir=self.s3_staging_dir,
                                         region_name=self.region_name)

        ab_query = """
        select field_name
        ,field_name
        ,field_name
        from table_name{test_name}
        """

        for i in range(len(ab_query)):
            if ab_query[i] == '{':
                first_indices = i
            elif ab_query[i] == '}':
                second_indices = i

        ab_query = ab_query[:first_indices] + self.test_number + ab_query[second_indices + 1:]

        df = pd.read_sql_query(ab_query, connection_Athena)
        print(df.head())
        print(df.info())

        df.to_csv(r'file_name.csv')




    def analyze(self, test_start_date, expected_control_cvr, expected_treatment_cvr, conversion_rates):

        df = pd.read_csv(r'file_name.csv')

        test_start_date = datetime.strptime(test_start_date, '%Y-%m-%d')
        current_run_time_in_days = datetime.today() - test_start_date
        current_run_time_in_days = current_run_time_in_days.days

        initial_effect_size = sms.proportion_effectsize(expected_control_cvr, expected_treatment_cvr)
        # Calculating effect size based on our expected rates

        initial_required_n = sms.NormalIndPower().solve_power(
            initial_effect_size,
            power=0.8,
            alpha=0.05,
            ratio=1
            )                                                  # Calculating sample size needed

        initial_required_n = ceil(initial_required_n)                          # Rounding up to next whole number

        print(f"Given the expected CVR difference, we'll need {initial_required_n} users from each group to reach statistical significance.\n")

        print(df.info())

        print(df.groupby('experiment_cohort').nunique())

        conversion_rate_num = 0
        for fraction in conversion_rates:
            print(fraction[0], "/", fraction[1])
            numerator = fraction[0]
            denominator = fraction[1]

            control_numerator = df[df['experiment_cohort'] == 'Recipe A: Control'].nunique()[numerator]
            control_denominator = df[df['experiment_cohort'] == 'Recipe A: Control'].nunique()[denominator]
            treatment_numerator = df[df['experiment_cohort'] == 'Recipe B'].nunique()[numerator]
            treatment_denominator = df[df['experiment_cohort'] == 'Recipe B'].nunique()[denominator]

            control_conv_rate = control_numerator / control_denominator
            treatment_conv_rate = treatment_numerator / treatment_denominator
            print(f"\nControl conversion rate for {numerator}/{denominator} is: {control_conv_rate:.4f}")
            print(f"Treatment conversion rate for {numerator}/{denominator} is: {treatment_conv_rate:.4f}\n")


            successes = [control_numerator, treatment_numerator]
            nobs = [control_denominator, treatment_denominator]
            z_stat, pval = proportions_ztest(successes, nobs=nobs)
            (lower_con, lower_treat), (upper_con, upper_treat) = proportion_confint(successes, nobs=nobs, alpha=0.05)

            print(f'z statistic: {z_stat:.2f}')
            print(f'p-value: {pval:.3f}')
            print(f'ci 95% for control group: [{lower_con:.3f}, {upper_con:.3f}]')
            print(f'ci 95% for treatment group: [{lower_treat:.3f}, {upper_treat:.3f}]')

            effect_size = sms.proportion_effectsize(control_conv_rate, treatment_conv_rate)

            required_n = sms.NormalIndPower().solve_power(
                effect_size,
                power=0.8,
                alpha=0.05,
                ratio=1
                )                                                  # Calculating sample size needed

            required_n = ceil(required_n)

            total_test_obs = control_denominator + treatment_denominator
            avg_daily_test_users_per_group = int((total_test_obs / current_run_time_in_days) / 2)
            users_needed_per_group = int(required_n - (total_test_obs/2))
            days_left_to_reach_sig = int(users_needed_per_group / avg_daily_test_users_per_group)

            print(f"\nWe'll need {required_n} users from each group for {numerator}/{denominator} to reach statistical significance.\n")
            print(f"The test will need to run for {days_left_to_reach_sig} more days for {numerator}/{denominator} to reach statistical significance.")
