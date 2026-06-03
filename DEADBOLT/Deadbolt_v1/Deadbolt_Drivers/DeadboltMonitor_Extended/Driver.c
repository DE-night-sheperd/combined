/*
    Deadbolt Endpoint Shield - FULL EDR Kernel Driver
    Extended with:
    - Process creation/exit callbacks
    - Thread creation/exit callbacks
    - Image load callbacks
    - Registry callbacks
    - Event queue management
*/

#include <ntddk.h>
#include <wdf.h>
#include <ntstrsafe.h>

#define DEADBOLT_POOL_TAG 'tbDd'
#define DEADBOLT_MAX_EVENT_QUEUE 1000

typedef enum _DEADBOLT_EVENT_TYPE {
    EventTypeProcessCreate,
    EventTypeProcessExit,
    EventTypeThreadCreate,
    EventTypeThreadExit,
    EventTypeImageLoad,
    EventTypeRegistryCreateKey,
    EventTypeRegistryDeleteKey,
    EventTypeRegistrySetValue,
    EventTypeRegistryDeleteValue
} DEADBOLT_EVENT_TYPE;

typedef struct _DEADBOLT_EVENT {
    DEADBOLT_EVENT_TYPE EventType;
    LARGE_INTEGER Timestamp;
    HANDLE ProcessId;
    HANDLE ParentProcessId;
    HANDLE ThreadId;
    WCHAR ImageName[260];
    WCHAR Details[512];
} DEADBOLT_EVENT, *PDEADBOLT_EVENT;

typedef struct _DEVICE_CONTEXT {
    WDFDEVICE WdfDevice;
    BOOLEAN IsMonitoringActive;
    KSPIN_LOCK EventQueueLock;
    PDEADBOLT_EVENT EventQueue[DEADBOLT_MAX_EVENT_QUEUE];
    ULONG EventQueueHead;
    ULONG EventQueueTail;
    ULONG EventQueueCount;
    LARGE_INTEGER RegistryCookie;
} DEVICE_CONTEXT, *PDEVICE_CONTEXT;

WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(DEVICE_CONTEXT, GetDeviceContext)

DRIVER_INITIALIZE DriverEntry;
EVT_WDF_DRIVER_DEVICE_ADD DeadboltEvtDeviceAdd;
EVT_WDF_OBJECT_CONTEXT_CLEANUP DeadboltEvtDriverContextCleanup;
EVT_WDF_DEVICE_FILE_CREATE DeadboltEvtDeviceFileCreate;
EVT_WDF_DEVICE_FILE_CLOSE DeadboltEvtDeviceFileClose;
EVT_WDF_IO_QUEUE_IO_DEVICE_CONTROL DeadboltEvtIoDeviceControl;

VOID DeadboltProcessNotifyRoutineEx(
    _Inout_ PEPROCESS Process,
    _In_ HANDLE ProcessId,
    _Inout_opt_ PPS_CREATE_NOTIFY_INFO CreateInfo
);

VOID DeadboltThreadNotifyRoutine(
    _In_ HANDLE ProcessId,
    _In_ HANDLE ThreadId,
    _In_ BOOLEAN Create
);

VOID DeadboltImageLoadNotifyRoutine(
    _In_opt_ PUNICODE_STRING FullImageName,
    _In_ HANDLE ProcessId,
    _In_ PIMAGE_INFO ImageInfo
);

NTSTATUS DeadboltRegistryCallback(
    _In_ PVOID CallbackContext,
    _In_opt_ PVOID Argument1,
    _In_opt_ PVOID Argument2
);

NTSTATUS AddEventToQueue(PDEVICE_CONTEXT DeviceContext, PDEADBOLT_EVENT Event);
PDEADBOLT_EVENT AllocateEvent(VOID);
VOID FreeEvent(PDEADBOLT_EVENT Event);

