from abc import ABC,abstractmethod
from blues_lib.command.NodeCommand import NodeCommand
from blues_lib.type.model.Model import Model
from blues_lib.type.output.STDOut import STDOut
from blues_lib.hook.command.CommandHook import CommandHook

class LoopCommand(NodeCommand,ABC):

  NAME = None

  def _setup(self)->bool: 
    super()._setup()
    self._loop:dict = self._config.get('loop') or {}
    self._entities:list[dict] = self._loop.get('entities') or []
    self._map:dict = self._loop.get('map') or {}
    self._count:int = int(self._loop.get('count') or -1)
  
  def _invoke(self)->STDOut:
    items:list[dict] = []
    if self._entities:
      items = self._run()
    else:
      items = self._run_once(self._model)

    if not items:
      raise ValueError(f'{self.NAME} faild to execute, got zero items')

    return STDOut(200,'ok',items)
  
  def _run(self)->list[dict]:
    items:list[dict] = []
    for entity in self._entities:
      model = self._get_loop_model(entity)
      sub_items = self._run_once(model,entity)
      if not sub_items:
        continue

      items.extend(sub_items)
      
      if self._count > 0 and len(items) >= self._count:
        break
    
    return items

  def _run_once(self,model:Model,entity:dict|None=None)->list[dict]:
    self._before_each_invoked()
    output:STDOut = self._run_once_cal(model)
    result:dict = self._get_once_result(output,entity)
    
    self._logger.info(f'{self.NAME} once result: {result}')
    self._after_each_invoked(result)
    return result['data']
  
  @abstractmethod
  def _run_once_cal(self,model:Model)->STDOut:
    pass

  def _get_loop_model(self,entity:dict)->Model:
    # don't update the original bizdata
    bizdata:dict = self._model.bizdata.copy() 
    meta:dict = self._model.meta.copy()

    if self._map:    
      for entity_key,bizdata_key in self._map.items():
        bizdata[bizdata_key] = entity.get(entity_key)
    else:
      # bizdata and entity has the same field names
      for key,value in entity.items():
        bizdata[key] = value
    
    return Model(meta,bizdata)
  
  def _get_loop_items(self,items:list[dict],entity:dict)->list[dict]:
    filter_entity = {k:v for k,v in entity.items() if k not in self._map.keys()}
    merged_items:list[dict] = []
    for item in items:
      # llm输出优先
      merged = {**filter_entity,**item}
      merged_items.append(merged)
    return merged_items
  
  def _get_once_result(self,output:STDOut,entity:dict|None=None)->dict:
    code:int = output.code
    data:any = output.data
    if code == 200 and data:
      items:list[dict] = data if isinstance(data,list) else [data]
      merged_items = self._get_loop_items(items,entity) if entity else items
      output.data = merged_items
    else:
      output.data = []
    return output.to_dict()

  def _before_each_invoked(self)->None:
    hook_defs:list[dict] = self._task_def.get('before_each_invoked')
    options:dict = {'ti':self._ti}
    CommandHook(hook_defs,options).execute()

  def _after_each_invoked(self,result:dict)->None:
    # update the items directly 
    hook_defs:list[dict] = self._task_def.get('after_each_invoked')
    options:dict = {'ti':self._ti,'result':result}
    CommandHook(hook_defs,options).execute()