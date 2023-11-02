#!/bin/sh
cd "$(dirname "$0")";
CWD="$(pwd)"
echo $CWD
/home/oseloka/pyprojects/maplecourt_py/venv_mc/bin/python expenses_daily_ETL.py
