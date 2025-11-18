from blues_lib.command.FlowCommand import FlowCommand
from blues_lib.namespace.CommandName import CommandName
from blues_lib.type.output.STDOut import STDOut

class Loop(FlowCommand):

  NAME = CommandName.Flow.LOOP

  def _run(self)->STDOut:

    loop:dict = self._config.get('loop') or {}
    entities:list[dict] = loop.get('entities') or []
    count:int = int(loop.get('count') or -1)
    
    if not entities:
      raise Exception(f'{self.NAME} must have loop entities')

    # one by one
    items:list[dict] = []
    for entity in entities:
      sub_items:list[dict] = self._run_one([entity])
      items.extend(sub_items)

      if count > 0 and len(items) >= count:
        break

    if not items:
      raise ValueError(f'{self.NAME} faild to execute, got zero items')

    return STDOut(200,'ok',items)

  def _run_one(self,start_data:any=None)->list[dict]:
    start_bizdata = {"data":start_data} if start_data else None
    task_defs:list[dict] = self._get_tasks_with_start(start_bizdata)
    result:dict = self._run_flow(task_defs)
    return result.get('data') or []
  