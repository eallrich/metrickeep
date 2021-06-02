import csv
import datetime

import requests

r = requests.get('http://metrics.unguku.com/metrics/stats.timers.nori.metrickeep.metrics.post.median')
metrics = r.json()

data = []
timestamps = range(metrics['start'], metrics['stop']+1, metrics['step'])
for ts, value in zip(timestamps, metrics['values']):
    clock_time = datetime.datetime.fromtimestamp(ts)
    human_time = clock_time.strftime("%H:%M:%S")
    data.append({'Time': human_time, 'Value': value})

with open('metrics.csv','wb') as f:
    writer = csv.DictWriter(f, fieldnames=['Time', 'Value'])
    writer.writeheader()
    writer.writerows(data)

