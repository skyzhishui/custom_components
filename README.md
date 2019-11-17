使用说明
==== 
lifesmart 开关接入 HomeAssistant插件

目前支持的设备：
-------  
1、开关；

2、灯光：目前仅支持超级碗夜灯；

3、万能遥控；

4、窗帘电机（仅支持杜亚电机）

5、动态感应器、门磁、环境感应器、甲醛/燃气感应器

使用方法：
-------  
1、将lifesmart目录复制到config/custom_components/下

2、在configuration.yaml文件中增加配置：


lifesmart:
  appkey: "your_appkey" <br>
  apptoken: "your_apptoken"<br>
  usertoken: "your_usertoken" <br>
  userid: "your_userid"<br>
  exclude:<br>
    - 0011 #需屏蔽设备的me值<br>
    
