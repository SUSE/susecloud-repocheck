#!/usr/bin/python3

"""This script will perform an instance repository check and attempt
   to fix any issues which prevent the instance from registering to 
   the SUSE update infrastructure """

import argparse
import datetime
import json
import logging
import os
import re
import requests
import shlex
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from requests.packages import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VERSION = "1.2.8"
SCRIPT_NAME = "sc-repocheck"
BASEPRODUCT_FILE = "/etc/products.d/baseproduct"
pint_data = {}
problem_count = 0

# ----------------------------------------------------------------------------
# JSON Data
# ----------------------------------------------------------------------------

# PINT START
pint_data["azure"] = \
"""
[
    {
      "ip": "51.4.145.155",
      "name": "smt-azure.susecloud.net",
      "region": "Germany Central",
      "type": "smt-sles"
    },
    {
      "ip": "51.4.145.156",
      "name": "smt-azure.susecloud.net",
      "region": "Germany Central",
      "type": "smt-sles"
    },
    {
      "ip": "51.5.145.14",
      "name": "smt-azure.susecloud.net",
      "region": "Germany Northeast",
      "type": "smt-sles"
    },
    {
      "ip": "51.5.145.15",
      "name": "smt-azure.susecloud.net",
      "region": "Germany Northeast",
      "type": "smt-sles"
    },
    {
      "ip": "23.101.216.104",
      "name": "smt-azure.susecloud.net",
      "region": "australiacentral",
      "type": "smt"
    },
    {
      "ip": "23.101.210.206",
      "name": "smt-azure.susecloud.net",
      "region": "australiacentral",
      "type": "smt"
    },
    {
      "ip": "13.70.94.71",
      "name": "smt-azure.susecloud.net",
      "region": "australiacentral",
      "type": "smt"
    },
    {
      "ip": "23.101.235.14",
      "name": "smt-azure.susecloud.net",
      "region": "australiacentral2",
      "type": "smt"
    },
    {
      "ip": "23.101.231.234",
      "name": "smt-azure.susecloud.net",
      "region": "australiacentral2",
      "type": "smt"
    },
    {
      "ip": "13.73.107.146",
      "name": "smt-azure.susecloud.net",
      "region": "australiacentral2",
      "type": "smt"
    },
    {
      "ip": "23.101.216.104",
      "name": "smt-azure.susecloud.net",
      "region": "australiaeast",
      "type": "smt"
    },
    {
      "ip": "23.101.210.206",
      "name": "smt-azure.susecloud.net",
      "region": "australiaeast",
      "type": "smt"
    },
    {
      "ip": "13.70.94.71",
      "name": "smt-azure.susecloud.net",
      "region": "australiaeast",
      "type": "smt"
    },
    {
      "ip": "23.101.235.14",
      "name": "smt-azure.susecloud.net",
      "region": "australiasoutheast",
      "type": "smt"
    },
    {
      "ip": "23.101.231.234",
      "name": "smt-azure.susecloud.net",
      "region": "australiasoutheast",
      "type": "smt"
    },
    {
      "ip": "13.73.107.146",
      "name": "smt-azure.susecloud.net",
      "region": "australiasoutheast",
      "type": "smt"
    },
    {
      "ip": "191.237.255.212",
      "name": "smt-azure.susecloud.net",
      "region": "brazilsouth",
      "type": "smt"
    },
    {
      "ip": "191.237.253.40",
      "name": "smt-azure.susecloud.net",
      "region": "brazilsouth",
      "type": "smt"
    },
    {
      "ip": "191.235.81.180",
      "name": "smt-azure.susecloud.net",
      "region": "brazilsouth",
      "type": "smt"
    },
    {
      "ip": "191.237.255.212",
      "name": "smt-azure.susecloud.net",
      "region": "brazilsoutheast",
      "type": "smt"
    },
    {
      "ip": "191.237.253.40",
      "name": "smt-azure.susecloud.net",
      "region": "brazilsoutheast",
      "type": "smt"
    },
    {
      "ip": "191.235.81.180",
      "name": "smt-azure.susecloud.net",
      "region": "brazilsoutheast",
      "type": "smt"
    },
    {
      "ip": "40.85.225.32",
      "name": "smt-azure.susecloud.net",
      "region": "canadacentral",
      "type": "smt"
    },
    {
      "ip": "40.85.225.240",
      "name": "smt-azure.susecloud.net",
      "region": "canadacentral",
      "type": "smt"
    },
    {
      "ip": "52.228.41.50",
      "name": "smt-azure.susecloud.net",
      "region": "canadacentral",
      "type": "smt"
    },
    {
      "ip": "40.86.231.97",
      "name": "smt-azure.susecloud.net",
      "region": "canadaeast",
      "type": "smt"
    },
    {
      "ip": "40.86.231.128",
      "name": "smt-azure.susecloud.net",
      "region": "canadaeast",
      "type": "smt"
    },
    {
      "ip": "52.229.125.108",
      "name": "smt-azure.susecloud.net",
      "region": "canadaeast",
      "type": "smt"
    },
    {
      "ip": "40.66.32.54",
      "name": "smt-azure.susecloud.net",
      "region": "centralfrance",
      "type": "smt"
    },
    {
      "ip": "40.66.41.99",
      "name": "smt-azure.susecloud.net",
      "region": "centralfrance",
      "type": "smt"
    },
    {
      "ip": "40.66.48.231",
      "name": "smt-azure.susecloud.net",
      "region": "centralfrance",
      "type": "smt"
    },
    {
      "ip": "104.211.97.78",
      "name": "smt-azure.susecloud.net",
      "region": "centralindia",
      "type": "smt"
    },
    {
      "ip": "104.211.98.58",
      "name": "smt-azure.susecloud.net",
      "region": "centralindia",
      "type": "smt"
    },
    {
      "ip": "52.172.187.74",
      "name": "smt-azure.susecloud.net",
      "region": "centralindia",
      "type": "smt"
    },
    {
      "ip": "13.86.112.4",
      "name": "smt-azure.susecloud.net",
      "region": "centralus",
      "type": "smt"
    },
    {
      "ip": "52.165.88.13",
      "name": "smt-azure.susecloud.net",
      "region": "centralus",
      "type": "smt"
    },
    {
      "ip": "13.86.104.2",
      "name": "smt-azure.susecloud.net",
      "region": "centralus",
      "type": "smt"
    },
    {
      "ip": "13.86.112.4",
      "name": "smt-azure.susecloud.net",
      "region": "centraluseuap",
      "type": "smt"
    },
    {
      "ip": "52.165.88.13",
      "name": "smt-azure.susecloud.net",
      "region": "centraluseuap",
      "type": "smt"
    },
    {
      "ip": "13.86.104.2",
      "name": "smt-azure.susecloud.net",
      "region": "centraluseuap",
      "type": "smt"
    },
    {
      "ip": "23.101.14.157",
      "name": "smt-azure.susecloud.net",
      "region": "chinaeast",
      "type": "smt"
    },
    {
      "ip": "23.101.3.47",
      "name": "smt-azure.susecloud.net",
      "region": "chinaeast",
      "type": "smt"
    },
    {
      "ip": "13.75.123.198",
      "name": "smt-azure.susecloud.net",
      "region": "chinaeast",
      "type": "smt"
    },
    {
      "ip": "23.101.14.157",
      "name": "smt-azure.susecloud.net",
      "region": "chinaeast2",
      "type": "smt"
    },
    {
      "ip": "23.101.3.47",
      "name": "smt-azure.susecloud.net",
      "region": "chinaeast2",
      "type": "smt"
    },
    {
      "ip": "13.75.123.198",
      "name": "smt-azure.susecloud.net",
      "region": "chinaeast2",
      "type": "smt"
    },
    {
      "ip": "23.101.14.157",
      "name": "smt-azure.susecloud.net",
      "region": "chinanorth",
      "type": "smt"
    },
    {
      "ip": "23.101.3.47",
      "name": "smt-azure.susecloud.net",
      "region": "chinanorth",
      "type": "smt"
    },
    {
      "ip": "13.75.123.198",
      "name": "smt-azure.susecloud.net",
      "region": "chinanorth",
      "type": "smt"
    },
    {
      "ip": "23.101.14.157",
      "name": "smt-azure.susecloud.net",
      "region": "chinanorth2",
      "type": "smt"
    },
    {
      "ip": "23.101.3.47",
      "name": "smt-azure.susecloud.net",
      "region": "chinanorth2",
      "type": "smt"
    },
    {
      "ip": "13.75.123.198",
      "name": "smt-azure.susecloud.net",
      "region": "chinanorth2",
      "type": "smt"
    },
    {
      "ip": "23.101.14.157",
      "name": "smt-azure.susecloud.net",
      "region": "eastasia",
      "type": "smt"
    },
    {
      "ip": "23.101.3.47",
      "name": "smt-azure.susecloud.net",
      "region": "eastasia",
      "type": "smt"
    },
    {
      "ip": "13.75.123.198",
      "name": "smt-azure.susecloud.net",
      "region": "eastasia",
      "type": "smt"
    },
    {
      "ip": "52.188.224.179",
      "name": "smt-azure.susecloud.net",
      "region": "eastus",
      "type": "smt"
    },
    {
      "ip": "52.188.81.163",
      "name": "smt-azure.susecloud.net",
      "region": "eastus",
      "type": "smt"
    },
    {
      "ip": "52.186.168.210",
      "name": "smt-azure.susecloud.net",
      "region": "eastus",
      "type": "smt"
    },
    {
      "ip": "52.147.176.11",
      "name": "smt-azure.susecloud.net",
      "region": "eastus2",
      "type": "smt"
    },
    {
      "ip": "20.186.88.79",
      "name": "smt-azure.susecloud.net",
      "region": "eastus2",
      "type": "smt"
    },
    {
      "ip": "20.186.112.116",
      "name": "smt-azure.susecloud.net",
      "region": "eastus2",
      "type": "smt"
    },
    {
      "ip": "52.147.176.11",
      "name": "smt-azure.susecloud.net",
      "region": "eastus2euap",
      "type": "smt"
    },
    {
      "ip": "20.186.88.79",
      "name": "smt-azure.susecloud.net",
      "region": "eastus2euap",
      "type": "smt"
    },
    {
      "ip": "20.186.112.116",
      "name": "smt-azure.susecloud.net",
      "region": "eastus2euap",
      "type": "smt"
    },
    {
      "ip": "40.66.32.54",
      "name": "smt-azure.susecloud.net",
      "region": "francecentral",
      "type": "smt"
    },
    {
      "ip": "40.66.41.99",
      "name": "smt-azure.susecloud.net",
      "region": "francecentral",
      "type": "smt"
    },
    {
      "ip": "40.66.48.231",
      "name": "smt-azure.susecloud.net",
      "region": "francecentral",
      "type": "smt"
    },
    {
      "ip": "51.116.98.203",
      "name": "smt-azure.susecloud.net",
      "region": "germanycentral",
      "type": "smt"
    },
    {
      "ip": "51.116.98.214",
      "name": "smt-azure.susecloud.net",
      "region": "germanycentral",
      "type": "smt"
    },
    {
      "ip": "51.116.96.37",
      "name": "smt-azure.susecloud.net",
      "region": "germanycentral",
      "type": "smt"
    },
    {
      "ip": "51.116.98.203",
      "name": "smt-azure.susecloud.net",
      "region": "germanynorth",
      "type": "smt"
    },
    {
      "ip": "51.116.98.214",
      "name": "smt-azure.susecloud.net",
      "region": "germanynorth",
      "type": "smt"
    },
    {
      "ip": "51.116.96.37",
      "name": "smt-azure.susecloud.net",
      "region": "germanynorth",
      "type": "smt"
    },
    {
      "ip": "51.116.98.203",
      "name": "smt-azure.susecloud.net",
      "region": "germanynortheast",
      "type": "smt"
    },
    {
      "ip": "51.116.98.214",
      "name": "smt-azure.susecloud.net",
      "region": "germanynortheast",
      "type": "smt"
    },
    {
      "ip": "51.116.96.37",
      "name": "smt-azure.susecloud.net",
      "region": "germanynortheast",
      "type": "smt"
    },
    {
      "ip": "51.116.98.203",
      "name": "smt-azure.susecloud.net",
      "region": "germanywestcentral",
      "type": "smt"
    },
    {
      "ip": "51.116.98.214",
      "name": "smt-azure.susecloud.net",
      "region": "germanywestcentral",
      "type": "smt"
    },
    {
      "ip": "51.116.96.37",
      "name": "smt-azure.susecloud.net",
      "region": "germanywestcentral",
      "type": "smt"
    },
    {
      "ip": "52.185.185.83",
      "name": "smt-azure.susecloud.net",
      "region": "japaneast",
      "type": "smt"
    },
    {
      "ip": "40.81.208.103",
      "name": "smt-azure.susecloud.net",
      "region": "japaneast",
      "type": "smt"
    },
    {
      "ip": "40.81.200.4",
      "name": "smt-azure.susecloud.net",
      "region": "japaneast",
      "type": "smt"
    },
    {
      "ip": "104.46.239.62",
      "name": "smt-azure.susecloud.net",
      "region": "japanwest",
      "type": "smt"
    },
    {
      "ip": "104.46.239.65",
      "name": "smt-azure.susecloud.net",
      "region": "japanwest",
      "type": "smt"
    },
    {
      "ip": "40.74.120.164",
      "name": "smt-azure.susecloud.net",
      "region": "japanwest",
      "type": "smt"
    },
    {
      "ip": "52.231.39.82",
      "name": "smt-azure.susecloud.net",
      "region": "koreacentral",
      "type": "smt"
    },
    {
      "ip": "52.231.39.83",
      "name": "smt-azure.susecloud.net",
      "region": "koreacentral",
      "type": "smt"
    },
    {
      "ip": "52.231.34.241",
      "name": "smt-azure.susecloud.net",
      "region": "koreacentral",
      "type": "smt"
    },
    {
      "ip": "52.231.201.188",
      "name": "smt-azure.susecloud.net",
      "region": "koreasouth",
      "type": "smt"
    },
    {
      "ip": "52.231.201.178",
      "name": "smt-azure.susecloud.net",
      "region": "koreasouth",
      "type": "smt"
    },
    {
      "ip": "52.231.202.220",
      "name": "smt-azure.susecloud.net",
      "region": "koreasouth",
      "type": "smt"
    },
    {
      "ip": "23.101.164.199",
      "name": "smt-azure.susecloud.net",
      "region": "northcentralus",
      "type": "smt"
    },
    {
      "ip": "23.101.171.119",
      "name": "smt-azure.susecloud.net",
      "region": "northcentralus",
      "type": "smt"
    },
    {
      "ip": "23.96.231.74",
      "name": "smt-azure.susecloud.net",
      "region": "northcentralus",
      "type": "smt"
    },
    {
      "ip": "52.158.42.90",
      "name": "smt-azure.susecloud.net",
      "region": "northeurope",
      "type": "smt"
    },
    {
      "ip": "13.79.120.39",
      "name": "smt-azure.susecloud.net",
      "region": "northeurope",
      "type": "smt"
    },
    {
      "ip": "52.155.248.41",
      "name": "smt-azure.susecloud.net",
      "region": "northeurope",
      "type": "smt"
    },
    {
      "ip": "51.120.2.195",
      "name": "smt-azure.susecloud.net",
      "region": "norwayeast",
      "type": "smt"
    },
    {
      "ip": "51.120.0.31",
      "name": "smt-azure.susecloud.net",
      "region": "norwayeast",
      "type": "smt"
    },
    {
      "ip": "51.120.2.159",
      "name": "smt-azure.susecloud.net",
      "region": "norwayeast",
      "type": "smt"
    },
    {
      "ip": "51.120.2.195",
      "name": "smt-azure.susecloud.net",
      "region": "norwaywest",
      "type": "smt"
    },
    {
      "ip": "51.120.0.31",
      "name": "smt-azure.susecloud.net",
      "region": "norwaywest",
      "type": "smt"
    },
    {
      "ip": "51.120.2.159",
      "name": "smt-azure.susecloud.net",
      "region": "norwaywest",
      "type": "smt"
    },
    {
      "ip": "102.133.128.124",
      "name": "smt-azure.susecloud.net",
      "region": "southafricanorth",
      "type": "smt"
    },
    {
      "ip": "102.133.128.67",
      "name": "smt-azure.susecloud.net",
      "region": "southafricanorth",
      "type": "smt"
    },
    {
      "ip": "102.133.129.51",
      "name": "smt-azure.susecloud.net",
      "region": "southafricanorth",
      "type": "smt"
    },
    {
      "ip": "102.133.128.124",
      "name": "smt-azure.susecloud.net",
      "region": "southafricawest",
      "type": "smt"
    },
    {
      "ip": "102.133.128.67",
      "name": "smt-azure.susecloud.net",
      "region": "southafricawest",
      "type": "smt"
    },
    {
      "ip": "102.133.129.51",
      "name": "smt-azure.susecloud.net",
      "region": "southafricawest",
      "type": "smt"
    },
    {
      "ip": "23.101.186.158",
      "name": "smt-azure.susecloud.net",
      "region": "southcentralus",
      "type": "smt"
    },
    {
      "ip": "23.101.188.13",
      "name": "smt-azure.susecloud.net",
      "region": "southcentralus",
      "type": "smt"
    },
    {
      "ip": "13.65.81.103",
      "name": "smt-azure.susecloud.net",
      "region": "southcentralus",
      "type": "smt"
    },
    {
      "ip": "23.101.186.158",
      "name": "smt-azure.susecloud.net",
      "region": "southcentralusstg",
      "type": "smt"
    },
    {
      "ip": "23.101.188.13",
      "name": "smt-azure.susecloud.net",
      "region": "southcentralusstg",
      "type": "smt"
    },
    {
      "ip": "13.65.81.103",
      "name": "smt-azure.susecloud.net",
      "region": "southcentralusstg",
      "type": "smt"
    },
    {
      "ip": "52.230.96.47",
      "name": "smt-azure.susecloud.net",
      "region": "southeastasia",
      "type": "smt"
    },
    {
      "ip": "52.237.80.2",
      "name": "smt-azure.susecloud.net",
      "region": "southeastasia",
      "type": "smt"
    },
    {
      "ip": "52.139.216.51",
      "name": "smt-azure.susecloud.net",
      "region": "southeastasia",
      "type": "smt"
    },
    {
      "ip": "40.66.32.54",
      "name": "smt-azure.susecloud.net",
      "region": "francesouth",
      "type": "smt"
    },
    {
      "ip": "40.66.41.99",
      "name": "smt-azure.susecloud.net",
      "region": "francesouth",
      "type": "smt"
    },
    {
      "ip": "40.66.48.231",
      "name": "smt-azure.susecloud.net",
      "region": "francesouth",
      "type": "smt"
    },
    {
      "ip": "104.211.227.174",
      "name": "smt-azure.susecloud.net",
      "region": "southindia",
      "type": "smt"
    },
    {
      "ip": "104.211.227.169",
      "name": "smt-azure.susecloud.net",
      "region": "southindia",
      "type": "smt"
    },
    {
      "ip": "52.172.51.125",
      "name": "smt-azure.susecloud.net",
      "region": "southindia",
      "type": "smt"
    },
    {
      "ip": "51.107.0.120",
      "name": "smt-azure.susecloud.net",
      "region": "switzerlandnorth",
      "type": "smt"
    },
    {
      "ip": "51.107.0.121",
      "name": "smt-azure.susecloud.net",
      "region": "switzerlandnorth",
      "type": "smt"
    },
    {
      "ip": "51.107.0.122",
      "name": "smt-azure.susecloud.net",
      "region": "switzerlandnorth",
      "type": "smt"
    },
    {
      "ip": "51.107.0.120",
      "name": "smt-azure.susecloud.net",
      "region": "switzerlandwest",
      "type": "smt"
    },
    {
      "ip": "51.107.0.121",
      "name": "smt-azure.susecloud.net",
      "region": "switzerlandwest",
      "type": "smt"
    },
    {
      "ip": "51.107.0.122",
      "name": "smt-azure.susecloud.net",
      "region": "switzerlandwest",
      "type": "smt"
    },
    {
      "ip": "20.46.144.230",
      "name": "smt-azure.susecloud.net",
      "region": "uaenorth",
      "type": "smt"
    },
    {
      "ip": "20.46.144.239",
      "name": "smt-azure.susecloud.net",
      "region": "uaenorth",
      "type": "smt"
    },
    {
      "ip": "20.46.146.20",
      "name": "smt-azure.susecloud.net",
      "region": "uaenorth",
      "type": "smt"
    },
    {
      "ip": "20.46.144.230",
      "name": "smt-azure.susecloud.net",
      "region": "uaecentral",
      "type": "smt"
    },
    {
      "ip": "20.46.144.239",
      "name": "smt-azure.susecloud.net",
      "region": "uaecentral",
      "type": "smt"
    },
    {
      "ip": "20.46.146.20",
      "name": "smt-azure.susecloud.net",
      "region": "uaecentral",
      "type": "smt"
    },
    {
      "ip": "51.141.12.56",
      "name": "smt-azure.susecloud.net",
      "region": "uknorth",
      "type": "smt"
    },
    {
      "ip": "51.141.12.57",
      "name": "smt-azure.susecloud.net",
      "region": "uknorth",
      "type": "smt"
    },
    {
      "ip": "51.141.11.221",
      "name": "smt-azure.susecloud.net",
      "region": "uknorth",
      "type": "smt"
    },
    {
      "ip": "20.39.208.99",
      "name": "smt-azure.susecloud.net",
      "region": "uksouth",
      "type": "smt"
    },
    {
      "ip": "20.39.216.18",
      "name": "smt-azure.susecloud.net",
      "region": "uksouth",
      "type": "smt"
    },
    {
      "ip": "20.39.224.10",
      "name": "smt-azure.susecloud.net",
      "region": "uksouth",
      "type": "smt"
    },
    {
      "ip": "20.39.208.99",
      "name": "smt-azure.susecloud.net",
      "region": "uksouth2",
      "type": "smt"
    },
    {
      "ip": "20.39.216.18",
      "name": "smt-azure.susecloud.net",
      "region": "uksouth2",
      "type": "smt"
    },
    {
      "ip": "20.39.224.10",
      "name": "smt-azure.susecloud.net",
      "region": "uksouth2",
      "type": "smt"
    },
    {
      "ip": "51.141.12.56",
      "name": "smt-azure.susecloud.net",
      "region": "ukwest",
      "type": "smt"
    },
    {
      "ip": "51.141.12.57",
      "name": "smt-azure.susecloud.net",
      "region": "ukwest",
      "type": "smt"
    },
    {
      "ip": "51.141.11.221",
      "name": "smt-azure.susecloud.net",
      "region": "ukwest",
      "type": "smt"
    },
    {
      "ip": "52.161.26.245",
      "name": "smt-azure.susecloud.net",
      "region": "westcentralus",
      "type": "smt"
    },
    {
      "ip": "52.161.27.73",
      "name": "smt-azure.susecloud.net",
      "region": "westcentralus",
      "type": "smt"
    },
    {
      "ip": "52.161.26.42",
      "name": "smt-azure.susecloud.net",
      "region": "westcentralus",
      "type": "smt"
    },
    {
      "ip": "104.211.161.139",
      "name": "smt-azure.susecloud.net",
      "region": "westindia",
      "type": "smt"
    },
    {
      "ip": "104.211.161.138",
      "name": "smt-azure.susecloud.net",
      "region": "westindia",
      "type": "smt"
    },
    {
      "ip": "104.211.166.161",
      "name": "smt-azure.susecloud.net",
      "region": "westindia",
      "type": "smt"
    },
    {
      "ip": "52.149.120.86",
      "name": "smt-azure.susecloud.net",
      "region": "westeurope",
      "type": "smt"
    },
    {
      "ip": "51.145.209.119",
      "name": "smt-azure.susecloud.net",
      "region": "westeurope",
      "type": "smt"
    },
    {
      "ip": "52.157.241.14",
      "name": "smt-azure.susecloud.net",
      "region": "westeurope",
      "type": "smt"
    },
    {
      "ip": "23.100.46.123",
      "name": "smt-azure.susecloud.net",
      "region": "westus",
      "type": "smt"
    },
    {
      "ip": "23.101.192.253",
      "name": "smt-azure.susecloud.net",
      "region": "westus",
      "type": "smt"
    },
    {
      "ip": "40.112.248.207",
      "name": "smt-azure.susecloud.net",
      "region": "westus",
      "type": "smt"
    },
    {
      "ip": "40.90.192.185",
      "name": "smt-azure.susecloud.net",
      "region": "westus2",
      "type": "smt"
    },
    {
      "ip": "52.148.152.22",
      "name": "smt-azure.susecloud.net",
      "region": "westus2",
      "type": "smt"
    },
    {
      "ip": "52.156.104.18",
      "name": "smt-azure.susecloud.net",
      "region": "westus2",
      "type": "smt"
    },
    {
      "ip": "20.38.0.87",
      "name": "smt-azure.susecloud.net",
      "region": "westus3",
      "type": "smt"
    },
    {
      "ip": "20.38.1.19",
      "name": "smt-azure.susecloud.net",
      "region": "westus3",
      "type": "smt"
    },
    {
      "ip": "20.38.0.31",
      "name": "smt-azure.susecloud.net",
      "region": "westus3",
      "type": "smt"
    },
    {
      "ip": "23.101.164.199",
      "name": "smt-azure.susecloud.net",
      "region": "usdodcentral",
      "type": "smt"
    },
    {
      "ip": "23.101.171.119",
      "name": "smt-azure.susecloud.net",
      "region": "usdodcentral",
      "type": "smt"
    },
    {
      "ip": "23.96.231.74",
      "name": "smt-azure.susecloud.net",
      "region": "usdodcentral",
      "type": "smt"
    },
    {
      "ip": "52.188.224.179",
      "name": "smt-azure.susecloud.net",
      "region": "usdodeast",
      "type": "smt"
    },
    {
      "ip": "52.188.81.163",
      "name": "smt-azure.susecloud.net",
      "region": "usdodeast",
      "type": "smt"
    },
    {
      "ip": "52.186.168.210",
      "name": "smt-azure.susecloud.net",
      "region": "usdodeast",
      "type": "smt"
    },
    {
      "ip": "52.161.26.245",
      "name": "smt-azure.susecloud.net",
      "region": "usgovarizona",
      "type": "smt"
    },
    {
      "ip": "52.161.27.73",
      "name": "smt-azure.susecloud.net",
      "region": "usgovarizona",
      "type": "smt"
    },
    {
      "ip": "52.161.26.42",
      "name": "smt-azure.susecloud.net",
      "region": "usgovarizona",
      "type": "smt"
    },
    {
      "ip": "13.86.112.4",
      "name": "smt-azure.susecloud.net",
      "region": "usgoviowa",
      "type": "smt"
    },
    {
      "ip": "52.165.88.13",
      "name": "smt-azure.susecloud.net",
      "region": "usgoviowa",
      "type": "smt"
    },
    {
      "ip": "13.86.104.2",
      "name": "smt-azure.susecloud.net",
      "region": "usgoviowa",
      "type": "smt"
    },
    {
      "ip": "23.101.186.158",
      "name": "smt-azure.susecloud.net",
      "region": "usgovtexas",
      "type": "smt"
    },
    {
      "ip": "23.101.188.13",
      "name": "smt-azure.susecloud.net",
      "region": "usgovtexas",
      "type": "smt"
    },
    {
      "ip": "13.65.81.103",
      "name": "smt-azure.susecloud.net",
      "region": "usgovtexas",
      "type": "smt"
    },
    {
      "ip": "52.147.176.11",
      "name": "smt-azure.susecloud.net",
      "region": "usgovvirginia",
      "type": "smt"
    },
    {
      "ip": "20.186.88.79",
      "name": "smt-azure.susecloud.net",
      "region": "usgovvirginia",
      "type": "smt"
    },
    {
      "ip": "20.186.112.116",
      "name": "smt-azure.susecloud.net",
      "region": "usgovvirginia",
      "type": "smt"
    }
  ]
"""
pint_data["ec2"] = \
"""
[
    {
      "ip": "13.244.54.57",
      "name": "smt-ec2.susecloud.net",
      "region": "af-south-1",
      "type": "smt"
    },
    {
      "ip": "13.244.40.27",
      "name": "smt-ec2.susecloud.net",
      "region": "af-south-1",
      "type": "smt"
    },
    {
      "ip": "13.245.60.134",
      "name": "smt-ec2.susecloud.net",
      "region": "af-south-1",
      "type": "smt"
    },
    {
      "ip": "18.162.90.181",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-east-1",
      "type": "smt"
    },
    {
      "ip": "18.162.132.113",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-east-1",
      "type": "smt"
    },
    {
      "ip": "18.162.83.253",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-east-1",
      "type": "smt"
    },
    {
      "ip": "54.248.86.233",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-northeast-1",
      "type": "smt"
    },
    {
      "ip": "54.248.240.93",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-northeast-1",
      "type": "smt"
    },
    {
      "ip": "54.248.226.128",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-northeast-1",
      "type": "smt"
    },
    {
      "ip": "52.79.38.96",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-northeast-2",
      "type": "smt"
    },
    {
      "ip": "52.79.39.98",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-northeast-2",
      "type": "smt"
    },
    {
      "ip": "52.79.134.51",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-northeast-2",
      "type": "smt"
    },
    {
      "ip": "52.66.49.238",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-south-1",
      "type": "smt"
    },
    {
      "ip": "52.66.45.16",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-south-1",
      "type": "smt"
    },
    {
      "ip": "52.66.51.63",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-south-1",
      "type": "smt"
    },
    {
      "ip": "122.248.246.124",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-southeast-1",
      "type": "smt"
    },
    {
      "ip": "54.254.106.151",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-southeast-1",
      "type": "smt"
    },
    {
      "ip": "54.251.254.125",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-southeast-1",
      "type": "smt"
    },
    {
      "ip": "54.253.249.15",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-southeast-2",
      "type": "smt"
    },
    {
      "ip": "54.253.114.150",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-southeast-2",
      "type": "smt"
    },
    {
      "ip": "54.66.121.137",
      "name": "smt-ec2.susecloud.net",
      "region": "ap-southeast-2",
      "type": "smt"
    },
    {
      "ip": "52.60.53.175",
      "name": "smt-ec2.susecloud.net",
      "region": "ca-central-1",
      "type": "smt"
    },
    {
      "ip": "52.60.53.224",
      "name": "smt-ec2.susecloud.net",
      "region": "ca-central-1",
      "type": "smt"
    },
    {
      "ip": "52.60.50.162",
      "name": "smt-ec2.susecloud.net",
      "region": "ca-central-1",
      "type": "smt"
    },
    {
      "ip": "54.223.131.108",
      "name": "smt-ec2.susecloud.net",
      "region": "cn-north-1",
      "type": "smt"
    },
    {
      "ip": "54.223.140.138",
      "name": "smt-ec2.susecloud.net",
      "region": "cn-north-1",
      "type": "smt"
    },
    {
      "ip": "54.222.142.49",
      "name": "smt-ec2.susecloud.net",
      "region": "cn-north-1",
      "type": "smt"
    },
    {
      "ip": "52.83.151.90",
      "name": "smt-ec2.susecloud.net",
      "region": "cn-northwest-1",
      "type": "smt"
    },
    {
      "ip": "52.83.113.211",
      "name": "smt-ec2.susecloud.net",
      "region": "cn-northwest-1",
      "type": "smt"
    },
    {
      "ip": "52.83.247.110",
      "name": "smt-ec2.susecloud.net",
      "region": "cn-northwest-1",
      "type": "smt"
    },
    {
      "ip": "54.93.130.182",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-central-1",
      "type": "smt"
    },
    {
      "ip": "54.93.131.24",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-central-1",
      "type": "smt"
    },
    {
      "ip": "52.28.214.37",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-central-1",
      "type": "smt"
    },
    {
      "ip": "15.161.33.0",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-south-1",
      "type": "smt"
    },
    {
      "ip": "15.161.39.2",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-south-1",
      "type": "smt"
    },
    {
      "ip": "15.161.27.146",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-south-1",
      "type": "smt"
    },
    {
      "ip": "13.53.91.131",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-north-1",
      "type": "smt"
    },
    {
      "ip": "13.53.91.167",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-north-1",
      "type": "smt"
    },
    {
      "ip": "13.53.77.232",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-north-1",
      "type": "smt"
    },
    {
      "ip": "54.246.90.215",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-west-1",
      "type": "smt"
    },
    {
      "ip": "54.75.232.245",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-west-1",
      "type": "smt"
    },
    {
      "ip": "176.34.126.172",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-west-1",
      "type": "smt"
    },
    {
      "ip": "52.56.58.194",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-west-2",
      "type": "smt"
    },
    {
      "ip": "52.56.58.190",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-west-2",
      "type": "smt"
    },
    {
      "ip": "52.56.59.89",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-west-2",
      "type": "smt"
    },
    {
      "ip": "52.47.108.87",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-west-3",
      "type": "smt"
    },
    {
      "ip": "52.47.113.10",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-west-3",
      "type": "smt"
    },
    {
      "ip": "52.47.92.102",
      "name": "smt-ec2.susecloud.net",
      "region": "eu-west-3",
      "type": "smt"
    },
    {
      "ip": "15.185.47.44",
      "name": "smt-ec2.susecloud.net",
      "region": "me-south-1",
      "type": "smt"
    },
    {
      "ip": "157.175.138.207",
      "name": "smt-ec2.susecloud.net",
      "region": "me-south-1",
      "type": "smt"
    },
    {
      "ip": "157.175.6.182",
      "name": "smt-ec2.susecloud.net",
      "region": "me-south-1",
      "type": "smt"
    },
    {
      "ip": "177.71.187.15",
      "name": "smt-ec2.susecloud.net",
      "region": "sa-east-1",
      "type": "smt"
    },
    {
      "ip": "54.232.112.38",
      "name": "smt-ec2.susecloud.net",
      "region": "sa-east-1",
      "type": "smt"
    },
    {
      "ip": "54.232.114.156",
      "name": "smt-ec2.susecloud.net",
      "region": "sa-east-1",
      "type": "smt"
    },
    {
      "ip": "54.197.240.216",
      "name": "smt-ec2.susecloud.net",
      "region": "us-east-1",
      "type": "smt"
    },
    {
      "ip": "54.225.105.144",
      "name": "smt-ec2.susecloud.net",
      "region": "us-east-1",
      "type": "smt"
    },
    {
      "ip": "107.22.231.220",
      "name": "smt-ec2.susecloud.net",
      "region": "us-east-1",
      "type": "smt"
    },
    {
      "ip": "52.15.49.139",
      "name": "smt-ec2.susecloud.net",
      "region": "us-east-2",
      "type": "smt"
    },
    {
      "ip": "52.15.84.50",
      "name": "smt-ec2.susecloud.net",
      "region": "us-east-2",
      "type": "smt"
    },
    {
      "ip": "52.15.50.30",
      "name": "smt-ec2.susecloud.net",
      "region": "us-east-2",
      "type": "smt"
    },
    {
      "ip": "50.18.104.175",
      "name": "smt-ec2.susecloud.net",
      "region": "us-west-1",
      "type": "smt"
    },
    {
      "ip": "50.18.105.39",
      "name": "smt-ec2.susecloud.net",
      "region": "us-west-1",
      "type": "smt"
    },
    {
      "ip": "54.215.80.72",
      "name": "smt-ec2.susecloud.net",
      "region": "us-west-1",
      "type": "smt"
    },
    {
      "ip": "54.244.114.254",
      "name": "smt-ec2.susecloud.net",
      "region": "us-west-2",
      "type": "smt"
    },
    {
      "ip": "54.245.112.93",
      "name": "smt-ec2.susecloud.net",
      "region": "us-west-2",
      "type": "smt"
    },
    {
      "ip": "54.245.101.73",
      "name": "smt-ec2.susecloud.net",
      "region": "us-west-2",
      "type": "smt"
    }
  ]
"""
pint_data["gce"] = \
"""
[
    {
      "ip": "107.167.177.171",
      "name": "smt-gce.susecloud.net",
      "region": "asia-east1",
      "type": "smt"
    },
    {
      "ip": "107.167.180.126",
      "name": "smt-gce.susecloud.net",
      "region": "asia-east1",
      "type": "smt"
    },
    {
      "ip": "104.199.135.44",
      "name": "smt-gce.susecloud.net",
      "region": "asia-east1",
      "type": "smt"
    },
    {
      "ip": "35.220.221.180",
      "name": "smt-gce.susecloud.net",
      "region": "asia-east2",
      "type": "smt"
    },
    {
      "ip": "35.220.133.207",
      "name": "smt-gce.susecloud.net",
      "region": "asia-east2",
      "type": "smt"
    },
    {
      "ip": "35.241.72.175",
      "name": "smt-gce.susecloud.net",
      "region": "asia-east2",
      "type": "smt"
    },
    {
      "ip": "104.198.124.121",
      "name": "smt-gce.susecloud.net",
      "region": "asia-northeast1",
      "type": "smt"
    },
    {
      "ip": "104.198.115.243",
      "name": "smt-gce.susecloud.net",
      "region": "asia-northeast1",
      "type": "smt"
    },
    {
      "ip": "35.187.203.149",
      "name": "smt-gce.susecloud.net",
      "region": "asia-northeast1",
      "type": "smt"
    },
    {
      "ip": "34.97.17.129",
      "name": "smt-gce.susecloud.net",
      "region": "asia-northeast2",
      "type": "smt"
    },
    {
      "ip": "34.97.135.188",
      "name": "smt-gce.susecloud.net",
      "region": "asia-northeast2",
      "type": "smt"
    },
    {
      "ip": "34.97.1.22",
      "name": "smt-gce.susecloud.net",
      "region": "asia-northeast2",
      "type": "smt"
    },
    {
      "ip": "34.64.156.194",
      "name": "smt-gce.susecloud.net",
      "region": "asia-northeast3",
      "type": "smt"
    },
    {
      "ip": "34.64.220.20",
      "name": "smt-gce.susecloud.net",
      "region": "asia-northeast3",
      "type": "smt"
    },
    {
      "ip": "34.64.191.36",
      "name": "smt-gce.susecloud.net",
      "region": "asia-northeast3",
      "type": "smt"
    },
    {
      "ip": "35.244.47.233",
      "name": "smt-gce.susecloud.net",
      "region": "asia-south1",
      "type": "smt"
    },
    {
      "ip": "35.244.53.235",
      "name": "smt-gce.susecloud.net",
      "region": "asia-south1",
      "type": "smt"
    },
    {
      "ip": "35.244.54.174",
      "name": "smt-gce.susecloud.net",
      "region": "asia-south1",
      "type": "smt"
    },
    {
      "ip": "35.185.189.204",
      "name": "smt-gce.susecloud.net",
      "region": "asia-southeast1",
      "type": "smt"
    },
    {
      "ip": "35.185.180.225",
      "name": "smt-gce.susecloud.net",
      "region": "asia-southeast1",
      "type": "smt"
    },
    {
      "ip": "35.185.180.164",
      "name": "smt-gce.susecloud.net",
      "region": "asia-southeast1",
      "type": "smt"
    },
    {
      "ip": "34.101.118.189",
      "name": "smt-gce.susecloud.net",
      "region": "asia-southeast2",
      "type": "smt"
    },
    {
      "ip": "34.101.129.134",
      "name": "smt-gce.susecloud.net",
      "region": "asia-southeast2",
      "type": "smt"
    },
    {
      "ip": "34.101.150.228",
      "name": "smt-gce.susecloud.net",
      "region": "asia-southeast2",
      "type": "smt"
    },
    {
      "ip": "35.197.189.68",
      "name": "smt-gce.susecloud.net",
      "region": "australia-southeast1",
      "type": "smt"
    },
    {
      "ip": "35.189.52.87",
      "name": "smt-gce.susecloud.net",
      "region": "australia-southeast1",
      "type": "smt"
    },
    {
      "ip": "35.201.31.111",
      "name": "smt-gce.susecloud.net",
      "region": "australia-southeast1",
      "type": "smt"
    },
    {
      "ip": "35.228.142.43",
      "name": "smt-gce.susecloud.net",
      "region": "europe-north1",
      "type": "smt"
    },
    {
      "ip": "35.228.148.188",
      "name": "smt-gce.susecloud.net",
      "region": "europe-north1",
      "type": "smt"
    },
    {
      "ip": "35.228.201.140",
      "name": "smt-gce.susecloud.net",
      "region": "europe-north1",
      "type": "smt"
    },
    {
      "ip": "192.158.29.172",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west1",
      "type": "smt"
    },
    {
      "ip": "23.251.128.172",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west1",
      "type": "smt"
    },
    {
      "ip": "35.187.10.100",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west1",
      "type": "smt"
    },
    {
      "ip": "35.189.71.14",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west2",
      "type": "smt"
    },
    {
      "ip": "35.189.66.119",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west2",
      "type": "smt"
    },
    {
      "ip": "35.189.74.184",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west2",
      "type": "smt"
    },
    {
      "ip": "35.198.79.254",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west3",
      "type": "smt"
    },
    {
      "ip": "35.198.102.220",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west3",
      "type": "smt"
    },
    {
      "ip": "35.198.118.99",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west3",
      "type": "smt"
    },
    {
      "ip": "35.204.184.183",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west4",
      "type": "smt"
    },
    {
      "ip": "35.204.109.102",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west4",
      "type": "smt"
    },
    {
      "ip": "35.204.122.117",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west4",
      "type": "smt"
    },
    {
      "ip": "34.65.167.82",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west6",
      "type": "smt"
    },
    {
      "ip": "34.65.120.183",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west6",
      "type": "smt"
    },
    {
      "ip": "34.65.187.174",
      "name": "smt-gce.susecloud.net",
      "region": "europe-west6",
      "type": "smt"
    },
    {
      "ip": "35.203.93.203",
      "name": "smt-gce.susecloud.net",
      "region": "northamerica-northeast1",
      "type": "smt"
    },
    {
      "ip": "35.203.20.10",
      "name": "smt-gce.susecloud.net",
      "region": "northamerica-northeast1",
      "type": "smt"
    },
    {
      "ip": "35.203.24.115",
      "name": "smt-gce.susecloud.net",
      "region": "northamerica-northeast1",
      "type": "smt"
    },
    {
      "ip": "35.198.16.136",
      "name": "smt-gce.susecloud.net",
      "region": "southamerica-east1",
      "type": "smt"
    },
    {
      "ip": "35.198.30.115",
      "name": "smt-gce.susecloud.net",
      "region": "southamerica-east1",
      "type": "smt"
    },
    {
      "ip": "35.199.89.249",
      "name": "smt-gce.susecloud.net",
      "region": "southamerica-east1",
      "type": "smt"
    },
    {
      "ip": "108.59.80.221",
      "name": "smt-gce.susecloud.net",
      "region": "us-central1",
      "type": "smt"
    },
    {
      "ip": "108.59.85.41",
      "name": "smt-gce.susecloud.net",
      "region": "us-central1",
      "type": "smt"
    },
    {
      "ip": "108.59.80.58",
      "name": "smt-gce.susecloud.net",
      "region": "us-central1",
      "type": "smt"
    },
    {
      "ip": "35.186.86.137",
      "name": "smt-gce.susecloud.net",
      "region": "us-central2",
      "type": "smt"
    },
    {
      "ip": "173.255.121.33",
      "name": "smt-gce.susecloud.net",
      "region": "us-central2",
      "type": "smt"
    },
    {
      "ip": "35.186.92.214",
      "name": "smt-gce.susecloud.net",
      "region": "us-central2",
      "type": "smt"
    },
    {
      "ip": "104.196.61.109",
      "name": "smt-gce.susecloud.net",
      "region": "us-east1",
      "type": "smt"
    },
    {
      "ip": "104.196.26.155",
      "name": "smt-gce.susecloud.net",
      "region": "us-east1",
      "type": "smt"
    },
    {
      "ip": "104.196.220.87",
      "name": "smt-gce.susecloud.net",
      "region": "us-east1",
      "type": "smt"
    },
    {
      "ip": "35.186.167.77",
      "name": "smt-gce.susecloud.net",
      "region": "us-east4",
      "type": "smt"
    },
    {
      "ip": "35.186.173.156",
      "name": "smt-gce.susecloud.net",
      "region": "us-east4",
      "type": "smt"
    },
    {
      "ip": "35.186.187.53",
      "name": "smt-gce.susecloud.net",
      "region": "us-east4",
      "type": "smt"
    },
    {
      "ip": "104.196.227.89",
      "name": "smt-gce.susecloud.net",
      "region": "us-west1",
      "type": "smt"
    },
    {
      "ip": "104.196.231.164",
      "name": "smt-gce.susecloud.net",
      "region": "us-west1",
      "type": "smt"
    },
    {
      "ip": "104.198.14.82",
      "name": "smt-gce.susecloud.net",
      "region": "us-west1",
      "type": "smt"
    },
    {
      "ip": "35.236.105.72",
      "name": "smt-gce.susecloud.net",
      "region": "us-west2",
      "type": "smt"
    },
    {
      "ip": "35.235.125.59",
      "name": "smt-gce.susecloud.net",
      "region": "us-west2",
      "type": "smt"
    },
    {
      "ip": "35.235.80.144",
      "name": "smt-gce.susecloud.net",
      "region": "us-west2",
      "type": "smt"
    },
    {
      "ip": "34.106.238.55",
      "name": "smt-gce.susecloud.net",
      "region": "us-west3",
      "type": "smt"
    },
    {
      "ip": "34.106.44.78",
      "name": "smt-gce.susecloud.net",
      "region": "us-west3",
      "type": "smt"
    },
    {
      "ip": "34.106.145.162",
      "name": "smt-gce.susecloud.net",
      "region": "us-west3",
      "type": "smt"
    },
    {
      "ip": "34.125.184.158",
      "name": "smt-gce.susecloud.net",
      "region": "us-west4",
      "type": "smt"
    },
    {
      "ip": "34.125.236.91",
      "name": "smt-gce.susecloud.net",
      "region": "us-west4",
      "type": "smt"
    },
    {
      "ip": "34.125.105.13",
      "name": "smt-gce.susecloud.net",
      "region": "us-west4",
      "type": "smt"
    }
  ]
"""
# PINT END

