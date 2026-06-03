/*
    Deadlock Endpoint Shield - File System Minifilter Driver
    Monitors and enforces file system operations
*/

#include <fltKernel.h>
#include <dontuse.h>
#include <ntstrsafe.h>

#define DEADLOCK_MINIFILTER_POOL_TAG 'tbmD'
#define DEADLOCK_MINIFILTER_MAX_NAME 1024
#define DEADLOCK_MAX_RULES 256

typedef enum _DEADLOCK_RULE_TYPE {
    RuleTypeBlockAll = 0,
    RuleTypeBlockRead,
    RuleTypeBlockWrite,
    RuleTypeBlockDelete,
    RuleTypeBlockRename
} DEADLOCK_RULE_TYPE;

typedef struct _DEADLOCK_ACCESS_RULE {
    UNICODE_STRING Path;
    DEADLOCK_RULE_TYPE RuleType;
    BOOLEAN Enabled;
} DEADLOCK_ACCESS_RULE, *PDEADLOCK_ACCESS_RULE;

typedef struct _DEADLOCK_GLOBAL_DATA {
    PFLT_FILTER FilterHandle;
    DEADLOCK_ACCESS_RULE Rules[DEADLOCK_MAX_RULES];
    ULONG RuleCount;
    KSPIN_LOCK RulesLock;
    PDEVICE_OBJECT ControlDeviceObject;
    UNICODE_STRING DeviceName;
    UNICODE_STRING DosDeviceName;
} DEADLOCK_GLOBAL_DATA, *PDEADLOCK_GLOBAL_DATA;

DEADLOCK_GLOBAL_DATA gDeadlockData = { 0 };

NTSTATUS
DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath
);

NTSTATUS
DeadlockMinifilterUnload(
    _In_ FLT_FILTER_UNLOAD_FLAGS Flags
);

NTSTATUS
DeadlockMinifilterInstanceSetup(
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _In_ FLT_INSTANCE_SETUP_FLAGS Flags,
    _In_ DEVICE_TYPE VolumeDeviceType,
    _In_ FLT_FILESYSTEM_TYPE VolumeFilesystemType
);

FLT_PREOP_CALLBACK_STATUS
DeadlockMinifilterPreCreate(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
);

FLT_PREOP_CALLBACK_STATUS
DeadlockMinifilterPreWrite(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
);

FLT_PREOP_CALLBACK_STATUS
DeadlockMinifilterPreSetInformation(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
);

NTSTATUS
DeadlockCreateControlDevice(
    _In_ PDRIVER_OBJECT DriverObject
);

VOID
DeadlockDeleteControlDevice(
    VOID
);

NTSTATUS
DeadlockControlDeviceDispatch(
    _In_ PDEVICE_OBJECT DeviceObject,
    _Inout_ PIRP Irp
);

BOOLEAN
DeadlockCheckAccess(
    _In_ PUNICODE_STRING FilePath,
    _In_ DEADLOCK_RULE_TYPE OperationType
);

CONST FLT_OPERATION_REGISTRATION Callbacks[] = {
    { IRP_MJ_CREATE,
      0,
      DeadlockMinifilterPreCreate,
      NULL },

    { IRP_MJ_WRITE,
      0,
      DeadlockMinifilterPreWrite,
      NULL },

    { IRP_MJ_SET_INFORMATION,
      0,
      DeadlockMinifilterPreSetInformation,
      NULL },

    { IRP_MJ_OPERATION_END }
};

CONST FLT_REGISTRATION FilterRegistration = {
    sizeof(FLT_REGISTRATION),
    FLT_REGISTRATION_VERSION,
    0,
    NULL,
    Callbacks,
    DeadlockMinifilterUnload,
    NULL,
    DeadlockMinifilterInstanceSetup,
    NULL,
    NULL,
    NULL,
    NULL
};

