## 一、项目简介

​	obespoir 是一款个人独立开发的彻底分布式的开源游戏框架，主要基于python3.7 进行开发，采取了 asyncio,uvloop 等异步编程技术，保障高性能的同时，从框架层面彻底解决生产环境中单节点或服务的高可用需求问题。

该框架的主要特点如下：

1. 支持动态热更新：通过嵌入 http 接口实现游戏内各类型节点的实时更新，支持配置文件和数据库等多种方式；

2. 自适应高可用：框架中的每一个节点可根据需求动态添加或删除，任何节点发生故障无需停服，框架会自动发现合适的节点维持业务运行；

3. 性能卓越：基于异步 asyncio, uvloop 等优秀三方库开发，并发性能接近于 golang, c等编译型语言, 普通单机并发可达到万数量级；

4. 安全可靠：节点间根据配置进行分层权限管理，有效应对 DDOS 瘫痪全局节点；高效 rpc 通信加密机制，防止数据伪造及篡改；

5. 跨平台：提供 websocket 连接服务，支持客户端 h5 游戏引擎开发，一份代码适用移动端，PC 端，浏览器等各终端。

## 二、安装部署

### 1. 使用环境

```wiki
1. 代码基于python3.7进行开发，请预先装好相应环境；
2. 有使用到三方库ujson, pymongo(如果配置不用mongo可不装)
```

### 2. 使用说明

安装步骤：

```shell
pip3 install -i https://pypi.python.org/simple obEspoir
```

引入该框架需要对接一下几处地方：

#### 2.1 配置文件

​	配置文件采用json格式，每一个节点（进程）有一个自己的配置文件，配置文件里包括该节点监听的各类端口，日志的目录，连接的数据库地址，连接加密密码、路由信息等等。

​	其中rpc接口部分需要配置哪些消息需要转发，又需要转发往哪些节点，支持两种方式：：

```json
"route": {                     //配置消息转发的路由
            "range": {
                "route": [[0, 5000]], "service": [[5001, 1000000]]
            },
            "special": {
                "route":  [1000] // like "proxy": [110119]
            }
        }
1. 消息ID范围：range中说明哪些范围段内的消息往哪类型节点发，比如上述[0,5000] 发往route类型节点（如果本节点就是route类型，则本地处理），[5001, 10000]内的消息发往service类型节点;
2. 具体的消息ID：special中可以具体写明哪些指定的消息发往哪个节点，如1000消息发往route处理，如果该部分和range冲突，以special配置优先；
```

总体配置信息参考如下：

proxy类型节点：

```json
{
    "log_level": "debug",                                        // 日志级别
    "name": "proxy_1",                                           // 节点名称
    "log_dir": "logs/obEspoir/",                           // 项目运行日志存放目录（不同测试环境目录不同）

    "host": "127.0.0.1",
    "type": "proxy",
    "api_path": "proxy.include_libs",   // api 路径, 项目启动时导入自定义的各类api模块的地方
    "available_way": "local",   // 高可用性配置使用哪种方式存储： local（本地文件存储，默认方式）, mongo(mongodb存储)
    "mongo_uri":"mongodb://test:xxxx@xxxx.mongodb.rds.aliyuncs.com:3717,xxxx.mongodb.rds.aliyuncs.com:3717/admin",       // 如果使用了MongoDB作为存储，则该项需要配置
    "remote_ports": [       //需要连接的远程rpc端口信息
        {
            "host": "127.0.0.1",
            "port":  21002,
            "token": "helloworldiloveyou~1234567890123",
            "encode": 0,
            "type": "route"                      // 节点类型(字符串标识)
        }
    ],
    "websocket": {           // 本地监听的websocket端口配置
        "port": 20000,
        "token": "helloworldiloveyou~1234567890123",      // 32位秘钥 websocket通信
        "encode": 0,                                      // 是否启用加密
        "timeout": 300,                                   //多久连接超时（单位为秒）
        "no_state": {            // 无状态的消息ID
          "range": [[0, 100000]],
            "special": []       // like "game": [110119]
        }
    },
    "http": {						// 本地监听的http端口信息
        "port": 20001,
        "token": "helloworldiloveyou~1234567890123",      // 32位秘钥 httpserver web通信
        "encode": 0                                       // 是否启用加密
    },
    "rpc": {           // 本地监听的rpc端口信息
        "port": 20002,
        "token": "helloworldiloveyou~1234567890123",      // 32位秘钥 rpc通信
        "encode": 0,                                      // 是否启用加密
        "type": "proxy",                                   // 节点类型
        "reconnect_time": 5                              // 连接断开时重连时间间隔，默认最多重试3次
    }
}
```