# ----------------------------------------------------------------------------
def check_baseproduct():
    """If baseproduct symbolic link is wrong, there can be update issues
    Check if baseproduct link is correct for installed OS and fix if not"""
    sap_baseproduct = "/etc/products.d/SLES_SAP.prod"
    sles_baseproduct = "/etc/products.d/SLES.prod"
    baseproduct_exists = True
    
    logging.info("Checking baseproduct.")

    if not os.path.exists(sap_baseproduct) and not os.path.exists(sles_baseproduct):
        logging.error("No SLES_SAP or SLES baseproduct exists. Cannot continue.")
        sys.exit()

    if not os.path.exists(BASEPRODUCT_FILE):
        baseproduct_exists = False

    # baseproduct matches SLES_SAP.prod
    if os.path.exists(sap_baseproduct):
        if baseproduct_exists:
            if (os.path.basename(os.readlink(BASEPRODUCT_FILE)) == \
                os.path.basename(sap_baseproduct)):
                logging.info("SLES_SAP baseproduct OK.")
                return 0
            else:
                fix_baseproduct(sap_baseproduct)
    else:
        if baseproduct_exists:
            if (os.path.basename(os.readlink(BASEPRODUCT_FILE)) == \
                os.path.basename(sles_baseproduct)):
                logging.info("SLES baseproduct OK.")
                return 0
            else:
                fix_baseproduct(sles_baseproduct)

