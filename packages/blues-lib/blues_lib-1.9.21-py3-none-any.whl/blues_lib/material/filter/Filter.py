from copy import deepcopy
from blues_lib.material.MatHandler import MatHandler
from blues_lib.type.output.STDOut import STDOut
from blues_lib.dao.material.MatMutator import MatMutator 

class Filter(MatHandler):

  def resolve(self)->STDOut:
    self._setup()

    if not self._entities:
      raise Exception(f'{self.__class__.__name__} entities is empty')


    # 遍历原列表的副本（用 list(entities) 或 entities[:] 创建副本）
    for item in list(self._entities):

      # must deepcopy to avoid modify the original item (list to string)
      rows:list[dict] = [deepcopy(item)]
      output:STDOut = MatMutator().insert(rows)
      self._logger.info(f'{self.__class__.__name__} insert output: {output}')
      if output.code !=200:
        item['mat_stat'] = 'invalid'
        item['mat_remark'] = output.message

      if item.get("mat_stat") != "available":
        self._entities.remove(item)          # 从原列表删除该元素
        
