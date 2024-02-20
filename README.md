# susecloud-repocheck

SUSE Public Cloud Update Infrastructure check tool for PAYG On-demand SLES based resources on AWS, Azure or GCP.

## To automatically check, fix, report and collect debug data

If the host is able to make outbound HTTPS request to the public internet, from the host, run the following command:

```bash
python3 <(curl -sL https://raw.githubusercontent.com/SUSE/susecloud-repocheck/main/sc-repocheck.py)
```

OR download the script seperately and transfer it to the host:

```
curl -sL 'https://raw.githubusercontent.com/SUSE/susecloud-repocheck/main/sc-repocheck.py' -O
```

After transferring the script to the host, run the following command:

```
python3 sc-repocheck.py
```

## Reporting of realtime status (e.g. during live troubleshooting)

This option allows user to see repocheck report in realtime over a specific interval (default:10 seconds). This will run in a loop until user cancels, which can be used while the admin of a proxy is making adjustments to the proxy configuration, modifying security related rules or making other changes to security appliance(s) within the environment.

Download the script to the instance or locally and then transfer the script to the host:

```bash
curl -sL 'https://raw.githubusercontent.com/SUSE/susecloud-repocheck/main/sc-repocheck.py' -O
```

Then run:

```bash
python3 sc-repocheck.py -r -i <interval>
```

For example, to check every 30 seconds:

```bash
python3 sc-repocheck.py -r -i 30
```