# ----------------------------------------------------------------------------
def check_current_rmt(framework, rmt_servers):
    global problem_count
    """Check if current smt server in /etc/hosts is region correct"""
    domain_name = ("smt-" + framework + ".susecloud.net")
    logging.info("Checking RMT server entry is for correct region.")
    
    try:    
      if socket.gethostbyname(domain_name) in rmt_servers:
        logging.info("RMT server entry OK.")
    except: 
      logging.error("Cannot get IP of RMT server entry.")
    else:
      if not socket.gethostbyname(domain_name) in rmt_servers:
        logging.warning("PROBLEM: RMT server entry is for wrong region.")
        problem_count += 1
        check_hosts(framework, True)

# ----------------------------------------------------------------------------
def check_hosts(framework, delete_record):
    """If there are multiple SMT entries in /etc/hosts, there can be update
    issues. Check /etc/hosts file for problems and fix if there are."""
    etc_hosts = "/etc/hosts"
    domain_name = ("smt-" + framework + ".susecloud.net")

    new_hosts_content = []
    if delete_record == False:
        logging.info("Checking {0} for multiple records.".format(etc_hosts))

    try:
        with open(etc_hosts, 'r') as hosts_file:
            content = hosts_file.readlines()
        # Initialize variable to count number of smt records in hosts file
        entry_count = 0
    except FileNotFoundError:
        logging.error("File {0} doesn't exist.".format(etc_hosts))
        logging.error("Cannot continue {0} check.".format(etc_hosts))
        return
    else:
        for entry in content:
            if domain_name in entry:
                entry_count += 1
                continue
            if '# Added by SMT' in entry:
                continue
            new_hosts_content.append(entry)

        if entry_count == 0 and delete_record == False:
            logging.warning("No rmt records exist.")
        elif entry_count == 1 and delete_record == False:
            logging.info("%s OK." % etc_hosts)
        elif entry_count >= 2 or delete_record == True:
            logging.warning("PROBLEM: Multiple or incorrect rmt records exist, deleting.")
            with open(etc_hosts, 'w') as hosts_file:
                for entry in new_hosts_content:
                    hosts_file.write(entry)

