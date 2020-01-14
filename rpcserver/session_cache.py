# coding=utf-8
"""
author = jamon
"""


from share.singleton import Singleton


class SessionCache(object, metaclass=Singleton):

    def __init__(self):
        self.cache = {}   # {session_id: {NodeType1:node_id, ...}, ...} 该会话和各类型节点的缓存关系

    def add_cache(self, session_id, node_type, node_id):
        if session_id not in self.cache.keys():
            self.cache[session_id] = {node_type: node_id}
        else:
            self.cache[session_id][node_type] = node_id

    def del_cache(self, session_id):
        if session_id in self.cache:
            self.cache.pop(session_id)

    def get_node(self, session_id, node_type):
        return self.cache.get(session_id, {}).get(node_type, None)

