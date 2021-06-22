<!--
 Copyright (c) 2021 Erik Zwiefel
 
 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
-->

# YNAB Python API

Yet another YNAB Python API - the difference here is that it's more 
object-oriented than the other examples that I've seen.

Start with a client:
```python
client = ynab.YNABBudgetClient(
        budget_id=[ENTER YOUR BUDGET ID],
        pat_token=[ENTER YOUR PAT TOKEN]
    )

```