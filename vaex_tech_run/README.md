
## Vaex tech

网址：https://www.vaex.tech/

API手册：https://exdocs.gitbook.io/v/spot#an-quan-lei-xing-trade

部署文档：<br>
1、配置好python3环境<br>
2、在src目录运行python3 vaex_trade.py，注意修改api key和api secret(在vaex_trade.py的第16行)<br>
3、参数配置：在vaex_trade.py的第128行后面，主要调整参数包括：
- self_tradeFrequence：self交易频率，越小越快
- cross_tradeFrequence：cross交易频率，越小越快
- cross_trade_price_max：保护价格上限，0是不设置
- cross_trade_price_min：保护价格下限，0是不设置

