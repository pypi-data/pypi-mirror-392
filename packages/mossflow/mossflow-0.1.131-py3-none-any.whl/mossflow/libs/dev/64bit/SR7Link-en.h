#ifndef SR7LINK__H
#define SR7LINK__H

#include <stdio.h>

#ifdef WIN32
#define  SR7_IF_API __declspec(dllexport)
#else
#define  SR7_IF_API extern
#endif

typedef void * SR7IF_Data;
typedef void * SR7IF_UserData;

/// \brief                      	  Callback function interface for high speed data communication. 
///	\param pBuffer     [in]           A pointer to the buffer where the summary data is stored.
///	\param dwSize      [in]           The number of bytes per unit (row).   
///	\param dwCount     [in]           The number of units of memory stored in the pBuffer.   
///	\param dwNotify    [in]           Notifications such as interruption or batch end.
///	\param dwDeviceId  [in]           The ID(0-63) of control device that is executing the callback function.  
///
typedef void (*SR7IF_CALLBACK)(char* pBuffer, unsigned int dwSize, unsigned int dwCount, unsigned int dwNotify, unsigned int dwDeviceId);


/// \brief                      	  Callback function interface for each batch.
///	\param info  	   [in]           A pointer to the buffer contain the info of the structure of SR7IF_STR_CALLBACK_INFO.
///	\param data        [in]           The pointer of internal data communication.
///
typedef void (*SR7IF_BatchOneTimeCallBack)(const void *info, const SR7IF_Data *data);

/// \brief                      	  Callback function interface for the device goes offline or the device license has expired. 
///	\param dwDeviceId  [in]           The ID(0-63) of control device.
///	\param cmd         [in]           error code value(Value is not 0).
///
typedef void (*TcpConnectFunc)(int dwDeviceId, int cmd);

typedef struct {
    unsigned char	abyIpAddress[4];
} SR7IF_ETHERNET_CONFIG;

#define SR7IF_ERROR_NOT_FOUND                     (-999)                  // Function/device does not exist.
#define SR7IF_ERROR_COMMAND                       (-998)                  // This command is not supported. 
#define SR7IF_ERROR_PARAMETER                     (-997)                  // parameter error.  
#define SR7IF_ERROR_UNIMPLEMENTED                 (-996)                  // Function not implemented.    
#define SR7IF_ERROR_HANDLE                        (-995)                  // Invalid handle. 
#define SR7IF_ERROR_MEMORY                        (-994)                  // Memory (overflow/definition) error.   
#define SR7IF_ERROR_TIMEOUT                       (-993)                  // Operation timeout.   
#define SR7IF_ERROR_DATABUFFER                    (-992)                  // The data buffer is too small.   
#define SR7IF_ERROR_STREAM                        (-991)                  // Data flow error.   
#define SR7IF_ERROR_CLOSED                        (-990)                  // The interface is closed and unavailable.
#define SR7IF_ERROR_VERSION                       (-989)                  // The current version does not support.
#define SR7IF_ERROR_ABORT                         (-988)                  // The operation is terminated, for example: the software is terminated, the connection is closed, or the connection is interrupted when batch processing.
#define SR7IF_ERROR_ALREADY_EXISTS                (-987)                  // Operation conflicts with current configuration.   
#define SR7IF_ERROR_FRAME_LOSS                    (-986)                  // Batch processing frame loss.   
#define SR7IF_ERROR_ROLL_DATA_OVERFLOW            (-985)                  // Infinite loop overflow exception.   
#define SR7IF_ERROR_ROLL_BUSY                     (-984)                  // Infinite loop reading data busy.  
#define SR7IF_ERROR_MODE                          (-983)                  // Batch processing mode conflict. 
#define SR7IF_ERROR_CAMERA_NOT_ONLINE             (-982)                  // The camera (sensor head) is not online.  
#define SR7IF_ERROR                               (-1)                    // Common errors, such as link failure, setting failure, and data acquisition failure. 
#define SR7IF_NORMAL_STOP                         (-100)                  // Stop normally; For example, external I/O stop batch processing operations. 
#define SR7IF_OK                                  (0)                     // Succeed/proper operation.   