NTSTATUS DriverEntry(_In_ PDRIVER_OBJECT DriverObject, _In_ PUNICODE_STRING RegistryPath)
{
    NTSTATUS status;
    WDF_DRIVER_CONFIG config;
    WDF_OBJECT_ATTRIBUTES attributes;

    KdPrint(("[DeadboltEDR] DriverEntry called - FULL EDR MODE\n"));

    WDF_DRIVER_CONFIG_INIT(&config, DeadboltEvtDeviceAdd);
    config.EvtDriverContextCleanup = DeadboltEvtDriverContextCleanup;

    WDF_OBJECT_ATTRIBUTES_INIT(&attributes);

    status = WdfDriverCreate(DriverObject, RegistryPath, &attributes, &config, WDF_NO_HANDLE);
    if (!NT_SUCCESS(status)) {
        KdPrint(("[DeadboltEDR] WdfDriverCreate failed: 0x%X\n", status));
        return status;
    }

    KdPrint(("[DeadboltEDR] DriverEntry succeeded\n"));
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
    KdPrint(("[DeadboltEDR] DeadboltEvtDeviceAdd called\n"));

    RtlInitUnicodeString(&deviceName, L"\\Device\\DeadboltEDR");
    RtlInitUnicodeString(&dosDeviceName, L"\\DosDevices\\DeadboltEDR");

    WDF_FILEOBJECT_CONFIG_INIT(&fileObjectConfig, DeadboltEvtDeviceFileCreate, DeadboltEvtDeviceFileClose, WDF_NO_EVENT_CALLBACK);
    WdfDeviceInitSetFileObjectConfig(DeviceInit, &fileObjectConfig, WDF_NO_OBJECT_ATTRIBUTES);

    status = WdfDeviceInitAssignName(DeviceInit, &deviceName);
    if (!NT_SUCCESS(status)) {
        KdPrint(("[DeadboltEDR] WdfDeviceInitAssignName failed: 0x%X\n", status));
        return status;
    }

    WDF_OBJECT_ATTRIBUTES_INIT_CONTEXT_TYPE(&deviceAttributes, DEVICE_CONTEXT);

    status = WdfDeviceCreate(&DeviceInit, &deviceAttributes, &device);
    if (!NT_SUCCESS(status)) {
        KdPrint(("[DeadboltEDR] WdfDeviceCreate failed: 0x%X\n", status));
        return status;
    }

    deviceContext = GetDeviceContext(device);
    deviceContext->WdfDevice = device;
    deviceContext->IsMonitoringActive = FALSE;
    KeInitializeSpinLock(&deviceContext->EventQueueLock);
    deviceContext->EventQueueHead = 0;
    deviceContext->EventQueueTail = 0;
    deviceContext->EventQueueCount = 0;
    deviceContext->RegistryCookie.QuadPart = 0;

    status = WdfDeviceCreateSymbolicLink(device, &dosDeviceName);
    if (!NT_SUCCESS(status)) {
        KdPrint(("[DeadboltEDR] WdfDeviceCreateSymbolicLink failed: 0x%X\n", status));
        return status;
    }

    WDF_IO_QUEUE_CONFIG_INIT_DEFAULT_QUEUE(&ioQueueConfig, WdfIoQueueDispatchParallel);
    ioQueueConfig.EvtIoDeviceControl = DeadboltEvtIoDeviceControl;

    status = WdfIoQueueCreate(device, &ioQueueConfig, WDF_NO_OBJECT_ATTRIBUTES, WDF_NO_HANDLE);
    if (!NT_SUCCESS(status)) {
        KdPrint(("[DeadboltEDR] WdfIoQueueCreate failed: 0x%X\n", status));
        return status;
    }

    KdPrint(("[DeadboltEDR] DeadboltEvtDeviceAdd succeeded\n"));
    return STATUS_SUCCESS;
}

VOID DeadboltEvtDriverContextCleanup(_In_ WDFOBJECT DriverObject)
{
    UNREFERENCED_PARAMETER(DriverObject);
    KdPrint(("[DeadboltEDR] DeadboltEvtDriverContextCleanup called\n"));
}