NTSTATUS
DriverEntry(
    _In_ PDRIVER_OBJECT DriverObject,
    _In_ PUNICODE_STRING RegistryPath
)
{
    NTSTATUS status;

    UNREFERENCED_PARAMETER(RegistryPath);

    KdPrint(("[DeadlockMinifilter] DriverEntry called\n"));

    KeInitializeSpinLock(&gDeadlockData.RulesLock);
    gDeadlockData.RuleCount = 0;
    RtlZeroMemory(&gDeadlockData.Rules, sizeof(gDeadlockData.Rules));

    status = FltRegisterFilter(DriverObject, &FilterRegistration, &gDeadlockData.FilterHandle);
    if (!NT_SUCCESS(status)) {
        KdPrint(("[DeadlockMinifilter] FltRegisterFilter failed: 0x%X\n", status));
        return status;
    }

    status = DeadlockCreateControlDevice(DriverObject);
    if (!NT_SUCCESS(status)) {
        KdPrint(("[DeadlockMinifilter] DeadlockCreateControlDevice failed: 0x%X\n", status));
        FltUnregisterFilter(gDeadlockData.FilterHandle);
        return status;
    }

    status = FltStartFiltering(gDeadlockData.FilterHandle);
    if (!NT_SUCCESS(status)) {
        KdPrint(("[DeadlockMinifilter] FltStartFiltering failed: 0x%X\n", status));
        DeadlockDeleteControlDevice();
        FltUnregisterFilter(gDeadlockData.FilterHandle);
        return status;
    }

    KdPrint(("[DeadlockMinifilter] DriverEntry succeeded\n"));
    return STATUS_SUCCESS;
}

NTSTATUS
DeadlockMinifilterUnload(
    _In_ FLT_FILTER_UNLOAD_FLAGS Flags
)
{
    UNREFERENCED_PARAMETER(Flags);
    ULONG i;
    KIRQL oldIrql;

    KdPrint(("[DeadlockMinifilter] Unload called\n"));

    DeadlockDeleteControlDevice();

    KeAcquireSpinLock(&gDeadlockData.RulesLock, &oldIrql);
    for (i = 0; i < gDeadlockData.RuleCount; i++) {
        if (gDeadlockData.Rules[i].Path.Buffer != NULL) {
            ExFreePoolWithTag(gDeadlockData.Rules[i].Path.Buffer, DEADLOCK_MINIFILTER_POOL_TAG);
            gDeadlockData.Rules[i].Path.Buffer = NULL;
        }
    }
    gDeadlockData.RuleCount = 0;
    KeReleaseSpinLock(&gDeadlockData.RulesLock, oldIrql);

    if (gDeadlockData.FilterHandle != NULL) {
        FltUnregisterFilter(gDeadlockData.FilterHandle);
        gDeadlockData.FilterHandle = NULL;
    }

    KdPrint(("[DeadlockMinifilter] Unload succeeded\n"));
    return STATUS_SUCCESS;
}

NTSTATUS
DeadlockMinifilterInstanceSetup(
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _In_ FLT_INSTANCE_SETUP_FLAGS Flags,
    _In_ DEVICE_TYPE VolumeDeviceType,
    _In_ FLT_FILESYSTEM_TYPE VolumeFilesystemType
)
{
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(Flags);
    UNREFERENCED_PARAMETER(VolumeDeviceType);
    UNREFERENCED_PARAMETER(VolumeFilesystemType);

    KdPrint(("[DeadlockMinifilter] InstanceSetup called\n"));
    return STATUS_SUCCESS;
}

BOOLEAN
DeadlockCheckAccess(
    _In_ PUNICODE_STRING FilePath,
    _In_ DEADLOCK_RULE_TYPE OperationType
)
{
    KIRQL oldIrql;
    ULONG i;
    BOOLEAN blockAccess = FALSE;

    if (FilePath == NULL || FilePath->Buffer == NULL) {
        return FALSE;
    }

    KeAcquireSpinLock(&gDeadlockData.RulesLock, &oldIrql);

    for (i = 0; i < gDeadlockData.RuleCount; i++) {
        PDEADLOCK_ACCESS_RULE rule = &gDeadlockData.Rules[i];
        
        if (!rule->Enabled || rule->Path.Buffer == NULL) {
            continue;
        }

        if (FilePath->Length >= rule->Path.Length) {
            if (RtlPrefixUnicodeString(&rule->Path, FilePath, TRUE)) {
                if (rule->RuleType == RuleTypeBlockAll) {
                    blockAccess = TRUE;
                    break;
                }
                if (rule->RuleType == OperationType) {
                    blockAccess = TRUE;
                    break;
                }
            }
        }
    }

    KeReleaseSpinLock(&gDeadlockData.RulesLock, oldIrql);
    return blockAccess;
}

