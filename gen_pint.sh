#!/bin/bash

echo > pint.data
echo 'pint_data["azure"] = \' >> pint.data
echo '"""'                     >> pint.data
echo '['                       >> pint.data
pint microsoft servers --smt --json | tail -n +3 | head -n -1 >> pint.data
echo '"""'                     >> pint.data

echo 'pint_data["ec2"] = \'    >> pint.data 
echo '"""'                     >> pint.data
echo '['                       >> pint.data
pint amazon servers --smt --json | tail -n +3 | head -n -1 >> pint.data
echo '"""'                     >> pint.data

echo 'pint_data["gce"] = \'    >> pint.data
echo '"""'                     >> pint.data
echo '['                       >> pint.data
pint google servers --smt --json | tail -n +3 | head -n -1 >> pint.data
echo '"""'                     >> pint.data
