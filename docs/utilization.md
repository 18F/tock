# Utilization reports in Tock

[:arrow_left: Back to Tock Documentation](../docs)


Tock utilization reports display progress towards billing targets
for each user, business unit, and the overall organization.

Each user has a billing target which is the percentage of worked hours that are expected to be tocked to billable projects.

We calculate utilization, or progress, towards these targets by totaling the hours worked on billable projects and dividing by the total number of hours which were worked.

A few example calculations are included below.

## Definitions

### Utilization
The percentage of `BILLABLE HOURS` to `TARGET-BILLABLE-HOURS` tocked over a period of time.

    < 100% - a user has not reached their billable goal

    100% - a user has reached their billable goal

    > 100% - a user has exceeded their billable goal

### BILLABLE HOURS
The sum of hours tocked to billable projects.

### NON BILLABLE HOURS
The sum of hours tocked to non-billable projects, excluding hours which were not worked like `Out of Office`.

### TARGET BILLABLE HOURS
A user's expected number of `BILLABLE HOURS` over a period of time. Determined by their `BILLING EXPECTATION` over that period and the total number of billable and non-billable hours tocked.

```python
TARGET_BILLABLE_HOURS = (BILLABLE_HOURS + NON_BILLABLE_HOURS) * BILLING_EXPECTATION
```

### BILLING EXPECTATION

The percent of `TOTAL HOURS` which are expected to be billable for a given reporting period. Set per user, per timecard, and will vary as an individual's role, position, or organization change. See [the handbook](https://handbook.tts.gsa.gov/tock/#weekly-billable-hour-expectations) for additional details on billing expectations.


**Default: 80%**

## Example

Stacey is an active and billable 18F employee, here's a look at their recent tock activity! As an individual contributor, Stacey has a `BILLING_EXPECTATION` of 80%.

Project | Week 1 | Week 2 | Week 3 | Week 4
--------|--------|--------|--------|--------
Out of Office| 0.0 | 8.0 | 0.0 | 0.0
Billable | 24.0 | 28 | 32.0 | 32.0
Non-Billable | 16.0 | 4.0 | 8.0 | 8.0

### Week 1
Stacey's `utilization` for Week 1 is 75%.
Stacey tocked 24 of an expected 32 billable hours.

```python
# Week 1
billable_hours = 24.0
non_billable_hours = 16.0
billing_expectation = 0.80

total_hours = billable_hours + non_billable_hours
# 24.0 + 16.0 = 40

target_billable_hours = total_hours * billing_expectation
# 40 * 0.80 = 32

utilization = billable_hours / target_billable_hours
# 24 / 32 = 0.75
```

### Week 2
Stacey's `utilization` for Week 1 is 109%.
Stacey tocked 28 hours when their target was ~25 billable hours.

Stacey's target was less than the previous week because they were `Out of Office` for 8 hours in week 2.

```python
# Week 2
billable_hours = 28.0
non_billable_hours = 4.0
billing_expectation = 0.80

total_hours = billable_hours + non_billable_hours
# 28.0 + 4.0 = 32

target_billable_hours = total_hours * billing_expectation
# 40 * 0.80 = 25.6

utilization = billable_hours / target_billable_hours
# 28 / 25.6 = 1.09
```

### Weeks 1-4
Stacey's `utilization` over the last 4 weeks is 95%. Stacey tocked 116 of an expected ~122 billable hours over the 4 week period.

Stacey had eight hours of `Out of Office` time in week 2, which is excluded from all totals. Notice the `total_hours` is 152 for the 4 weeks.

```python
# Weeks 1-4
billable_hours = sum(24.0, 28.0, 32.0 , 32.0)
non_billable_hours = sum(16.0, 4.0, 8.0, 8.0)
billing_expectation = 0.80

total_hours = billable_hours + non_billable_hours
# 116 + 40 = 152

target_billable_hours = (billable_hours + non_billable_hours) * billing_expectation
# 152 * 0.80 = 121.6

utilization = billable_hours / target_billable_hours
# 116 / 122 = 0.95
```


## What if I Tock in excess of 40 hours?

Target billable hours is capped for each period at the target for a 40 hour work week.

### Example

Stacey's `utilization` for week 1 is 156%. Stacey tocked 50 billable hours of an expected 32 for the week.

Project | Week 1 |
--------|--------|
Out of Office| 0.0 |
Billable | 50.0 |
Non-Billable | 16.0 |