route路由类型节点参考配置（大多和proxy相同）：

```json
{
    "log_level": "debug",                                        // 日志级别
    "name": "route_1",                                     // 项目名称
    "log_dir": "logs/obEspoir/",                            // 项目运行日志存放目录（不同测试环境目录不同）

    "host": "127.0.0.1",
    "type": "route",
    "api_path": "route.include_libs",   // api 路径
    "http": {
        "port": 21001,
        "token": "helloworldiloveyou~1234567890123",      // 32位秘钥 httpserver web通信
        "encode": 0                                       // 是否启用加密
    },
    "rpc": {
        "port": 21002,
        "token": "helloworldiloveyou~1234567890123",      // 32位秘钥 rpc通信
        "encode": 0,                                      // 是否启用加密
        "type": "game",                                   // 节点类型

        // rpc会收到三类消息：待本地处理消息、待转发的消息、待直接推送到websocket client的消息
        "route": {                     //配置消息转发的路由
            "range": {
                "route": [[0, 5000]], "service": [[5001, 1000000]]
            },
            "special": {
                "route":  [1000] // like "proxy": [110119]
            }
        }
    },

    "remote_ports": [
        {
            "host": "127.0.0.1",
            "port":  20002,
            "token": "helloworldiloveyou~1234567890123",
            "encode": 0,
            "type": "proxy"                      // 节点类型(字符串标识)
        },
        {
            "host": "127.0.0.1",
            "port":  22002,
            "token": "helloworldiloveyou~1234567890123",
            "encode": 0,
            "type": "service"                      // 节点类型(字符串标识)
        }
    ]


}
```

service业务节点参考配置(大多和proxy相同)：

```json
{
    "log_level": "debug",                                        // 日志级别
    "name": "service_1",                                     // 项目名称
    "log_dir": "logs/obEspoir/",                            // 项目运行日志存放目录（不同测试环境目录不同）

    "host": "127.0.0.1",
    "type": "service",
    "api_path": "service.include_libs",   // api 路径
    "http": {
        "port": 22001,
        "token": "helloworldiloveyou~1234567890123",      // 32位秘钥 httpserver web通信
        "encode": 0                                       // 是否启用加密
    },
    "rpc": {
        "port": 22002,
        "token": "helloworldiloveyou~1234567890123",      // 32位秘钥 rpc通信
        "encode": 0,                                      // 是否启用加密
        "type": "service",                                   // 节点类型

        // rpc会收到三类消息：待本地处理消息、待转发的消息、待直接推送到websocket client的消息
        "route": {                     //配置消息转发的路径
            "range": {
                "service": [[5001, 1000000]]
            },
            "special": {
                            // like "proxy": [110119]
            }
        }
    },

    "remote_ports": [
        {
            "host": "127.0.0.1",
            "port":  21002,
            "token": "helloworldiloveyou~1234567890123",
            "encode": 0,
            "type": "route"                      // 节点类型(字符串标识)
        }
    ]


}
```

#### 2.2 自定义接口配置

​	实际的应用中我们可以根据需要定制不同节点的接口服务，包括rpc接口消息处理，http接口消息处理，websocket接口消息处理。最后将自定义的三类接口文件在配置文件中的“api_path”对应的文件中导入即可，如：

![image-自定义接口导入.jpg](doc/自定义接口导入.jpg)

##### 2.2.1 http接口

​	每个节点都可以对外提供http服务，收到不同的http服务请求，然后调用不同的处理方法，比如可以做服务端热更新，或者用来不同模块间实时更新用户个人信息。

