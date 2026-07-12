# 一、Firmware Image
## 1.1、**Firmware**生命周期是什么？
**Firmware**是由开发好的.c文件--->complie--->.o文件--->link--->.elf文件--->objcpoy---->.bin并最终烧录到固件上的文件，因此其生命周期我理解是从.elf文件开始，直到烧录到固件上为止。
## 1.2为什么会存在这么多种Firmware格式？
不同格式的Firmware应用于不同阶段、不同对象中。Firmware 格式不是为了区分芯片，而是为了满足不同软件（开发工具、烧录工具、Bootloader）的需求：
#### 初始时：elf文件主要面向开发者，用于调试和开发
#### 传输时：Intel HEX、Motorola SREC 的作用是在传输过程中记录地址、数据和校验，使烧录工具能够可靠地将数据写入指定地址。
#### 运行时：Raw Binary、ESP Image主要面向Bootloader，需要让Bootloader理解哪些是Image Header、Segment、Checksum等数据
## 1.3 ELF、RawBinary、ESP Image、Intel HEX分别解决什么问题？
**ELF**文件主要面向开发者，用于调试和开发；  
**ESP Image**主要面向Bootloader，需要让Bootloader理解哪些是Image Header、Segment、Checksum等数据;  
**Intel HEX、 Motorola SREC**主要面向串口、烧录器等底层设备，因为传输工具只关注数据的完整性，因此这个阶段中文件主要以01比特串的形式记录信息


### 本阶段总结

Firmware 格式不是厂家随意设计的，而是针对不同的使用对象设计的。

ELF 面向开发和调试；

Intel HEX、Motorola SREC 面向烧录和传输；

Raw Binary、ESP Image、uImage、FIT Image 面向 Bootloader 加载和 CPU 运行。

因此，在分析一个新的 Firmware 时，首先应该识别它属于哪一种格式，再决定采用什么方式进行解析。