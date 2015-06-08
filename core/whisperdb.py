import logging
import os
import time

import whisper

from . import settings

logger = logging.getLogger(__name__)

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
    
    def save(self, value, timestamp):
        logger.debug("Saving %s: %f" % (self.name, value))
        whisper.update(self.path, value, timestamp)
    
    def fetch(self, start, end=None):
        if not end:
            end = int(time.time())
        # Returns ((start, end, step), [value1, value2, ...])
        return whisper.fetch(self.path, start, end)