VOID DeadboltEvtDeviceFileCreate(_In_ WDFDEVICE Device, _In_ WDFREQUEST Request, _In_ WDFFILEOBJECT FileObject)
{
    UNREFERENCED_PARAMETER(Device);
    UNREFERENCED_PARAMETER(FileObject);
    KdPrint(("[DeadboltEDR] DeadboltEvtDeviceFileCreate called\n"));
    WdfRequestComplete(Request, STATUS_SUCCESS);
}

VOID DeadboltEvtDeviceFileClose(_In_ WDFFILEOBJECT FileObject)
{
    UNREFERENCED_PARAMETER(FileObject);
    KdPrint(("[DeadboltEDR] DeadboltEvtDeviceFileClose called\n"));
}

VOID DeadboltEvtIoDeviceControl(_In_ WDFQUEUE Queue, _In_ WDFREQUEST Request, _In_ size_t OutputBufferLength, _In_ size_t InputBufferLength, _In_ ULONG IoControlCode)
{
    NTSTATUS status = STATUS_SUCCESS;
    PVOID buffer;
    size_t bufferLength;
    WDFDEVICE device;
    PDEVICE_CONTEXT deviceContext;
    KLOCK_QUEUE_HANDLE lockHandle;

    UNREFERENCED_PARAMETER(Queue);
    UNREFERENCED_PARAMETER(InputBufferLength);

    device = WdfIoQueueGetDevice(Queue);
    deviceContext = GetDeviceContext(device);

    KdPrint(("[DeadboltEDR] IoControlCode: 0x%X\n", IoControlCode));

    switch (IoControlCode) {
        case 0x800:
            KdPrint(("[DeadboltEDR] Starting FULL EDR monitoring...\n"));
            
            status = PsSetCreateProcessNotifyRoutineEx(DeadboltProcessNotifyRoutineEx, FALSE);
            if (!NT_SUCCESS(status)) {
                KdPrint(("[DeadboltEDR] PsSetCreateProcessNotifyRoutineEx failed: 0x%X\n", status));
            }
            
            status = PsSetCreateThreadNotifyRoutine(DeadboltThreadNotifyRoutine);
            if (!NT_SUCCESS(status)) {
                KdPrint(("[DeadboltEDR] PsSetCreateThreadNotifyRoutine failed: 0x%X\n", status));
            }
            
            status = PsSetLoadImageNotifyRoutine(DeadboltImageLoadNotifyRoutine);
            if (!NT_SUCCESS(status)) {
                KdPrint(("[DeadboltEDR] PsSetLoadImageNotifyRoutine failed: 0x%X\n", status));
            }
            
            status = CmRegisterCallbackEx(DeadboltRegistryCallback, NULL, (PVOID)deviceContext, NULL, NULL, &deviceContext->RegistryCookie);
            if (!NT_SUCCESS(status)) {
                KdPrint(("[DeadboltEDR] CmRegisterCallbackEx failed: 0x%X\n", status));
            }
            
            deviceContext->IsMonitoringActive = TRUE;
            status = STATUS_SUCCESS;
            break;

        case 0x801:
            KdPrint(("[DeadboltEDR] Stopping FULL EDR monitoring...\n"));
            PsSetCreateProcessNotifyRoutineEx(DeadboltProcessNotifyRoutineEx, TRUE);
            PsRemoveCreateThreadNotifyRoutine(DeadboltThreadNotifyRoutine);
            PsRemoveLoadImageNotifyRoutine(DeadboltImageLoadNotifyRoutine);
            if (deviceContext->RegistryCookie.QuadPart != 0) {
                CmUnRegisterCallback(deviceContext->RegistryCookie);
                deviceContext->RegistryCookie.QuadPart = 0;
            }
            deviceContext->IsMonitoringActive = FALSE;
            status = STATUS_SUCCESS;
            break;

        case 0x802:
            KdPrint(("[DeadboltEDR] Getting status...\n"));
            status = WdfRequestRetrieveOutputBuffer(Request, sizeof(BOOLEAN), &buffer, &bufferLength);
            if (NT_SUCCESS(status)) {
                *(PBOOLEAN)buffer = deviceContext->IsMonitoringActive;
                WdfRequestCompleteWithInformation(Request, status, sizeof(BOOLEAN));
                return;
            }
            break;

        case 0x803:
            KdPrint(("[DeadboltEDR] Getting events...\n"));
            status = WdfRequestRetrieveOutputBuffer(Request, OutputBufferLength, &buffer, &bufferLength);
            if (NT_SUCCESS(status)) {
                ULONG eventsCopied = 0;
                PDEADBOLT_EVENT outputEvents = (PDEADBOLT_EVENT)buffer;
                
                KeAcquireInStackQueuedSpinLock(&deviceContext->EventQueueLock, &lockHandle);
                
                while (deviceContext->EventQueueCount > 0 && 
                       (eventsCopied + 1) * sizeof(DEADBOLT_EVENT) <= bufferLength) {
                    RtlCopyMemory(&outputEvents[eventsCopied], 
                                  deviceContext->EventQueue[deviceContext->EventQueueHead], 
                                  sizeof(DEADBOLT_EVENT));
                    
                    FreeEvent(deviceContext->EventQueue[deviceContext->EventQueueHead]);
                    deviceContext->EventQueueHead = (deviceContext->EventQueueHead + 1) % DEADBOLT_MAX_EVENT_QUEUE;
                    deviceContext->EventQueueCount--;
                    eventsCopied++;
                }
                
                KeReleaseInStackQueuedSpinLock(&lockHandle);
                
                WdfRequestCompleteWithInformation(Request, STATUS_SUCCESS, eventsCopied * sizeof(DEADBOLT_EVENT));
                return;
            }
            break;

        default:
            status = STATUS_INVALID_DEVICE_REQUEST;
            break;
    }

    WdfRequestComplete(Request, status);
}

