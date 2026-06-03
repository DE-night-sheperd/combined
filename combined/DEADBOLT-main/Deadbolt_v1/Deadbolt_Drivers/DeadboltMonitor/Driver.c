/*
    Deadbolt Endpoint Shield - Kernel-Mode Monitor Driver
    Built with KMDF (Kernel-Mode Driver Framework)
*/

#include <ntddk.h>
#include <wdf.h>

#define DEADBOLT_POOL_TAG 'tbDd'
#define DEADBOLT_DEVICE_NAME L"\\Device\\DeadboltMonitor"
#define DEADBOLT_DOS_DEVICE_NAME L"\\DosDevices\\DeadboltMonitor"

typedef struct _DEVICE_CONTEXT {
    WDFDEVICE WdfDevice;
    BOOLEAN IsMonitoringActive;
} DEVICE_CONTEXT, *PDEVICE_CONTEXT;

WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(DEVICE_CONTEXT, GetDeviceContext)

DRIVER_INITIALIZE DriverEntry;
EVT_WDF_DRIVER_DEVICE_ADD DeadboltEvtDeviceAdd;
EVT_WDF_OBJECT_CONTEXT_CLEANUP DeadboltEvtDriverContextCleanup;
EVT_WDF_DEVICE_FILE_CREATE DeadboltEvtDeviceFileCreate;
EVT_WDF_DEVICE_FILE_CLOSE DeadboltEvtDeviceFileClose;
EVT_WDF_IO_QUEUE_IO_DEVICE_CONTROL DeadboltEvtIoDeviceControl;

NTSTATUS DriverEntry(_In_ PDRIVER_OBJECT DriverObject, _In_ PUNICODE_STRING RegistryPath)
{
    NTSTATUS status;
    WDF_DRIVER_CONFIG config;
    WDF_OBJECT_ATTRIBUTES attributes;

    KdPrint(("[DeadboltMonitor] DriverEntry called\n"));

    WDF_DRIVER_CONFIG_INIT(&config, DeadboltEvtDeviceAdd);
    config.EvtDriverContextCleanup = DeadboltEvtDriverContextCleanup;

    WDF_OBJECT_ATTRIBUTES_INIT(&attributes);

    status = WdfDriverCreate(DriverObject, RegistryPath, &attributes, &config, WDF_NO_HANDLE);
    if (!NT_SUCCESS(status)) {
        KdPrint(("[DeadboltMonitor] WdfDriverCreate failed: 0x%X\n", status));
        return status;
    }

    KdPrint(("[DeadboltMonitor] DriverEntry succeeded\n"));
    return status;
}

NTSTATUS DeadboltEvtDeviceAdd(_In_ WDFDRIVER Driver, _Inout_ PWDFDEVICE_INIT DeviceInit)
{
    NTSTATUS status;
    WDF_OBJECT_ATTRIBUTES deviceAttributes;
    WDFDEVICE device;
    PDEVICE_CONTEXT deviceContext;
    WDF_IO_QUEUE_CONFIG ioQueueConfig;
    WDF_FILEOBJECT_CONFIG fileObjectConfig;
    UNICODE_STRING deviceName;
    UNICODE_STRING dosDeviceName;

    UNREFERENCED_PARAMETER(Driver);
    KdPrint(("[DeadboltMonitor] DeadboltEvtDeviceAdd called\n"));

    WDF_FILEOBJECT_CONFIG_INIT(&fileObjectConfig, DeadboltEvtDeviceFileCreate, DeadboltEvtDeviceFileClose, WDF_NO_EVENT_CALLBACK);
    WdfDeviceInitSetFileObjectConfig(DeviceInit, &fileObjectConfig, WDF_NO_OBJECT_ATTRIBUTES);

    RtlInitUnicodeString(&deviceName, DEADBOLT_DEVICE_NAME);
    status = WdfDeviceInitAssignName(DeviceInit, &deviceName);
    if (!NT_SUCCESS(status)) {
        KdPrint(("[DeadboltMonitor] WdfDeviceInitAssignName failed: 0x%X\n", status));
        return status;
    }

    WDF_OBJECT_ATTRIBUTES_INIT_CONTEXT_TYPE(&deviceAttributes, DEVICE_CONTEXT);

    status = WdfDeviceCreate(&DeviceInit, &deviceAttributes, &device);
    if (!NT_SUCCESS(status)) {
        KdPrint(("[DeadboltMonitor] WdfDeviceCreate failed: 0x%X\n", status));
        return status;
    }

    deviceContext = GetDeviceContext(device);
    deviceContext->WdfDevice = device;
    deviceContext->IsMonitoringActive = FALSE;

    RtlInitUnicodeString(&dosDeviceName, DEADBOLT_DOS_DEVICE_NAME);
    status = WdfDeviceCreateSymbolicLink(device, &dosDeviceName);
    if (!NT_SUCCESS(status)) {
        KdPrint(("[DeadboltMonitor] WdfDeviceCreateSymbolicLink failed: 0x%X\n", status));
        return status;
    }

    WDF_IO_QUEUE_CONFIG_INIT_DEFAULT_QUEUE(&ioQueueConfig, WdfIoQueueDispatchParallel);
    ioQueueConfig.EvtIoDeviceControl = DeadboltEvtIoDeviceControl;

    status = WdfIoQueueCreate(device, &ioQueueConfig, WDF_NO_OBJECT_ATTRIBUTES, WDF_NO_HANDLE);
    if (!NT_SUCCESS(status)) {
        KdPrint(("[DeadboltMonitor] WdfIoQueueCreate failed: 0x%X\n", status));
        return status;
    }

    KdPrint(("[DeadboltMonitor] DeadboltEvtDeviceAdd succeeded\n"));
    return STATUS_SUCCESS;
}

