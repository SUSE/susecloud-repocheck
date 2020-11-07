#!/usr/bin/env bash
#
# Perform instance check and attempt fixes for registration to SUSE Update Infrastructure.
#
VERSION="1.0.0"
SCRIPTNAME="sc-repocheck"
# Clean the environment
PATH="/sbin:/usr/sbin:/usr/local/sbin:/usr/local/bin:/bin:/usr/bin"
test -n "${TERM}" || TERM="raw"
LANG="POSIX"
export PATH TERM LANG

# baseproduct symbolic link should reference if SLES for SAP
readonly SAP_BASEPRODUCT="/etc/products.d/SLES_SAP.prod"
# baseproduct symbolic link should reference if SLES
readonly SLES_BASEPRODUCT="/etc/products.d/SLES.prod"
# Keep track of the number of problems. If > 0, run registercloudguest at end 
COUNT=0


#######################################
# Header display to user
#######################################
function header() {
  cecho -c 'bold' "## SUSECLOUD-REPOCHECK ##"
  cecho -c 'bold' "`date`"
}

#######################################
# If there are multiple SMT entries in /etc/hosts, there can be update issues
# Check /etc/hosts files for problems and fix if there are
# Globals:
#   ETC_HOSTS
#	  PATTERN1
#   PATTERN2
# Arguments:
#   None
#######################################
function check_hosts() {
  ETC_HOSTS="/etc/hosts"
  PATTERN1="smt-${FRAMEWORK}.susecloud.net"
  PATTERN2="Added by SMT registration do not remove"
  cecho -c 'bold' "-Checking /etc/hosts for multiple records"
  NUM_HOST_ENTRIES="$(grep -c $PATTERN1 $ETC_HOSTS)"
  if [[ "${NUM_HOST_ENTRIES}" -ge 2 ]]; then
    COUNT="$((COUNT+1))"
	cecho -c 'red' "PROBLEM: Multiple SMT records exist, deleting"
    delete_hosts
  elif [[ "${NUM_HOST_ENTRIES}" -eq 0 ]]; then
    COUNT="$((COUNT+1))"
    cecho -c 'red' "PROBLEM: No SMT records exist. Running registercloudguest before continuing"
  else
	cecho -c 'green' "/etc/hosts OK"
	# Now check that the hosts records matches correct region
	check_current_smt
  fi
}

#######################################
# Delete /etc/hosts entry
# Globals:
#   None
# Arguments:
#   None
#######################################
function delete_hosts() {
  sed --in-place=.sc-repocheck "/$PATTERN1/d" $ETC_HOSTS
  sed -i "/$PATTERN2/d" $ETC_HOSTS
}

#######################################
# Get the cloud service provider
# Globals:
#   FRAMEWORK
# Arguments:
#   None
#######################################
function framework() {
#Check which framework script is checking
  if dmidecode | grep -qi Amazon; then
	FRAMEWORK="ec2"
  elif dmidecode | grep -qi Google; then
	FRAMEWORK="gce"
  elif dmidecode | grep -qi Microsoft; then
	FRAMEWORK="azure"
  else
    cecho -c 'red' "No supported framework. Exiting"
	safe_exit
  fi
}

#######################################
# Is this SLES-SAP or SLES?
# Globals:
#   OS
# Arguments:
#   None
#######################################
function os() {
  if test -f "${SAP_BASEPRODUCT}"; then
	OS="SAP"
  elif test -f "${SLES_BASEPRODUCT}"; then
    OS="SLES"
  else 
    cecho -c 'red' "No supported OS. Exiting"
	safe_exit
  fi	
}

#######################################
# If baseproduct symbolic link is wrong, there can be update issues
# Check if baseproduct link is correct for installed OS and fix if not
# Globals:
#   None
# Arguments:
#   None
#######################################
function check_baseproduct() {
  cecho -c 'bold' "-Checking baseproduct symbolic link"
  local baseproduct_file="/etc/products.d/baseproduct"
  local baselink="$(readlink -f ${baseproduct_file})"
  if [[ "${OS}" = "SAP" ]]; then
    if [[ "${baselink}" = "${SAP_BASEPRODUCT}" ]]; then
	  cecho -c 'green' "baseproduct OK"
    else
	  COUNT=$((COUNT+1))
	  cecho -c 'yellow' "Baseproduct problem found. Fixing"
	  ln -sf "${SAP_BASEPRODUCT}" "${baseproduct_file}"
    fi
  elif [[ "${OS}" = "SLES" ]]; then
	if [[ "${baselink}" = "${SLES_BASEPRODUCT}" ]]; then
			cecho -c 'green' "baseproduct OK"
	else
	COUNT=$((COUNT+1))
			cecho -c 'yello' "Baseproduct problem found. Fixing"
			ln -sf "${SLES_BASEPRODUCT}" "${baseproduct_file}"
	fi
  fi
}

