# Utilization reports in Tock

[:arrow_left: Back to Tock Documentation](../docs)

Tock utilization reports display progress towards billing targets for each user, business unit, and the overall organization.

Each user has a billing target which is the percentage of worked hours that are expected to be tocked to billable projects.

We calculate utilization, or progress, towards these targets by totaling the hours worked on billable projects and dividing by the expected number of billable hours worked.

A few more detailed definitions and example calculations are included below.

## Definitions

### Utilization for a single timecard

The sum of two percentages:
1. For hourly projects, the percentage of [billable hours](#billable-hours) to [target billable hours](#target-billable-hours) tocked to the timecard
2. For weekly projects, the total [billable allocation](#billable-allocation) tocked to the timecard

### Utilization in aggregate

The sum of [billable hours](#billable-hours) and [billable allocation hours](#billable-allocation-hours) divided by the sum of [target billable hours](#target-billable-hours).

This formula is used when calculating utilization across durations (e.g., the past month) and groups (e.g., all account managers).

### Billable hours

The sum of hours tocked to hourly billable projects.

### Non-billable hours

The sum of hours tocked to hourly non-billable projects, excluding hours which were not worked like `Out of Office`.

### Billable allocation

The sum of allocation percentages (e.g., 100%, 50%, 25%, 12.5%) tocked to weekly billable projects.

### Billable allocation hours

The sum of hours tocked to weekly billable projects. This is a derived value based on billable allocation and the default number of billable hours in a week. Used when calculating [aggregate utilization](#utilization-in-aggregate).

```
DEFAULT_EXPECTATION = (HOURS_IN_WEEK - HOURS_NOT_WORKED) * .8
BILLABLE_ALLOCATION_HOURS = BILLABLE_ALLOCATION * DEFAULT_EXPECTATION
```

**Note:** Allocation percentages technically refer to an employee's availability on a project rather than a specific number of hours worked. But we convert this percentage to an _equivalent_ number of hours to enable utilization rate calculations in aggregate.

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
## Timecard examples

Stacey is an active and billable 18F employee, here's a look at their recent tock activity! As an individual contributor, Stacey has a billing expectation of 80%.

Project | Week 1 | Week 2 | Week 3
--------|--------|--------|--------
Out of Office| 0.0 | 8.0 | 0.0
Hourly Billable | 24.0 | 30.0 | 0.0
Weekly Billable | 25% | 0% | 100%
Hourly Non-Billable | 8.0 | 2.0 | 8.0

### Week 1
Stacey's `utilization` for Week 1 is 100%.

Stacey tocked 24 billable hours to an hourly project out of 32 target hours (75%) and 25% allocation to a weekly project.

```python
# Week 1
billable_hours = 24.0
non_billable_hours = 8.0
billable_allocation = .25
out_of_office = 0
billing_expectation = 0.80

target_billable_hours = (hours_in_week - out_of_office) * billing_expectation
# (40 - 0) * 0.80 = 32

utilization = billable_allocation + (billable_hours / target_billable_hours)
# .25 + (24 / 32) = 1
```

### Week 2

Stacey's `utilization` for Week 2 is 117%.

Stacey tocked 30 billable hours when their target was ~25 billable hours.

Stacey's target was less than the previous week because they were `Out of Office` for 8 hours.

Project | Week 1 | Week 2 | Week 3
--------|--------|--------|--------
Out of Office| 0.0 | 8.0 | 0.0
Hourly Billable | 24.0 | 30.0 | 0.0
Weekly Billable | 25% | 0% | 100%
Hourly Non-Billable | 8.0 | 2.0 | 8.0

```python
# Week 2
billable_hours = 30.0
non_billable_hours = 2.0
billable_allocation = 0
out_of_office = 8
billing_expectation = 0.80

target_billable_hours = (hours_in_week - out_of_office) * billing_expectation
# (40 - 8) * 0.80 = 25.6

utilization = billable_allocation + (billable_hours / target_billable_hours)
# 0 + (30 / 25.6) = 1.17
```

### Week 3

Stacey's `utilization` for Week 3 is 100%.

Stacey tocked 100% to a weekly billing project and no hours to hourly billable projects.

Project | Week 1 | Week 2 | Week 3
--------|--------|--------|--------
Out of Office| 0.0 | 8.0 | 0.0
Hourly Billable | 24.0 | 30.0 | 0.0
Weekly Billable | 25% | 0% | 100%
Hourly Non-Billable | 8.0 | 2.0 | 8.0

```python
# Week 2
billable_hours = 0
non_billable_hours = 0
billable_allocation = 1.0
out_of_office = 0
billing_expectation = 0.80

target_billable_hours = (hours_in_week - out_of_office) * billing_expectation
# (40 - 8) * 0.80 = 32

utilization = billable_allocation + (billable_hours / target_billable_hours)
# 1 + (0 / 32) = 1
```

### What if I Tock in excess of 40 hours?

Target billable hours is capped for each period at a user's expectation for a 40 hour work week, regardless of the number of billable hours or allocation a user tocks.

#### Example

Stacey's target billable hours for each week is 32. Stacey took no out of office time in either week and has a billing expectation of 80%.

Stacey's `utilization` for week 1 is 156%. Stacey tocked 50 billable hours of an expected 32 target billable hours for the week.

Stacey's `utilization` for week 2 is 125%. Stacey tocked a cumulative 125% allocation to weekly projects.

Project | Week 1 | Week 2
--------|--------|--------|
Out of Office| 0.0 | 0.0
Hourly Billable | 50.0 | 0.0
Weekly Billable | 0% | 125%
Hourly Non-Billable | 16.0 | 0.0

## Aggregate examples

A hypothetical 3-person 18F chapter consists of one individual contributor, one supervisor, and one non-billable director:

&nbsp; | Stacey | Frances | Leslie
-|--------|---------|--------------|
Role | Individual contributor | Supervisor | Director
Billable expectation | 80% | 40% | 0%

Week-to-week each individual may Tock varying amounts of hourly, weekly, and OOO time. We calculate aggregate utilization to show progress towards billable expectations for the entire cohort.

### Week 1

&nbsp; | Stacey | Frances | Leslie
----------------|--------|---------|--------|
Billable hours              | 0 | 0 | 0
Billable allocation         | 100% | 50% | 0%
OOO                         | 0 | 0 | 0
Billable allocation hours   | 32 | 16 | 0
Target billable hours       | 32 | 16 | 0

The chapter's aggregate utilization for week 1 is 100%. Each individual tocked an allocation equal to their billable expectation.

```python
billable_hours = [0, 0, 0]
allocation_hours = [32, 16, 0]
target_hours = [32, 16, 0]

utilization = (sum(billable_hours) + sum(allocation_hours)) / sum(target_billable_hours)
# (0 + 48) / 48 = 1
```

### Week 2

&nbsp; | Stacey | Frances | Leslie
----------------|--------|---------|--------|
Billable hours              | 0 | 0 | 0
Billable allocation         | 100% | 50% | 0%
OOO                         | 0 | 20 | 0
Billable allocation hours   | 32 | 8 | 0
Target billable hours       | 32 | 8 | 0

The chapter's aggregate utilization for week 2 is also 100%. Each individual tocked an allocation equal to their billable expectation. Frances took 20 hours of OOO and their billable allocation hours and target hours were reduced accordingly.

```python
billable_hours = [0, 0, 0]
allocation_hours = [32, 8, 0]
target_hours = [32, 8, 0]

utilization = (sum(billable_hours) + sum(allocation_hours)) / sum(target_billable_hours)
# (0 + 40) / 40 = 1
```

### Week 3

&nbsp; | Stacey | Frances | Leslie
----------------|--------|---------|--------|
Billable hours              | 0 | 4 | 0
Billable allocation         | 100% | 50% | 0%
OOO                         | 0 | 20 | 0
Billable allocation hours   | 32 | 8 | 0
Target billable hours       | 32 | 8 | 0

The chapter's aggregate utilization for week 3 is 110%. Each individual tocked an allocation equal to their billable expectation and Frances tocked an additional 4 hours of billable hourly work.

```python
billable_hours = [0, 4, 0]
allocation_hours = [32, 8, 0]
target_hours = [32, 8, 0]

utilization = (sum(billable_hours) + sum(allocation_hours)) / sum(target_billable_hours)
# (4 + 40) / 40 = 1.1
```

### Week 4

&nbsp; | Stacey | Frances | Leslie
----------------|--------|---------|--------|
Billable hours              | 0 | 0 | 0
Billable allocation         | 100% | 50% | 12.5%
OOO                         | 0 | 20 | 0
Billable allocation hours   | 32 | 8 | 4
Target billable hours       | 32 | 8 | 0

The chapter's aggregate utilization for week 4 is 110%. Stacey and Frances tocked an allocation equal to their billable expectation. Leslie tocked 12.5% to single weekly billing project. Because Leslie is non-billable, their target hours remain 0.

```python
billable_hours = [0, 0, 0]
allocation_hours = [32, 8, 4]
target_hours = [32, 8, 0]

utilization = (sum(billable_hours) + sum(allocation_hours)) / sum(target_billable_hours)
# (0 + 44) / 40 = 1.1
```