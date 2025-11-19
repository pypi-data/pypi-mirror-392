from pyboot.commons.utils.log import Logger
from pyboot.commons.utils.reflect import get_fullname
# from pyboot.commons.pybatis.pydbc import PydbcTools
from pyboot.commons.pybatis.pybatis import Mapper as _Mapper, SELECT as _SELECT, UPDATE as _UPDATE, XMLConfig
from pyboot.dataflowx.context.datasource.datasource import DataSourceContext,DataSource
from pyboot.dataflow.module import Context

_logger = Logger('dataflowx.context.pybatisplus')

def _get_datasource(datasource:str|DataSource=None):
    if datasource:
        if datasource is None or isinstance(datasource, str):
            datasource = DataSourceContext.getDS(datasource)
        elif isinstance(datasource, DataSource):
            datasource = datasource
        else:
            raise KeyError(f'缺少 datasource：{id}')
    else:
        datasource = DataSourceContext.getDS()
            
    return datasource
    

def Mapper(datasource:str|DataSource=None,namespace:str=None, table:str=None, id_col=None):
    datasource = _get_datasource(datasource)
    decorator = _Mapper(datasource.getTools(), namespace=namespace, table=table, id_col=id_col)
    def mapper_decorator(cls):
        wrap = decorator(cls)
        service = wrap()
        service_name = get_fullname(cls)
        Context.getContext().registerBean(service_name=service_name, service=service)
        _logger.DEBUG(f'添加Mapper服务{service_name}=>{service}')
        return wrap
    return mapper_decorator

def Select(datasource:str|DataSource, sql:str=None, *, resultType:type|str=dict):
    datasource = _get_datasource(datasource)        
    return _SELECT(datasource.getTools(), sql=sql, resultType=resultType)

def Update(datasource:str|DataSource, sql:str=None):
    datasource = _get_datasource(datasource)        
    return _UPDATE(datasource.getTools(), sql=sql)


_prefix = 'dataflowx.pybatisplus'


@Context.Configurationable(prefix=_prefix)
def _init_datasource_context(config:dict):
    config.setdefault('root','conf')
    config.setdefault('pattern','/**/*Mapper.xml')    
    root:str = config['root']
    pattern:str = config['pattern']    
    XMLConfig.scan_mapping_xml(root=root, pattern=pattern)