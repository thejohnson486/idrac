#!/bin/bash

##############################################################################
# Script: disable_ipmi_idrac.sh
# Purpose: Disable IPMI-over-LAN on Dell iDRAC systems via SSH
# Reference: https://www.dell.com/support/kbdoc/en-us/000222162
##############################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IDRAC_USER=""
IDRAC_PASSWORD=""
IDRAC_LIST_FILE="idrac_hosts.txt"
LOG_FILE="ipmi_disable_$(date +%Y%m%d_%H%M%S).log"
INTERACTIVE_MODE=true
MODE="" # Will be 'single' or 'multiple'

# SSH options
SSH_OPTS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10"

##############################################################################
# Functions
##############################################################################

print_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    -u USERNAME     iDRAC username (skips interactive prompt)
    -p PASSWORD     iDRAC password (skips interactive prompt)
    -s HOSTNAME     Single iDRAC host (skips mode selection)
    -f FILE         File containing list of iDRAC IPs/hostnames (default: idrac_hosts.txt)
    -h              Show this help message

Interactive Mode (no arguments):
    $0
    
Single Device Mode:
    $0 -u root -p YourPassword -s 192.168.1.100

Multiple Devices Mode:
    $0 -u root -p YourPassword -f idrac_list.txt

The hosts file should contain one iDRAC IP or hostname per line:
    192.168.1.100
    192.168.1.101
    idrac-server1.domain.com

EOF
}

print_banner() {
    echo -e "${BLUE}=========================================="
    echo -e "  iDRAC IPMI-over-LAN Disable Script"
    echo -e "==========================================${NC}"
    echo ""
}

get_credentials() {
    if [ -z "${IDRAC_USER}" ]; then
        echo -e "${YELLOW}Enter iDRAC credentials:${NC}"
        read -p "Username [root]: " IDRAC_USER
        IDRAC_USER=${IDRAC_USER:-root}
    fi
    
    if [ -z "${IDRAC_PASSWORD}" ]; then
        read -s -p "Password: " IDRAC_PASSWORD
        echo ""
    fi
    
    if [ -z "${IDRAC_PASSWORD}" ]; then
        echo -e "${RED}Error: Password cannot be empty${NC}"
        exit 1
    fi
}

select_mode() {
    if [ -n "${MODE}" ]; then
        return 0
    fi
    
    echo ""
    echo -e "${YELLOW}Select operation mode:${NC}"
    echo "  1) Single iDRAC device"
    echo "  2) Multiple iDRAC devices (from file)"
    echo ""
    read -p "Enter choice [1-2]: " mode_choice
    
    case ${mode_choice} in
        1)
            MODE="single"
            read -p "Enter iDRAC IP or hostname: " SINGLE_HOST
            if [ -z "${SINGLE_HOST}" ]; then
                echo -e "${RED}Error: Hostname cannot be empty${NC}"
                exit 1
            fi
            ;;
        2)
            MODE="multiple"
            if [ ! -f "${IDRAC_LIST_FILE}" ]; then
                echo ""
                echo -e "${RED}Error: Host list file '${IDRAC_LIST_FILE}' not found${NC}"
                read -p "Enter path to hosts file: " IDRAC_LIST_FILE
                if [ ! -f "${IDRAC_LIST_FILE}" ]; then
                    echo -e "${RED}Error: File '${IDRAC_LIST_FILE}' not found${NC}"
                    exit 1
                fi
            fi
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
}

