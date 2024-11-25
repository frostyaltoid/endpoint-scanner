# endpoint-scanner
Logs system information into CSV file while looking for previous entry discrepancies.
# Output
The program outputs a CSV file with:
- MAC Address (primary id)
- Computer Name
- Timezone
- IP Address
- Processor Model
- OS
- WAN Speed (Download)
- Ports (Top TCP Ports)
# Required libraries:
- speedtest-cli
- psutil

pip install speedtest-cli psutil