# ----------------------------------------------------------------------------
def check_http(rmt_servers):
    """If httpsOnly isn't true, check for http access to RMT servers"""
    global problem_count
    logging.info("Checking http port access to RMT servers.")
    content = read_regionserverclnt()
    for entry in content:
        if 'httpsOnly = true' in entry:
            logging.info("http check unnecessary.")
            return
    for server in rmt_servers:
        try:
            requests.get('http://' + server + '/rmt.crt',timeout=5)
        except:
                logging.warning("PROBLEM: http access issue. Open port 80 to RMT servers:")
                logging.warning(rmt_servers)
                problem_count += 1
                return
    logging.info("http access OK.")
    return

# ----------------------------------------------------------------------------
def check_https_cert(rmt_hostname):
    """Check https cert"""
    global problem_count

    logging.info("Checking https access using RMT certs.")
    certfiles = [filename for filename in os.listdir('/usr/share/pki/trust/anchors') if filename.startswith("registration_server")]  
    try:
        requests.get('https://' + rmt_hostname + '/api/health/status', verify='/usr/share/pki/trust/anchors/'+certfiles[0],timeout=5)
    except requests.exceptions.SSLError:
        logging.warning("PROBLEM: MITM proxy misconfiguration. Proxy cannot intercept RMT certs. Exempt {0}.".format(rmt_hostname))
        problem_count += 1
        return
    except Exception as ex:      
        template = "An exception of type {0} occurred."  
        message = template.format(type(ex).__name__, ex.args)
        logging.info(message + " Disregarding.")
        return
    logging.info("RMT certs OK.")
    return

