# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import os
import hashlib
import secrets
from google.protobuf.any_pb2 import Any

from cegalprizm.hub import HubClient, ConnectionParameters, ConnectorFilter

from . import logger
from .prizmworkflowrunner_pb2 import DownloadFileRequest, DownloadFileResult, UploadFileRequest, UploadFileResult, HashType


class FileServices:

    @staticmethod
    def download_file(src_path: str, dest_path: str, overwrite: bool = False):
        """Download a file to pycoderunner from the source path

        Args:
            src_path (str): the source path of the file
            dest_path (str): the destination path to save the file on the pycoderunner
            overwrite (bool, optional): Whether or not to permit file overwrite if the file exists on the destination path. Defaults to False.

        Raises:
            ValueError: if there is an issue with the provided arguments
            Exception: If there was an issue downloading the file.
        """
        session_id_env_var = _get_session_id_from_env_var("download_file")

        if not src_path:
            raise ValueError("src_path not specified")

        if not dest_path:
            raise ValueError("dest_path not specified")

        path_exists = os.path.exists(dest_path)
        if path_exists is True and overwrite is False:
            raise ValueError(f"the destination file '{dest_path}' already exists but overwrite is not specified")
        folder_path = os.path.dirname(dest_path)
        random_data = secrets.token_bytes(16)
        filename_hash_object = _get_hash_object(HashType.MD5)
        filename_hash_object.update(random_data)
        temp_file_path = f"{folder_path}/{filename_hash_object.hexdigest()}.tmp"
        msg = DownloadFileRequest()
        msg.session_id = session_id_env_var
        msg.path = src_path
        msg.hash_type = HashType.SHA256
        payload = Any()
        payload.Pack(msg)

        try:
            hash_object = None
            with open(temp_file_path, 'wb') as f:
                logger.debug(f"created temp file: '{temp_file_path}'")
                message_hash = ""
                if msg.hash_type != HashType.NOHASH:
                    hash_object = _get_hash_object(msg.hash_type)
                hub_client = HubClient(connection_parameters=ConnectionParameters())
                logger.debug(f"requesting download of file: '{src_path}'")
                responses = hub_client.do_server_streaming("cegal.hub.petrel", "cegal.prizmworkflowrunner.download_file", payload,
                                                           connector_filter=ConnectorFilter(), major_version=1, minor_version=0)
                for ok, resp, connector_id in responses:
                    if not ok:
                        raise Exception(f"error downloading file: {resp} on connector_id {connector_id}")
                    data = DownloadFileResult()
                    resp.Unpack(data)
                    f.write(data.file_bytes)
                    if hash_object is not None:
                        hash_object.update(data.file_bytes)
                    if data.hash is not None and data.hash != "":
                        message_hash = data.hash
                logger.debug("download file results retrieved")
            file_content_hash = hash_object.hexdigest() if hash_object is not None else ""
            file_content_hash = file_content_hash.replace("-", "").lower()
            if file_content_hash == message_hash:
                logger.debug("download file hash check verified")
                os.replace(temp_file_path, dest_path)
                logger.debug("download file completed")
            else:
                logger.debug(f"download file hash check invalid. downloaded file for destination '{dest_path}', but file checksum '{file_content_hash}' does not match message checksum '{message_hash}'.")
                raise Exception("Cannot verify the hash of the downloaded file. File download not completed.")
        except Exception as error:
            path_exists = os.path.exists(temp_file_path)
            if (path_exists):
                os.remove(path=temp_file_path)
                logger.debug(f"error when downloading file. removed temp file '{temp_file_path}'")
            raise Exception(error)
        return

    @staticmethod
    def upload_file(src_path: str, abs_dest_path: str, overwrite: bool = False, open_file_on_complete: bool = False):
        """Upload a file from the pycoderunner to the destination path

        Args:
            src_path (str): the source path of the file on the pycoderunner
            abs_dest_path (str): the absolute destination path to upload the file to
            overwrite (bool, optional): whether or not you want to overwrite the file if already existing on the destination path. Defaults to False.
            open_file_on_complete (bool, optional): whether or not you want the file to be opened after uploading. Defaults to False.

        Raises:
            ValueError: if there is an issue with the provided arguments
            Exception: if there is an issue uploading the file

        Returns:
            UploadFileResult: the empty upload result message if successful
        """
        session_id_env_var = _get_session_id_from_env_var("upload_file")

        if not src_path:
            raise ValueError("src_path not specified")

        if not abs_dest_path:
            raise ValueError("abs_dest_path not specified")

        if os.path.exists(src_path) is False:
            raise ValueError(f"file src_path:'{src_path}' does not exist")
        else:
            connector_filter = ConnectorFilter()
            connection_parameters = ConnectionParameters()
            hub_client = HubClient(connection_parameters)
            ok, result, connector_id = hub_client.do_client_streaming("cegal.hub.petrel", "cegal.prizmworkflowrunner.upload_file",
                                                                      _upload_message_from_file(src_path, abs_dest_path, overwrite, open_file_on_complete, session_id_env_var),
                                                                      connector_filter=connector_filter, major_version=1, minor_version=0)
            if (ok):
                response = UploadFileResult()
                result.Unpack(response)
                logger.debug(f"upload file finished on connector_id {connector_id}")
                print(f"File uploaded to: {abs_dest_path}")
                return response
            else:
                raise Exception(f"failed to upload file '{src_path}': {result} on connector_id {connector_id}")


def _upload_message_from_file(filename, dest_path, overwrite, open_file_on_complete, session_id_env_var):
    one_time = False
    file_size = os.path.getsize(filename)
    hash_type = HashType.SHA256
    hash_object = _get_hash_object(hash_type)
    with open(filename, "rb") as f:
        while True:
            msg = UploadFileRequest()
            msg.session_id = session_id_env_var
            msg.hash_type = hash_type
            msg.open_on_complete = open_file_on_complete
            msg.absolute_path = dest_path
            msg.overwrite = overwrite
            bytes = f.read(4096)
            hash_object.update(bytes)
            msg.file_bytes = bytes
            if f.tell() == file_size:
                hash = hash_object.hexdigest()
                msg.hash = hash.replace("-", "").lower()
            payload = Any()
            payload.Pack(msg)
            if not bytes and one_time:
                break
            one_time = True
            yield payload


def _get_hash_object(hash_type=HashType.SHA256):
    if hash_type == HashType.SHA256:
        return hashlib.sha256()
    elif hash_type == HashType.MD5:
        return hashlib.md5()


def _get_session_id_from_env_var(method_in_use):
    session_id_env_var = os.environ.get("session_id", None)
    if (session_id_env_var is None):
        logger.debug(f"{method_in_use}: no session_id set for this workflow execution")
        raise Exception(f"Error verifying the session_id, '{__name__}.{method_in_use}' must be used within Prizm Workflow Runner workflow to safely copy files.")
    logger.debug(f"{method_in_use}: session_id successfully retrieved")
    return session_id_env_var
