param (
    [string]$ResourceGroupName = "test-vm-vivek"
)

# Authenticate to Azure (if needed)
# Uncomment if not using Azure DevOps task for authentication
# Connect-AzAccount

# Function to stop VMs in a specific resource group
function Stop-VMsInResourceGroup {
    param (
        [string]$ResourceGroupName
    )

    $vms = Get-AzVM -ResourceGroupName $ResourceGroupName
    foreach ($vm in $vms) {
        Stop-AzVM -ResourceGroupName $vm.ResourceGroupName -Name $vm.Name -Force
        Write-Output "Stopped VM: $($vm.Name) in Resource Group: $($vm.ResourceGroupName)"
    }
}

# Function to stop all VMs in all resource groups
function Stop-AllVMs {
    $vms = Get-AzVM
    foreach ($vm in $vms) {
        Stop-AzVM -ResourceGroupName $vm.ResourceGroupName -Name $vm.Name -Force
        Write-Output "Stopped VM: $($vm.Name) in Resource Group: $($vm.ResourceGroupName)"
    }
}

# Check if a specific resource group name is provided
if ([string]::IsNullOrEmpty($ResourceGroupName)) {
    Write-Output "Stopping all VMs in all resource groups..."
    Stop-AllVMs
} else {
    Write-Output "Stopping all VMs in resource group: $ResourceGroupName"
    Stop-VMsInResourceGroup -ResourceGroupName $ResourceGroupName
}
