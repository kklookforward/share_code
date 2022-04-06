
## Vaex tech

网址：https://www.vaex.tech/

API手册：https://exdocs.gitbook.io/v/spot#an-quan-lei-xing-trade

部署文档：<br>
1、配置好python3环境<br>
2、修改配置文件src/default_config.py，首次运行前需要配置key和secret，其他参数根据需要修改，具体说明请查看配置文件注释。<br>
2、在src目录运行python3 vaex_trade.py即可，可以查看打印的日志信息观察运行情况。<br>
3、获取成交和撤单报告数据：程序每天在固定时间点输出csv格式报告文件（可配置参数report_hour，默认16点），存放在reports目录下。<br>
