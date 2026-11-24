# SPDX-License-Identifier: Apache-2.0
# Native Windows registry and PnP metadata only; no device handles.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$result = [ordered]@{
    audio_status='UNAVAILABLE'; audio_outputs=$null; audio_active=$null;
    audio_default_count=$null; audio_truncated=$null;
    usb_status='UNAVAILABLE'; usb_devices=$null; usb_interfaces=$null;
    serial_nodes=$null; usbtmc_signatures=$null; em_listing_truncated=$null;
    usb_devnodes=$null; usb_descriptor_unreadable=$null
}
try {
    # MMDevices Render registry inventory, not public MMDevice API enumeration.
    # Includes inactive/stale endpoints; active state is registry metadata only.
    $key = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render'
    $items = @(Get-ChildItem -LiteralPath $key -ErrorAction Stop)
    if ($items.Count -gt 4096) { throw 'audio inventory bound' }
    $active = 0
    foreach ($item in $items) {
        $state = (Get-ItemProperty -LiteralPath $item.PSPath -Name DeviceState).DeviceState
        if ($state -eq 1) { $active++ }
    }
    $result.audio_status='OBSERVED'
    $result.audio_outputs=$items.Count
    $result.audio_active=$active
    $result.audio_truncated=$false
} catch {}
try {
    $nodes = @(Get-PnpDevice -PresentOnly -ErrorAction Stop)
    if ($nodes.Count -gt 4096) { throw 'PnP inventory bound' }
    $usb = @($nodes | Where-Object { $_.InstanceId -like 'USB\*' })
    $ports = @($nodes | Where-Object { $_.Class -eq 'Ports' })
    $signatures = 0
    $unreadable = 0
    foreach ($node in $usb) {
        try {
            $ids = @( (Get-PnpDeviceProperty -InstanceId $node.InstanceId -KeyName 'DEVPKEY_Device_CompatibleIds' -ErrorAction Stop).Data )
            if ($ids.Count -eq 0 -or $null -eq $ids[0]) { $unreadable++; continue }
            if (@($ids | Where-Object { $_ -match '^USB\\Class_FE&SubClass_03&Prot_0[01]$' }).Count -gt 0) { $signatures++ }
        } catch { $unreadable++ }
    }
    $result.usb_status = $(if ($unreadable -eq 0) {'OBSERVED'} else {'PARTIAL'})
    $result.usb_devnodes = $usb.Count
    $result.serial_nodes = $ports.Count
    $result.usbtmc_signatures = $signatures
    $result.usb_descriptor_unreadable = $unreadable
    $result.em_listing_truncated = $false
} catch {}
$result | ConvertTo-Json -Compress
