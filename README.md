lifesmart 开关接入 HomeAssistant插件，配置比较麻烦，但能用。
使用方法：将lifesmart目录复制到config/custom_components/下
再configuration.yaml文件中增加配置：
配置模式一：手动添加开关设备
switch:
  - platform: lifesmart 
    appkey: "your_appkey" 
    apptoken: "your_apptoken" 
    userid: "your_userid" 
    usertoken: "your_usertoken" 
    add_type: "mt"
    switches: 
      lifesmart_test: 
        friendly_name: 'lifesmart开关' 
        agt: "设备agt属性" 
        me: "设备me属性" 
        idx: "设备idx属性"
配置模式二：自动注册开关设备
switch:
  - platform: lifesmart 
    appkey: "your_appkey" 
    apptoken: "your_apptoken" 
    userid: "your_userid" 
    usertoken: "your_usertoken" 
    add_type: "at"
