#pragma once

#ifdef WIN32
#define  SR7_IF25D_API __declspec(dllexport)

#include "Winsock2.h"
#include "Ws2tcpip.h"
#pragma comment(lib, "WS2_32.lib")
#else
#define  SR7_IF_API extern
#endif

// IP address
typedef struct {
#ifdef WIN32
	IN_ADDR				IPAddress;
#else
	struct in_addr IPAddress;
#endif
} SRIF_OPENPARAM_ETHERNET;

#ifdef __cplusplus
extern "C"
{
#endif
	///
	/// \brief SR7IF_EthernetOpen25D	通信连接.
	/// \param lDeviceId				设备ID号，范围为0-63.
	/// \param pEthernetConfig			Ethernet 通信设定.
	/// \return
	///     <0:							失败.
	///     =0:							成功.
	///
	SR7_IF25D_API int SR7IF_EthernetOpen25D(unsigned int lDeviceId, SRIF_OPENPARAM_ETHERNET* pEthernetConfig);

	///
	/// \brief SR7IF_CommClose25D		断开与相机的连接.
	/// \param lDeviceId				设备ID号，范围为0-63.
	/// \return
	///     <0:							失败.
	///     =0:							成功.
	///
	SR7_IF25D_API int SR7IF_CommClose25D(unsigned int lDeviceId);

	///
	/// \brief SR7IF_GetSetting25D      参数设定.
	/// \param lDeviceId				设备ID号，范围为0-63.
	/// \param Depth					设置的值的级别.
	/// \param Type						设置类型.-1:为设置当前配方参数  0x10-0x4F:为配方0-63号配方
	/// \param Category					设置种类.
	/// \param Item						设置项目.
	/// \param Target[4]				根据发送 / 接收的设定，可能需要进行相应的指定。无需设定时，指定为 0。
	/// \param pData					设置数据.
	/// \param DataSize					设置数据的长度.
	/// \return
	///     <0:							失败.
	///     =0:							成功.
	///
	SR7_IF25D_API int SR7IF_SetSetting25D(unsigned int lDeviceId, int Depth, int Type, int Category, int Item, int Target[4], void *pData, int DataSize);

	///
	/// \brief SR7IF_GetSetting25D      获取参数设定.当获取的配方号为非当前运行的配方时，会导致批处理中断
	/// \param lDeviceId				设备ID号，范围为0-63.
	/// \param Type						获取类型. -1:为获取当前配方参数;0x10-0x4F:为配方0-63号配方
	/// \param Category					获取种类.
	/// \param Item						获取项目.
	/// \param Target[4]				根据发送 / 接收的设定，可能需要进行相应的指定。无需设定时，指定为 0。
	/// \param pData					获取的数据.
	/// \param DataSize					获取数据的长度.
	/// \return
	///     <0:							失败.
	///     =0:							成功.
	///
	SR7_IF25D_API int SR7IF_GetSetting25D(unsigned int lDeviceId, int Type, int Category, int Item, int Target[4], void *pData, int DataSize);

	///
	///\brief SR7IF_ClearMemory25D		清理内存
	///\param lDeviceId					设备ID号，范围为0-63.
	/// \return
	///     <0:							失败.
	///     =0:							成功.
	///
	SR7_IF25D_API int SR7IF_ClearMemory25D(unsigned int lDeviceId);

	///
	///\brief SR7IF_StartStorage25D		开始存储数据
	///\param lDeviceId					设备ID号，范围为0-63.
	///\param StorageNum				存储数量。0-800000.
	/// \return
	///     <0:							失败.
	///     =0:							成功.
	///
	SR7_IF25D_API int SR7IF_StartStorage25D(unsigned int lDeviceId, unsigned int StorageNum);

	///
	///\brief SR7IF_StopStorage25D		控制存储数据
	///\param lDeviceId					设备ID号，范围为0-63.
	///\param mode						数据存储控制模式。0:暂停，1：继续.
	/// \return
	///     <0:							失败.
	///     =0:							成功.
	///
	SR7_IF25D_API int SR7IF_ControlsStorage25D(unsigned int lDeviceId, unsigned int mode);

	///
	///\brief SR7IF_GetStorageStatus25D	获取存储状态
	///\param lDeviceId					设备ID号，范围为0-63.
	///\param dataNum					已存储数量总数.
	///\param status					存储状态。0：停止中，1：存储中.
	/// \return
	///     <0:							失败.
	///     =0:							成功.
	///
	SR7_IF25D_API int SR7IF_GetStorageStatus25D(unsigned int lDeviceId, unsigned int* dataNum, unsigned int* status);

	///
	///\brief SR7IF_GetStorageData25D		获取存储数据
	///\param lDeviceId（in）				设备ID号，范围为0-63.
	///\param OutNo（in）					指定获取编号1-16；
	///\param NumOfBuffer（in）				缓冲区大小（最多可接受多少个数据）
	///\param OutBuffer（out）				数据数组
	///\param NumReceived（out）				实际接收的数据个数
	/// \return
	///     <0:							失败.
	///     =0:							成功.
	///
	SR7_IF25D_API int SR7IF_GetStorageData25D(unsigned int lDeviceId, unsigned int OutNo, unsigned int NumOfBuffer, float * OutBuffer, unsigned int *NumReceived);
#ifdef __cplusplus
}
#endif