# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

from cegalprizm.hub import ClientConfig

from typing import Dict
from . import logger


def _get_hub_user_identity(metadata: Dict[str, str]) -> str:
    if 'identity' in metadata.keys():
        return metadata['identity']
    else:   
        return "anonymous"

def _set_hub_user_access(metadata: Dict[str, str]):
    logger.debug("Setting hub user access")
    # if 'identity' in metadata.keys():
    #     cegal_hub_identity = metadata['identity']
    #     if len(cegal_hub_identity) > 0 and cegal_hub_identity != "anonymous":
    #         ClientConfig.set_use_auth(True)

    if 'impersonationid' in metadata.keys():
        cegal_impersonation_id = metadata['impersonationid']
        logger.debug(f"{cegal_impersonation_id}")
        if len(cegal_impersonation_id) > 0:
            ClientConfig.set_user_impersonation_token(cegal_impersonation_id)


def _clear_hub_user_access():
    logger.debug("Clearing hub user access")
    # ClientConfig.set_use_auth(None)
    ClientConfig.set_user_impersonation_token(None)
