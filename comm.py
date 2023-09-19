import os
import paramiko
from scp import SCPClient
import time
import socket

def create_ssh_client(hostname, username, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)
    return client

    
    

def copy_files(ssh_client, local_folder, remote_folder):
    try:
        scp = SCPClient(ssh_client.get_transport())
        for file_name in os.listdir(local_folder):
            if os.path.isfile(os.path.join(local_folder, file_name)):
                start_time = time.time()
                scp.put(os.path.join(local_folder, file_name), os.path.join(remote_folder, file_name))
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"Copied file {file_name} in {elapsed_time:.2f} seconds")
        scp.close()
    except Exception as e:
        print(f"An error occurred: {e}")
        ssh_client.close()

raspberry_pi_host = '10.50.60.172'
username = 'pi'
password = '1234'
#local_folder = 'D:\\Mhacks\\wifi_comm\\patch'

local_folder = 'C:\\Users\\manikantasaiguduru\\Desktop\\MHacks2023\\DemoFiles\\DeployFiles'
remote_folder = '/home/pi/Documents/'

ssh_client = create_ssh_client(raspberry_pi_host, username, password)
if ssh_client:
    copy_files(ssh_client, local_folder, remote_folder)
    ssh_client.close()
