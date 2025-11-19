from pyboot.dataflow.module import Context
from pyboot.commons.utils.log import Logger
from pyboot.commons.utils.reflect import get_fullname
from pyboot.commons.redis import RedisTools, initRedisWithConfig
from typing import Callable
import functools
from pyboot.commons.utils.utils import str_isEmpty,str_strip,json_to_str
from pyboot.commons.utils.sign import b64_encode
from fastapi import Request

_prefix = 'context.redis'

_logger = Logger('dataflow.module.context.redis')


class RedisTemplate:
    def __init__(self, template:RedisTools):
        self.template=template
        
    def getTemplate(self):
        return self.template
    
    # 万能转发：找不到的属性/方法都落到 _a 上
    def __getattr__(self, name):
        return getattr(self.template, name)

class RedisContext:
    ENABLED:bool = False
    @staticmethod    
    def getTemplate()->RedisTemplate:                
        return Context.getContext().getBean(get_fullname(RedisTemplate))
    
    @staticmethod
    def Lock(lock:str, *, acquire_timeout=10, lock_timeout=600, error:Callable=None):                
        
        def _do_lock_logic(lock, func, *args, **kwargs):            
            lock = str.format(lock, *args, **kwargs)
            _logger.DEBUG(f'使用Lock={lock}')
            t:RedisTemplate = RedisContext.getTemplate()
            t:RedisTools = t.getTemplate()
            
            try:
                return t.do_with_lock(lock_name=lock, acquire_timeout=acquire_timeout, lock_timeout=lock_timeout, func=func, *args, **kwargs)
            except Exception as e:
                if error:
                    error(e,*args, **kwargs)
                else:
                    _logger.WARN(f'调用锁操作失败，{e}')    
        
        def lock_decorator(func: Callable):                                    
            @functools.wraps(func)
            def wrapper(*args, **kwargs):            
                return _do_lock_logic(lock, func, *args, **kwargs)        
            return wrapper
        
        return lock_decorator
        
    @staticmethod ## 过期时间（秒）
    def redis_cache(*,ttl:int=None,prefix:str=None,single:bool=False):
        rs_prefix = None
        if str_isEmpty(prefix):
            rs_prefix = 'context:redis:cache'
        else:
            rs_prefix = str_strip(prefix)        
        def _redis_cache_decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):                
                # 调用原始的路由处理函数
                
                if RedisContext.ENABLED:
                    t:RedisTemplate = RedisContext.getTemplate()
                    t:RedisTools = t.getTemplate()
                    if single:
                        k = rs_prefix
                    else:
                        param = {}          
                        # param.update(kwargs)
                        # param.pop('request', None)
                        for k, v in kwargs.items():
                            if isinstance(v, Request):
                                continue
                            if callable(v):
                                continue
                            
                            param[k] = v
                        
                        k = rs_prefix+':'+b64_encode(json_to_str(param))
                    result = t.getObject(k)
                    if not result:
                        result = await func(*args, **kwargs)
                        t.set(k, result, ttl)
                        _logger.DEBUG(f'没有命中缓存，获取值放入缓存[{k}-{ttl}]=>{result}')
                    else:
                        _logger.DEBUG(f'命中缓存，从缓存中获取值[{k}=>{result}]')
                else:
                    result = await func(*args, **kwargs)
                
                # 在请求处理完成之后执行的逻辑
                # print("After the request is processed")
                return result
            return wrapper
        _logger.DEBUG(f'创建Redis_cache装饰器[{rs_prefix},{single}]=>{_redis_cache_decorator}')            
        return _redis_cache_decorator
    
_config_prefix = 'dataflowx.redis'

@Context.Configurationable(prefix=_config_prefix)
def _init_redis_context(config):
    c = config
    if c:
        _logger.INFO(f'初始化Redis源{_prefix}[{c}]开始')
        r = RedisTemplate(initRedisWithConfig(c))
        Context.getContext().registerBean(get_fullname(RedisTemplate), r)
        _logger.INFO(f'初始化Redis源{_prefix}[{c}]={r}结束')      
        RedisContext.ENABLED = True  
    else:
        _logger.INFO('没有配置Redis源，跳过初始化')

