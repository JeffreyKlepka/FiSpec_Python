/**
  * Copyright (c) 2020 FiSens GmbH
  * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
  * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
  * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <windows.h>

int main()
{
    /* Windows COM-Port */
    HANDLE comPort;
    DWORD read_write_length;
    int portNo = 23;
    char portName[32];
    int n;
    /* Windows COM-Port */

    /* Buffer for send/receive */
    char send[32];
    char receive[1024] = {0};
    char int_buf[12];
    /* Buffer for send/receive */

    /* Open COM-Port */
    sprintf(portName, "\\\\.\\COM%d", portNo);
    comPort = CreateFile(portName, GENERIC_READ|GENERIC_WRITE, 0, 0, OPEN_EXISTING, 0, 0);

    if(comPort == INVALID_HANDLE_VALUE)
    {
        printf("\terror: COM%d is not available. \n", portNo);
        return -1;
    }
    /* Open COM-Port */

    /* COM-Port configuration */
    DCB dcbSerialParameters = {0};
    dcbSerialParameters.DCBlength = sizeof(dcbSerialParameters);

    if(!GetCommState(comPort, &dcbSerialParameters))
    {
        printf("Error");
    }

    dcbSerialParameters.BaudRate = 3000000;
    dcbSerialParameters.ByteSize = 8;
    dcbSerialParameters.StopBits = ONESTOPBIT;
    dcbSerialParameters.Parity   = NOPARITY;

    if(!SetCommState(comPort, &dcbSerialParameters))
    {
        printf("Unable to set serial port settings\n");
    }
    /* COM-Port configuration */

    /* Timeout configuration */
    COMMTIMEOUTS timeouts = {0};

    timeouts.ReadIntervalTimeout = 50;
    timeouts.ReadTotalTimeoutConstant = 50;
    timeouts.ReadTotalTimeoutMultiplier = 10;
    timeouts.WriteTotalTimeoutConstant = 50;
    timeouts.WriteTotalTimeoutMultiplier = 10;

    if(!SetCommTimeouts(comPort, &timeouts))
    {
        printf("Error setting timeouts\n");
    }
    /* Timeout configuration */

    /* COM-Port is open */
    printf("COM%d opened successfully\n", portNo);
    /* COM-Port is open */

    /* Connect to device */
    _Bool device_available = 0;
    while(!device_available)
    {
        printf("Connecting...\n");
        /* Send command "?>" */
        strcpy(send,"?>");
        n = strlen(send);
        WriteFile(comPort, send, n, &read_write_length, 0);
        /* Send command "?>" */

        /* Receive data */
        strset(receive, 0);
        Sleep(100);
        ReadFile(comPort, receive, sizeof(receive), &read_write_length, 0);
        /* Receive data */

        if(read_write_length > 0)
        {
            if(strncmp(receive, "FiSpec FBG X100", 15) == 0) {device_available = 1;}
            else if(strncmp(receive, "FiSpec FBG X150", 15) == 0) {device_available = 1;}
            else {device_available = 0;}
        }
    }
    printf("Connected to: %s", receive);
    /* Connect to device */

    /* Configuring the device */
    /* Set active channels */
    int FBG_count = 4;
    int FBG_wavelength[4] = {8200000, 8300000, 8400000, 8500000};
    int FBG_halfwidth = 15000;
    for(int i=0; i<FBG_count; i++)
    {
        strcpy(send,"Ke,");
        sprintf(int_buf, "%d", i);
        strcat(send,int_buf);
        strcat(send,",");
        sprintf(int_buf, "%d", FBG_wavelength[i]-FBG_halfwidth);
        strcat(send,int_buf);
        strcat(send,",");
        sprintf(int_buf, "%d", FBG_wavelength[i]+FBG_halfwidth);
        strcat(send,int_buf);
        strcat(send,">");
        n = strlen(send);
        WriteFile(comPort, send, n, &read_write_length, 0);
        Sleep(10);
    }
    /* Set active channels */

    /* Set quantity of active FBG */
    strcpy(send,"KA,");
    sprintf(int_buf, "%d", FBG_count);
    strcat(send,int_buf);
    strcat(send,">");
    n = strlen(send);
    WriteFile(comPort, send, n, &read_write_length, 0);
    Sleep(10);
    /* Set quantity of active FBG */

    /* Set integration time */
    int integration_time = 50000;
    strcpy(send,"iz,");
    sprintf(int_buf, "%d", integration_time);
    strcat(send,int_buf);
    strcat(send,">");
    n = strlen(send);
    WriteFile(comPort, send, n, &read_write_length, 0);
    Sleep(10);
    /* Set integration time */

    /* LED on */
    strcpy(send,"LED,1>");
    n = strlen(send);
    WriteFile(comPort, send, n, &read_write_length, 0);
    Sleep(10);
    /* LED on */

    /* Starting internal measurements */
    strcpy(send,"a>");
    n = strlen(send);
    WriteFile(comPort, send, n, &read_write_length, 0);
    Sleep(10);
    /* Starting internal measurements */
    /* Configuring the device */

    /* Repeat measurements */
    int FBG_peak[4] = {8200000, 8300000, 8400000, 8500000};
    int FBG_ampl[4] = {0, 0, 0, 0};
    strcpy(send,"P>");
    n = strlen(send);
    while(1)
    {
        /* Send command "P>" */
        WriteFile(comPort, send, n, &read_write_length, 0);
        Sleep(10);
        /* Send command "P>" */

        /* Receive data */
        strset(receive, 0);
        ReadFile(comPort, receive, sizeof(receive), &read_write_length, 0);
        /* Receive data */

        /* If end marker is recognized, display the data with timestamps */
        if(receive[read_write_length-4] == 'E' &&
           receive[read_write_length-3] == 'n' &&
           receive[read_write_length-2] == 'd' &&
           receive[read_write_length-1] == 'e')
        {
            printf("\n%d", (int)time(NULL));
            for(int i=0;i<FBG_count;i++)
            {
                FBG_peak[i] = (unsigned char)receive[8*i] + 256*(unsigned char)receive[8*i + 1] + 65536*(unsigned char)receive[8*i + 2] + 16777216*(unsigned char)receive[8*i + 3];
                FBG_ampl[i] = (unsigned char)receive[8*i + 4] + 256*(unsigned char)receive[8*i + 5] + 65536*(unsigned char)receive[8*i + 6] + 16777216*(unsigned char)receive[8*i + 7];
                printf(",%d,%d", FBG_peak[i], FBG_ampl[i]);
            }
        }
        /* If end marker is recognized, display the data  with timestamps */

        /* Wait twice the integration time (converted to ms) */
        Sleep(integration_time/500);
        /* Wait twice the integration time (converted to ms) */
    }
    /* Repeat measurements */

    /* Stop internal measurements */
    strcpy(send,"o>");
    n = strlen(send);
    WriteFile(comPort, send, n, &read_write_length, 0);
    Sleep(10);
    /* Stop internal measurements */

    /* LED off */
    strcpy(send,"LED,0>");
    n = strlen(send);
    WriteFile(comPort, send, n, &read_write_length, 0);
    Sleep(10);
    /* LED off */

    /* Close COM-Port */
    CloseHandle(comPort);
    /* Close COM-Port */

    return 0;
}