VOID DeadboltEvtDriverContextCleanup(_In_ WDFOBJECT DriverObject)
{
    UNREFERENCED_PARAMETER(DriverObject);
    KdPrint(("[DeadboltMonitor] DeadboltEvtDriverContextCleanup called\n"));
}

VOID DeadboltEvtDeviceFileCreate(_In_ WDFDEVICE Device, _In_ WDFREQUEST Request, _In_ WDFFILEOBJECT FileObject)
{
    UNREFERENCED_PARAMETER(Device);
    UNREFERENCED_PARAMETER(FileObject);
    KdPrint(("[DeadboltMonitor] DeadboltEvtDeviceFileCreate called\n"));
    WdfRequestComplete(Request, STATUS_SUCCESS);
}

VOID DeadboltEvtDeviceFileClose(_In_ WDFFILEOBJECT FileObject)
{
    UNREFERENCED_PARAMETER(FileObject);
    KdPrint(("[DeadboltMonitor] DeadboltEvtDeviceFileClose called\n"));
}

VOID DeadboltEvtIoDeviceControl(_In_ WDFQUEUE Queue, _In_ WDFREQUEST Request, _In_ size_t OutputBufferLength, _In_ size_t InputBufferLength, _In_ ULONG IoControlCode)
{
    NTSTATUS status = STATUS_SUCCESS;
    PVOID buffer;
    size_t bufferLength;
    WDFDEVICE device;
    PDEVICE_CONTEXT deviceContext;

    UNREFERENCED_PARAMETER(Queue);
    UNREFERENCED_PARAMETER(OutputBufferLength);
    UNREFERENCED_PARAMETER(InputBufferLength);

    device = WdfIoQueueGetDevice(Queue);
    deviceContext = GetDeviceContext(device);

    KdPrint(("[DeadboltMonitor] DeadboltEvtIoDeviceControl called, IoControlCode: 0x%X\n", IoControlCode));

    switch (IoControlCode) {
        case 0x800:
            KdPrint(("[DeadboltMonitor] Starting monitoring...\n"));
            deviceContext->IsMonitoringActive = TRUE;
            status = STATUS_SUCCESS;
            break;

        case 0x801:
            KdPrint(("[DeadboltMonitor] Stopping monitoring...\n"));
            deviceContext->IsMonitoringActive = FALSE;
            status = STATUS_SUCCESS;
            break;

        case 0x802:
            KdPrint(("[DeadboltMonitor] Getting status...\n"));
            status = WdfRequestRetrieveOutputBuffer(Request, sizeof(BOOLEAN), &buffer, &bufferLength);
            if (NT_SUCCESS(status)) {
                *(PBOOLEAN)buffer = deviceContext->IsMonitoringActive;
                WdfRequestCompleteWithInformation(Request, status, sizeof(BOOLEAN));
                return;
            }
            break;

        default:
            KdPrint(("[DeadboltMonitor] Unknown IoControlCode: 0x%X\n", IoControlCode));
            status = STATUS_INVALID_DEVICE_REQUEST;
            break;
    }

    WdfRequestComplete(Request, status);
}
