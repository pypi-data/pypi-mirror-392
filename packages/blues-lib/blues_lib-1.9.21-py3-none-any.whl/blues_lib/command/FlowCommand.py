from copy import deepcopy
from abc import ABC,abstractmethod
from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.type.output.STDOut import STDOut
from blues_lib.namespace.CommandName import CommandName
from blues_lib.flow.Flow import Flow

class FlowCommand(NodeCommand,ABC):

  NAME = None

  def _invoke(self)->STDOut:
    if not self._children:
      raise Exception(f'{self.NAME} must have children')
    
    self._task_defs:list[dict] = self._children.get('tasks')
    if not self._task_defs or not isinstance(self._task_defs,list):
      raise Exception(f'{self.NAME} must have children task list')

    return self._run()

  @abstractmethod
  def _run(self)->STDOut: 
    pass
  
  def _run_flow(self,task_defs:list[dict])->dict:
    flow = self._get_flow(task_defs)
    stdout:STDOut = flow.execute() 

    if stdout.code == 200:
      result:dict = flow.last_task_result()
      self._logger.info(f'{self.NAME} last command of suf flow result : {result}')
      return result
    else:
      self._logger.info(f'{self.NAME} Failed to run flow; sub flow error - {stdout.message}')
      return stdout.to_dict()

  def _get_flow(self,task_defs:list[dict])->Flow:
    # avoid circular import
    from blues_lib.flow.FlowFactory import FlowFactory
    flow = FlowFactory(task_defs).create()
    if not flow:
      raise Exception(f'{self.NAME} Failed to create flow')
    return flow

  def _get_tasks_with_start(self,bizdata:dict|None=None)->list[dict]:
    if not bizdata:
      return deepcopy(self._task_defs)

    start_task_def:dict = self._get_start_task(bizdata)
    return [start_task_def] + deepcopy(self._task_defs)
    
  def _get_start_task(self,bizdata:dict)->dict:
    task_def:dict = {
      "id":"start",
      "command":"command.standard.dummy",
      "meta":{
        "summary":{
          "code":"${code}",
          "message":"${message}",
          "data":"${data}",
          "detail":"${detail}"
        }
      },
      "bizdata":bizdata,
    }
    return task_def