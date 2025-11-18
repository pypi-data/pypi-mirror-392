import uvicorn
from pyboot.commons.utils.log import Logger, initLogWithYaml
from pyboot.commons.utils.file import get_file_with_profile
from pyboot.commons.utils.utils import str_isEmpty
from pyboot.commons.utils.config import YamlConfigation  # noqa: F401
import logging
from pyboot.commons.utils.utils import parse_long_args_plus,set_cn_timezone
from pathlib import Path
import importlib.metadata

set_cn_timezone()

# 设置时区（必须在导入其他时间相关模块前设置）
# os.environ["TZ"] = "Asia/Shanghai"
# if hasattr(time, 'tzset'):          # Unix / macOS / WSL
#     time.tzset()
    
    
# if os.name == 'posix':    
#     time.tzset()  # 使时区生效（仅 Unix 系统有效）

# port=45080

### USE python3.6.8
# async def run_server():
#     config = Config("main:app", host="0.0.0.0", port=port)
#     server = Server(config)
#     await server.serve()

# print(f'Start http server on {port}')
# # 在 Python 3.6.8 中运行
# try:
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(run_server())
# except KeyboardInterrupt:
#     print('CTRL+C to quit')
# except Exception as e:
#     print('Exit 1 with error {e}', e)

### USE python3.12.10

# initLogWithYaml('conf/logback.yaml')


class ApplicationBoot:
    scan:str
    application_yaml:str
    applicationConfig:YamlConfigation
    configuration:dict
    @staticmethod
    def Start(application_yaml:str='conf/application.yaml', scan:str|list[str]='application.**', configuration:dict=parse_long_args_plus()):
                
        if 'config' in configuration and not str_isEmpty(configuration['config']):
            application_yaml = configuration['config']
            
        ApplicationBoot.application_yaml = application_yaml
        ApplicationBoot.scan = scan
        
        if 'port' in configuration and not str_isEmpty(configuration['port']):
            configuration['application.server.port'] = configuration['port']
        
        if 'host' in configuration and not str_isEmpty(configuration['host']):
            configuration['application.server.host'] = configuration['host']
            
        if 'workers' in configuration and not str_isEmpty(configuration['workers']):
            configuration['application.server.workers'] = configuration['workers']
            
            
        server_name = 'pyboot-server'
        version = importlib.metadata.version('pyboot-dataflow')
        
        if 'server' in configuration and not str_isEmpty(configuration['server']):
            configuration['application.server.name'] = configuration['server']
                            
        _c:YamlConfigation = ApplicationBoot._prepareApplicationConfig(application_yaml, configuration)
        
        ApplicationBoot.applicationConfig = _c
        ApplicationBoot.configuration = configuration
        
        host = _c.getStr('application.server.host', 'localhost')
        workers = _c.getInt('application.server.workers', 1)        
        port = _c.getInt('application.server.port', 9000)
        server_name = _c.getStr('application.server.name', server_name)
        

        log_config = _c.getStr('logging.config', None)
        if  log_config is not None and  log_config.strip()!='':
            initLogWithYaml(log_config)
            print(f'LOG Config : {log_config}')

        log_level = _c.getStr('logging.level', None)
        if  log_level is not None and  log_level.strip()!='':
            logging.basicConfig(level=log_level)
            print(f'LOG Level : {log_level}')

        _logger = Logger("dataflow.boot")
        
        _logger.INFO(f"{_c.getStr('application.name', 'Pyboot DataFlow Application')} {_c.getStr('application.version', '1.0.0')} Start server on {host}:{port}")
        uvicorn.run("pyboot.dataflow.router.endpoint:app", host=host, port=port, reload=False, workers=workers, headers=[("Server", f"{server_name}/{version}")])
        _logger.INFO(f"{_c.getStr('application.name', 'Pyboot DataFlow Application')} {_c.getStr('application.version', '1.0.0')} End server on {host}:{port}")        
        
    @staticmethod
    def _prepareApplicationConfig(application_yaml:str='conf/application.yaml', configuration:dict={})->YamlConfigation:
        _c:YamlConfigation = YamlConfigation.loadConfiguration(application_yaml)
        
        if 'profile' in configuration:
            application_profile = configuration['profile']
        else:
            application_profile = _c.getStr('application.profiles.active')       
            
        print(f'启动Profile={application_profile}')                 
        
        if not str_isEmpty(application_profile):
            application_profile:Path = get_file_with_profile(application_yaml, application_profile)
            if application_profile.exists():
                _c.mergeFile(application_profile)
        
        _c.mergeDict(configuration)
        return _c