# ----------------------------------------------------------------------------
def check_https_port(rmt_servers):
    """Check https is open to RMT servers"""
    global problem_count
    logging.info("Checking https port access to RMT servers.")
    for server in rmt_servers:
        try:
            requests.get('https://' + server + '/api/health/status', verify=False, timeout=5)
        except:
            logging.warning("PROBLEM: https access issue. Open port 443 to RMT servers:")
            logging.warning(rmt_servers)
            problem_count += 1
            return
    logging.info("https access OK.")
    return

# ----------------------------------------------------------------------------
def check_metadata(framework, args):
    """Metadata access is required. Check metadata is accessible."""
    """Return instance region if successful"""
    metadata_base_url = "http://169.254.169.254"
    logging.info("Checking metadata access.")
    if framework == "azure":
        instance_api_version = "2019-03-11"
        instance_endpoint = metadata_base_url + "/metadata/instance/compute/location?api-version=" + instance_api_version + "&format=text"
        headers = {'Metadata': 'True'}
        try:
            r = requests.get(instance_endpoint, headers=headers, timeout=5)
        except:
            logging.warning("PROBLEM: Metadata is not accessible. Fix access to metadata at 169.254.169.254.")
            if args.r:
                return None
            collect_debug_data(framework, args, True)
            sys.exit()
        else:
            location = r.text

    elif framework == "gce":
        instance_endpoint = metadata_base_url + "/computeMetadata/v1/instance/zone"
        headers = {'Metadata-Flavor': 'Google'}
        try:
            r = requests.get(instance_endpoint, headers=headers, timeout=5)
        except:
            logging.warning("PROBLEM: Metadata is not accessible. Fix access to metadata at 169.254.169.254.")
            if args.r:
                return None
            collect_debug_data(framework, args, True)
            sys.exit()     
        else:     
            location = r.text.split('/')[3]
            location = location.split('-', 2)
            location = location[0] + "-" + location[1]
        
    elif framework == "ec2":
        instance_api_version = "2008-02-01"
        instance_endpoint = metadata_base_url + "/latest/meta-data/placement/region"
        request = urllib.request.Request(
        'http://169.254.169.254/latest/api/token',
        headers={'X-aws-ec2-metadata-token-ttl-seconds': '21600'},
        method='PUT')
        try:
            token = urllib.request.urlopen(request).read().decode()
        except urllib.error.URLError:
            request_header = {}
        request_header = {'X-aws-ec2-metadata-token': token}
        try:
            r = requests.get(instance_endpoint, headers=request_header, timeout=5)
        except:
            logging.warning("PROBLEM: Metadata is not accessible. Fix access to metadata at 169.254.169.254.")
            if args.r:
                return None
            collect_debug_data(framework, args, True)
            sys.exit()     
        else:        
            location = r.text

    logging.info("Metadata OK.")
    return location

