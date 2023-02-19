
# zood init

这部分内容用于测试搜索

## 摘要

- 三种CXL协议
- 讨论了最优的PCIe存储设备选择(Type3)
- 做对比实现讨论CXL带来了的性能提升
- 探索网络拓扑和管理内存扩展的方式

## 术语表

|名词|释义|
|:--:|:--:|
|BARs|PCIe base address registers|
|FlexBus|CXL.io创建的高速IO通道|
|CXL RP|CXL root port|
|HDM|host-managed device memory|
|CXL flit|主机设备通过CXL RP发送给type3设备用于同步的信息|
|USP|upstream ports|
|DSP|downstream ports|
|fabric manager|swicth's crossbar,交换机连接USP,DSP的部分|
|VH|virtual hierarchy|
|MLD|multiple logical device|
|GPF|global persistent flush|
|DT|deterministic|
|ND|non-deterministic|
|BF|bufferable|
|NB|non-bufferable|