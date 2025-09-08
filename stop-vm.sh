param (
    [string]$ResourceGroupName = "test-vm-vivek"
)

# Authenticate to Azure (if needed)
# Uncomment if not using Azure DevOps task for authentication
# Connect-AzAccount

# Function to check if a resource group has a lock
function Check-ResourceGroupLock {
    param (
        [string]$ResourceGroupName
    )

    $locks = Get-AzResourceLock -ResourceGroupName $ResourceGroupName -ErrorAction SilentlyContinue
    if ($locks) {
        Write-Output "Resource Group $ResourceGroupName has the following lock(s):"
        foreach ($lock in $locks) {
            Write-Output "Lock Name: $($lock.LockName), Level: $($lock.Level), Notes: $($lock.Notes)"
        }
        return $true
    }
    return $false
}

# Function to remove VMs in a specific resource group
function Remove-VMsInResourceGroup {
    param (
        [string]$ResourceGroupName
    )

    # Check if the resource group has a lock
    if (Check-ResourceGroupLock -ResourceGroupName $ResourceGroupName) {
        Write-Output "Cannot remove VMs from locked resource group: $ResourceGroupName"
        return
    }

    $vms = Get-AzVM -ResourceGroupName $ResourceGroupName
    foreach ($vm in $vms) {
        Remove-AzVM -ResourceGroupName $vm.ResourceGroupName -Name $vm.Name -Force
        Write-Output "Removed VM: $($vm.Name) in Resource Group: $($vm.ResourceGroupName)"
    }
}

# Function to remove all VMs in all resource groups
function Remove-AllVMs {
    $vms = Get-AzVM
    foreach ($vm in $vms) {
        # Check if the resource group has a lock
        if (Check-ResourceGroupLock -ResourceGroupName $vm.ResourceGroupName) {
            Write-Output "Cannot remove VMs from locked resource group: $($vm.ResourceGroupName)"
            continue
        }

        Remove-AzVM -ResourceGroupName $vm.ResourceGroupName -Name $vm.Name -Force
        Write-Output "Removed VM: $($vm.Name) in Resource Group: $($vm.ResourceGroupName)"
    }
}

# Check if a specific resource group name is provided
if ([string]::IsNullOrEmpty($ResourceGroupName)) {
    Write-Output "Removing all VMs in all resource groups..."
    Remove-AllVMs
} else {
    Write-Output "Removing all VMs in resource group: $ResourceGroupName"
    Remove-VMsInResourceGroup -ResourceGroupName $ResourceGroupName
}