VOID DeadboltProcessNotifyRoutineEx(
    _Inout_ PEPROCESS Process,
    _In_ HANDLE ProcessId,
    _Inout_opt_ PPS_CREATE_NOTIFY_INFO CreateInfo
)
{
    UNREFERENCED_PARAMETER(Process);
    PDEADBOLT_EVENT event;
    WDFDEVICE device;
    PDEVICE_CONTEXT deviceContext;
    
    device = WdfDriverGetDefaultDevice(WdfGetDriver());
    if (device == NULL) {
        return;
    }
    deviceContext = GetDeviceContext(device);
    
    if (!deviceContext->IsMonitoringActive) {
        return;
    }
    
    event = AllocateEvent();
    if (event == NULL) {
        return;
    }
    
    KeQuerySystemTimePrecise(&event->Timestamp);
    event->ProcessId = ProcessId;
    
    if (CreateInfo != NULL) {
        event->EventType = EventTypeProcessCreate;
        event->ParentProcessId = CreateInfo->ParentProcessId;
        
        if (CreateInfo->ImageFileName != NULL) {
            RtlStringCchCopyNW(event->ImageName, RTL_NUMBER_OF(event->ImageName), 
                              CreateInfo->ImageFileName->Buffer, 
                              CreateInfo->ImageFileName->Length / sizeof(WCHAR));
        }
        
        KdPrint(("[DeadboltEDR] PROCESS CREATE: PID %lu, Parent %lu, Image: %wZ\n", 
                 (ULONG)ProcessId, (ULONG)CreateInfo->ParentProcessId, CreateInfo->ImageFileName));
    } else {
        event->EventType = EventTypeProcessExit;
        KdPrint(("[DeadboltEDR] PROCESS EXIT: PID %lu\n", (ULONG)ProcessId));
    }
    
    AddEventToQueue(deviceContext, event);
}

