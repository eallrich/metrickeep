import logging
import os
import time

from statsd import StatsClient
import whisper

from . import settings

logger = logging.getLogger(__name__)

host = platform.node().replace('.', '_')
statsd = StatsClient('localhost', 48125, prefix="%s.metrickeep.whisper" % host)

class Whisper(object):
    @staticmethod
    def make_db_name(metric_name):
        with_dirs = metric_name.replace('.', '/')
        with_extension = "%s.wsp" % with_dirs
        return with_extension
    
    @staticmethod
    def make_db_path(db_name):
        return os.path.join(settings.whisper_path, db_name)
    
    def __init__(self, metric):
        self.name = Whisper.make_db_name(metric)
        self.path = Whisper.make_db_path(self.name)
        
        if not os.path.isfile(self.path):
            logger.info("Creating new whisper DB '%s'" % self.name)
            if not os.path.exists(os.path.dirname(self.path)):
                os.makedirs(os.path.dirname(self.path))
            retentions = settings.whisper_archives.split(',')
            logger.debug("Retentions: %s" % retentions)
            # Convert the human-readable retentions into (seconds/period, # periods)
            archives = map(whisper.parseRetentionDef, retentions)
            logger.debug("Archives: %s" % archives)
            whisper.create(
                self.path,
                archives,
                xFilesFactor=settings.whisper_xfilesfactor,
                aggregationMethod=settings.whisper_aggregation
            )
    
    def save(self, value, timestamp, lenient=False):
        logger.debug("Saving %s: %f" % (self.name, value))
        try:
            whisper.update(self.path, value, timestamp)
        except whisper.TimestampNotCovered as exc:
            # The timestamp we were given is either "in the future" (perhaps
            # because our own clock is delayed) or "before the time the
            # database remembers". If we're willing to fudge the timestamp,
            # check whether the difference is less than the configured
            # epsilon for clock drift. If it is, then try saving the value
            # again using a timestamp from one second earlier than reported.
            # If that's still not accepted, a new (unhandled) TimestampNot-
            # Covered exception will be raised for the caller to handle.
            statsd.incr('error.timestampnotcovered')
            if lenient:
                delta = timestamp - time.time() # in seconds
                statsd.timing('timestamp_drift', delta * 1000) # report in ms
                if abs(delta) < settings.drift_epsilon:
                    # Ensure lenient is set to False for the next attempt so
                    # that we don't end up in a loop
                    self.save(value, timestamp-1, lenient=False)
                    # Report only successful lenient saves
                    statsd.incr('lenient_save')
            else:
                raise
    
    def fetch(self, start, end=None):
        if not end:
            end = int(time.time())
        # Returns ((start, end, step), [value1, value2, ...])
        return whisper.fetch(self.path, start, end)

