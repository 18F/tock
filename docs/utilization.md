# Utilization reports in Tock

[:arrow_left: Back to Tock Documentation](../docs)

Tock utilization reports display progress towards billing targets for each user, business unit, and the overall organization.

Each user has a billing target which is the percentage of worked hours that are expected to be tocked to billable projects.

We calculate utilization, or progress, towards these targets by totaling the hours worked on billable projects (both hourly and weekly) and dividing by the expected number of billable hours worked.

A few more detailed definitions and example calculations are included below.

## Definitions

### Utilization

The sum of two percentages:
1. For hourly projects, the percentage of [billable hours](#billable-hours) to [target billable hours](#target-billable-hours) tocked over a period of time
2. For weekly projects, the percentage of [billable allocation hours](#billable-allocation-hours) to target billable hours tocked over a period of time

Utilization | Description
------------|-------------
< 100% | a user has not reached their billable goal
100% | a user has reached their billable goal
\> 100% | a user has exceeded their billable goal

### Billable hours

The sum of hours tocked to hourly billable projects.

### Non-billable hours

The sum of hours tocked to hourly non-billable projects, excluding hours which were not worked like `Out of Office`.

### Billable allocation

The sum of allocation percentages (e.g., 100%, 50%, 25%, 12.5%) tocked to weekly billable projects.

### Billable allocation hours

The sum of hours tocked to weekly billable projects. This is a derived value based on billable allocation and target billable hours: `BILLABLE_ALLOCATION * TARGET_BILLABLE_HOURS = BILLABLE_ALLOCATION_HOURS`.

**Note:** Allocation percentages technically refer to an employee's availability on a project rather than a specific number of hours worked. But we convert this percentage to an _expected_ hourly value to enable utilization rate calculations across durations (e.g., the past month) and groups (e.g., all of `Project ABC`) that may include varying combinations of hourly, weekly, and excluded hours projects.

### Target billable hours
A user's expected number of hours tocked to billable projects over a period of time. Determined by their [billing expectation](#billing-expectation) over that period and the total number of hours in a week less any hours which were not worked like `Out of office`.

```
TARGET_BILLABLE_HOURS = (HOURS_IN_WEEK - HOURS_NOT_WORKED) * BILLING_EXPECTATION
```

### Billing expectation
The percent of [hours in a week](#hours-in-a-week) which are expected to be billable for a given reporting period. Set per user, per timecard, and will vary as an individual's role, position, or organization change. See [the handbook](https://handbook.tts.gsa.gov/tock/#weekly-billable-hour-expectations) for additional details on billing expectations.

**Default: 80%**

### Hours in a week
The number of hours in a standard week, i.e., `40`. This value is static.

### Non-billable employee
An employee is considered non-billable if their [target billable hours](#target-billable-hours) over a time period is 0. Utilization is not calculated for these individuals because we're currently unable to <a href="https://en.wikipedia.org/wiki/Division_by_zero">divide by zero</a>.

All billable hours and allocation tocked by non-billable employees are included in aggregations for their respective business unit and organization.
## Example

Stacey is an active and billable 18F employee, here's a look at their recent tock activity! As an individual contributor, Stacey has a billing expectation of 80%.

Project | Week 1 | Week 2 | Week 3 | Week 4
--------|--------|--------|--------|--------
Out of Office| 0.0 | 8.0 | 0.0 | 0.0
Hourly Billable | 24.0 | 30.0 | 0.0 | 32.0
Weekly Billable | 25% | 0% | 100% | 0%
Hourly Non-Billable | 8.0 | 2.0 | 8.0 | 8.0

### Week 1
Stacey's `utilization` for Week 1 is 100%.

Stacey tocked 24 billable hours to an hourly project and 8 billable hours to a weekly project, for a combined 32 hours of an expected 32 target billable hours.

```python
# Week 1
billable_hours = 24.0
non_billable_hours = 8.0
billable_allocation = .25
out_of_office = 0
billing_expectation = 0.80

target_billable_hours = (hours_in_week - out_of_office) * billing_expectation
# (40 - 0) * 0.80 = 32

billable_allocation_hours = billable_allocation * target_billable_hours
# .25 * 32 = 8

utilization = (billable_hours + billable_allocation_hours) / target_billable_hours
# (24 + 8) / 32 = 1
```

### Week 2
Stacey's `utilization` for Week 2 is 117%.

Stacey tocked 30 billable hours when their target was ~25 billable hours.

Stacey's target was less than the previous week because they were `Out of Office` for 8 hours.

```python
# Week 2
billable_hours = 30.0
non_billable_hours = 2.0
billable_allocation = 0
out_of_office = 8
billing_expectation = 0.80

target_billable_hours = (hours_in_week - out_of_office) * billing_expectation
# (40 - 8) * 0.80 = 25.6

billable_allocation_hours = billable_allocation * target_billable_hours
# 0 * 25.6 = 0

utilization = (billable_hours + billable_allocation_hours) / target_billable_hours
# (30 + 0) / 25.6 = 1.17
```

### Week 3
Stacey's `utilization` for Week 3 is 100%.

Stacey tocked 100% to a weekly billing project and no hours to hourly billable projects.

```python
# Week 2
billable_hours = 0
non_billable_hours = 0
billable_allocation = 1.0
out_of_office = 0
billing_expectation = 0.80

target_billable_hours = (hours_in_week - out_of_office) * billing_expectation
# (40 - 8) * 0.80 = 32

billable_allocation_hours = billable_allocation * target_billable_hours
# 1.0 * 32 = 32

utilization = (billable_hours + billable_allocation_hours) / target_billable_hours
# (0 + 32) / 32 = 1
```

### Weeks 1-4
Stacey's `utilization` over the last 4 weeks is ~104%.

Notice how values for each week are calculated independently and then summed to produce a utilization number over the 4-week time frame. Because the target billable hours denominator may fluctuate week-to-week, we can not simply take the average of each week's utilization percentages.

```python
# Weeks 1-4
billable_hours = [24.0, 30.0, 0.0 , 32.0]
non_billable_hours = [16.0, 2.0, 8.0, 8.0]
billable_allocation = [.25, 0.0, 1.0, 0.0]
billing_expectation = 0.80
out_of_office = [0.0, 8.0, 0.0, 0.0]

target_billable_hours = [(hours_in_week - ooo) * billing_expectation for ooo in out_of_office]
# [32, 25, 32, 32]

billable_allocation_hours = [b * t for b, t in zip(billable_allocation, target_billable_hours)]
# [.25 * 32, 0.0 * 25, 1.0 * 32, 0.0 * 32] = [8, 0, 32, 0]

utilization = (sum(billable_allocation_hours) + sum(billable_hours))  / sum(target_billable_hours)
# (40 + 86) / 121 = 1.04
```

## What if I Tock in excess of 40 hours?

Target billable hours is capped for each period at a user's expectation for a 40 hour work week, regardless of the number of billable hours or allocation a user tocks.
### Example

Stacey's target billable hours for each week is 32. Stacey took no out of office time in either week and has a billing expectation of 80%.

Stacey's `utilization` for week 1 is 156%. Stacey tocked 50 billable hours of an expected 32 target billable hours for the week.

Stacey's `utilization` for week 2 is 125%. Stacey tocked a cumulative 125% allocation to weekly projects. This represents 40 hours of an expected 32.

Project | Week 1 | Week 2
--------|--------|--------|
Out of Office| 0.0 | 0.0
Hourly Billable | 50.0 | 0.0
Weekly Billable | 0% | 125%
Hourly Non-Billable | 16.0 | 0.0

## What if I'm non-billable but worked on a billable project?

All billable hours and allocation count towards unit and organizational targets.

### Hourly example

Stacey is a non-billable employee, their target billable hours is 0 hours per week. Leslie's target billable hours is 32 hours per week. Stacey and Leslie are in the same Business unit: `Tockonauts`

The `Tockonauts` utilization for week 1 is 100%.

Leslie's utilization for week 1 is 97%.

Stacey's utilization for week 1 is `None` but their 1 billable hour contributes to the overall calculations and utilization for `Tockonauts`.

Employee | Project      | Week 1 |
---------|--------------|--------|
Stacey   | Billable     | 1.0 |
Stacey   | Non-Billable | 39.0 |
---------|--------------|----|
Leslie   | Billable     | 31.0 |
Leslie   | Non-Billable | 9.0 |
---------|--------------|----|

### Weekly example

Leslie's utilization for week 1 is 100%. They worked a full work week and tocked 100% to a single weekly billable project.

Stacey's utilization for week 1 is `None`. They worked a full work week but have a billing expectation of 0. Their 12.5% billable allocation still contributes to the overall calculations and utilization for `Tockonauts`.

The `Tockonauts` utilization for week 1 is 112.5%.

Employee | Project      | Week 1 |
---------|--------------|--------|
Stacey   | Billable     | 12.5% |
Stacey   | Non-Billable | 100% |
---------|--------------|----|
Leslie   | Billable     | 100% |
Leslie   | Non-Billable | 0 |
---------|--------------|----|
