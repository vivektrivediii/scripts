param (
    [string]$ResourceGroupName = ""
)

# Authenticate to Azure (if needed)
# Uncomment if not using Azure DevOps task for authentication
# Connect-AzAccount

# Function to check if a resource group is locked
function Is-ResourceGroupLocked {
    param (
        [string]$ResourceGroupName
    )

    $locks = Get-AzResourceLock -ResourceGroupName $ResourceGroupName -ErrorAction SilentlyContinue
    return $locks.Count -gt 0
}

# Function to remove VMs in a specific resource group
function Remove-VMsInResourceGroup {
    param (
        [string]$ResourceGroupName
    )

    if (Is-ResourceGroupLocked -ResourceGroupName $ResourceGroupName) {
        Write-Output "Resource group $ResourceGroupName is locked and will be skipped."
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
    $resourceGroups = Get-AzResourceGroup
    foreach ($rg in $resourceGroups) {
        if (Is-ResourceGroupLocked -ResourceGroupName $rg.ResourceGroupName) {
            Write-Output "Resource group $($rg.ResourceGroupName) is locked and will be skipped."
            continue
        }

        $vms = Get-AzVM -ResourceGroupName $rg.ResourceGroupName
        foreach ($vm in $vms) {
            Remove-AzVM -ResourceGroupName $vm.ResourceGroupName -Name $vm.Name -Force
            Write-Output "Removed VM: $($vm.Name) in Resource Group: $($vm.ResourceGroupName)"
        }
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