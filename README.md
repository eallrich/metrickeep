metrickeep
==========

Receives metrics in JSON via HTTP and stores them in Whisper databases.

Overview
--------
The Keep is intended to house and protect metrics as they are received. All
received metrics are stored in Whisper databases on disk.

History
-------
This project was originally conceived as part of a grand scheme of collecting
and persisting metrics on the heroku platform through a combination of multiple
free dynos and the DreamObjects storage service. It was known as metrickdock,
but once heroku nerfed the free dyno tier (max of 18 hours uptime per day),
the original experiment ended.

But! Having migrated to dreamhost, the metrickeep functionality found a new
use: receiving metrics from across my fleet as HTTP (supported by dreamhost)
and then persisting them to whisper databases on dreamhost's disks.