# ----------------------------------------------------------------------------
def check_pkg_versions(framework):
    """Check package version is at a certain level"""
    required_version = "9.0.10"
    global problem_count
    logging.info("Checking package versions.")

    try:
        ver = subprocess.check_output(['rpm', '-q', 'cloud-regionsrv-client', '--queryformat', '%{VERSION}']).decode("utf-8")
    except subprocess.CalledProcessError:
        ver = 0
    
    if (ver > required_version) - (ver < required_version) == -1:
        logging.warning("PROBLEM: Update infrastructure packages need to be updated.")
        logging.info("Attempting to upgrade packages.")
        ret = upgrade_packages(framework)

        if ret == 1:
            logging.warning("PROBLEM: Update infrastructure packages need to be updated manually.")
            logging.warning("Follow Situation 4 at https://www.suse.com/support/kb/doc/?id=000019633")
            logging.warning("Cannot continue. Exiting.")
            sys.exit()
    logging.info("Package versions OK.")

# ----------------------------------------------------------------------------
def check_realtime(args):
    """Check access in real-time for troubleshooting with proxy administrators""" 
    if (args.i == None):
        args.i = 10
    print_header()
    logging.info("Check interval is {0} seconds".format(args.i))
    logging.info("CTRL-C to exit")
    logging.info("")
    time.sleep(3)

    try:
        while True:
            framework = get_framework()
            region = check_metadata(framework, args)
            if region == None:
                logging.info("Cannot continue until metadata access is fixed")
            else:
                check_region_servers(region)
                rmt_servers = get_rmt_servers(framework, region)
                check_http(rmt_servers)
                check_https_port(rmt_servers)
                check_https_cert("smt-" + framework + ".susecloud.net")
            logging.info("")
            time.sleep(args.i)
    except KeyboardInterrupt:
        logging.info("Exiting real-time.")
        sys.exit()

