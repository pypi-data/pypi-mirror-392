from blues_lib.command.FlowCommand import FlowCommand
from blues_lib.namespace.CommandName import CommandName
from blues_lib.type.output.STDOut import STDOut

class Engine(FlowCommand):

  NAME = CommandName.Flow.ENGINE

  def _run(self)->STDOut: 
    result:dict = self._run_flow(self._task_defs)
    code:int = result.get('code') or 500
    message:str = result.get('message') or ''
    data:any = result.get('data')
    detail:any = result.get('detail')
    return STDOut(code,message,data,detail)
  