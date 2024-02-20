# susecloud-repocheck
SUSECloud Update Infrastructure Check for Azure, AWS, GCP PAYG/On-demand Instances

## To autofix, report, and collect debugdata


- If you have outbound https opened on the instance, from the instance, run:  
python3 <(curl -sL https://raw.githubusercontent.com/SUSE/susecloud-repocheck/main/sc-repocheck.py)

- Or download and transfer the script to the instance:  
https://raw.githubusercontent.com/SUSE/susecloud-repocheck/main/sc-repocheck.py<br>
Then run:  
python3 sc-repocheck.py

## To report realtime status while troubleshooting (e.g. while proxy administration is dynamically fixing configuration)

This option allows user to see repocheck report in realtime over a specific interval (default:10 seconds).  This will run in a loop until user cancels so this would ideally be used while security rules are modified or appliances configured in realtime.

Download and transfer the script to the instance:  
https://raw.githubusercontent.com/SUSE/susecloud-repocheck/main/sc-repocheck.py

Then run:  
python3 sc-repocheck.py -r -i \<INTERVAL><br>
e.g. to check every 30 seconds: python3 sc-repocheck.py -r -i 30 
  
 