VOID DeadboltThreadNotifyRoutine(
    _In_ HANDLE ProcessId,
    _In_ HANDLE ThreadId,
    _In_ BOOLEAN Create
)
{
    PDEADBOLT_EVENT event;
    WDFDEVICE device;
    PDEVICE_CONTEXT deviceContext;
    
    device = WdfDriverGetDefaultDevice(WdfGetDriver());
    if (device == NULL) {
        return;
    }
    deviceContext = GetDeviceContext(device);
    
    if (!deviceContext->IsMonitoringActive) {
        return;
    }
    
    event = AllocateEvent();
    if (event == NULL) {
        return;
    }
    
    KeQuerySystemTimePrecise(&event->Timestamp);
    event->ProcessId = ProcessId;
    event->ThreadId = ThreadId;
    
    if (Create) {
        event->EventType = EventTypeThreadCreate;
        KdPrint(("[DeadboltEDR] THREAD CREATE: PID %lu, TID %lu\n", 
                 (ULONG)ProcessId, (ULONG)ThreadId));
    } else {
        event->EventType = EventTypeThreadExit;
        KdPrint(("[DeadboltEDR] THREAD EXIT: PID %lu, TID %lu\n", 
                 (ULONG)ProcessId, (ULONG)ThreadId));
    }
    
    AddEventToQueue(deviceContext, event);
}

VOID DeadboltImageLoadNotifyRoutine(
    _In_opt_ PUNICODE_STRING FullImageName,
    _In_ HANDLE ProcessId,
    _In_ PIMAGE_INFO ImageInfo
)
{
    UNREFERENCED_PARAMETER(ImageInfo);
    PDEADBOLT_EVENT event;
    WDFDEVICE device;
    PDEVICE_CONTEXT deviceContext;
    
    device = WdfDriverGetDefaultDevice(WdfGetDriver());
    if (device == NULL) {
        return;
    }
    deviceContext = GetDeviceContext(device);
    
    if (!deviceContext->IsMonitoringActive) {
        return;
    }
    
    if (FullImageName == NULL) {
        return;
    }
    
    event = AllocateEvent();
    if (event == NULL) {
        return;
    }
    
    KeQuerySystemTimePrecise(&event->Timestamp);
    event->EventType = EventTypeImageLoad;
    event->ProcessId = ProcessId;
    
    RtlStringCchCopyNW(event->ImageName, RTL_NUMBER_OF(event->ImageName), 
                      FullImageName->Buffer, 
                      FullImageName->Length / sizeof(WCHAR));
    
    KdPrint(("[DeadboltEDR] IMAGE LOAD: PID %lu, Image: %wZ\n", 
             (ULONG)ProcessId, FullImageName));
    
    AddEventToQueue(deviceContext, event);
}

