import csv
import os
import platform
import datetime
import uuid
import socket
import speedtest  # pip install speedtest-cli
import psutil  # pip install psutil


# Get the system's MAC Address.
def get_mac_address():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(40, -8, -8)])
    return mac


# Get the system's IP Address.
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    return local_ip


# Get the system's timezone.
def get_system_timezone():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().tzname()


# Get the system's WAN Speed.
def get_wan_speed():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed_mbps = st.download() / 10**6  # Convert to Mbps
        return round(download_speed_mbps, 2)
    except Exception as e:
        print(f"Error fetching WAN speed: {e}")
        return None


# Get a list of active ports.
def get_active_ports():
    top_ports = {21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080}
    active_top_ports = set()

    for conn in psutil.net_connections(kind='tcp'):
        if conn.laddr and conn.laddr.port in top_ports:
            active_top_ports.add(conn.laddr.port)

    # Format the output as a sorted, semicolon-separated string for CSV compatibility
    return "; ".join(map(str, sorted(active_top_ports)))


# Consolidate all system information.
def get_system_info():
    system_info = {
        'MAC Address': get_mac_address(),
        'Computer Name': platform.node(),
        'System Timezone': get_system_timezone(),
        'IP Address': get_local_ip(),
        'Processor Model': platform.processor(),
        'Operating System': f"{platform.system()} {platform.release()}",
        'WAN Speed': get_wan_speed(),
        'Active Ports': get_active_ports()
    }
    return system_info


# Write data to a CSV file.
def write_to_csv(file_path, data):
    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        if csvfile.tell() == 0:  # Write header if the file is empty
            writer.writeheader()
        writer.writerow(data)


# Check for data discrepancies and update the CSV file.
def check_data_discrepancy(file_path, data):
    if os.path.exists(file_path):
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            mac_address_exists = False

            for row in rows:
                if row['MAC Address'] == data['MAC Address']:
                    mac_address_exists = True
                    discrepancies = []

                    # Check for discrepancies
                    for key in row.keys():
                        if key in data and row[key] != str(data[key]):
                            if key == 'WAN Speed' and data[key] is not None:
                                prev_speed = float(row[key])
                                curr_speed = data[key]
                                if abs(curr_speed - prev_speed) > 10:  # Allow 10 Mbps buffer
                                    discrepancies.append(f"{key}: previous '{row[key]}', current '{data[key]}'")
                            else:
                                discrepancies.append(f"{key}: previous '{row[key]}', current '{data[key]}'")

                    if discrepancies:
                        print(f"Data discrepancies found for this system:")
                        for discrepancy in discrepancies:
                            print(f"- {discrepancy}")

                    row.update(data)  # Update row with new data
                    break

            if not mac_address_exists:
                rows.append(data)

        # Rewrite the CSV file with updated data
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    else:
        # File does not exist; create and write data
        with open(file_path, 'w', newline='') as csvfile:
            fieldnames = ['MAC Address', 'Computer Name', 'System Timezone',
                          'IP Address', 'Processor Model', 'Operating System',
                          'WAN Speed', 'Active Ports']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data)


# Main script to collect and process system information.
if __name__ == "__main__":
    # Save the CSV file in the same directory as the script
    script_directory = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(script_directory, "endpoint-scanner-output.csv")

    system_information = get_system_info()

    # Convert Active Ports list to string for CSV compatibility
    system_information['Active Ports'] = str(system_information['Active Ports'])

    check_data_discrepancy(csv_file_path, system_information)
    print("System information has been collected and stored in", csv_file_path)
