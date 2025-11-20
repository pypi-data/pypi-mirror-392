######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.19.9.1+obcheckpoint(0.2.8);ob(v1)                                                    #
# Generated on 2025-11-19T00:17:31.018583                                                            #
######################################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import typing


class SerializationHandler(object, metaclass=type):
    def serialze(self, *args, **kwargs) -> typing.Union[str, bytes]:
        ...
    def deserialize(self, *args, **kwargs) -> typing.Any:
        ...
    ...

