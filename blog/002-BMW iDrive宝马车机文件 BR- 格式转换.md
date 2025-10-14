# BMW iDrive车机文件 BR* 格式转换

  从宝马车机的 iDrive 导出的歌曲往往是 .BR* 的格式，车机软件对歌曲编码进行了部分替换操作，导出的USB或硬盘设备接入其他系统后往往不能直接音乐播放器打开播放，需要重新转换编码。然而当前 2025年10月份的 `ffmpeg` 工具尚不支持直接转换这些类型的文件，需要用工具转换或理解编码格式手动按位取反不通格式混淆的部分二进制数据。

  常用的就是其中的 BR4、BR5 文件转换为对应的 mp3、wma格式，当然其他格式也可以转换。![image-20251014160738308](https://raw.githubusercontent.com/EzXxY/EzXxY.github.io/main/Typora/img/2025/10/20251014_image-20251014160738308_1760429270.png)

## 一、直接转换

  使用 GitHub 开源的软件 [BMW Media Converter](https://github.com/sivu22/BMC/) 可以直接转换为 mp3、wma、flac 等其他音乐别放软件也可以识别播放的格式。这个项目是一个BMW媒体文件格式转换工具，将 BMW iDrive 系统创建的 .br* 格式文件转换回原始的音频/视频/图片格式。选择源文件路径、转化后输出文件路径后，直接点击转换按钮 `Convert` 即可。

#### [【备份的 v2.2.0 版本下载链接】](https://EzXxY.github.io/file/BMC.exe)

![img](https://raw.githubusercontent.com/EzXxY/EzXxY.github.io/main/Typora/img/2025/10/20251014_Screenshot_1760427379.png)

> [!CAUTION]
>
> 1.  默认选择的车机系统模式为 `NBT/NBT Evo`，若为 `CIC` 模式，请切换 iDrive 版本。
> 2.  软件需要在 Windows 系统下运行，且具有 .NET Framework ≥ 4.7.2 运行时环境。

## 二、编码原理

  BR* 文件并没有对源文件进行加密操作，而是对二进制数据进行 **不同程度的** `按位取反`  操作，BMW使用了如下不同的策略来"混淆"不同格式的文件。

#### 1. 对于 BR29, BR34, BR48 格式

> **类型1：**部分混淆（前128KB）
>
> ```c#
> if (i < 0x20000) // 前 131072 字节 (128KB)
>       bytesOut[i] = (byte)(~bytesIn[i]);  // 取反
> else
>        bytesOut[i] = bytesIn[i];  // 保持原样
> ```
>
>   - 只加密前128KB，后面的数据不变
> - 这些格式对应：WMA (BR29/BR5)、MP4 (BR34)、FLAC (BR48)

#### 2. 对于 BR25, BR4 格式

> **类型2：**保留最后3个字节
>
> ```c#
> if (bytesIn.Length - i > 3)
>       bytesOut[i] = (byte)(~bytesIn[i]);  // 取反
> else if (hu != HeadUnit.CIC)
>       bytesOut[i] = bytesIn[i];  // NBT系统：最后3字节不变
> else
>       bytesOut[i] = (byte)(~bytesIn[i]);  // CIC系统：全部取反
> ```
>
> - NBT Evo系统：最后3个字节保持原样（可能是文件标识）
> - CIC系统：全部取反
> - 这些格式对应：AAC (BR25)、MP3 (BR4)

#### 3. 对于 BR28, BR30 格式

> **类型3：**保留最后1个字节
>
> ```c#
> if (bytesIn.Length - i > 1)
>       bytesOut[i] = (byte)(~bytesIn[i]);  // 取反
> else
>       bytesOut[i] = bytesIn[i];  // 最后1字节不变
> ```
>
> - 最后1个字节保持原样
> - 这些格式对应：MP3 (BR28)、M3U播放列表 (BR30)
>   

#### 4. 对于 BR1, BR27, BR3, BR5, BR67 等其他格式

> **类型4：**完全混淆
>
> ```c#
> bytesOut[i] = (byte)(~bytesIn[i]);  // 全部取反
> ```
>
> - 整个文件所有字节都取反

