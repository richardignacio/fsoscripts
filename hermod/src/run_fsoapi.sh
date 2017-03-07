#!/bin/bash
source /opt/fireeye/fso/config/iso_package_dev_env
rm -f hermod.log*
kill `ps aux | grep hermod | grep -v grep | tr -s " " | cut -d ' ' -f 2`
nohup /opt/fireeye/fso/apps/engine/python/global/bin/python hermod.py > /dev/null 2>&1 &
