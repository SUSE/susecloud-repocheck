# susecloud-repocheck
SUSECloud Update Infrastructure Check for Azure, AWS, GCP PAYG/On-demand Instances

There are two ways to run.

1. If you have outbound https opened on the instance, from the instance, run:
bash <(curl -sL https://raw.githubusercontent.com/rfparedes/susecloud-repocheck/main/sc-repocheck.sh)

2. Download and transfer the script to the instance:
https://raw.githubusercontent.com/rfparedes/susecloud-repocheck/main/sc-repocheck.sh
Then run:
./sc-repocheck.sh

![](sc-repo.gif)
