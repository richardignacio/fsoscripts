#!/bin/bash
source /opt/fireeye/fso/config/iso_package_dev_env
nohup /opt/fireeye/fso/apps/engine/python/global/bin/python hermod.py > /dev/null 2>&1 &
