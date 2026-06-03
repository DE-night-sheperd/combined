/*
    Deadbolt Endpoint Shield - FULL EDR Controller
    Communicates with DeadboltEDR.sys kernel driver
*/

#include <windows.h>
#include <stdio.h>
#include <tchar.h>
#include <time.h>

#define DEADBOLT_EDR_DEVICE_PATH L"\\\\.\\DeadboltEDR"

#define IOCTL_DEADBOLT_START_MONITORING CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_DEADBOLT_STOP_MONITORING  CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_DEADBOLT_GET_STATUS         CTL_CODE(FILE_DEVICE_UNKNOWN, 0x802, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_DEADBOLT_GET_EVENTS         CTL_CODE(FILE_DEVICE_UNKNOWN, 0x803, METHOD_BUFFERED, FILE_ANY_ACCESS)

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

void PrintBanner()
{
    printf("========================================\n");
    printf("  DEADBOLT ENDPOINT SHIELD - FULL EDR\n");
    printf("  User-Mode Controller\n");
    printf("========================================\n\n");
}

void PrintUsage()
{
    printf("Usage:\n");
    printf("  EDRController.exe [command]\n\n");
    printf("Commands:\n");
    printf("  start    - Start full EDR monitoring\n");
    printf("  stop     - Stop full EDR monitoring\n");
    printf("  status   - Get current driver status\n");
    printf("  events   - Get and display events\n");
    printf("  help     - Show this help message\n\n");
}

const char* GetEventTypeName(DEADBOLT_EVENT_TYPE type)
{
    switch (type) {
        case EventTypeProcessCreate: return "PROCESS CREATE";
        case EventTypeProcessExit: return "PROCESS EXIT";
        case EventTypeThreadCreate: return "THREAD CREATE";
        case EventTypeThreadExit: return "THREAD EXIT";
        case EventTypeImageLoad: return "IMAGE LOAD";
        case EventTypeRegistryCreateKey: return "REG CREATE KEY";
        case EventTypeRegistryDeleteKey: return "REG DELETE KEY";
        case EventTypeRegistrySetValue: return "REG SET VALUE";
        case EventTypeRegistryDeleteValue: return "REG DELETE VALUE";
        default: return "UNKNOWN";
    }
}

void PrintEvent(PDEADBOLT_EVENT event)
{
    SYSTEMTIME st;
    FILETIME ft;
    ft.dwLowDateTime = event->Timestamp.LowPart;
    ft.dwHighDateTime = event->Timestamp.HighPart;
    FileTimeToSystemTime(&ft, &st);

    printf("[%04d-%02d-%02d %02d:%02d:%02d.%03d] ",
           st.wYear, st.wMonth, st.wDay,
           st.wHour, st.wMinute, st.wSecond, st.wMilliseconds);
    
    printf("%-16s ", GetEventTypeName(event->EventType));
    printf("PID: %6lu ", (ULONG)event->ProcessId);
    
    if (event->ParentProcessId != NULL) {
        printf("PPID: %6lu ", (ULONG)event->ParentProcessId);
    }
    if (event->ThreadId != NULL) {
        printf("TID: %6lu ", (ULONG)event->ThreadId);
    }
    if (event->ImageName[0] != L'\0') {
        printf("Image: %ws ", event->ImageName);
    }
    if (event->Details[0] != L'\0') {
        printf("Details: %ws", event->Details);
    }
    printf("\n");
}

int _tmain(int argc, _TCHAR* argv[])
{
    PrintBanner();

    HANDLE hDevice = CreateFile(
        DEADBOLT_EDR_DEVICE_PATH,
        GENERIC_READ | GENERIC_WRITE,
        0,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (hDevice == INVALID_HANDLE_VALUE) {
        printf("[ERROR] Could not open DeadboltEDR driver!\n");
        printf("        Error code: %d\n", GetLastError());
        printf("\nMake sure the driver is loaded and running!\n");
        printf("Use 'sc start DeadboltEDR' to start it.\n");
        return 1;
    }

    printf("[OK] Successfully connected to DeadboltEDR driver!\n\n");

    if (argc < 2) {
        PrintUsage();
        CloseHandle(hDevice);
        return 0;
    }

    DWORD bytesReturned = 0;
    BOOL result = FALSE;
    TCHAR* command = argv[1];

    if (_tcscmp(command, _T("start")) == 0) {
        printf("[*] Sending START_MONITORING command...\n");
        result = DeviceIoControl(
            hDevice,
            IOCTL_DEADBOLT_START_MONITORING,
            NULL,
            0,
            NULL,
            0,
            &bytesReturned,
            NULL
        );

        if (result) {
            printf("[OK] FULL EDR monitoring started successfully!\n");
        } else {
            printf("[ERROR] Failed to start monitoring! Error: %d\n", GetLastError());
        }

    } else if (_tcscmp(command, _T("stop")) == 0) {
        printf("[*] Sending STOP_MONITORING command...\n");
        result = DeviceIoControl(
            hDevice,
            IOCTL_DEADBOLT_STOP_MONITORING,
            NULL,
            0,
            NULL,
            0,
            &bytesReturned,
            NULL
        );

        if (result) {
            printf("[OK] FULL EDR monitoring stopped successfully!\n");
        } else {
            printf("[ERROR] Failed to stop monitoring! Error: %d\n", GetLastError());
        }

    } else if (_tcscmp(command, _T("status")) == 0) {
        printf("[*] Sending GET_STATUS command...\n");
        BOOLEAN isActive = FALSE;
        result = DeviceIoControl(
            hDevice,
            IOCTL_DEADBOLT_GET_STATUS,
            NULL,
            0,
            &isActive,
            sizeof(isActive),
            &bytesReturned,
            NULL
        );

        if (result) {
            printf("[OK] Driver status: %s\n", isActive ? "ACTIVE (Full EDR Mode)" : "INACTIVE");
        } else {
            printf("[ERROR] Failed to get status! Error: %d\n", GetLastError());
        }

    } else if (_tcscmp(command, _T("events")) == 0) {
        printf("[*] Sending GET_EVENTS command...\n");
        BYTE buffer[65536];
        result = DeviceIoControl(
            hDevice,
            IOCTL_DEADBOLT_GET_EVENTS,
            NULL,
            0,
            buffer,
            sizeof(buffer),
            &bytesReturned,
            NULL
        );

        if (result) {
            ULONG eventCount = bytesReturned / sizeof(DEADBOLT_EVENT);
            printf("[OK] Received %lu events:\n\n", eventCount);
            
            PDEADBOLT_EVENT events = (PDEADBOLT_EVENT)buffer;
            for (ULONG i = 0; i < eventCount; i++) {
                PrintEvent(&events[i]);
            }
        } else {
            printf("[ERROR] Failed to get events! Error: %d\n", GetLastError());
        }

    } else if (_tcscmp(command, _T("help")) == 0) {
        PrintUsage();

    } else {
        printf("[ERROR] Unknown command: %ls\n", command);
        PrintUsage();
    }

    CloseHandle(hDevice);
    printf("\nDone.\n");
    return 0;
}