# ----------------------------------------------------------------------------
def check_region_servers(region):
    """Check if the instance has access to one region server over https"""
    global problem_count
    to_cnt = 0
    se_cnt = 0
    re_cnt = 0
    cert_dir = "/var/lib/regionService/certs"
    logging.info("Checking regionserver access.")
    content = read_regionserverclnt()
    for entry in content:
        if "regionsrv" in entry:
            break
    entry = entry.rsplit()
    region_servers = entry[2].split(",")
    for region_server in region_servers:
        certfile = cert_dir + '/' + region_server + '.pem'
        try:
            requests.get('https://' + region_server + '/regionInfo?regionHint=' + region,verify=certfile, timeout=5)
        except requests.exceptions.Timeout:
            to_cnt += 1
        except requests.exceptions.SSLError:
            se_cnt += 1
        except requests.exceptions.RequestException:
            re_cnt += 1
    regsrv_cnt = (len(region_servers))
    if to_cnt == regsrv_cnt:
        logging.warning("PROBLEM: No access to a region server. Open port 443 to a region server:")
        logging.warning("Region Server IPs: {0}".format(region_servers))
        problem_count += 1
    if se_cnt == regsrv_cnt:
        logging.warning("PROBLEM: MITM proxy misconfiguration. Proxy cannot intercept certs in %s. Exempt at least one region server.", cert_dir)
        logging.warning("Region Server IPs: {0}".format(region_servers))
        problem_count += 1
    if re_cnt == regsrv_cnt:
        logging.warning("PROBLEM: No access to a region server.")
        logging.warning("Region Server IPs: {0}".format(region_servers))
        problem_count += 1
    if to_cnt != regsrv_cnt and se_cnt != regsrv_cnt and re_cnt != regsrv_cnt:
        logging.info("Region server access OK.")
    return

# ----------------------------------------------------------------------------
def collect_debug_data(framework, disable_tcpdump, disable_metadata_collect):
    var_location="/var/log/"
    domain_name = ("smt-" + framework + ".susecloud.net")
    suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    filename = "_".join([SCRIPT_NAME, suffix])
    tmp_dir="/tmp/" + filename
    tarball_name = os.path.join(var_location,filename + ".tar.xz")
    logging.info("Collecting debug data. Please wait 1-2 minutes maybe longer, depending on machine type.")
    try:
        os.mkdir(tmp_dir)
    except OSError:
        logging.error("Cannot make {0}. Not collecting debug data.".format(tmp_dir))
        return

    if disable_metadata_collect == False:

        try:
            if framework == "azure":
                if supported_metadata_version == True:
                    with open(os.path.join(tmp_dir, "azuremetadata.latest"), "wb") as file:
                        file.write(subprocess.check_output(['azuremetadata', '--api', 'latest']))

                with open(os.path.join(tmp_dir, "azuremetadata.default"), "wb") as file:
                    file.write(subprocess.check_output(['azuremetadata']))

            elif framework == "ec2":
                with open(os.path.join(tmp_dir, "ec2metadata.latest"), "wb") as file:
                    file.write(subprocess.check_output(['ec2metadata', '--api', 'latest']))
                with open(os.path.join(tmp_dir, "ec2metadata.default"), "wb") as file:
                    file.write(subprocess.check_output(['ec2metadata']))

            elif framework == "gce":
                with open(os.path.join(tmp_dir, "gcemetadata.default"), "wb") as file:
                    file.write(subprocess.check_output(['gcemetadata']))

            cmd = get_dataprovider()
            with open(os.path.join(tmp_dir, "metadata.dataprovider"), "wb") as file:
                file.write(subprocess.check_output(shlex.split(cmd)))
        except:
            if framework == "azure":
                logging.error("PROBLEM: Issue with azuremetadata output. Check metadata access.")
            elif framework == "ec2":
                logging.error("PROBLEM: Issue with ec2metadata output. Check metadata access.")
            elif framework == "gce":
                logging.error("PROBLEM: Issue with gcemetadata output. Check metadata access.")

    shutil.copy("/var/log/sc-repocheck", tmp_dir)

    with open(os.path.join(tmp_dir, "baseproduct"), "wb") as file:
        file.write(subprocess.check_output(['/bin/ls', '-lA', '--time-style=long-iso', '/etc/products.d/']))

    try:
        with open(os.path.join(tmp_dir, "zypper-lr-before"), "wb") as file:
            file.write(subprocess.check_output(['zypper', 'lr']))
    except subprocess.CalledProcessError:
        pass
    
    try:
        with open(os.path.join(tmp_dir, "zypper-ls-before"), "wb") as file:
            file.write(subprocess.check_output(['zypper', 'ls']))    
    except subprocess.CalledProcessError:
        pass

    shutil.copy("/etc/hosts", tmp_dir)
    orig_file = os.path.join(tmp_dir, "hosts")
    new_file = os.path.join(tmp_dir, "etc-hosts-before") 
    os.rename(orig_file, new_file )

    curl_out_filename = os.path.join(tmp_dir, "rmt-curl-https.trace")
    url = 'https://' + domain_name + '/api/health/status'
    try:
        subprocess.check_output(['curl', '-s', '--connect-timeout', '5', '--trace-ascii', curl_out_filename, '--digest', '--remote-time', '--fail', url])
    except:
        pass

    if args.t == False:
        tcpdump_file = os.path.join(tmp_dir, "registercloudguest.pcap")
        p = subprocess.Popen(['tcpdump', '-s0', '-C', '100', '-W', '1', '-w', tcpdump_file, 'tcp', 'port', '443', 'or', 'tcp', 'port', '80'], stderr=subprocess.DEVNULL)

    strace_file = os.path.join(tmp_dir, "strace.out")

    try:
        subprocess.call(['strace', '-f', '-s512', '-o', strace_file, '/usr/sbin/registercloudguest', '--force-new'])
    except:
        logging.error("PROBLEM: Cannot run registercloudguest. There are unknown issues. Please provide debug data.")

    if args.t == False:
        p.send_signal(subprocess.signal.SIGTERM)
    
    shutil.copy("/var/log/cloudregister", tmp_dir)
    
    with open(os.path.join(tmp_dir, "zypper-lr-after"), "wb") as file:
        try:
            file.write(subprocess.check_output(['zypper', 'lr']))
        except:
            pass
    
    with open(os.path.join(tmp_dir, "zypper-ls-after"), "wb") as file:
        try:
            file.write(subprocess.check_output(['zypper', 'ls']))
        except:
            pass

    shutil.copy("/etc/hosts", tmp_dir)
    orig_file = os.path.join(tmp_dir, "hosts")
    new_file = os.path.join(tmp_dir, "etc-hosts-after") 
    os.rename(orig_file, new_file )

    shutil.copy("/etc/regionserverclnt.cfg", tmp_dir)

    rpms = subprocess.check_output(['rpm', '-qa','*region*', '*metadata']).decode("utf-8")
    rpms = rpms.split()

    with open(os.path.join(tmp_dir, "rpms.verify"), "ab") as file:
        for package in rpms:
            p = subprocess.Popen(['rpm', '-q', package],stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE,bufsize=-1)
            p2 = subprocess.Popen(['rpm', '-Vv', package],stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE,bufsize=-1)
            output, _ = p.communicate()
            output2, _ = p2.communicate()
            file.write(output)     
            file.write(output2)
        
    p = subprocess.Popen(['tar', 'J', '-C', '/tmp/', '-cf', tarball_name, filename],subprocess.PIPE)
    p.communicate()
    logging.info("Check repositories. An attempt was made to fix.")
    logging.info("Debug data location: {0}".format(tarball_name))
    try:
        shutil.rmtree(tmp_dir)
    except:
        logging.error("Cannot delete {0}. Delete manually.".format(tmp_dir))

    print_footer()