#######################################
# If instance isn't yet set for https_only, check if port 80 is open.  If 
# not opened, report and exit
# Globals:
#   None
# Arguments:
#   None
#######################################
function check_http() {
  cecho -c 'bold' "-Checking http access"
  if (cat /etc/regionserverclnt.cfg | grep -q "httpsOnly = true"); then
	cecho -c 'green' "http check unnecessary. httpsOnly=true. OK"
  else
	for i in "${smt_servers[@]}"; do
	  http_return_code=$(curl -m 5 -s -o /dev/null -w "%{http_code}"  http://$i/rmt.crt)
	  if [ $http_return_code -ne "200" ]; then
        cecho -c 'red' "PROBLEM: http access issue. Open port 80 to SMT servers:"
        cecho -c 'red' "${smt_servers[*]}"
	    safe_exit
	  else 
	    cecho -c 'green' "http access OK"
		break
	  fi
	done	
fi
}

#######################################
# Check if smt servers are accessible over https
# Globals:
#   None
# Arguments:
#   None
#######################################
function check_https() {
  cecho -c 'bold' "-Checking https access"
  for i in "${smt_servers[@]}"; do
    local https_return_code=$(curl -k -m 5 -s -o /dev/null -w "%{http_code}" https://$i/api/health/status)
	if [ $https_return_code -ne "200" ]; then
	  cecho -c 'red' "PROBLEM: https access issue. Open port 443 to SMT servers:"
	  cecho -c 'red' "${smt_servers[*]}"
	  safe_exit
	else
      cecho -c 'green' "https access OK"
	  break
	fi
  done
}

#######################################
# functions to verify if package versions are less than equal
# Globals:
#   None
# Arguments:
#   None
#######################################
function verlte() {
  [  "${1}" = "`echo -e "${1}\n${2}" | sort -V | head -n1`" ]
}

#######################################
# functions to verify if package versions are less than
# Globals:
#   None
# Arguments:
#   None
#######################################
function verlt() {
  [ "${1}" = "${2}" ] && return 1 || verlte "${1}" "${2}"
}

#######################################
# Check that package versions are at minimum recommended
# Globals:
#   None
# Arguments:
#   None
#######################################
function check_regionclient_version() {
  cecho -c 'bold' "-Checking cloud-regionsrv-client version"
  local required_version="9.0.10"
  local installed_version="$(rpm -q cloud-regionsrv-client --queryformat "%{VERSION}")"
  if verlt $installed_version $required_version; then
	cecho -c 'red' "PROBLEM: Update infrastructure packages need to be updated manually"
	cecho -c 'red' "Follow Situation 4 at https://www.suse.com/support/kb/doc/?id=000019633"
	safe_exit
  else 
	cecho -c 'green' "cloud-regionsrv-client OK"
  fi
}

#######################################
# Metadata access is required. Check metadata is accessible
# Globals:
#   None
# Arguments:
#   None
#######################################
function check_metadata() {
  cecho -c 'bold' "-Checking metadata access"
  if [[ "${FRAMEWORK}" == "azure" ]]; then
    local company="microsoft"
    local check_region="$(timeout 5 azuremetadata --location 2>/dev/null | awk {'print $2'})"
  elif [[ "${FRAMEWORK}" == "ec2" ]]; then
    local company="amazon"
    local check_region="$(timeout 5 ec2metadata --availability-zone 2>/dev/null | rev | cut -c 2- | rev)"
  elif [[ "${FRAMEWORK}" == "gce" ]]; then
    local company="google"
    local check_region="$(timeout 5 gcemetadata --query instance --zone 2>/dev/null | cut -d/ -f4 | rev | cut -c 3- | rev)"
  fi

  if [[ -z "${check_region}" ]]; then
	  cecho -c 'red' "PROBLEM: Metadata is not accessible. Fix access to metadata at 169.254.169.254"
	  collect_debug_data
	  safe_exit
  else
    cecho -c 'green' "Metadata OK"
	local CMD="xml_grep --pretty_print --strict 'server[@region=\"$check_region\"]' | grep server | awk {'print \$2'} | cut -d '\"' -f2"
	# Get SMT servers that are in region
    local get_smt="$(echo ${!company} | eval $CMD)"
	IFS=" " read -a smt_servers <<< $get_smt
  fi
}

#######################################
# Check if current smt server in /etc/hosts is region correct
# Globals:
#   None
# Arguments:
#   None
#######################################
function check_current_smt() {
  cecho -c 'bold' "-Checking SMT server entry is correct in /etc/hosts"
  # Get current /etc/hosts
  local smt_ip="$(getent hosts smt-azure.susecloud.net | awk {'print $1'})"

  if [[ "${smt_servers[@]}" =~ "${smt_ip}" ]]; then
    cecho -c 'green' "SMT server entry OK"
  fi

  if [[ ! "${smt_servers[@]}" =~ "${smt_ip}" ]]; then
    cecho -c 'red' "PROBLEM: SMT server entry is for wrong region"
  fi
}  

#######################################
# Check if the instance has access to at least 1 region server over https
# Globals:
#   None
# Arguments:
#   None
#######################################
function check_region_servers() {
  local good_count=0
  local get_region_servers="$(cat /etc/regionserverclnt.cfg | grep regionsrv | awk {'print $3'})"
  IFS=', ' read -r -a region_servers <<< "$get_region_servers"
  cecho -c 'bold' "-Checking regionserver access"
  for i in "${region_servers[@]}"; do
    local https_return_code=$(curl -k -m 5 -s -o /dev/null -w "%{http_code}" https://$i/regionInfo)
	if [ $https_return_code -eq "200" ]; then
	  good_count=$((good_count+1))
	fi
  done

  if [ $good_count -eq 0 ]; then
	cecho -c 'red' "PROBLEM: No access to a region server. Open port 443 to a region server:"
	cecho -c 'red' "${region_servers[*]}"
	safe_exit
  else
    cecho -c 'green' "region server access OK"
  fi
}

#######################################
# Force the client to register to SMT again
# Globals:
#   None
# Arguments:
#   tmp_dir 
#######################################
function registercloudguestnow() {
  strace -fttTyy -s 256 -o $1/strace.out /usr/sbin/registercloudguest --force-new 
}  
#######################################
# End of run report
# Globals:
#   None
# Arguments:
#   None
#######################################
function report() {
  if [ $COUNT -eq 0 ]; then
    cecho -c 'green' "EVERYTHING OK. Running registercloudguest"
	collect_debug_data

  else 
	cecho -c 'yellow' "There were problems fixed. Running registercloudguest"
	collect_debug_data
fi
}

#######################################
# Collection of debug data if healing fails
# Globals:
#   tmp_dir
# Arguments:
#   None
#######################################
function collect_debug_data() {
  cecho -c 'yellow' "Collecting debug data. Please wait..."
  local date=$(date +"%Y-%m-%d_%H-%M-%S")
  local var_location="/var/log/"
  tmp_dir="/tmp/${SCRIPTNAME}.$RANDOM.$$"
  (umask 077 && mkdir "${tmp_dir}") || { 
  die "Could not create temporary directory! Exiting."
  }
  local data_provider="$(cat /etc/regionserverclnt.cfg | grep dataProvider | cut -d "=" -f2)" 
  if [[ "${FRAMEWORK}" == "azure" ]]; then
    /usr/bin/azuremetadata --api latest > $tmp_dir/azuremetadata.latest 2>&1
    /usr/bin/azuremetadata > $tmp_dir/azuremetadata.default 2>&1
  elif [[ "${FRAMEWORK}" == "ec2" ]]; then
    /usr/bin/ec2metadata --api latest > $tmp_dir/ec2metadata.latest 2>&1
    /usr/bin/ec2metadata > $tmp_dir/ec2metadata.default 2>&1
  elif [[ "${FRAMEWORK}" == "gce" ]]; then
    /usr/bin/gcemetadata > $tmp_dir/gcemetadata.default 2>&1
  fi

  ($data_provider > $tmp_dir/metadata.dataprovider 2>&1)
  cp /var/log/sc-repocheck $tmp_dir
  /bin/ls -lA --time-style=long-iso /etc/products.d/ > $tmp_dir/baseproduct
  zypper lr > $tmp_dir/zypper-lr-before
  zypper ls > $tmp_dir/zypper-ls-before
  cat /etc/hosts > $tmp_dir/etc-hosts-before
  curl -s --connect-timeout 5 --trace-ascii $tmp_dir/rmt-curl-https.trace --digest --remote-time --fail https://$PATTERN1/api/health/status > /dev/null


  if [[ "$TCPDUMP_OFF" -eq 0 ]]; then
    tcpdump -s0 -C 100 -W 1 -w $tmp_dir/registercloudguest.pcap tcp port 443 or tcp port 80 2> /dev/null &
    tcpdumppid=$(echo $!)
  fi	
  
    registercloudguestnow $tmp_dir

  if [[ "$TCPDUMP_OFF" -eq 0 ]]; then
    kill -13 ${tcpdumppid}
    mv $tmp_dir/registercloudguest.pcap $tmp_dir/registercloudguest.${tcpdumppid}.pcap
  fi

  cp /var/log/cloudregister $tmp_dir
  zypper lr > $tmp_dir/zypper-lr-after
  zypper ls > $tmp_dir/zypper-ls-after
  cat /etc/hosts > $tmp_dir/etc-hosts-after
  cat /etc/regionserverclnt.cfg > $tmp_dir/regionserverclnt.cfg
  rpm -qa | grep 'region\|metadata' > $tmp_dir/rpms.list

  local filename="${var_location}${SCRIPTNAME}-${date}.tar.xz"
  # compress and move debugging data to /var/log
  tar J -C /tmp/ -cf $filename ${SCRIPTNAME}
  cecho -c 'yellow' "Debug data location: $filename"
  cecho -c 'yellow' "Check repository access now."
}

#######################################
# Any actions that should be taken if the script is prematurely
# exited. 
# Globals:
#   None
# Arguments:
#   None
#######################################
function trap_cleanup() {
  echo ""
  if [ -d "${tmp_dir}" ]; then
    rm -r "${tmp_dir}"
  fi
  die "Script exited prematurely. Exit trapped."
}

#######################################
# Exit safely
# Globals:
#   None
# Arguments:
#   None
#######################################
function safe_exit() {
  # Delete temp files, if any
  if [ -d "${tmp_dir}" ] ; then
    rm -r "${tmp_dir}"
  fi
  trap - INT TERM EXIT
  exit
}

#######################################
# The following function prints a text using custom color
# -c or --color define the color for the print. See the array colors for the available options.
# -n or --noline directs the system not to print a new line after the content.
# Last argument is the message to be printed.
#######################################
function cecho () {
 
    declare -A colors;
    colors=(\
        ['black']='\E[0;47m'\
        ['red']='\E[0;31m'\
        ['green']='\E[0;32m'\
        ['yellow']='\E[0;33m'\
        ['blue']='\E[0;34m'\
        ['magenta']='\E[0;35m'\
        ['cyan']='\E[0;36m'\
        ['white']='\E[0;37m'\
		['bold']='\E[0;1m'\

    );
 
    local defaultMSG="No message passed.";
    local defaultColor="black";
    local defaultNewLine=true;
 
    while [[ $# -gt 1 ]];
    do
    key="$1";
 
    case $key in
        -c|--color)
            color="$2";
            shift;
        ;;
        -n|--noline)
            newLine=false;
        ;;
        *)
            # unknown option
        ;;
    esac
    shift;
    done
 
    message=${1:-$defaultMSG};   # Defaults to default message.
    color=${color:-$defaultColor};   # Defaults to default color, if not specified.
    newLine=${newLine:-$defaultNewLine};
 
    echo -en "${colors[$color]}";
    echo -en "$message" | tee -a /var/log/sc-repocheck;
    echo >> /var/log/sc-repocheck;
    if [ "$newLine" = true ] ; then
        echo;
    fi
    tput sgr0; #  Reset text attributes to normal without clearing screen.
 
    return;
}
#######################################
# Print usage
# Globals:
#   None
# Arguments:
#   None
#######################################
usage() {
  echo -n "${SCRIPTNAME} [OPTION]...

SUSECloud Update Infrastructure Check

 Options:
  -h, --help        Display this help and exit
      --no-tcpdump  Don't run tcpdump during debug collection
      --version     Output version information and exit
"
}

#######################################
# die
# Globals:
#   None
# Arguments:
#   None
#######################################
die() 
{ echo "$*" 1>&2 ; exit 1; }

#######################################
# Run through all checks
# Globals:
#   None
# Arguments:
#   None
#######################################
function main_script() {
  header
  framework
  os
  check_metadata
  check_http
  check_https
  check_region_servers
  check_hosts
  check_baseproduct
  check_regionclient_version
  report
}


amazon=$(cat <<EOF
<?xml version='1.0' encoding='UTF-8'?>
<servers>
  <server type="smt" name="smt-ec2.susecloud.net" ip="13.244.54.57" region="af-south-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="13.244.40.27" region="af-south-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="13.245.60.134" region="af-south-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="18.162.90.181" region="ap-east-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="18.162.132.113" region="ap-east-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="18.162.83.253" region="ap-east-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.248.86.233" region="ap-northeast-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.248.240.93" region="ap-northeast-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.248.226.128" region="ap-northeast-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.79.38.96" region="ap-northeast-2"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.79.39.98" region="ap-northeast-2"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.79.134.51" region="ap-northeast-2"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.66.49.238" region="ap-south-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.66.45.16" region="ap-south-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.66.51.63" region="ap-south-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="122.248.246.124" region="ap-southeast-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.254.106.151" region="ap-southeast-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.251.254.125" region="ap-southeast-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.253.249.15" region="ap-southeast-2"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.253.114.150" region="ap-southeast-2"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.66.121.137" region="ap-southeast-2"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.60.53.175" region="ca-central-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.60.53.224" region="ca-central-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.60.50.162" region="ca-central-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.223.131.108" region="cn-north-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.223.140.138" region="cn-north-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.222.142.49" region="cn-north-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.83.151.90" region="cn-northwest-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.83.113.211" region="cn-northwest-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.83.247.110" region="cn-northwest-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.93.130.182" region="eu-central-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.93.131.24" region="eu-central-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.28.214.37" region="eu-central-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="15.161.33.0" region="eu-south-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="15.161.39.2" region="eu-south-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="15.161.27.146" region="eu-south-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="13.53.91.131" region="eu-north-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="13.53.91.167" region="eu-north-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="13.53.77.232" region="eu-north-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.246.90.215" region="eu-west-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.75.232.245" region="eu-west-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="176.34.126.172" region="eu-west-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.56.58.194" region="eu-west-2"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.56.58.190" region="eu-west-2"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.56.59.89" region="eu-west-2"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.47.108.87" region="eu-west-3"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.47.113.10" region="eu-west-3"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.47.92.102" region="eu-west-3"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="15.185.47.44" region="me-south-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="157.175.138.207" region="me-south-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="157.175.6.182" region="me-south-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="177.71.187.15" region="sa-east-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.232.112.38" region="sa-east-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.232.114.156" region="sa-east-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.197.240.216" region="us-east-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.225.105.144" region="us-east-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="107.22.231.220" region="us-east-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.15.49.139" region="us-east-2"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.15.84.50" region="us-east-2"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="52.15.50.30" region="us-east-2"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="50.18.104.175" region="us-west-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="50.18.105.39" region="us-west-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.215.80.72" region="us-west-1"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.244.114.254" region="us-west-2"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.245.112.93" region="us-west-2"/>
  <server type="smt" name="smt-ec2.susecloud.net" ip="54.245.101.73" region="us-west-2"/>
</servers>
EOF
)

microsoft=$(cat <<EOF
<?xml version='1.0' encoding='UTF-8'?>
<servers>
  <server type="smt" name="smt-azure.susecloud.net" ip="23.101.216.104" region="australiaeast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="23.101.210.206" region="australiaeast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="13.70.94.71" region="australiaeast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="23.101.235.14" region="australiasoutheast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="23.101.231.234" region="australiasoutheast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="13.73.107.146" region="australiasoutheast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="191.237.255.212" region="brazilsouth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="191.237.253.40" region="brazilsouth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="191.235.81.180" region="brazilsouth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="40.85.225.32" region="canadacentral"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="40.85.225.240" region="canadacentral"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.228.41.50" region="canadacentral"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="40.86.231.97" region="canadaeast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="40.86.231.128" region="canadaeast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.229.125.108" region="canadaeast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="104.211.97.78" region="centralindia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="104.211.98.58" region="centralindia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.172.187.74" region="centralindia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="13.86.112.4" region="centralus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.165.88.13" region="centralus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="13.86.104.2" region="centralus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="23.101.14.157" region="eastasia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="23.101.3.47" region="eastasia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="13.75.123.198" region="eastasia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.188.224.179" region="eastus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.188.81.163" region="eastus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.186.168.210" region="eastus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.147.176.11" region="eastus2"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="20.186.88.79" region="eastus2"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="20.186.112.116" region="eastus2"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="40.66.32.54" region="francecentral"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="40.66.41.99" region="francecentral"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="40.66.48.231" region="francecentral"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="51.116.98.203" region="germanywestcentral"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="51.116.98.214" region="germanywestcentral"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="51.116.96.37" region="germanywestcentral"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.185.185.83" region="japaneast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="40.81.208.103" region="japaneast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="40.81.200.4" region="japaneast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="104.46.239.62" region="japanwest"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="104.46.239.65" region="japanwest"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="40.74.120.164" region="japanwest"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.231.39.82" region="koreacentral"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.231.39.83" region="koreacentral"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.231.34.241" region="koreacentral"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.231.201.188" region="koreasouth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.231.201.178" region="koreasouth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.231.202.220" region="koreasouth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="23.101.164.199" region="northcentralus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="23.101.171.119" region="northcentralus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="23.96.231.74" region="northcentralus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.158.42.90" region="northeurope"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="13.79.120.39" region="northeurope"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.155.248.41" region="northeurope"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="51.120.2.195" region="norwayeast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="51.120.0.31" region="norwayeast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="51.120.2.159" region="norwayeast"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="102.133.128.124" region="southafricanorth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="102.133.128.67" region="southafricanorth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="102.133.129.51" region="southafricanorth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="23.101.186.158" region="southcentralus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="23.101.188.13" region="southcentralus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="13.65.81.103" region="southcentralus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.230.96.47" region="southeastasia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.237.80.2" region="southeastasia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.139.216.51" region="southeastasia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="104.211.227.174" region="southindia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="104.211.227.169" region="southindia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.172.51.125" region="southindia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="51.107.0.120" region="switzerlandnorth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="51.107.0.121" region="switzerlandnorth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="51.107.0.122" region="switzerlandnorth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="20.46.144.230" region="uaenorth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="20.46.144.239" region="uaenorth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="20.46.146.20" region="uaenorth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="20.39.208.99" region="uksouth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="20.39.216.18" region="uksouth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="20.39.224.10" region="uksouth"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="51.141.12.56" region="ukwest"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="51.141.12.57" region="ukwest"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="51.141.11.221" region="ukwest"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.161.26.245" region="westcentralus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.161.27.73" region="westcentralus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.161.26.42" region="westcentralus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="104.211.161.139" region="westindia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="104.211.161.138" region="westindia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="104.211.166.161" region="westindia"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.149.120.86" region="westeurope"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="51.145.209.119" region="westeurope"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.157.241.14" region="westeurope"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="23.100.46.123" region="westus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="23.101.192.253" region="westus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="40.112.248.207" region="westus"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="40.90.192.185" region="westus2"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.148.152.22" region="westus2"/>
  <server type="smt" name="smt-azure.susecloud.net" ip="52.156.104.18" region="westus2"/>
</servers>
EOF
)

google=$(cat <<EOF
<servers>
  <server type="smt" name="smt-gce.susecloud.net" ip="107.167.177.171" region="asia-east1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="107.167.180.126" region="asia-east1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="104.199.135.44" region="asia-east1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.220.221.180" region="asia-east2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.220.133.207" region="asia-east2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.241.72.175" region="asia-east2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="104.198.124.121" region="asia-northeast1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="104.198.115.243" region="asia-northeast1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.187.203.149" region="asia-northeast1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.97.17.129" region="asia-northeast2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.97.135.188" region="asia-northeast2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.97.1.22" region="asia-northeast2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.64.156.194" region="asia-northeast3"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.64.220.20" region="asia-northeast3"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.64.191.36" region="asia-northeast3"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.244.47.233" region="asia-south1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.244.53.235" region="asia-south1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.244.54.174" region="asia-south1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.185.189.204" region="asia-southeast1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.185.180.225" region="asia-southeast1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.185.180.164" region="asia-southeast1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.101.118.189" region="asia-southeast2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.101.129.134" region="asia-southeast2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.101.150.228" region="asia-southeast2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.197.189.68" region="australia-southeast1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.189.52.87" region="australia-southeast1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.201.31.111" region="australia-southeast1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.228.142.43" region="europe-north1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.228.148.188" region="europe-north1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.228.201.140" region="europe-north1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="192.158.29.172" region="europe-west1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="23.251.128.172" region="europe-west1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.187.10.100" region="europe-west1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.189.71.14" region="europe-west2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.189.66.119" region="europe-west2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.189.74.184" region="europe-west2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.198.79.254" region="europe-west3"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.198.102.220" region="europe-west3"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.198.118.99" region="europe-west3"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.204.184.183" region="europe-west4"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.204.109.102" region="europe-west4"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.204.122.117" region="europe-west4"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.65.167.82" region="europe-west6"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.65.120.183" region="europe-west6"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.65.187.174" region="europe-west6"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.203.93.203" region="northamerica-northeast1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.203.20.10" region="northamerica-northeast1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.203.24.115" region="northamerica-northeast1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.198.16.136" region="southamerica-east1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.198.30.115" region="southamerica-east1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.199.89.249" region="southamerica-east1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="108.59.80.221" region="us-central1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="108.59.85.41" region="us-central1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="108.59.80.58" region="us-central1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="104.196.61.109" region="us-east1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="104.196.26.155" region="us-east1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="104.196.220.87" region="us-east1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.186.167.77" region="us-east4"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.186.173.156" region="us-east4"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.186.187.53" region="us-east4"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="104.196.227.89" region="us-west1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="104.196.231.164" region="us-west1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="104.198.14.82" region="us-west1"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.236.105.72" region="us-west2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.235.125.59" region="us-west2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="35.235.80.144" region="us-west2"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.106.238.55" region="us-west3"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.106.44.78" region="us-west3"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.106.145.162" region="us-west3"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.125.184.158" region="us-west4"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.125.236.91" region="us-west4"/>
  <server type="smt" name="smt-gce.susecloud.net" ip="34.125.105.13" region="us-west4"/>
</servers>
EOF
)

############## End of Function definitions ###################
# Iterate over options breaking -ab into -a -b when needed and --foo=bar into
# --foo bar
optstring=h
unset options
while (($#)); do
  case $1 in
    # If option is of type -ab
    -[!-]?*)
      # Loop over each character starting with the second
      for ((i=1; i < ${#1}; i++)); do
        c=${1:i:1}

        # Add current char to options
        options+=("-$c")

        # If option takes a required argument, and it's not the last char make
        # the rest of the string its argument
        if [[ $optstring = *"$c:"* && ${1:i+1} ]]; then
          options+=("${1:i+1}")
          break
        fi
      done
      ;;

    # If option is of type --foo=bar
    --?*=*) options+=("${1%%=*}" "${1#*=}") ;;
    # add --endopts for --
    --) options+=(--endopts) ;;
    # Otherwise, nothing special
    *) options+=("$1") ;;
  esac
  shift
done
set -- "${options[@]}"
unset options

# Read the options and set stuff
while [[ $1 = -?* ]]; do
  case $1 in
    -h|--help) usage >&2; safe_exit ;;
	--no-tcpdump) declare -i TCPDUMP_OFF=1 ;;
    --version) echo "${SCRIPTNAME} ${VERSION}"; safe_exit ;;
    *) die "invalid option: '$1'." ;;
  esac
  shift
done

# Store the remaining part as arguments.
args+=("$@")

############## End of Options ###################

# Trap bad exits
trap trap_cleanup EXIT INT TERM

# Run all checks
main_script
# Safely exit script
safe_exit