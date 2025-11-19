from pyboot.dataflow.module import Context, Bean
from pyboot.commons.pybatis.pydbc import PydbcTools,Propagation as _Propagation, TX as _tx

from pyboot.commons.utils.utils import str_isEmpty
from pyboot.commons.utils.log import Logger
from pyboot.commons.utils.reflect import get_fullname
from typing import Union,Type,Tuple
from enum import Enum

_prefix = 'context.database'

_config_prefix = 'dataflowx.datasource'

_logger = Logger('dataflowx.context.datasource')

class DataSource:
    def __init__(self, tools:PydbcTools):
        self.tools:PydbcTools = tools
        
    # 万能转发：找不到的属性/方法都落到 _a 上
    def __getattr__(self, name):
        return getattr(self.tools, name)
    
    def getTools(self):
        return self.tools

class Propagation(Enum):    
    """事务传播行为"""
    REQUIRED = _Propagation.REQUIRED.value  # "REQUIRED"        # 支持当前事务，如果不存在则创建新事务
    REQUIRES_NEW = _Propagation.REQUIRES_NEW.value  # "REQUIRES_NEW" # 总是创建新事务
    SUPPORTS = _Propagation.SUPPORTS.value   # "SUPPORTS"        # 支持当前事务，如果不存在则以非事务方式执行
    NOT_SUPPORTED = _Propagation.NOT_SUPPORTED.value # "NOT_SUPPORTED" # 以非事务方式执行，挂起当前事务
    MANDATORY = _Propagation.MANDATORY.value  # "MANDATORY"      # 必须存在当前事务，否则抛出异常
    NEVER = _Propagation.NEVER.value  # "NEVER"              # 必须不存在事务，否则抛出异常

class DataSourceContext:
    @staticmethod
    def getDefaultKey():
        return get_fullname(DataSource)
    
    @staticmethod    
    def getDS(ds_name:str=None)->DataSource:        
        if str_isEmpty(ds_name):
            ds_name = DataSourceContext.getDefaultKey()
                        
        return Context.getContext().getBean(f'{ds_name}')
    
class TransactionManager:
    def __init__(self, ds:DataSource):
        self._pydbc = ds
    
def TX(tx_name:str=None, *, propagation:Propagation=Propagation.REQUIRED,rollback_for:Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception):
    
    if tx_name and isinstance(tx_name, str):
        tx = Bean(tx_name)
    elif tx_name:
        raise Context.ContextException('只能使用TransacrtionManager实例名称作为参数')
    else:
        tx = Bean(get_fullname(TransactionManager))
        
    tx:TransactionManager = tx    
    return _tx(tx._pydbc.getTools(), propagation=propagation, rollback_for=rollback_for)

@Context.Configurationable(prefix=_config_prefix)
def _init_datasource_context(config):
    c = config
    if c:
        default_ok:bool = False
        _default_c = {}
        for k, v in c.items(): 
            if isinstance(v, dict):
                _logger.INFO(f'初始化数据源{_prefix}.{k}[{v}]开始')
                pt = DataSource(PydbcTools(**v))
                Context.getContext().registerBean(f'{k}', pt)
                _logger.INFO(f'初始化数据源{_prefix}.{k}[{v}]={pt}成功')
                if not default_ok:
                    Context.getContext().registerBean(DataSourceContext.getDefaultKey(), pt)
                    default_ok = True
                    _logger.INFO(f'设置默认数据源={pt}')
            else:
                _default_c[k] = v
                
        if _default_c and 'url' in _default_c:            
            pt = DataSource(PydbcTools(**_default_c))
            _logger.INFO(f'初始化DEFAULT数据源{_prefix}.ds[{_default_c}]={pt}成功')
            Context.getContext().registerBean(DataSourceContext.getDefaultKey(), pt)
            _logger.INFO(f'设置默认数据源={pt}')
        
        # 注册默认的TransactionManager实例，作为TX默认事务管理器
        tm:TransactionManager = TransactionManager(DataSourceContext.getDS(DataSourceContext.getDefaultKey()))
        Context.getContext().registerBean(get_fullname(TransactionManager), tm)
        _logger.INFO(f'设置默认TX事务管理器={tm}')
            
    else:
        _logger.INFO('没有配置数据源，跳过初始化')
