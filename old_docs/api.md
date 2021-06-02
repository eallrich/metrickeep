API
===

Publishing
----------
To store one or more new metrics, POST a JSON document to the /publish endpoint.

To send a single value for the metric foo.bar.baz:
```shell
$ curl -i -X POST -H "Content-Type: application/json" -d '{"metric": "foo.bar.bar", "value": 4.2, "timestamp": 1395019746}' http://metrics1.example.com/publish
HTTP/1.1 201 CREATED
Content-Type: text/html; charset=utf-8
Date: Mon, 17 Mar 2014 01:34:23 GMT
Server: gunicorn/18.0
Content-Length: 16
Connection: keep-alive

Saved 1 metrics
```

Send either multiple values for a metric (as shown below) or multiple metrics using a JSON list:
```shell
$ curl -i -X POST -H "Content-Type: application/json" -d '[{"metric": "foo.bar.bar", "value": 4.2, "timestamp": 1395019746}, {"metric": "foo.bar.baz", "value": 3.14159, "timestamp": 1395020046}]' http://metrics1.example.com/publish
HTTP/1.1 201 CREATED
Content-Type: text/html; charset=utf-8
Date: Mon, 17 Mar 2014 01:40:58 GMT
Server: gunicorn/18.0
Content-Length: 16
Connection: keep-alive

Saved 2 metrics
```

Retrieving
----------
The /fetch endpoint supports retrieving data for a given metric within a specified time interval. The GET method is always expected here.

Retrieving /fetch by itself returns a JSON document describing the set of recorded metrics. A specific metric may be retrieved via /fetch/\<metric\>/\<start timestamp\>/\<end timestamp\>. For convenience, the /fetch/\<metric\>/hour endpoint automatically retrieves the past hour of data for the metric.

Deleting
--------
Deleting a metric (i.e. the entire Whisper database for that metric) is accomplished by sending a DELETE request to the /delete/<metric> endpoint.

To delete foo.bar.baz, then:
```shell
$ curl -i -X DELETE http://metrics1.example.com/delete/foo.bar.baz
HTTP/1.1 204 NO CONTENT
Content-length: 0
Content-Type: text/html; charset=utf-8
Date: Mon, 17 Mar 2014 01:45:18 GMT
Server: gunicorn/18.0
Connection: keep-alive
```

Latest Queue
------------
Endpoints for interacting with the queue of latest metrics are /latest and /trim. Both return 200 on success.

To get the metrics in the queue:
```shell
$ curl -X GET http://metrics1.example.com/latest
```

To trim the queue down to the configured time interval:
```shell
$ curl -x POST http://metrics1.example.com/trim
```

