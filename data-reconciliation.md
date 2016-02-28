# Data Reconciliation

18F uses Tock to track past staff project allocations and uses
[Float](https://www.float.com/) to predict future staff project allocations.
Both systems contain very similar information but with very different temporal
aspects: Tock contains historical data, while Float contains projected future
data. However, the data elements are very similar.

Since both applications are used for managing the business of 18F, it is
critical that the common data elements between the two are regularly
reconciled. For instance, analysis quickly breaks down if a project in Float
has a name attribute that varies from the project name attribute in Tock.

To reconcile the names of users, clients, and projects between Tock and Float,
a command-line tool named [onena](https://github.com/cwarden/onena) can be
used, which will help identify similar, but not exact matches.
