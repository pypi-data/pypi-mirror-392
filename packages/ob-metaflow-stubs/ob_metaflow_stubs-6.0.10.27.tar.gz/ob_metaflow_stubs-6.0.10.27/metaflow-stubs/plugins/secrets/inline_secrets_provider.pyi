######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.19.9.1+obcheckpoint(0.2.8);ob(v1)                                                    #
# Generated on 2025-11-19T00:17:30.946629                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import abc
import typing
if typing.TYPE_CHECKING:
    import metaflow.plugins.secrets
    import abc

from . import SecretsProvider as SecretsProvider

class InlineSecretsProvider(metaflow.plugins.secrets.SecretsProvider, metaclass=abc.ABCMeta):
    def get_secret_as_dict(self, secret_id, options = {}, role = None):
        """
        Intended to be used for testing purposes only.
        """
        ...
    ...