​	参考自定义接口文件http_handler.py写法：

```python
from aiohttp import web

from obespoir.httpserver.route import HttpHandler
from obespoir.server.server import Server


@HttpHandler("/")
async def index(request):
    return web.Response(body="hello", content_type="text/html")


@HttpHandler("/update_remote_rpc_config")
async def update_remote_rpc_config(request):
    await Server().update_remote_rpc_config()
    return web.Response(body="ok~", content_type="text/html")
```

##### 2.2.2 rpc接口

​	每个节点同时也可以对外支持rpc服务，收到不同的rpc调用请求，调用不同的处理方法，实际处理的自定义接口，参考写法如下(rpc_handler.py，文件名和include_libs.py中import路径保持一致即可)：

```python
from obespoir.base.common_define import NodeType
from obespoir.base.ob_handler import BaseHandler, RegisterEvent
from obespoir.rpcserver.push_lib import push_message
from obespoir.share.ob_log import logger


@RegisterEvent(100002)
class LoginHandler(BaseHandler):

    async def execute(self, *args, **kwargs):
        logger.info("login_handler:{}  {}".format(args, kwargs))
        user_id = self.params.get("user_id", -1)
        passwd = self.params.get("passwd", "")
        if -1 == user_id or not passwd:
            return {}
        # ...
        pass
        return {"code": 200, "data": {}}


@RegisterEvent(100130, need_return=False)
class OfflineHandler(BaseHandler):

    async def execute(self, *args, **kwargs):
        logger.info("offline: {}, {}".format(args, kwargs))
        pass
        return {"code": 200}


@RegisterEvent(10000, need_return=True)
class HeartBeatHandler(BaseHandler):

    async def execute(self, *args, **kwargs):
        logger.info("heartbeat: {}, {}".format(args, kwargs))
        pass
        return {"code": 200}
```

##### 2.2.3 websocket接口

​	理论上每个节点都可以对外提供websocket服务（实际中一般只有proxy节点才会配置），收到websocket消息请求后，具体的接口处理方法和逻辑由用户自己决定，接口参考写法（ws_handler.py）如下：

```python
import asyncio
import ujson

from websockets.exceptions import ConnectionClosed

from obespoir.share.singleton import Singleton
from obespoir.share.ob_log import logger
from obespoir.base.common_define import NodeType
from obespoir.base.ob_protocol import DataException
from obespoir.base.global_object import GlobalObject
from obespoir.websocketserver.route import webSocketRouteHandle
from obespoir.rpcserver.push_lib import push_message


@webSocketRouteHandle
async def forward_0(command_id, data, session_id):
    """
    消息转发
    :param command_id: int
    :param data: json
    :param session_id: string
    :return: None
    """
    print("forward_0", command_id, data, type(data), data, session_id)
    if not isinstance(data, dict):
        try:
            data = ujson.loads(data)
            print("data type :", type(data))
        except Exception:
            logger.warn("param data parse error {}".format(data))
            return {}
    data.update({"message_id": command_id})
    await push_message(NodeType.ROUTE, command_id, data, session_id=session_id, to=None)
```

#### 2.3 示例demo

在项目中有一个test文件目录，其中为简单的测试demo，启动时执行以下文件即可

```shell
服务端启动：
python3 start_route.py        # 启动一个route类型节点
python3 start_proxy.py			  # 启动一个proxy类型节点
python3 start_service.py		  # 启动一个service类型节点

测试客户端：
python3 test_frame.py     #  客户端测试文件
```

## 三、功能介绍

设计原则： 拟计划设计出一款彻底分布式的，去中心化的分布式app后端引擎架构。
框架功能：封装基础通信父类，用户只需要修改配置文件，如果需要自定义，继承相应父类即可；

### 1. 接口设计

```wiki
1. webport: http接口
2. websocket port: 长连接接口： 供客户端使用   --- ws port
3. rpc port： rpc连接端口： 供其他进程rpc调用
4. remote port: 启动时希望去连接的其他节点地址和端口
```

### 2. 自动高可用性

