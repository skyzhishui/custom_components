lifesmart 开关接入 HomeAssistant插件，配置比较麻烦，但能用。
使用方法：将lifesmart目录复制到config/custom_components/下
再configuration.yaml文件中增加配置：
switch:
  - platform: lifesmart
    appkey: "appkey"
    apptoken: "apptoken"
    userid: "userid"
    usertoken: "usertoken"
    switches:
      lifesmart_test:
        friendly_name: 'lifesmart_test'
        agt: "agt"
        me: "me"
        idx: "idx"
