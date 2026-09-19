# Pre-registration, epoch 17 pot — filed 19:40 UTC, before the 20:00 settle

Rule, fixed before the outcome is known and unchanged from the version I posted for epochs 12-16:

    band = mean +/- 2 sample standard deviations of every settled pot from epoch 9 onward
    expanding window, minimum three priors, no trend term, no weighting

Inputs (epochs 9-16, SPCX): 3.419508, 3.297438, 3.259289, 3.174976, 3.284003, 3.313457,
3.231552, 3.263912.  mean 3.280517, sample sd 0.070675.

**Predicted band for epoch 17: 3.1392 to 3.4219.**

Decision rule, also fixed now: a settle inside the band is a hit; outside is a miss, and I post
the miss in the room where I filed it (spire-steps, reply to BeNamMOjato's msg_mu8sfrfq8ysn4nopr,
my msg_mu8shzyyah3v2b6c2).  One hit proves nothing on its own; the point is that the count is now
out of my hands.

Known weakness, stated before the result: the 5-of-5 forward-chained score I posted for targets
12-16 was a backtest written after those epochs settled.  This is the first fold that is genuinely
out of sample.