NTSTATUS DeadboltRegistryCallback(
    _In_ PVOID CallbackContext,
    _In_opt_ PVOID Argument1,
    _In_opt_ PVOID Argument2
)
{
    PDEVICE_CONTEXT deviceContext;
    REG_NOTIFY_CLASS notifyClass;
    PDEADBOLT_EVENT event;
    PCM_CREATE_KEY_CONTEXT createContext;
    PCM_KEY_CONTEXT keyContext;
    PCM_SET_VALUE_KEY_CONTEXT setValueContext;
    PCM_DELETE_VALUE_KEY_CONTEXT deleteValueContext;
    
    UNREFERENCED_PARAMETER(Argument2);
    
    deviceContext = (PDEVICE_CONTEXT)CallbackContext;
    if (!deviceContext->IsMonitoringActive) {
        return STATUS_SUCCESS;
    }
    
    notifyClass = (REG_NOTIFY_CLASS)(ULONG_PTR)Argument1;
    
    event = AllocateEvent();
    if (event == NULL) {
        return STATUS_SUCCESS;
    }
    
    KeQuerySystemTimePrecise(&event->Timestamp);
    event->ProcessId = PsGetCurrentProcessId();
    
    switch (notifyClass) {
        case RegNtPreCreateKeyEx:
            event->EventType = EventTypeRegistryCreateKey;
            createContext = (PCM_CREATE_KEY_CONTEXT)Argument2;
            if (createContext != NULL && createContext->CompleteName != NULL) {
                RtlStringCchCopyNW(event->Details, RTL_NUMBER_OF(event->Details), 
                                  createContext->CompleteName->Buffer, 
                                  createContext->CompleteName->Length / sizeof(WCHAR));
            }
            KdPrint(("[DeadboltEDR] REGISTRY CREATE KEY: %wZ\n", 
                     createContext ? createContext->CompleteName : L"(unknown)"));
            break;
            
        case RegNtPreDeleteKey:
            event->EventType = EventTypeRegistryDeleteKey;
            keyContext = (PCM_KEY_CONTEXT)Argument2;
            KdPrint(("[DeadboltEDR] REGISTRY DELETE KEY\n"));
            break;
            
        case RegNtPreSetValueKey:
            event->EventType = EventTypeRegistrySetValue;
            setValueContext = (PCM_SET_VALUE_KEY_CONTEXT)Argument2;
            if (setValueContext != NULL && setValueContext->ValueName != NULL) {
                RtlStringCchCopyNW(event->Details, RTL_NUMBER_OF(event->Details), 
                                  setValueContext->ValueName->Buffer, 
                                  setValueContext->ValueName->Length / sizeof(WCHAR));
            }
            KdPrint(("[DeadboltEDR] REGISTRY SET VALUE: %wZ\n", 
                     setValueContext ? setValueContext->ValueName : L"(unknown)"));
            break;
            
        case RegNtPreDeleteValueKey:
            event->EventType = EventTypeRegistryDeleteValue;
            deleteValueContext = (PCM_DELETE_VALUE_KEY_CONTEXT)Argument2;
            if (deleteValueContext != NULL && deleteValueContext->ValueName != NULL) {
                RtlStringCchCopyNW(event->Details, RTL_NUMBER_OF(event->Details), 
                                  deleteValueContext->ValueName->Buffer, 
                                  deleteValueContext->ValueName->Length / sizeof(WCHAR));
            }
            KdPrint(("[DeadboltEDR] REGISTRY DELETE VALUE: %wZ\n", 
                     deleteValueContext ? deleteValueContext->ValueName : L"(unknown)"));
            break;
            
        default:
            FreeEvent(event);
            return STATUS_SUCCESS;
    }
    
    AddEventToQueue(deviceContext, event);
    return STATUS_SUCCESS;
}

PDEADBOLT_EVENT AllocateEvent(VOID)
{
    PDEADBOLT_EVENT event = (PDEADBOLT_EVENT)ExAllocatePoolWithTag(
        NonPagedPoolNx, 
        sizeof(DEADBOLT_EVENT), 
        DEADBOLT_POOL_TAG
    );
    
    if (event != NULL) {
        RtlZeroMemory(event, sizeof(DEADBOLT_EVENT));
    }
    
    return event;
}

NTSTATUS AddEventToQueue(PDEVICE_CONTEXT DeviceContext, PDEADBOLT_EVENT Event)
{
    KLOCK_QUEUE_HANDLE lockHandle;
    NTSTATUS status = STATUS_SUCCESS;
    
    KeAcquireInStackQueuedSpinLock(&DeviceContext->EventQueueLock, &lockHandle);
    
    if (DeviceContext->EventQueueCount >= DEADBOLT_MAX_EVENT_QUEUE) {
        FreeEvent(DeviceContext->EventQueue[DeviceContext->EventQueueHead]);
        DeviceContext->EventQueueHead = (DeviceContext->EventQueueHead + 1) % DEADBOLT_MAX_EVENT_QUEUE;
        DeviceContext->EventQueueCount--;
    }
    
    DeviceContext->EventQueue[DeviceContext->EventQueueTail] = Event;
    DeviceContext->EventQueueTail = (DeviceContext->EventQueueTail + 1) % DEADBOLT_MAX_EVENT_QUEUE;
    DeviceContext->EventQueueCount++;
    
    KeReleaseInStackQueuedSpinLock(&lockHandle);
    
    return status;
}

VOID FreeEvent(PDEADBOLT_EVENT Event)
{
    if (Event != NULL) {
        ExFreePoolWithTag(Event, DEADBOLT_POOL_TAG);
    }
}