FLT_PREOP_CALLBACK_STATUS
DeadlockMinifilterPreCreate(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
)
{
    NTSTATUS status;
    PFLT_FILE_NAME_INFORMATION fileNameInfo;
    ACCESS_MASK desiredAccess;

    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(CompletionContext);

    *CompletionContext = NULL;

    status = FltGetFileNameInformation(Data, FLT_FILE_NAME_NORMALIZED | FLT_FILE_NAME_QUERY_DEFAULT, &fileNameInfo);
    if (NT_SUCCESS(status)) {
        desiredAccess = Data->Iopb->Parameters.Create.SecurityContext->DesiredAccess;
        
        KdPrint(("[DeadlockMinifilter] FILE CREATE/OPEN: %wZ\n", &fileNameInfo->Name));

        DEADLOCK_RULE_TYPE opType = RuleTypeBlockRead;
        if (desiredAccess & (FILE_WRITE_DATA | FILE_APPEND_DATA | FILE_WRITE_EA | FILE_WRITE_ATTRIBUTES)) {
            opType = RuleTypeBlockWrite;
        }

        if (DeadlockCheckAccess(&fileNameInfo->Name, opType)) {
            KdPrint(("[DeadlockMinifilter] BLOCKING ACCESS to: %wZ\n", &fileNameInfo->Name));
            FltReleaseFileNameInformation(fileNameInfo);
            Data->IoStatus.Status = STATUS_ACCESS_DENIED;
            Data->IoStatus.Information = 0;
            return FLT_PREOP_COMPLETE;
        }
        
        FltReleaseFileNameInformation(fileNameInfo);
    }

    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

FLT_PREOP_CALLBACK_STATUS
DeadlockMinifilterPreWrite(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
)
{
    NTSTATUS status;
    PFLT_FILE_NAME_INFORMATION fileNameInfo;

    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(CompletionContext);

    *CompletionContext = NULL;

    status = FltGetFileNameInformation(Data, FLT_FILE_NAME_NORMALIZED | FLT_FILE_NAME_QUERY_DEFAULT, &fileNameInfo);
    if (NT_SUCCESS(status)) {
        KdPrint(("[DeadlockMinifilter] FILE WRITE: %wZ, Bytes: %llu\n", 
                 &fileNameInfo->Name, 
                 Data->Iopb->Parameters.Write.Length));

        if (DeadlockCheckAccess(&fileNameInfo->Name, RuleTypeBlockWrite)) {
            KdPrint(("[DeadlockMinifilter] BLOCKING WRITE to: %wZ\n", &fileNameInfo->Name));
            FltReleaseFileNameInformation(fileNameInfo);
            Data->IoStatus.Status = STATUS_ACCESS_DENIED;
            Data->IoStatus.Information = 0;
            return FLT_PREOP_COMPLETE;
        }
        
        FltReleaseFileNameInformation(fileNameInfo);
    }

    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

FLT_PREOP_CALLBACK_STATUS
DeadlockMinifilterPreSetInformation(
    _Inout_ PFLT_CALLBACK_DATA Data,
    _In_ PCFLT_RELATED_OBJECTS FltObjects,
    _Flt_CompletionContext_Outptr_ PVOID *CompletionContext
)
{
    NTSTATUS status;
    PFLT_FILE_NAME_INFORMATION fileNameInfo;
    DEADLOCK_RULE_TYPE opType = RuleTypeBlockAll;

    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(CompletionContext);

    *CompletionContext = NULL;

    if (Data->Iopb->Parameters.SetFileInformation.FileInformationClass == FileDispositionInformation ||
        Data->Iopb->Parameters.SetFileInformation.FileInformationClass == FileDispositionInformationEx) {
        
        opType = RuleTypeBlockDelete;
    } else if (Data->Iopb->Parameters.SetFileInformation.FileInformationClass == FileRenameInformation ||
               Data->Iopb->Parameters.SetFileInformation.FileInformationClass == FileRenameInformationEx) {
        opType = RuleTypeBlockRename;
    } else {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }
        
    status = FltGetFileNameInformation(Data, FLT_FILE_NAME_NORMALIZED | FLT_FILE_NAME_QUERY_DEFAULT, &fileNameInfo);
    if (NT_SUCCESS(status)) {
        KdPrint(("[DeadlockMinifilter] FILE OP: %wZ\n", &fileNameInfo->Name));

        if (DeadlockCheckAccess(&fileNameInfo->Name, opType)) {
            KdPrint(("[DeadlockMinifilter] BLOCKING OPERATION on: %wZ\n", &fileNameInfo->Name));
            FltReleaseFileNameInformation(fileNameInfo);
            Data->IoStatus.Status = STATUS_ACCESS_DENIED;
            Data->IoStatus.Information = 0;
            return FLT_PREOP_COMPLETE;
        }
        
        FltReleaseFileNameInformation(fileNameInfo);
    }

    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

NTSTATUS
DeadlockCreateControlDevice(
    _In_ PDRIVER_OBJECT DriverObject
)
{
    NTSTATUS status;
    UNICODE_STRING deviceName;
    UNICODE_STRING dosDeviceName;

    RtlInitUnicodeString(&deviceName, L"\\Device\\DeadlockMinifilter");
    RtlInitUnicodeString(&dosDeviceName, L"\\DosDevices\\DeadlockMinifilter");

    status = IoCreateDevice(
        DriverObject,
        0,
        &deviceName,
        FILE_DEVICE_UNKNOWN,
        FILE_DEVICE_SECURE_OPEN,
        FALSE,
        &gDeadlockData.ControlDeviceObject
    );

    if (!NT_SUCCESS(status)) {
        return status;
    }

    status = IoCreateSymbolicLink(&dosDeviceName, &deviceName);
    if (!NT_SUCCESS(status)) {
        IoDeleteDevice(gDeadlockData.ControlDeviceObject);
        gDeadlockData.ControlDeviceObject = NULL;
        return status;
    }

    RtlCopyUnicodeString(&gDeadlockData.DeviceName, &deviceName);
    RtlCopyUnicodeString(&gDeadlockData.DosDeviceName, &dosDeviceName);

    DriverObject->MajorFunction[IRP_MJ_CREATE] = DeadlockControlDeviceDispatch;
    DriverObject->MajorFunction[IRP_MJ_CLOSE] = DeadlockControlDeviceDispatch;
    DriverObject->MajorFunction[IRP_MJ_DEVICE_CONTROL] = DeadlockControlDeviceDispatch;

    gDeadlockData.ControlDeviceObject->Flags |= DO_BUFFERED_IO;
    gDeadlockData.ControlDeviceObject->Flags &= ~DO_DEVICE_INITIALIZING;

    return STATUS_SUCCESS;
}

VOID
DeadlockDeleteControlDevice(
    VOID
)
{
    if (gDeadlockData.ControlDeviceObject != NULL) {
        IoDeleteSymbolicLink(&gDeadlockData.DosDeviceName);
        IoDeleteDevice(gDeadlockData.ControlDeviceObject);
        gDeadlockData.ControlDeviceObject = NULL;
    }
}

#define IOCTL_DEADLOCK_ADD_RULE CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_DEADLOCK_CLEAR_RULES CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_ANY_ACCESS)

NTSTATUS
DeadlockControlDeviceDispatch(
    _In_ PDEVICE_OBJECT DeviceObject,
    _Inout_ PIRP Irp
)
{
    NTSTATUS status = STATUS_SUCCESS;
    PIO_STACK_LOCATION irpSp;
    ULONG inBufferLength;
    PVOID inBuffer;
    KIRQL oldIrql;
    ULONG i;

    UNREFERENCED_PARAMETER(DeviceObject);

    irpSp = IoGetCurrentIrpStackLocation(Irp);

    switch (irpSp->MajorFunction) {
    case IRP_MJ_CREATE:
    case IRP_MJ_CLOSE:
        status = STATUS_SUCCESS;
        break;

    case IRP_MJ_DEVICE_CONTROL:
        inBuffer = Irp->AssociatedIrp.SystemBuffer;
        inBufferLength = irpSp->Parameters.DeviceIoControl.InputBufferLength;

        switch (irpSp->Parameters.DeviceIoControl.IoControlCode) {
        case IOCTL_DEADLOCK_ADD_RULE:
            if (inBufferLength >= sizeof(DEADLOCK_ACCESS_RULE)) {
                PDEADLOCK_ACCESS_RULE rule = (PDEADLOCK_ACCESS_RULE)inBuffer;
                
                KeAcquireSpinLock(&gDeadlockData.RulesLock, &oldIrql);
                if (gDeadlockData.RuleCount < DEADLOCK_MAX_RULES) {
                    RtlZeroMemory(&gDeadlockData.Rules[gDeadlockData.RuleCount], sizeof(DEADLOCK_ACCESS_RULE));
                    
                    gDeadlockData.Rules[gDeadlockData.RuleCount].Path.Length = rule->Path.Length;
                    gDeadlockData.Rules[gDeadlockData.RuleCount].Path.MaximumLength = (USHORT)(rule->Path.Length + sizeof(WCHAR));
                    gDeadlockData.Rules[gDeadlockData.RuleCount].Path.Buffer = ExAllocatePoolWithTag(
                        NonPagedPool,
                        rule->Path.Length + sizeof(WCHAR),
                        DEADLOCK_MINIFILTER_POOL_TAG
                    );
                    
                    if (gDeadlockData.Rules[gDeadlockData.RuleCount].Path.Buffer != NULL) {
                        RtlCopyMemory(
                            gDeadlockData.Rules[gDeadlockData.RuleCount].Path.Buffer,
                            rule->Path.Buffer,
                            rule->Path.Length
                        );
                        gDeadlockData.Rules[gDeadlockData.RuleCount].Path.Buffer[rule->Path.Length / sizeof(WCHAR)] = L'\0';
                        
                        gDeadlockData.Rules[gDeadlockData.RuleCount].RuleType = rule->RuleType;
                        gDeadlockData.Rules[gDeadlockData.RuleCount].Enabled = rule->Enabled;
                        
                        gDeadlockData.RuleCount++;
                        KdPrint(("[DeadlockMinifilter] Rule added: %wZ\n", &gDeadlockData.Rules[gDeadlockData.RuleCount - 1].Path));
                    }
                }
                KeReleaseSpinLock(&gDeadlockData.RulesLock, oldIrql);
                status = STATUS_SUCCESS;
            } else {
                status = STATUS_INVALID_BUFFER_SIZE;
            }
            break;

        case IOCTL_DEADLOCK_CLEAR_RULES:
            KeAcquireSpinLock(&gDeadlockData.RulesLock, &oldIrql);
            for (i = 0; i < gDeadlockData.RuleCount; i++) {
                if (gDeadlockData.Rules[i].Path.Buffer != NULL) {
                    ExFreePoolWithTag(gDeadlockData.Rules[i].Path.Buffer, DEADLOCK_MINIFILTER_POOL_TAG);
                    gDeadlockData.Rules[i].Path.Buffer = NULL;
                }
            }
            gDeadlockData.RuleCount = 0;
            KeReleaseSpinLock(&gDeadlockData.RulesLock, oldIrql);
            KdPrint(("[DeadlockMinifilter] All rules cleared\n"));
            status = STATUS_SUCCESS;
            break;

        default:
            status = STATUS_INVALID_DEVICE_REQUEST;
            break;
        }
        break;

    default:
        status = STATUS_INVALID_DEVICE_REQUEST;
        break;
    }

    Irp->IoStatus.Status = status;
    Irp->IoStatus.Information = 0;
    IoCompleteRequest(Irp, IO_NO_INCREMENT);

    return status;
}