​	该框架中节点一般分为三类型（可根据用户需求自行扩展）：proxy，route, service. 节点之间互不依赖, 支持分布式架构，任何一个节点故障不会影响到整体业务运行。

#### 2.1 节点类型

框架本身里面所有的节点本质都是一样的，只是赋予了不同节点不同类型的职能。初步职能如下：

```
proxy代理节点： （对公网开放，不承担消息转发功能）
		 客户端通过websocket端口连接某一个代理节点

route路由节点:  （只对内网开放）
	负责节点间消息转发，当其他节点不知道消息如何走向为最短路径时，消息发往路由节点进行中转；
	管理记录各节点的存活状态，响应节点相关请求

service业务节点:  （只对内网开放）
	负责处理各类业务逻辑
```

#### 2.2 节点标识

```wiki
节点id（节点id=md5(host+rpc_port)）
节点名称（同一台机器上节点名称不能一样）
节点类型：目前分为三种，可自定义
节点4个端口： http_port, websocket_port, rpc_port, remote_ports
节点所在主机标识（主机标识+节点名 唯一定位一个具体的节点）
路由节点地址
```

#### 2.3 节点热更新策略

​	新节点加入时：读取配置，尝试连接配置中其需要rpc连接的所有节点， 失败则重试若干次；同时着重通知当前所有的route节点，有新的存活的节点加入；
​
​	路由节点加入：路由节点需要和所有其他普通节点间保持双向rpc连接，收到其他节点建立连接请求时：鉴权正确，则建立连接；
​	未知原因和其他节点主动进行的rpc连接断开时：隔指定周期询问route节点断开连接的另一端节点是否存活，若存活则重新尝试连接；

### 3. 消息通信

#### 3.1 消息流程

a. 客户端主动请求示例消息：
client发送消息--> proxy节点websocket port收到消息--> rpc调用后续service节点rpc端口 --> service消息处理完后发送消息给proxy

b. service发送消息给proxy时，如果没有直接连接，则发往路由节点route.

c. 服务端推送消息时：
	service发送推送消息时，如果没有proxy节点的直接连接，则同样发往路由节点route.

d. route路由节点：

```wiki
rpc端口收到消息时,判断消息的目的节点：
		目的节点为自己： 执行自我业务逻辑处理
		目的节点为其他： 向目的节点的rpc端口发送消息
```

e. proxy 节点：

```wiki
1. rpc端口收到消息时：
		直接调用websocket连接向客户端发送消息
2. 向远程的route或其他节点rpc发送消息时：
		如果没有明确发送目标，则发往路由节点
		有明确的目标类型，则随机发往一个目标类型的实例化节点
```

f. service 节点：

```wiki
判断消息的目的节点：
	目的节点为自己： 执行自我业务逻辑处理
	目的节点为其他： 向目的节点的rpc端口发送消息
```

#### 3.2 route路由节点

​	存放所有节点的路由信息，当系统中更新或删除节点时，更新路由节点，然后路由节点通知所有的其他节点

#### 3.3 proxy代理节点

```wiki
1. 连接序号生成：
	每次新增连接时产生一个新的连接序号，每次连接和一个连接序号相对应，连接序号和连接会缓存起来

2. websocket收到消息后，将合法消息发往route节点
	消息内容有：
	session_id: proxy节点id+连接序号
	to: 优先使用上一次去往的节点（如果上一次的节点不可用，则等待一段时间再试，三次后放弃请求，连接断开，连接断开时，清空缓存），为空值时，代表未知消息在哪里处理，此时由转发到的下一个节点决定，职位节点id

3. proxy节点需要缓存上一次消息通信的路径（即是否之后的消息都沿用之前消息处理的路径）
	消息分为两种类型： 有状态（下一个请求和上一个请求必须同一个service节点处理，默认有状态）和无状态（无需同一个service节点处理不同请求）
```

#### 3.4 service业务节点

​	该节点用来处理具体的业务逻辑，业务处理完后，调用相应的推送接口，向客户端返回消息，其中session_id中包括了该消息是由哪一个proxy发送过来，proxy中的哪一个websocket连接。

