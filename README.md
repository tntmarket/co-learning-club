# Ticket deadline likelihood demo

A local TypeSafe demo that estimates whether a JIRA ticket will meet a deadline.
The SEC-21521 example is preloaded in the text area.

## Run it

Use Python 3.9 or newer; the server uses only the Python standard library.
Make sure `TYPESAFE_API_KEY` is available in your environment or in a `.env`
file in this directory, then run:

```sh
python app.py
```

Open <http://127.0.0.1:8000>. The key stays in the local Python server and is
never sent to the browser. Enter a ticket and deadline. The app makes one
TypeSafe decision: the probability that one engineer can finish the ticket by
that date, given the ticket, available weekdays, and schedule assumption. If a
ticket includes an explicit effort breakdown, Jev is instructed to take it
into account.

The deadline likelihood is a model estimate, not a calibrated guarantee. It
assumes one engineer works full-time on the ticket, excludes today and weekends
when counting available workdays, and does not account for holidays, other
work, blockers, reviews, dependencies, or team scheduling. The likelihood
should be treated as a planning aid, not a delivery commitment.

This is a demo estimator, not a calibrated project-planning forecast. For
general tickets, compare predictions with past outcomes before relying on the
results.
