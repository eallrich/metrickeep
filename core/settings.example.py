import logging as logging_module
import os

# From metrickeep/core/settings.py to metrickeep/
cwd = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(cwd, os.pardir))


# logging
# -------
logging = {
    'format': '%(asctime)s | [%(levelname)s] %(message)s',
    'level':  'INFO',
}

logging_module.basicConfig(**logging)
logger = logging_module.getLogger(__name__)


# whisper
# -------
whisper_path = os.path.join(PROJECT_ROOT, "whispers")
whisper_archives = "10s:24h,1m:7d,5m:3y"
whisper_xfilesfactor = 0.0
whisper_aggregation = "average"
drift_epsilon = 2 # seconds