### 4. rpc消息

#### 4.1 rpc消息结构

消息目的地： 客户端过来的消息，即proxy的消息第一次时不知道去往哪里，此时proxy会将消息目的地置为route节点
消息来源：该消息的原始节点名称
消息内容：
	route根据消息ID， 决定接下来是否需要rpc请求不同的service节点

rpc连接建立时，验证token信息，通过后后续的请求才会被处理，验证失败则连接断开；
rpc通信时无需加密解密操作，但需要有打包解包（防止粘包现象）

#### 4.2 rpc消息处理流程

​	某个节点发送rpc消息时：

```wiki
根据两个参数判断： next_node_type(发送往下一个节点的类型)， to(最终的目的节点id)
a. next_node_type类型和自己相同，返回错误
b. 存在to对应的rpc连接（活跃状态），直接通过该连接发送消息
c. next_node_type存在，选择一个活着的next_node_type类型的实例，发送消息
	若没有，发往一个route节点；
	若route节点无活跃连接，该次暂停消息发送
```

​	接收rpc消息时：

```wiki
某个节点收到rpc消息时，会收到两个参数 session_id（消息最初来源于谁, proxy节点id+连接序号）, to（消息最终发往谁）
	a. 如果to有具体目标，同时该目标不是自己，并且有和该目标的直接rpc连接，则转发请求到目标节点
	b. 如果to有具体目标，同时该目标是自己， 则进入本节点消息处理逻辑；
	c. 如果to无具体目标：
		如果节点为proxy类型节点（终端节点），则调用websocket向客户端发送消息
		结合配置根据消息ID判断下一步流程：
			有路由走路由，调用发送rpc消息接口
			没有路由，本地消息处理：进入本节点消息处理
```

### 5. 客户端断线流程

服务端的检测到用户断线时, 会触发以下流程：

```wiki
清理proxy节点会话缓存
	向route发送断线消息
	route清理自己的缓存
	向后端节点发送断线消息
	后端特定service节点收到断线请求后，触发断线逻辑处理
	...
```

### 6. 配置更新

节点配置信息支持两种方式：
	a. 本地文件存储
	b. mongodb数据库存储
配置更新：节点对外开放一个web http服务接口，接口收到消息后，更新配置信息

### 7. 代码结构

```wiki
base/： 框架中抽象出来的基类库
		common_define.py: 常量定义，包括节点类型，连接状态等
		data_pack.py: 通信时数据的打包和解包类封装
		global_object.py：全局对象，封装进程中多个地方需要用到的变量信息
		ob_handler.py: 异步消息实际处理的自定义基类
		ob_protocol.py: 异步消息处理的协议
		ob_route.py: 消息分发的基类

db/： 数据存储相关，目前暂时只扩展了MongoDB
		mongo.py: 使用MongoDB存储配置信息，封装相应方法

httpserver/:    http请求相关
		handler.py: 不同http请求实际消息处理接口，用户需求不同，该文件实现即不同，此处只为参考
		route.py:  http请求路由封装类

rpcserver/:	   rpc请求相关
		connection_manager.py: rpc连接管理类
		handler.py：不同rpc消息实际处理接口，用户需求不同，该文件实现即不同，此处只为参考
		protocol.py: 接收rpc请求的消息处理协议
		push_lib.py: 向其他节点推送rpc消息封装类
		push_protocol.py: 推送rpc秦秋的消息处理协议
		route.py：rpc消息路由封装类
		session_cache.py: 长连接会话缓存处理类

server/:   服务主入口
		server.py: 框架启动的主入口类

share/:   项目公用工具库
		encodeutil.py: 加密解密封装类，消息通信时会调用
		ob_log.py:   自定义日志类
		parse_json.py:  带注释的json文件解析封装类
		singleton.py:  线程安全的单例基类封装

websocketserver:
		handler.py:  websocket请求的实际消息处理接口，用户需求不同，该文件实现可不同，此处只为参考
		manager.py:  websocket连接管理类
		protocol.py: websocket通信协议封装类
		route.py:  websocket消息路由封装类


```

