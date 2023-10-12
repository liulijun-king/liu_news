#!/bin/bash
exec python3 -u ./run/scheduling_find.py >> ./logs/scheduling_find.log  2>&1 &
exec python3 -u ./run/scheduling_verification.py >> ./logs/scheduling_verification.log 2>&1