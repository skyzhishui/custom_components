使用说明
==== 
lifesmart 设备接入 HomeAssistant插件

更新说明
-------  
[2020年2月4日更新]

优化实体ID生成逻辑：解决未加入或存在多个智慧中心时，me号可能存在重复的问题。
[2019年12月6日更新]

新增支持设备：

**中央空调面板**：V_AIR_P
**智能门锁反馈信息**：SL_LK_LS、SL_LK_GTM、SL_LK_AG、SL_LK_SG、SL_LK_YL

目前支持的设备：
-------  
1、开关；

2、灯光：目前仅支持超级碗夜灯；

3、万能遥控；

4、窗帘电机（仅支持杜亚电机）

5、动态感应器、门磁、环境感应器、甲醛/燃气感应器

6、空调控制面板

7、智能门锁信息反馈

使用方法：
-------  
1、将lifesmart目录复制到config/custom_components/下

2、在configuration.yaml文件中增加配置：

```
lifesmart:
  appkey: "your_appkey" 
  apptoken: "your_apptoken"
  usertoken: "your_usertoken" 
  userid: "your_userid"
  exclude:
    - 0011 #需屏蔽设备的me值,这个暂时为必填项，可以填任意内容
```
    
