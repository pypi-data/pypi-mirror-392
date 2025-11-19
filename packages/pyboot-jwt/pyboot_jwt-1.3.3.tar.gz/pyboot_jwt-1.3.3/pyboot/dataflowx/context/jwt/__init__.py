from pyboot.commons.utils.log import Logger
from pyboot.commons.utils.utils import str2Num,l_str,getAttrPlus
from pyboot.dataflow.module import Context, WebContext
from pyboot.dataflow.utils.web.asgi import get_remote_address,getRequestURLPath,getRequestHeader
from abc import ABC, abstractmethod

from pyboot.dataflowx.context.webmvc import filter
from pyboot.commons.jwt import create_jwt_token, verify_jwt_token,JWTExpiredError
from typing import Optional
from fastapi import Request
from fastapi.responses import JSONResponse

_logger = Logger('dataflow.module.context.jwt')

_ttl_minutes = str2Num(Context.Value('${dataflowx.jwt.ttl_minutes:21600}'))
_secret = l_str(Context.Value('${dataflowx.jwt.secret:replace-with-256-bit-secret}'), 32, '0')
_logger.DEBUG(f'JWT参数 ttl_minutes={_ttl_minutes} secret={_secret}')
_SECRET = _secret     # 32 字节以上

@Context.Service()
class JWTService:
    def create_token(self, data:dict|str, ttl_minutes: float = _ttl_minutes, secret:str=_SECRET, scope:str='read write') -> str:            
        # payload = {
        #     'data':data,
        #     'exp': date_datetime_cn() + datetime.timedelta(minutes=ttl_minutes),
        #     'iat': date_datetime_cn(),
        #     'scope': scope
        # }
        # return jwt.encode(payload, secret, algorithm='HS256')
        return create_jwt_token(data, ttl_minutes, secret, scope)


    def verify_token(self, token: str, secret:str=_SECRET) -> dict[str, any]:
        # try:
        #     return jwt.decode(token, secret, algorithms=['HS256'])
        # except jwt.ExpiredSignatureError:
        #     raise JWTExpiredError('token 已过期')
        # except jwt.InvalidTokenError:
        #     raise JWTExpiredError('token 无效')
        return verify_jwt_token(token, secret)
    

class JWTValidatorErrorHandler(ABC):
    @abstractmethod
    def handler_error(self, path:str, request: Request, error:JWTExpiredError)->Optional[any]:
        """当JWT Filter遇到出错，如何对错误进行处理，如果返回None，返回到调用链里，继续进行request请求，返回对象，则作为Response进行返回"""

class DefaultJWTValidatorErrorHandler(JWTValidatorErrorHandler):
    def handler_error(self, path:str, request: Request, error:JWTExpiredError)->Optional[any]:
        _logger.DEBUG(f'{path} JWT验证失败 : {error}')
        return JSONResponse(
            content={"msg": "用户登录过期"},
            status_code=400,
            headers={               # ← 这里加任意头
                "is-session-timeout": "1",
                "is-application-exception": "1",
            },)

_config_prefix = 'dataflowx.web.jwt.filter'
_DefaultJWTValidatorErrorHandler =  DefaultJWTValidatorErrorHandler()

@Context.Configurationable(prefix=_config_prefix)
def _init_jwt_fileter(config):
    c = config
    if not c:
        _logger.DEBUG('JWT配置项目为空，跳过配置')
        return 
        
    def _start_init_config(paths:list[str],excludes:list[str], config):
        _logger.DEBUG(f'JWT配置JWT过滤器，配置项目{config} Paths={paths}, excludes={excludes}')
        
        @filter(path=paths, excludes=excludes)
        async def costtime_handler(request: Request, call_next):
            jwt:JWTService = Context.getContext().getBean(JWTService)            
            # ====== 请求阶段 ======            
            path = getRequestURLPath(WebContext.getRequest())
            _logger.INFO(f"JWT过滤器过滤器==[{request.url}][{path}]")
            
            auth = getRequestHeader(request, 'authorization', None)
            if not auth:
                raise Context.ContextException("没有登录信息，请先进行登录")
            
            auth = auth.replace('Bearer ','')
            _logger.DEBUG(f'authorization = {auth}')
            
            try:
                jwt_object = jwt.verify_token(auth)['data']
                _logger.DEBUG(f'username = {jwt_object}')
                WebContext.setRequestUserObject(jwt_object)
            except JWTExpiredError as e:                
                _logger.DEBUG(f'verify_token={str(e)}')
                handler:JWTValidatorErrorHandler = None
                handler = Context.getContext().getBean(JWTValidatorErrorHandler)
                                
                if handler:                    
                    response = handler.handler_error(path, request, e)
                    if response:
                        return response                    
                else:                
                    _logger.DEBUG('没有找到JWTValidatorErrorHandler注册实例，使用默认处理Handler')
                    return _DefaultJWTValidatorErrorHandler.handler_error(path, request, e)
            except Exception as e:                
                raise e
                # _logger.DEBUG(f'verify_token={str(e)}')
                # return JSONResponse(
                #     content={"msg": "用户登录过期"},
                #     status_code=400,
                #     headers={               # ← 这里加任意头
                #         "is-session-timeout": "1",
                #         "is-application-exception": "1",
                #     },
                # )

            # ====== 继续往后走（路由、业务） ======
            try:
                response = await call_next(request)
                # ====== 响应阶段 ======                
                # response.headers["test-Cost-ms"] = str(cost)
                return response    
            finally:
                ip = get_remote_address(request)
                _logger.INFO(f"JWT过滤器==[{request.url}][{ip}]")
                WebContext.resetRequestUserObject()
    
    _paths = getAttrPlus(config, "paths", None)
    _excludes = getAttrPlus(config, "excludes", None)
    _start_init_config(_paths, _excludes, config)
            
    
    
    
    
    
    
    