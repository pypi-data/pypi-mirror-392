## Summary

Exporting prometheus metrics.

This cube provides a pyramid tween that will, when active, collect the metrics
configured in the settings pyramid.ini and expose them on route `/metrics`.

## Configuration

Include the metrics you want in pyramid.ini:

```
prometheus.pyramid.http_requests = True
prometheus.pyramid.current_requests = True
prometheus.pyramid.slow_routes = True
prometheus.pyramid.time_routes = True
prometheus.pyramid.count_routes = True

prometheus.cubicweb.sql.time = Histogram
prometheus.cubicweb.rql.time = Histogram

prometheus.uwsgi = True
prometheus.uwsgi.stats_url = http://127.0.0.1:1717
...
```

### Using labels from CubicWeb debug channels

The RQL debug channel publish the data defined in
[querier.py](https://forge.extranet.logilab.fr/cubicweb/cubicweb/-/blob/branch/default/cubicweb/server/querier.py?ref_type=heads).

Keys from the dict `query_debug_information` can be used as Prometheus labels
using the following syntax:

```
prometheus.cubicweb.rql.time.rql = Histogram
```

This will generate the following prometheus metrics with RQL query in labels `rql`.

```
rql_time_bucket{le="0.005",rql="Any X …"} 0.0
```

### UWSGI metrics

Add `stats` (and `stats-http` if needed) on `uwsgi.ini` file to enable UWSGI
metrics (<https://uwsgi-docs.readthedocs.io/en/latest/StatsServer.html>).

```ini
[uwsgi]
…
stats-http = true
stats = 127.0.0.1:1717
```

UWSGI will serve metrics on json format to `127.0.0.1:1717`. Pyramid will read
this metrics and serve them along the rest of its data.
