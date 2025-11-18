from blues_lib.hook.ProcFactory import ProcFactory

from .processor.Dummy import Dummy

from .processor.Skipper import Skipper
from .processor.Blocker import Blocker

from .processor.MatDeduplicator import MatDeduplicator
from .processor.MatValidator import MatValidator
from .processor.MatNormalizer import MatNormalizer
from .processor.MatLocalizer import MatLocalizer
from .processor.MatSinker import MatSinker
from .processor.MatFilter import MatFilter

class CommandProcFactory(ProcFactory):
  
  _PROC_CLASSES = {
    Dummy.__name__: Dummy,
      
    Skipper.__name__: Skipper,
    Blocker.__name__: Blocker,

    MatDeduplicator.__name__: MatDeduplicator,
    MatValidator.__name__: MatValidator,
    MatNormalizer.__name__: MatNormalizer,
    MatLocalizer.__name__: MatLocalizer,
    MatSinker.__name__: MatSinker,
    MatFilter.__name__: MatFilter,
  }