#ifdef __cplusplus
extern "C" {
#endif

/********************************************/
// [in]: Indicates  the parameter is an input parameter
// [out]: Indicates the parameter is an output parameter
/*******************************************/

///
/// \brief SR7IF_EthernetOpen   		Establish a connection so that the device can communicate with the controller connected via Ethernet.
/// \param lDeviceId       [in]      	Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param pEthernetConfig [in]    		Ethernet communication settings.  
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_EthernetOpen(unsigned int lDeviceId, SR7IF_ETHERNET_CONFIG* pEthernetConfig);


/// \brief SR7IF_EthernetOpenEx 		Connect the camera via Ethernet and support offline callback.
/// \param lDeviceId        [in]     	Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param pEthernetConfig  [in]    	Ethernet communication settings.   
/// \param timeOut          [in]   		Search time (ms), minimum value is 100. 
/// \param fun				[in]		Device offline Callback function.	
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_EthernetOpenExt(unsigned int lDeviceId, SR7IF_ETHERNET_CONFIG* pEthernetConfig, int timeOut = 2000, TcpConnectFunc fun = NULL);


/// \brief SR7IF_CommClose      		Disconnect the Ethernet connection. 
/// \param lDeviceId        [in]    	Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_CommClose(unsigned int lDeviceId);


/// \brief SR7IF_SwitchProgram  	 Switched camera parameter Settings. 
/// \param lDeviceId        [in]     Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param No:              [in]     Task parameter list number ranging 0-63. 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_SwitchProgram(unsigned int lDeviceId, int No);


/// \brief SR7IF_GetOnlineCameraB   Get information of whether the B camera is online
/// \param lDeviceId        [in]   	Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \return
///     <0:                     -982:Sensor head B is offline.
///                             Other: Obtaining failed.  
///     =0:                     Sensor head B is online. 
///
SR7_IF_API int SR7IF_GetOnlineCameraB(unsigned int lDeviceId);


/// \brief SR7IF_StartMeasure   	Start batch processing and execute batch processing program immediately.
/// \param lDeviceId       [in]     Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param Timeout         [in]     In the case of acyclic acquisition, the timeout period (unit: ms),-1 indicates infinite waiting. Cycle Mode This parameter can be set to -1. 
/// \return
///     <0:                     failure
///     =0:                     succeed
///
SR7_IF_API int SR7IF_StartMeasure(unsigned int lDeviceId, int Timeout = 50000);


/// \brief SR7IF_StartIOTriggerMeasure  Start batch: Hardware I/O triggers batch processing. 
/// \param lDeviceId       [in]     	Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param Timeout         [in]     	In the case of acyclic acquisition, the timeout period (unit: ms),-1 indicates infinite waiting. Cycle Mode This parameter can be set to -1. 
/// \param restart         [in]     	Reserved interface,the default is 0.
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_StartIOTriggerMeasure(unsigned int lDeviceId, int Timeout = 50000, int restart = 0);


/// \brief SR7IF_StopMeasure    	Stop batch processing.  
/// \param lDeviceId            	Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_StopMeasure(unsigned int lDeviceId);


/// \brief SR7IF_ReceiveData    	Obtain data in blocking mode.
/// \param lDeviceId      [in]      Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param DataObj        [out]     The pointer of return data. 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_ReceiveData(unsigned int lDeviceId, SR7IF_Data DataObj);


/// \brief SR7IF_ProfilePointSetCount   Gets the currently set number of batch rows.
/// \param lDeviceId     [in]       	Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param DataObj       [in]       	Reserved, set to NULL. 
/// \return                     		Returns the setting number of batch rows. 
///
SR7_IF_API int SR7IF_ProfilePointSetCount(unsigned int lDeviceId, const SR7IF_Data DataObj);


/// \brief SR7IF_ProfilePointCount 	Obtain the number of rows actually obtained in the batch. 
/// \param lDeviceId     [in]       Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param DataObj       [in]       Reserved, set to NULL. 
/// \return                     	Returns the number of rows actually obtained in the batch. 
///
SR7_IF_API int SR7IF_ProfilePointCount(unsigned int lDeviceId, const SR7IF_Data DataObj);


/// \brief SR7IF_ProfileDataWidth Get the width of one profile data.  
/// \param lDeviceId     [in]     Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param DataObj       [in]     Reserved, set to NULL. 
/// \return                       Return data width (unit:pixel).  
///
SR7_IF_API int SR7IF_ProfileDataWidth(unsigned int lDeviceId, const SR7IF_Data DataObj);


/// \brief SR7IF_ProfileData_XPitch Get the X-direction data spacing.
/// \param lDeviceId    [in]        Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param DataObj      [in]        Reserved, set to NULL. 
/// \return                     	Returns the point spacing of each two data points in the x direction.
///
SR7_IF_API double SR7IF_ProfileData_XPitch(unsigned int lDeviceId, const SR7IF_Data DataObj);


/// \brief SR7IF_GetEncoder     	Get encoder value(32bit).
/// \param lDeviceId    [in]        Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param DataObj      [in]        Reserved, set to NULL.  
/// \param Encoder      [out]       The pointer to store encoder data,In the case of dual cameras, the data order is alternating A/B cameras. 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetEncoder(unsigned int lDeviceId, const SR7IF_Data DataObj, unsigned int *Encoder);


/// \brief SR7IF_GetBatchEncoder64Bit   Get encoder value(64bit).
/// \param lDeviceId    [in]        	Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param DataObj      [in]        	Reserved, set to NULL.  
/// \param Encoder      [out]        	The pointer to store encoder data,In the case of dual cameras, the data order is alternating A/B cameras. 
/// \return
///     <0:                     failure.
///     >=0:                    Returns the number of encoder data.
///
SR7_IF_API int SR7IF_GetBatchEncoder64Bit(unsigned int lDeviceId, const SR7IF_Data DataObj, unsigned long long *Encoder);


/// \brief SR7IF_GetEncoderContiune Obtain the encoder value(32bit) in non-blocking mode 
/// \param lDeviceId   [in]         Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param DataObj     [in]         Reserved, set to NULL. 
/// \param Encoder     [out]        The pointer to store encoder data,In the case of dual cameras, the data order is alternating A/B cameras. 
/// \param GetCnt      [in]         The data length(line number) needs to be obtained. 
/// \return
///     <0:                     failure.
///     >=0:                    The actual length(the number of encoder data) of the returned data. 
///
SR7_IF_API int SR7IF_GetEncoderContiune(unsigned int lDeviceId, const SR7IF_Data DataObj, unsigned int *Encoder, unsigned int GetCnt);


/// \brief SR7IF_GetProfileData 	Obtain profile data in blocking mode. 
/// \param lDeviceId   [in]         Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param DataObj     [in]         Reserved, set to NULL. 
/// \param Profile     [out]        The pointer of returned data,In the case of dual cameras, the data order is alternating A/B cameras. 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetProfileData(unsigned int lDeviceId, const SR7IF_Data DataObj, int *Profile);


/// \brief SR7IF_GetLaserWidthData  Obtain laser width data(Only supported by SRI device). 
/// \param lDeviceId   [in]         Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param DataObj     [in]         Reserved, set to NULL. 
/// \param widthData   [out]        The pointer of returned data,In the case of dual cameras, the data order is alternating A/B cameras(an outline data).
/// \param GetCnt      [in]         The data length (line number )needs to be obtained. 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetLaserWidthData(unsigned int lDeviceId, const SR7IF_Data DataObj, unsigned char *widthData, int GetCnt = 0);


/// \brief SR7IF_GetProfileContiuneData  Obtain profile data in non-blocking mode. 
/// \param lDeviceId   [in]          	 Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param DataObj     [in]         	 Reserved, set to NULL.
/// \param Profile     [out]         	 The pointer of returned data,In the case of dual cameras, the data order is alternating A/B cameras.
/// \param GetCnt      [in]         	 The data length needs to be obtained.
/// \return
///     <0:                     failure.
///     >=0:                    The data length needs to be obtained. 
///Q
SR7_IF_API int SR7IF_GetProfileContiuneData(unsigned int lDeviceId, const SR7IF_Data DataObj, int *Profile, unsigned int GetCnt);


/// \brief SR7IF_GetIntensityData   Obtain intensity data in blocking mode.
/// \param lDeviceId   [in]         Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param DataObj     [in]         Reserved, set to NULL.  
/// \param Intensity   [out]        The pointer of returned data,In the case of dual cameras, the data order is alternating A/B cameras. 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetIntensityData(unsigned int lDeviceId, const SR7IF_Data DataObj, unsigned char *Intensity);


/// \brief SR7IF_GetIntensityContiuneData   Obtain intensity data in non-blocking mode.
/// \param lDeviceId   [in]                 Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param DataObj     [in]                 Reserved, set to NULL.
/// \param Intensity   [out]                The pointer of returned data,In the case of dual cameras, the data order is alternating A/B cameras.
/// \param GetCnt      [in]                 The data length needs to be obtained.
/// \return
///     <0:                     failure.
///     >=0:                    The data length needs to be obtained.  
///
SR7_IF_API int SR7IF_GetIntensityContiuneData(unsigned int lDeviceId, const SR7IF_Data DataObj, unsigned char *Intensity, unsigned int GetCnt);


/// \brief SR7IF_GetBatchRollData  	Get data in infinite loop mode.  
/// \param lDeviceId   [in]         Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param DataObj     [in]         Reserved, set to NULL.  
/// \param Profile     [out]        The pointer to profile data,In the case of dual cameras, the data order is alternating A/B cameras. 
/// \param Intensity   [out]        The pointer to intensity data,In the case of dual cameras, the data order is alternating A/B cameras. 
/// \param Encoder     [out]        The pointer to encoder data,In the case of dual cameras, the data order is alternating A/B cameras. 
/// \param FrameId     [out]        The pointer to frame id data,In the case of dual cameras, the data order is alternating A/B cameras. 
/// \param FrameLoss   [out]        The pointer to the number of frames dropped too fast in batch processing,In the case of dual cameras, the data order is alternating A/B cameras. 
/// \param GetCnt      [in]         The data length needs to be obtained. 
/// \return
///     <0:                     failure.
///     >=0:                    The data length needs to be obtained. 
///
SR7_IF_API int SR7IF_GetBatchRollData(unsigned int lDeviceId, const SR7IF_Data DataObj,
                                        int *Profile, unsigned char *Intensity, unsigned int *Encoder, long long *FrameId, unsigned int *FrameLoss,
                                        unsigned int GetCnt);



/// \brief SR7IF_SetBatchRollProfilePoint   Sets the number of rows for a non-terminating loop.
///                                   It is used for the number of lines required (50-65535) and the collection speed is fast. Insufficient transmission speed leads to coverage problems.
///                                   The function is set at least once during initialization and the parameter is not saved after power failure.
/// \param lDeviceId  [in]            Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param DataObj    [in]            Reserved, set to NULL.  
/// \param points     [in]            Set the number of rows，Range (0: No terminated loop,≥15000: Set number of terminated rows, others are not valid). Note: 1. The number of lines set by this interface is notsaved
///    after power off ;2. The number of rows defaults to 0.
/// \return
///     <0:                       failure.
///     >=0:                      succeed.
///
SR7_IF_API int SR7IF_SetBatchRollProfilePoint(unsigned int lDeviceId, const SR7IF_Data DataObj, unsigned int points);


/// \brief SR7IF_GetBatchRollError   The non-terminating loop gets the calculated value of the data exception. 
/// \param lDeviceId  [in]           Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param EthErrCnt  [out]          Returns the number of errors caused by network transmission.
/// \param UserErrCnt [out]          Returns the number of errors caused by user fetch.
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetBatchRollError(unsigned int lDeviceId, int *EthErrCnt, int *UserErrCnt);



/// \brief SR7IF_RollDataCallback    Non-terminating loop callback function.
/// \param pProfileBuffer    [out]   The pointer to profile data. 
/// \param pIntensityBuffer  [out]   The pointer to intensity data.
/// \param pEncoder          [out]   The pointer to encoder data.
/// \param dwSize            [out]   The data width.
/// \param dwCount           [out]   The batch lines.
/// \param dwRet             [out]   Return value, to be used.
/// \param dwDeviceId        [in]    Corresponding controller(0-63). 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
typedef void (*SR7IF_RollDataCallback)(int* pProfileBuffer, unsigned char* pIntensityBuffer, unsigned int* pEncoder,
                                       unsigned int dwSize, unsigned int dwCount, int dwRet, unsigned int dwDeviceId);


/// \brief SR7IF_RollDataCallbackInitalize   Initialization in non-terminating loop callback mode. 
/// \param lDeviceId      [in]      Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param pCallBack      [in]      The pointer of non-terminating loop callback function. 
/// \param dwProfileCnt   [in]      Number of callback lines in a single call.
/// \param pCallBack      [in]      Timeout period for obtaining the number of callback lines (unit: ms), value less than 0 turns off timeout. 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_RollDataCallbackInitalize(unsigned int lDeviceId, SR7IF_RollDataCallback pCallBack, unsigned int dwProfileCnt, int Timeout);


/// \brief SR7IF_SetBatchCtrlByIO   Enabled the function of continued transmission.  
///                                 During the camera a batch processing, you can pause or continue the batch using the IO control. 
///                                 IO control uses pin 11 and pin 14 of the controller to work together. Pin 11 starts the level control mode and pin 14 controls to pause and continue batch processing. 
/// \param lDeviceId     [in]       Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param DataObj       [in]       Reserved, set to NULL.  
/// \param Enable        [in]       Function Enable 0: disabled 1: enabled.
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_SetBatchCtrlByIO(unsigned int lDeviceId, const SR7IF_Data DataObj, unsigned int Enable);


/// \brief SR7IF_GetError       	Obtain the system error message.
/// \param lDeviceId     [in]       Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param pbyErrCnt     [out]      Return the number of error codes.
/// \param pwErrCode     [out]      Return an error code pointer with an array size of 2048 recommended. 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetError(unsigned int lDeviceId, int *pbyErrCnt, int *pwErrCode);


/// \brief SR7IF_ClearError     Clear system errors on the controller. 
/// \param lDeviceId	[in]    Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param wErrCode		[out]   Error code for the error that needs to be resolved.
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_ClearError(unsigned int lDeviceId, unsigned short wErrCode);


/// \brief SR7IF_GetVersion     Gets the version number of the communication library currently in use. 
/// \return                     Return version information. 
///
SR7_IF_API const char *SR7IF_GetVersion();

///
/// \brief SR7IF_GetModels      Get camera model. 
/// \param lDeviceId   [in]     Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \return                     Returns the camera model. 
///
SR7_IF_API const char *SR7IF_GetModels(unsigned int lDeviceId);


/// \brief SR7IF_GetHeaderSerial   Get the camera head serial number. 
/// \param lDeviceId   [in]        Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param Head        [in]            0: Sensor head A 1: Sensor head B. 0：
/// \return
///     !=NULL:                 Returns the camera serial number string. 
///     =NULL:                  Failed, the corresponding header does not exist or the parameter is incorrect. 
///
SR7_IF_API const char *SR7IF_GetHeaderSerial(unsigned int lDeviceId, int Head);

/// \brief SR7IF_SetOutputPortLevel      Sets the controller output port level.
/// \param lDeviceId   [in]         	 Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param Port        [in]         	 Specifies the output port of the controller(Min:0,Max:7). 
/// \param Level       [in]              Specify the port output level,0/False: low; 1/True: high. 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_SetOutputPortLevel(unsigned int lDeviceId, unsigned int Port, bool Level);


/// \brief SR7IF_GetInputPortLevel      Read the controller input port level.
/// \param lDeviceId   [in]        		Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param Port        [in]             Specifies the output port of the controller, ranging from 0 to 7. 
/// \param Level       [out]            Returns the input level of the specified port, 0/False: low; 1/True: high.  
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetInputPortLevel(unsigned int lDeviceId, unsigned int Port, bool *Level);


/// \brief SR7IF_GetSingleProfile   Get the current outline (2.5D mode in EdgeImaging for non-batch processing). 
/// \param lDeviceId      [in]      Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param pProfileData   [out]     Returns a pointer to the profile. 
/// \param pEncoder       [out]     Returns a pointer to the encoder.
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetSingleProfile(unsigned int lDeviceId, int *pProfileData, unsigned int *pEncoder);


/// \brief SR7IF_SetSetting         Parameter settings
/// \param lDeviceId     [in]       Specify Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param Depth         [in]       The level of the value set
/// \param Type          [in]       Set type.-1: to set the current formula parameter 0x10-0x50: to set formula 0-63.
/// \param Category      [in]       Set the Category. 
/// \param Item          [in]       Set item.
/// \param Target[4]     [in]       Depending on the send/receive Settings, you may need to specify them accordingly. If no setting is required, set this parameter to 0.
/// \param pData         [in]       Sets the data to be written to the register. 
/// \param DataSize      [in]       Sets the length of the data(Byte count). 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_SetSetting(unsigned int lDeviceId, int Depth, int Type, int Category, int Item, int Target[4], void *pData, int DataSize);


/// \brief SR7IF_GetSetting     Gets the parameter value(note: Batch processing will be interrupted when the recipe number obtained is not the currently running recipe). 
/// \param lDeviceId     [in]   Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param Type          [in]   Obtain the type. -1: indicates that the current formula is obtained. Parameter 0x10-0x50: indicates that formula 0-63 is obtained.
/// \param Category      [in]   Specifies the category that needs to be obtained.
/// \param Item          [in]   Specifies the item that needs to be obtained. 
/// \param Target[4]     [in]   Depending on the send/receive Settings, you may need to specify them accordingly. If no setting is required, set this parameter to 0.   
/// \param pData         [out]  Returns the parameter pointer. 
/// \param DataSize      [in]   Specify the Parameter Length. 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetSetting(unsigned int lDeviceId, int Type, int Category, int Item, int Target[4], void *pData, int DataSize);


/// \brief SR7IF_ExportParameters   Export the current System configuration parameters(note：Only the parameters of the current task are exported).
/// \param lDeviceId      [in]      Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param size           [out]     Returns the size of the parameter list. 
/// \return
///     NULL:                   failure.
///     other:                   succeed.
///
SR7_IF_API const char *SR7IF_ExportParameters(unsigned int lDeviceId, unsigned int *size);


/// \brief SR7IF_LoadParameters  	 Import system configuration parameters and overwrite the current configuration parameters.
/// \param lDeviceId      [in]       Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param pSettingdata   [in]       Import a character pointer to a parameter table. 
/// \param size           [in]       Import the character pointer size of the parameter table.
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_LoadParameters(unsigned int lDeviceId, const char *pSettingdata, unsigned int size);


/// \brief SR7IF_GetLicenseKey      Gets the product Days remaining in use. 
/// \param lDeviceId       [in]     Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param RemainDay       [out]    Returns a pointer to the number of days remaining. 
/// \return
///     < 0:                     failure, parameter error, or product is not registered.  
///     >=0:                     succeed,  Returns the number of days remaining in service for the product.
///
SR7_IF_API int SR7IF_GetLicenseKey(unsigned int lDeviceId, unsigned short *RemainDay);


/// \brief SR7IF_GetCurrentEncoder   Reads the current encoder(32bit) value. 
/// \param lDeviceId       [in]     Specifies which communication device is used forcommunication,ranging from 0 to 63.  
/// \param value           [out]    Returns a pointer to the current encoder.    
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetCurrentEncoder(unsigned int lDeviceId, unsigned int *value);


/// \brief SR7IF_GetCurrentEncoder64Bit     Reads the current encoder(64bit) value.
/// \param lDeviceId       [in]             Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param value           [out]            Returns a pointer to the current encoder.
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetCurrentEncoder64Bit(unsigned int lDeviceId, unsigned long long *value);


/// \brief SR7IF_GetCameraTemperature   Read the camera temperature, Unit 0.01 degrees Celsius.
/// \param lDeviceId    [in]       	 	Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param tempA        [out]           Temperature of camera A; If -1000000 is returned, reading the temperature is not supported.  
/// \param tempB        [out]           Temperature of camera B; If -1000000 is returned, reading the temperature is not supported.  
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetCameraTemperature(unsigned int lDeviceId, int *tempA, int *tempB);


/// \brief SR7IF_GetCameraBoardTemperature   Read the temperature of camera mainboard (unit:  1 degree Celsius). 
/// \param lDeviceId     [in]       Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param tempA         [out]      Temperature of camera board A; If -1000000 is returned, reading the temperature is not supported.  
/// \param tempB         [out]      Temperature of camera board B; If -1000000 is returned, reading the temperature is not supported.  
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetCameraBoardTemperature(unsigned int lDeviceId, int *tempA, int *tempB);


typedef struct {
    int xPoints;                //Number of points in the x direction data. 
    int BatchPoints;            //Number of batch rows.
    unsigned int BatchTimes;    //Batch times.

    double xPixth;              //x direction point spacing.
    unsigned int startEncoder;  //Encoder value at the start of batch processing.
    int HeadNumber;             //Number of camera heads.
    int returnStatus;           //SR7IF_OK:  Normal batch processing
                                //SR7IF_NORMAL_STOP
                                //SR7IF_ERROR_ABORT
                                //SR7IF_ERROR_CLOSED
} SR7IF_STR_CALLBACK_INFO;

/// \brief SR7IF_SetBatchOneTimeDataHandler   Callback function registration interface,It is recommended to start another thread for processing after obtaining data (Obtaining data mode: batch processing once callback once).  
/// \param lDeviceId     [in]       Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param CallFunc      [in]       Callback function.  
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_SetBatchOneTimeDataHandler(unsigned int lDeviceId, SR7IF_BatchOneTimeCallBack CallFunc);


/// \brief SR7IF_SetBatchOneTimeDataValidRange   Set valid data range of callback onetime(Get data mode: batch once callback once).
/// \param lDeviceId    [in]        Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param Left         [in]        Left cut quantity.  
/// \param Right        [in]        Right cut quantity. 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_SetBatchOneTimeDataValidRange(unsigned int lDeviceId, unsigned int Left, unsigned int Right);


/// \brief SR7IF_StartMeasureWithCallback   Start batch processing (Get data mode: batch once callback once). 
/// \param lDeviceId      [in]          Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param ImmediateBatch [in]          0: Batch starts immediately Non-0: Wait for signals from external hardware to start batch processing.
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_StartMeasureWithCallback(int iDeviceId, int ImmediateBatch);


/// \brief SR7IF_TriggerOneBatch    The batch process is triggered by the software.
/// \param lDeviceId     [in]       Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_TriggerOneBatch(int iDeviceId);


/// \brief SR7IF_GetBatchProfilePoint   Get the height data in the callback function. 
/// \param DataIndex    [in]         	An internal data communication pointer, passed in by a callback function. 
/// \param Head         [in]         	0: Sensor head A 1: Sensor head B. 
/// \return
///     !=NULL:                 Returns the data pointer. 
///     =NULL:                  Failed, no data or corresponding header does not exist. 
///
SR7_IF_API const int *SR7IF_GetBatchProfilePoint(const SR7IF_Data *DataIndex, int Head);


/// \brief SR7IF_GetBatchIntensityPoint     Get intensity data in callback function.
/// \param DataIndex    [in]         		An internal data communication pointer, passed in by a callback function.  
/// \param Head         [in]         		0: Sensor head A 1: Sensor head B.  
/// \return
///     !=NULL:                 Returns the data pointer. 
///     =NULL:                  Failed, no data or corresponding header does not exist. 
///
SR7_IF_API const unsigned char *SR7IF_GetBatchIntensityPoint(const SR7IF_Data *DataIndex, int Head);


/// \brief SR7IF_GetBatchEncoderPoint   Get the encoder data in the callback function.  
/// \param DataIndex   [in]          	An internal data communication pointer, passed in by a callback function.  
/// \param Head        [in]          	0: Sensor head A 1: Sensor head B. 
/// \return
///     !=NULL:                 Returns the data pointer. 
///     =NULL:                  Failed, no data or corresponding header does not exist. 
///
SR7_IF_API const unsigned int *SR7IF_GetBatchEncoderPoint(const SR7IF_Data *DataIndex, int Head);

///
/// \brief SR7IF_SearchOnline    	Query online device,The search may fail when EdgeImaging is used, when other programs call this interface, or when it is blocked by a firewall.
/// \param ReadNum     [out]        Number of cameras found online. 
/// \param timeOut     [in]         Search timeout (ms), minimum 500.  
/// \return
///     !=NULL:                 SR7IF_ETHERNET_CONFIG*：Returns the IP address pointer of the device that was searched.   
///     =NULL:                  Failed. Parameter error or no online camera.  
///
SR7_IF_API SR7IF_ETHERNET_CONFIG *SR7IF_SearchOnline(int *ReadNum, int timeOut);

///
/// \brief SR7IF_SetMultiEncoderInterval   Set the trigger interval for multiple sets of encoders.  
/// \param lDeviceId     [in]       The id of controller (value range:0-63) 
/// \param DataObj       [in]       Reserved, set to NULL.   
/// \param enable        [in]       Whether to enable multiple groups of encoders trigger interval, 1: enable; 0: Off.
/// \param Point[1-8]    [in]       Specifies the number of start frames for interval to take effect. For example, if Point1 is 100 and Interval1 is 10, then
/// Indicates that the number of frames of the batch starts from the 100th line, after which the encoder trigger interval of the scan is 10;
/// Parameter valid range: 0~15000; 0: indicates that the current group is invalid.
/// Note: When setting multiple groups, the number of numbered frames must be greater than the number of numbered frames (unless the number of frames is 0).
/// Point1<Point2<... <point8.     
/// \param Interval[1-8] [in]       Specifies the encoder trigger interval during a batch scan. the value ranges from 1 to 10000.    
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_SetMultiEncoderInterval(unsigned int lDeviceId, const SR7IF_Data DataObj, unsigned int enable,
                                  unsigned short Point1, unsigned short Interval1,
                                  unsigned short Point2, unsigned short Interval2,
                                  unsigned short Point3, unsigned short Interval3,
                                  unsigned short Point4, unsigned short Interval4,
                                  unsigned short Point5, unsigned short Interval5,
                                  unsigned short Point6, unsigned short Interval6,
                                  unsigned short Point7, unsigned short Interval7,
                                  unsigned short Point8, unsigned short Interval8);



/// \brief SR7IF_GetTimeStamp   Controller running time after this power-on.   
/// \param lDeviceId    [in]    Specifies which communication device is used forcommunication,ranging from 0 to 63. 
/// \param DataObj      [in]    Reserved, set to NULL. 
/// \param TimeStamp    [out]   Return running time (in seconds).  
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetTimeStamp(unsigned int lDeviceId, const SR7IF_Data DataObj, unsigned int *TimeStamp);


/// \brief SR7IF_GetStartIOTriggerCount   The camera starts batch processing I/O to be triggered by the number of counters, counting from power-on. 
/// \param lDeviceId    [in]    Specifies which communication device is used forcommunication,ranging from 0 to 63.  
/// \param DataObj      [in]    Reserved, set to NULL.  
/// \param TriggerCount [out]   Return trigger number. 
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetStartIOTriggerCount(unsigned int lDeviceId, const SR7IF_Data DataObj, unsigned int *pTriggerCount);


/// \brief SR7IF_GetBatchStatus         Querying batch processing status.
/// \param lDeviceId    [in]            Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param Status       [out]        	Batch status 1: The batch is being processed. 0: The batch is complete.   
/// \return
///     <0:                     failure.
///     =0:                     succeed.
///
SR7_IF_API int SR7IF_GetBatchStatus(unsigned int lDeviceId, int * Status);


/// \brief SR7IF_GetActivityProgramNo   Gets the current recipe serial number
/// \param lDeviceId	 [in]           Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param ProgramNo	 [in]           Parameter formula number, ranging from 0 to 63.
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_GetActivityProgramNo(unsigned int lDeviceId, int *ProgramNo);


/// \brief SR7IF_SetNetworkParam            Set controller network parameters.
/// \param lDeviceId	[in]                Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param ip			[in]				IP address.
/// \param netmask		[in]				Subnet mask.
/// \param gateway		[in]				Default gateway.
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_SetNetworkParam(unsigned int lDeviceId, const char *ip, const char *netmask, const char *gateway);


///
/// \brief SR7IF_Get16BitScale			Get 16bit height data physical unit
/// \param lDeviceId					Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param Scale						unit(mm)
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_Get16BitScale(unsigned int lDeviceId, float *Scale);


///////////////////////////////////High-Speed Callback////////////////////////////////

/// \brief                      High-Speed Transfer Mode Callback Function.
///	\param data					A pointer to the buffer that stores summary data.
///	\param ProfileCompressType  Compression type:32bit,1:16bit.
///	\param xPoints              The number of points in a line contour.
///	\param dwCount				The current callback returns the number of rows.
///	\param dwNotify             Callback state 0：Being called back，1：End of callback.
///	\param dwDeviceId           DeviceID ID.
///
typedef void(*SR7IF_ProfileCALLBACK)(const SR7IF_Data data, unsigned char ProfileCompressType, int xPoints, int dwCount, unsigned int dwNotify, unsigned int dwDeviceId);


/// \brief SR7IF_HighSpeedDataCallBackInitalize Initialize high-speed data communication over Ethernet.
/// \param lDeviceId       [in]     Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param pEthernetConfig [in]     Ethernet Communication settings.
/// \param pCallBack       [in]     Callback function.
/// \param dwProfileCnt    [in]     The frequency with which a finite loop callback function is called. range1-15000.
///                             	The number of times the infinite loop callback function is called. Applicable range 1-7500.
/// \return
///     <0:                     Failure
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_HighSpeedDataCallBackInitalize(unsigned int lDeviceId, const char* pEthernetConfig, SR7IF_ProfileCALLBACK pCallBack, unsigned int dwProfileCnt);


/// \brief SR7IF_StartMeasureWithHighSpeedCallback High-Speed Starts Batch Processing.
/// \param lDeviceId       [in]      	Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param ImmediateBatch  [in]     	0:Start batch processing immediately  1:Waiting for external signal.
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_StartMeasureWithHighSpeedCallback(unsigned int lDeviceId, unsigned int ImmediateBatch);


/// \brief SR7IF_StopMeasureWithHighSpeedCallback High-Speed Stop batch processing.
/// \param lDeviceId        [in]      	Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param ImmediateBatch   [in]    	0:Stop after data transmission is complete  1：Stop immediately.
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_StopMeasureWithHighSpeedCallback(unsigned int lDeviceId, unsigned int instantStop);


/// \brief SR7IF_GetProfilePointData32bit High-Speed Get 32-bit height data in a callback function.
/// \param DataObj        [in]      Callback data pointer.
/// \param head           [in]      0:camera A  1：camera B
/// \param Profile        [out]     Receive data pointer, size of individual data point is 4 bytes.
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_GetProfilePointData32bit(const SR7IF_Data DataObj, unsigned int head, int *Profile);


/// \brief SR7IF_GetProfilePointData16bit High-Speed Get 16-bit height data in a callback function.
/// \param DataObj       [in]       Callback data pointer.
/// \param head          [in]       0:camera A  1：camera B.
/// \param Profile       [out]      Receive data pointer, size of individual data point is 2 bytes.
/// \param Scale         [in]       Compression ratio
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_GetProfilePointData16bit(const SR7IF_Data DataObj, unsigned int head, short *Profile, double *Scale);


/// \brief SR7IF_GetHighSpeedIntensityData High-Speed Get gray-scale image data in a callback function.
/// \param DataObj       [in]     	 Callback data pointer.
/// \param head          [in]        0:camera A  1：camera B.
/// \param Intensity     [out]       Receive data pointer.
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_GetHighSpeedIntensityData(const SR7IF_Data DataObj, unsigned int head, unsigned char *Intensity);


/// \brief SR7IF_GetGrayData16Bit High-Speed Get 16-bit gray-scale image data in a callback function.
/// \param DataObj      [in]        Callback data pointer.
/// \param head         [in]        0:camera A  1：camera B
/// \param Profile      [out]       Receive data pointer, size of individual data point is 2 bytes.
/// \param Scale        [in]        Compression ratio
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_GetGrayData16Bit(const SR7IF_Data DataObj, unsigned int head, unsigned short *Profile, double *Scale);


/// \brief SR7IF_GetHighSpeedEncoderContiune  High-Speed Get encoder data in a callback function.
/// \param DataObj     [in]          Callback data pointer.
/// \param pEncoder    [out]         Receive data pointer.
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_GetHighSpeedEncoderContiune(const SR7IF_Data DataObj, unsigned int *pEncoder);

//////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////Asynchronous Callback /////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////
typedef void(*SR7IF_AsyncErrCallBack)(int dwDeviceId, unsigned int *errCode);

/// \brief SR7IF_AsyncEthernetOpen  Asynchronous Callback Establish a connection via Ethernet.
/// \param lDeviceId        [in]    Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param pEthernetConfig  [in]    Ethernet Communication settings.
/// \param timeOut          [in]    Search time (ms), minimum value 100.
/// \param fun				[in]	Disconnected callback function.
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_AsyncEthernetOpen(unsigned int lDeviceId, SR7IF_ETHERNET_CONFIG* pEthernetConfig, int timeOut = 2000,  SR7IF_AsyncErrCallBack errCallBackFunc = NULL);


/// \brief SR7IF_AsyncCALLBACK      Asynchronous callback mode callback function.
/// \param info				[in]	Reserved.
/// \param SR7IF_Data		[out]	Callback related information.
/// \param pUserData		[in]	Return the pointer passed in by the user during registration.
/// \param state			[out]	The current callback status.
/// state:(0x01 << 0) : The batch process has ended normally.
/// state:(0x01 << 1) : Sdk storage data overflow.
/// state:(0x01 << 2) : Controller storage data overflow.
/// state:(0x01 << 3) : Network exception, connection disconnected.
/// state:(0x01 << 4) : Other errors.
/// \param dwDeviceId		[in]	Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
typedef void(*SR7IF_AsyncCALLBACK)(const SR7IF_Data data, SR7IF_UserData pUserData, unsigned int state, unsigned int dwDeviceId);


/// \brief SR7IF_AsyncCallBackInitalize Initialize asynchronous callback data communication.
/// \param lDeviceId      [in]      Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param pCallBack      [in]      Callback function.
/// \param pUserData	  [in]		User registration passes in a pointer.
/// \param ProfileBits    [in]     0：Return 32-bit height data。1：Return 16-bit height data.
/// \param mMaxLine       [in]      Return the amount of data for the specified number of rows.
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_AsyncCallBackInitalize(unsigned int lDeviceId, SR7IF_AsyncCALLBACK pCallBack, SR7IF_UserData pUserData = NULL, unsigned int ProfileBits = 0, unsigned int mMaxLine = 0xFFFFFFFF);


/// \brief SR7IF_AsyncSoftStartBatch    Asynchronous Callback Starts Batch Processing.
/// \param lDeviceId        [in]      	Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_AsyncSoftStartBatch(unsigned int lDeviceId);


/// \brief SR7IF_AsyncStopStartBatch    Asynchronous Callback Stop batch processing.
/// \param lDeviceId        [in]      	Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \return
///     <0:                     Failure.
///     =0:                     Succeed.
///
SR7_IF_API int SR7IF_AsyncSoftStopBatch(unsigned int lDeviceId);


/// \brief SR7IF_GetAsyncProfilePointData   Asynchronous Callback Get 32-bit height data in a callback function.
/// \param DataObj       [in]       Internal data communicates with Pointers that store data passed in by callback functions.
/// \param head          [in]       0:camera A  1：camera B.
/// \return						data pointer.
///
SR7_IF_API const int* SR7IF_GetAsyncProfilePointData(const SR7IF_Data DataObj, unsigned int head);


////// \brief SR7IF_GetAsyncProfilePointData16Bit   Asynchronous Callback Get 16-bit height data in a callback function.
/// \param DataObj       [in]       Internal data communicates with Pointers that store data passed in by callback functions.
/// \param head          [in]       0:camera A  1：camera B.
/// \return						data pointer.
///
SR7_IF_API const short* SR7IF_GetAsyncProfilePointData16Bit(const SR7IF_Data DataObj, unsigned int head);


/// \brief SR7IF_GetAsyncIntensityContiuneData  Asynchronous Callback Get gray-scale image data in a callback function.
/// \param DataObj       [in]       Internal data communicates with Pointers that store data passed in by callback functions.
/// \param head          [in]       0:camera A  1：camera B.
/// \return						data pointer.
///
SR7_IF_API const unsigned char* SR7IF_GetAsyncIntensityContiuneData(const SR7IF_Data DataObj, unsigned int head);


/// \brief SR7IF_GetAsyncEncoderContiune    Asynchronous Callback Get encoder data in a callback function.
/// \param DataObj       [in]               Internal data communicates with Pointers that store data passed in by callback functions.
/// \param head          [in]               0:camera A  1：camera B.
/// \return						data pointer.
///
SR7_IF_API const unsigned int* SR7IF_GetAsyncEncoderContiune(const SR7IF_Data DataObj, unsigned int head);

///
/// \brief SR7IF_GetMeasuringRangeZ  Get the upper and lower limits of the measure ment range on current Z-axis(unit:mm).
/// \param lDeviceId            	 Specifies which communication device is used forcommunication,ranging from 0 to 63.
/// \param up						 Upper limit of measuring range(unit:mm).
/// \param down						 Lower limit of measuring range(unit:mm).
///
///     <0:                     Failure.
///     =0:                     Succeed.
SR7_IF_API int SR7IF_GetMeasuringRangeZ(unsigned int lDeviceId, double *up, double *down);
#ifdef __cplusplus
}
#endif
#endif //SR7LINK__H

