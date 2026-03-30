#!/bin/bash
dbt docs generate --profiles-dir /app/dbt
dbt docs serve --port 8081 --no-browser --host 0.0.0.0 &
tail -f /dev/null