confirm_action() {
    echo ""
    echo -e "${YELLOW}Configuration Summary:${NC}"
    echo "  Username: ${IDRAC_USER}"
    echo "  Mode: ${MODE}"
    if [ "${MODE}" = "single" ]; then
        echo "  Target: ${SINGLE_HOST}"
    else
        echo "  Hosts file: ${IDRAC_LIST_FILE}"
        local host_count=$(grep -v '^[[:space:]]*#' "${IDRAC_LIST_FILE}" | grep -v '^[[:space:]]*$' | wc -l)
        echo "  Number of hosts: ${host_count}"
    fi
    echo "  Log file: ${LOG_FILE}"
    echo ""
    read -p "Proceed with disabling IPMI-over-LAN? (yes/no): " confirm
    
    if [[ ! "${confirm}" =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${YELLOW}Operation cancelled${NC}"
        exit 0
    fi
}

log_message() {
    local message="$1"
    echo -e "${message}" | tee -a "${LOG_FILE}"
}

check_ipmi_status() {
    local host="$1"
    local user="$2"
    local pass="$3"
    
    sshpass -p "${pass}" ssh ${SSH_OPTS} "${user}@${host}" \
        "racadm get iDRAC.IPMILan.Enable" 2>/dev/null
}

disable_ipmi() {
    local host="$1"
    local user="$2"
    local pass="$3"
    
    log_message "${YELLOW}[${host}]${NC} Connecting to iDRAC..."
    
    # Check current status
    current_status=$(sshpass -p "${pass}" ssh ${SSH_OPTS} "${user}@${host}" \
        "racadm get iDRAC.IPMILan.Enable" 2>&1)
    
    if [ $? -ne 0 ]; then
        log_message "${RED}[${host}]${NC} Failed to connect or check status"
        log_message "${RED}[${host}]${NC} Error: ${current_status}"
        return 1
    fi
    
    log_message "${YELLOW}[${host}]${NC} Current IPMI status:"
    log_message "${current_status}"
    
    # Disable IPMI over LAN
    log_message "${YELLOW}[${host}]${NC} Disabling IPMI over LAN..."
    
    disable_output=$(sshpass -p "${pass}" ssh ${SSH_OPTS} "${user}@${host}" \
        "racadm set iDRAC.IPMILan.Enable 0" 2>&1)
    
    if [ $? -eq 0 ]; then
        log_message "${GREEN}[${host}]${NC} IPMI over LAN disabled successfully"
        log_message "${disable_output}"
        
        # Verify the change
        log_message "${YELLOW}[${host}]${NC} Verifying configuration..."
        verify_output=$(sshpass -p "${pass}" ssh ${SSH_OPTS} "${user}@${host}" \
            "racadm get iDRAC.IPMILan.Enable" 2>&1)
        log_message "${verify_output}"
        
        return 0
    else
        log_message "${RED}[${host}]${NC} Failed to disable IPMI over LAN"
        log_message "${RED}[${host}]${NC} Error: ${disable_output}"
        return 1
    fi
}

##############################################################################
# Main Script
##############################################################################

# Parse command line arguments
SINGLE_HOST=""
while getopts "u:p:s:f:h" opt; do
    case ${opt} in
        u) IDRAC_USER="${OPTARG}"; INTERACTIVE_MODE=false ;;
        p) IDRAC_PASSWORD="${OPTARG}"; INTERACTIVE_MODE=false ;;
        s) SINGLE_HOST="${OPTARG}"; MODE="single"; INTERACTIVE_MODE=false ;;
        f) IDRAC_LIST_FILE="${OPTARG}"; MODE="multiple"; INTERACTIVE_MODE=false ;;
        h) print_usage; exit 0 ;;
        *) print_usage; exit 1 ;;
    esac
done

# Check for sshpass
if ! command -v sshpass &> /dev/null; then
    echo -e "${RED}Error: sshpass is required but not installed${NC}"
    echo "Install with: sudo apt-get install sshpass (Ubuntu/Debian)"
    echo "            or: sudo yum install sshpass (RHEL/CentOS)"
    exit 1
fi

# Interactive mode
print_banner
get_credentials
select_mode

# Validate inputs based on mode
if [ "${MODE}" = "multiple" ] && [ ! -f "${IDRAC_LIST_FILE}" ]; then
    echo -e "${RED}Error: Host list file '${IDRAC_LIST_FILE}' not found${NC}"
    echo -e "Create a file with one iDRAC IP/hostname per line"
    exit 1
fi

# Confirm before proceeding
confirm_action

echo ""
echo -e "${GREEN}Starting IPMI disable process...${NC}"
echo ""

# Start processing
log_message "=========================================="
log_message "iDRAC IPMI-over-LAN Disable Script"
log_message "Started: $(date)"
log_message "Mode: ${MODE}"
log_message "User: ${IDRAC_USER}"
log_message "=========================================="
log_message ""

success_count=0
fail_count=0
total_hosts=0

# Process based on mode
if [ "${MODE}" = "single" ]; then
    # Single device mode
    total_hosts=1
    
    log_message ""
    log_message "=========================================="
    log_message "Processing iDRAC: ${SINGLE_HOST}"
    log_message "=========================================="
    
    if disable_ipmi "${SINGLE_HOST}" "${IDRAC_USER}" "${IDRAC_PASSWORD}"; then
        success_count=1
    else
        fail_count=1
    fi
    
    log_message ""
else
    # Multiple devices mode
    while IFS= read -r host || [ -n "$host" ]; do
        # Skip empty lines and comments
        [[ -z "$host" || "$host" =~ ^[[:space:]]*# ]] && continue
        
        total_hosts=$((total_hosts + 1))
        
        log_message ""
        log_message "=========================================="
        log_message "Processing iDRAC: ${host}"
        log_message "=========================================="
        
        if disable_ipmi "${host}" "${IDRAC_USER}" "${IDRAC_PASSWORD}"; then
            success_count=$((success_count + 1))
        else
            fail_count=$((fail_count + 1))
        fi
        
        log_message ""
        
    done < "${IDRAC_LIST_FILE}"
fi

# Summary
echo ""
log_message "=========================================="
log_message "Summary"
log_message "=========================================="
log_message "Total hosts processed: ${total_hosts}"
log_message "${GREEN}Successful: ${success_count}${NC}"
log_message "${RED}Failed: ${fail_count}${NC}"
log_message ""
log_message "Log file: ${LOG_FILE}"
log_message "Completed: $(date)"
log_message "=========================================="

if [ ${fail_count} -eq 0 ]; then
    echo -e "${GREEN}✓ All operations completed successfully!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ Some operations failed. Check log file for details.${NC}"
    exit 1
fi
