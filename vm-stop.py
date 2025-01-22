import os
import sys
import subprocess

def run_command(command):
    process = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return process.stdout

def stop_vms_in_resource_group(resource_group_name):
    command = f"az vm list --resource-group {resource_group_name} --query '[].name' -o tsv"
    vms = run_command(command).splitlines()
    for vm in vms:
        command = f"az vm stop --resource-group {resource_group_name} --name {vm} --no-wait"
        run_command(command)
        print(f"Stopped VM: {vm} in Resource Group: {resource_group_name}")

def stop_all_vms():
    command = "az vm list --query '[].{name:name,resourceGroup:resourceGroup}' -o tsv"
    vms = run_command(command).splitlines()
    for vm in vms:
        name, resource_group = vm.split()
        command = f"az vm stop --resource-group {resource_group} --name {name} --no-wait"
        run_command(command)
        print(f"Stopped VM: {name} in Resource Group: {resource_group}")

if __name__ == "__main__":
    # Specify the resource group name here as a command-line argument
    # For example: python stop_vms.py myResourceGroup
    resource_group_name = sys.argv[1] if len(sys.argv) > 1 else ""

    # Authenticate to Azure using az login
    # You can remove the following line if you've already authenticated
    #run_command("az login")

    if not resource_group_name:
        print("Stopping all VMs in all resource groups...")
        stop_all_vms()
    else:
        print(f"Stopping all VMs in resource group: {resource_group_name}")
        stop_vms_in_resource_group(resource_group_name)
