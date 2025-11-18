from blues_lib.hook.command.CommandProc import CommandProc

class Dummy(CommandProc):
  
  def execute(self)->None:
    '''
    @description: block the flow
    @return: None
    '''
    message:str = self._proc_conf.get('message','dummy')
    entities:list[dict] = self._result.get('data') or []

    if message:
      print(f'[{self.__class__.__name__}] {message}')
      print(f'[{self.__class__.__name__}] {entities}')