# ----------------------------------------------------------------------------
def fix_baseproduct(baseproduct):
    """Fix baseproduct symbolic link"""
    tmp_baseproduct_file = "/etc/products.d/baseproduct.sc-repocheck"
    logging.info("Baseproduct issue found. FIXING.")
    try:
        os.symlink(baseproduct, tmp_baseproduct_file)
        os.rename(tmp_baseproduct_file, BASEPRODUCT_FILE)
    except OSError:
        logging.error("Could not fix baseproduct link.")
        return
    
    if check_baseproduct() == 0:
        logging.info("Baseproduct issue confirmed FIXED.")

# ----------------------------------------------------------------------------
def get_dataprovider():
    """Return the instance data provider"""
    content = read_regionserverclnt()
    for entry in content:
        if "dataProvider" in entry:
            data_provider = entry
            break
    data_provider = data_provider.split("= ",1)[1]
    return data_provider

# ----------------------------------------------------------------------------
def get_framework():
    """Check which public cloud framework script is running in"""
    cmd = ['dmidecode']
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        logging.error("dmidecode error: %s" % e)
        sys.exit()
    except FileNotFoundError:
        logging.error("dmidecode binary not found.")
        sys.exit()
    else:
        dmidecode_output = str(proc.stdout.read().lower())
    if "microsoft" in dmidecode_output:
        framework =  "azure"
    elif "amazon" in dmidecode_output:
        framework = "ec2"
    elif "google" in dmidecode_output:
        framework = "gce"
    else:
        logging.error("No supported framework. Quitting.")
        sys.exit()
    return framework

# ----------------------------------------------------------------------------
def get_os_version():
    """Return OS version"""
    try:
        p = subprocess.check_output("""sh -c '. /etc/os-release; echo "$VERSION"'""", shell=True, universal_newlines=True).strip()
        return p.split("-")[0]
    except subprocess.CalledProcessError as e:
        print('Cannot get OS version. Make sure /etc/os-release has VERSION="<INSTALLED_OS>" line:',e)

# ----------------------------------------------------------------------------
def get_rmt_servers(framework, region):
    """Get RMT servers for region in particular framework."""
    rmt_servers = []
    rmt_dict = (json.loads(pint_data[framework]))
    for server in rmt_dict:
        if server['region'] == region:
            rmt_servers.append(server['ip'])
    return rmt_servers

# ----------------------------------------------------------------------------

def main(args):
    print_header()
    framework = get_framework()
    check_pkg_versions(framework)
    check_baseproduct()
    check_hosts(framework, False)
    region = check_metadata(framework, args)
    check_region_servers(region)
    rmt_servers = get_rmt_servers(framework, region)
    check_current_rmt(framework, rmt_servers)
    check_http(rmt_servers)
    check_https_port(rmt_servers)
    check_https_cert("smt-" + framework + ".susecloud.net")
    report()
    collect_debug_data(framework, args, False)

# ----------------------------------------------------------------------------
def mycmp(version1, version2):
    """To compare version numbers"""
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$','', v).split(".")]
    return (normalize(version1) > normalize(version2)) - (normalize(version1) < normalize(version2))

# ----------------------------------------------------------------------------
def print_footer():
    logging.info("Report bugs to https://github.com/rfparedes/susecloud-repocheck/issues")

# ----------------------------------------------------------------------------
def print_header():
    logging.info("~~ %s %s ~~" % (SCRIPT_NAME, VERSION))

# ----------------------------------------------------------------------------
def read_regionserverclnt():
    etc_regionserverclnt = "/etc/regionserverclnt.cfg"
    try:
        with open(etc_regionserverclnt, 'r') as regionserverclnt_file:
            content = regionserverclnt_file.readlines()
    except FileNotFoundError:
        logging.error("{0} File not found. Cannot continue.".format(etc_regionserverclnt))
        sys.exit(1)
    return content

# ----------------------------------------------------------------------------
def report():
    if problem_count == 0:
        logging.info("EVERYTHING OK.")
    elif problem_count == 1:
        logging.warning("There was 1 problem.")
    else:
        logging.warning("There were multiple problems.")

# ----------------------------------------------------------------------------
def start_logging():
    """Set up logging"""
    log_filename = '/var/log/sc-repocheck'
    stdout_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(filename=log_filename)
    handlers = [file_handler, stdout_handler]
    try:
        logging.basicConfig(
            level = logging.INFO,
            format = '%(asctime)s %(levelname)s: %(message)s',
            handlers = handlers
        )
    except IOError:
        print('Could not open log file "', log_filename, '" for writing.')
        sys.exit(1)

# ----------------------------------------------------------------------------
def supported_metadata_version():
    """Check azuremetadata package version as this affects using --api latest"""
    required_version = "5.1.2"
    try:
        ver = subprocess.check_output(['rpm', '-q', 'python3-azuremetadata', '--queryformat', '%{VERSION}']).decode("utf-8")
    except subprocess.CalledProcessError:
        ver = 0
    # metadata version does not meet requirements to us --api latest
    if (ver > required_version) - (ver < required_version) == -1:
        return False
    else:
        return True

# ----------------------------------------------------------------------------
def upgrade_packages(framework):
    os_vers = "SLE" + get_os_version()
    logging.info("Updating infrastructure packages.")
    if framework == "azure":
        url = "https://52.188.224.179/late_instance_offline_update_azure_" + os_vers + ".tar.gz"
        file_location = os.path.join("/tmp","late_instance_offline_update_azure_" + os_vers + ".tar.gz")
    elif framework == "gce":
        url = "https://104.196.61.109/late_instance_offline_update_gce_" + os_vers + ".tar.gz"
        file_location = os.path.join("/tmp","late_instance_offline_update_gce_" + os_vers + ".tar.gz")
    elif framework == "ec2":
        arch = subprocess.check_output(['uname', '-i']).decode("utf-8")
        url = "https://52.15.49.139/late_instance_offline_update_ec2_" + arch + "_" + os_vers + ".tar.gz"
        file_location = os.path.join("/tmp", "late_instance_offline_update_ec2_" + arch + "_" + os_vers + ".tar.gz")

    try:
        subprocess.call(['wget','--no-check-certificate','-P','/tmp','--quiet', url])
        subprocess.call(['/bin/tar', '-C', '/tmp','-xf', file_location])
        subprocess.call(["zypper -q --no-refresh --no-remote --non-interactive in /tmp/x86_64/*.rpm"], shell=True)
    except:
        logging.error("Something went wrong. Cannot upgrade packages.")
        return 1
                    
    logging.info("Infrastructure packages updated OK.")
    return 0

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    start_logging()
    parser = argparse.ArgumentParser(description=SCRIPT_NAME)

    parser.add_argument('--version','-v',
    action='store_true',
    help='script version' )
    
    parser.add_argument('-t',
    action='store_false',
    help='tcpdump enable during debug collection' )

    parser.add_argument('-r',
    action='store_true',
    help='Realtime debugging' )

    parser.add_argument('-i',
    action='store',
    help='Realtime interval in secs',
    type=int )

    args = parser.parse_args()

    if args.version:
        logging.info(SCRIPT_NAME + " " + VERSION)
        sys.exit()

    if args.r:
        check_realtime(args)

    main(args)
