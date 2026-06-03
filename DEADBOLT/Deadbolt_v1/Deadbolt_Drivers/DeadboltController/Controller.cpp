/*
    Deadbolt Endpoint Shield - User-Mode Controller
    Communicates with DeadboltMonitor.sys kernel driver
*/

#include <windows.h>
#include <stdio.h>
#include <tchar.h>

#define DEADBOLT_DEVICE_PATH L"\\\\.\\DeadboltMonitor"

#define IOCTL_DEADBOLT_START_MONITORING CTL_CODE(FILE_DEVICE_UNKNOWN, 0x800, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_DEADBOLT_STOP_MONITORING  CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_DEADBOLT_GET_STATUS         CTL_CODE(FILE_DEVICE_UNKNOWN, 0x802, METHOD_BUFFERED, FILE_ANY_ACCESS)

void PrintBanner()
{
    printf("========================================\n");
    printf("  DEADBOLT ENDPOINT SHIELD - DRIVER\n");
    printf("  User-Mode Controller\n");
    printf("========================================\n\n");
}

void PrintUsage()
{
    printf("Usage:\n");
    printf("  DeadboltController.exe [command]\n\n");
    printf("Commands:\n");
    printf("  start    - Start kernel-mode monitoring\n");
    printf("  stop     - Stop kernel-mode monitoring\n");
    printf("  status   - Get current driver status\n");
    printf("  help     - Show this help message\n\n");
}

int _tmain(int argc, _TCHAR* argv[])
{
    PrintBanner();

    HANDLE hDevice = CreateFile(
        DEADBOLT_DEVICE_PATH,
        GENERIC_READ | GENERIC_WRITE,
        0,
        NULL,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        NULL
    );

    if (hDevice == INVALID_HANDLE_VALUE) {
        printf("[ERROR] Could not open DeadboltMonitor driver!\n");
        printf("        Error code: %d\n", GetLastError());
        printf("\nMake sure the driver is loaded and running!\n");
        printf("Use 'sc start DeadboltMonitor' to start it.\n");
        return 1;
    }

    printf("[OK] Successfully connected to DeadboltMonitor driver!\n\n");

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
            printf("[OK] Monitoring started successfully!\n");
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
            printf("[OK] Monitoring stopped successfully!\n");
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
            printf("[OK] Driver status: %s\n", isActive ? "ACTIVE" : "INACTIVE");
        } else {
            printf("[ERROR] Failed to get status! Error: %d\n", GetLastError());
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
