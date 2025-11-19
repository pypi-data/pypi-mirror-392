# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import os
from typing import Sequence, List
from google.protobuf.any_pb2 import Any

from . import logger
from .client import HubClient
from .petrel import PetrelContext
from .base_ctx import BaseContext
from .connector_filter import ConnectorFilter
from .agent_pb2 import LaunchApplicationRequest, LaunchApplicationResult
from .agent_pb2 import ListFilesRequest, ListFilesResult
from .agent_pb2 import DownloadFileRequest, DownloadFileResult
from .agent_pb2 import UploadFileRequest, UploadFileResult


class AgentContext(BaseContext):
    """A context or handle to a Cegal Hub Agent or Agents.
    Connectors may be targeted by providing a ConnectorFilter"""

    def __init__(self, hub_client: HubClient, wellknown_connector_id: str, connector_filter: ConnectorFilter = None):
        """Create an AgentContext from the specified parameters.

        Args:
            hub_client (HubClient): The HubClient which makes client requests to Cegal Hub Server.
            wellknown_connector_id (str): The wellknown string that represents the type of connector. i.e cegal.hub.petrel or cegal.hub.agent etc
            connector_filter (ConnectorFilter, optional): A Connector filter to target a specific instance or instances of a Connector. Defaults to None.
        """
        super().__init__(hub_client, wellknown_connector_id, connector_filter)

    def new_petrel_instance(self, project_path: str = None, petrel_version: int = 2022, license_profile: str = None, read_only: bool = True,
                            wait_for_connect: bool = True, connect_timeout_secs: int = 180):
        """Launch a new instance of Petrel in the background.

        Args:
            project_path (str, optional): The path to a .pet file to ensure Petrel opens with a project already loaded. Defaults to None.
            petrel_version (int, optional): The version of Petrel i.e 2021 or 2022 etc. Defaults to 2022.
            license_profile (str, optional): The license profile name to use If not specified it will try to choose the last selected profile name. Defaults to None.
            read_only (bool, optional): Whether the Petrel project is opened in readonly mode. Defaults to True.
            wait_for_connect (bool, optional): If True this method will not return until Petrel has started up and connected to Cegal Hub Server. Defaults to True.
            connect_timeout_secs (int, optional): The number of seconds the Agent will wait for before assuming that Petrel Connector - Hub Server connection failed.
            Only relevant if wait_for_connect is True. Defaults to 180.

        Raises:
            Exception: If there was an error whilst trying to launch Petrel.

        Returns:
            PetrelContext: A strong handle to the launched instance of Petrel.
        """
        cmdline_args = []
        override_default_args = False
        ocean_env_var = "OCEAN" + str(petrel_version) + "HOME"

        # if need to specify a license profile then need to explicitly set cmdline args and that we are overriding the existing not augmenting
        # same is true if a project path is specified and must also respect the read_only flag
        if license_profile is not None or project_path is not None:
            override_default_args = True
            if license_profile is not None:
                cmdline_args.append("/licensePackage")
                cmdline_args.append(license_profile)
            if read_only and project_path is not None:
                cmdline_args.append("/readonly")
            cmdline_args.append("/quiet")
            cmdline_args.append("/nosplashscreen")
            cmdline_args.append("-exec")
            cmdline_args.append("Cegal.Hub.Main.Module, Cegal.Hub")
            cmdline_args.append("DoWork")
            if project_path is not None:
                cmdline_args.append(project_path)

        try:
            lar = self.launch_application("petrel", cmdline_args=cmdline_args, override_default_args=override_default_args, env_var_override=ocean_env_var,
                                          is_hub_connector=True, wait_for_connect=wait_for_connect, connect_timeout_secs=connect_timeout_secs)
            cf = ConnectorFilter(target_connector_id=lar.connector_id)
            petrel = PetrelContext(self._hub_client, "cegalhub.petrel", cf)
            if wait_for_connect:
                logger.info(f"Petrel version '{petrel_version}' successfully started!")
            else:
                logger.info(f"Petrel version '{petrel_version}' has been launched but will take some time to connect!")
            return petrel
        except Exception:
            raise Exception("Error launching Petrel")

    def list_files(self, path: str, suffix: str = "", timeout: int = 60, recursive: bool = False, skip_folder_starts_with: List[str] = [], skip_folder_contains=[]):
        """List the files seen by the Agent on the directory path provided.

        Args:
            path (str): The path directory to search on the Agent
            suffix (str, optional): An optional file suffix to filter search results. Defaults to "".
            timeout (int, optional): The maximum time in seconds to wait for the results of the search. Defaults to 60.
            recursive (bool, optional): Recursively search the directory specified in the path. Defaults to False.
            skip_folder_starts_with (List[str], optional): Skip folders that start with the given string. Defaults to [].
            skip_folder_contains (list, optional): Skip folders that contain the given string. Defaults to [].

        Raises:
            Exception: If there was an error during the list files search.

        Returns:
            ListFilesResult: An object containing the files found during the list files search.
        """
        msg = ListFilesRequest()
        msg.root_path = path
        msg.suffix = suffix
        msg.timeout_secs = timeout
        msg.recursive = recursive

        for sfs in skip_folder_starts_with:
            msg.skip_folder_starts_with.append(sfs)

        for sfc in skip_folder_contains:
            msg.skip_folder_contains.append(sfc)

        payload = Any()
        payload.Pack(msg)
        logger.info("attempting to find files on an agent this may take a while...")

        # reassemble a single find files message from the stream
        single = ListFilesResult()

        responses = self._hub_client.do_server_streaming("cegal.hub.agent", "cegal.hub.agent.list_files", payload, connector_filter=self.connector_filter, major_version=1, minor_version=0)
        cid = ""
        for ok, resp, connector_id in responses:
            if not ok:
                logger.warning(f"error finding files: {resp} on connector_id {connector_id}")
                raise Exception(f"error from Agent find files: {resp} on connector_id {connector_id}")
            cid = connector_id
            data = ListFilesResult()
            resp.Unpack(data)
            single.num_dirs_searched = data.num_dirs_searched
            single.num_dirs_skipped = data.num_dirs_skipped
            single.num_errors = data.num_errors
            single.num_results = data.num_results
            if data.paths is not None:
                for p in data.paths:
                    single.paths.append(p)
        logger.info(f"finding files finished on connector_id {cid}")
        return single

    def launch_application(self, profile_name: str, cmdline_args: Sequence = None, override_default_args: bool = False,
                           env_var_override: str = None, is_hub_connector: bool = False, wait_for_connect: bool = False, connect_timeout_secs: int = 120):
        """Lauch an application profile with the given name from the Agent.

        Args:
            profile_name (str): The name of the application profile
            cmdline_args (Sequence, optional): Additional cmdline arguments to those in the application profile. Defaults to None.
            override_default_args (bool, optional): Override the default profile cmdline arguments with those specified in cmdline_args. Defaults to False.
            env_var_override (str, optional): Override the environment variable name in the profile (if one was specified). Defaults to None.
            is_hub_connector (bool, optional): Inform the Agent that the application profile corresponds to Cegal Hub Connector and wait for the Connector
            to join accordingly. Defaults to False.
            wait_for_connect (bool, optional): True if the profile corresponds to a Cegal Hub Connector and should wait for the Connector to connect. Defaults to False.
            connect_timeout_secs (int, optional): The number of seconds to wait before assuming the Connector connect has failed. Only relevant if the application profile
            name corresponds to a Connector. Defaults to 120.

        Raises:
            Exception: If there was a problem launching the application profile.

        Returns:
            LaunchApplicationResult: An object representing the result of launching an application profile
        """
        if profile_name is None:
            raise Exception("You must specify an application profile name")

        msg = LaunchApplicationRequest()

        msg.profile_name = profile_name
        if env_var_override is not None:
            msg.env_var_override = env_var_override

        if cmdline_args is not None:
            for arg in cmdline_args:
                msg.args.append(arg)

        if wait_for_connect:
            is_hub_connector = True

        msg.override_default_args = override_default_args
        msg.is_hub_connector = is_hub_connector
        msg.wait_for_connect = wait_for_connect
        msg.connect_timeout_secs = connect_timeout_secs
        payload = Any()
        payload.Pack(msg)
        logger.info(f"attempting to launch {profile_name} on an agent this may take a while...")
        ok, result, connector_id = self._hub_client.do_unary_request("cegal.hub.agent", "cegal.hub.agent.launch_application", payload,
                                                                     connector_filter=self.connector_filter, major_version=1, minor_version=0)
        if (ok):
            response = LaunchApplicationResult()
            result.Unpack(response)
            logger.debug(response)
            return response
        else:
            logger.warning(f"failed to launch application profile {profile_name}: {result} on connector_id {connector_id}")
            raise Exception(f"failed to launch application profile {profile_name}: {result} on connector_id {connector_id}")

    def upload_file(self, src_path: str, rel_dest_path: str = None, abs_dest_path: str = None, overwrite: bool = False):
        """upload a file to a Cegal Hub Agent if the Cegal Hub Agent permits file upload. A file can be uploaded by only specifying the src file and the file will be uploaded
        to the default directory. The second alternative is to specify a relative destination path in addition to the src file path which will be the relative path from the
        default Agent upload directory. The last alternative is to specify an absolute path for upload on the Agent (again the Agent must support this).

        Args:
            src_path (str): the src path of the file on the client
            rel_dest_path (str): the relative path to the default file upload shared path on the Agent (if permitted by the Agent)
            abs_dest_path (str): the absolute path to upload to on the Agent (if permitted by the Agent)
            overwrite (bool, optional): whether or not you to overwrite the file if already existing on the Agent (if permitted by the Agent). Defaults to False.

        Raises:
            Exception: if there is an issue uploading the file
            

        Returns:
            UploadFileResult: the empty upload result message if successful
        """
        if src_path is None:
            raise Exception("src_path not specified!")
        if rel_dest_path is not None and abs_dest_path is not None:
            raise Exception("cannot specify both a relative destination path and an absolute destination path")
        relative = True
        if abs_dest_path is not None:
            relative = False
            dest_path = abs_dest_path
        elif rel_dest_path is not None:
            dest_path = rel_dest_path
        else:
            # construct the relative path from filename alone
            dest_path = os.path.basename(src_path)

        # check if the file exists
        path_exists = os.path.exists(src_path)

        if path_exists is False:
            raise Exception(f"file '{src_path}' does not exist ")
        else:
            # msg = UploadFileRequest()
            # msg.overwrite = overwrite
            # msg.open_on_complete = open_file_on_complete
            
            ok, result, connector_id = self._hub_client.do_client_streaming("cegal.hub.agent", "cegal.hub.agent.upload_file",
                                                                            _upload_message_from_file(src_path, dest_path, overwrite, relative),
                                                                            connector_filter=self.connector_filter, major_version=1, minor_version=0)
            if (ok):
                response = UploadFileResult()
                result.Unpack(response)
                logger.debug(response)
                return response
            else:
                logger.warning(f"failed to upload file {src_path}: to agent {result} on connector_id {connector_id}")
                raise Exception(f"failed to upload file {src_path}: to agent {result} on connector_id {connector_id}")

    def download_file(self, src_path: str, dest_path: str, overwrite: bool = False):
        """Download a file from a Cegal Hub Agent (if permitted by the Agent).

        Args:
            src_path (str): the src path of the file on the Agent
            dest_path (str): the destination path to save the file locally.
            overwrite (bool, optional): Whether or not to permit file overwrite if the file exists locally. Defaults to False.

        Raises:
            Exception: If there was an issue downloading the file.
        """
        if src_path is None or dest_path is None:
            raise Exception("both src_path and dest_path must be specified")
        path_exists = os.path.exists(dest_path)
        if path_exists is True and overwrite is False:
            raise Exception(f"the destination file '{dest_path}' already exists but overwrite is not specified")
        msg = DownloadFileRequest()
        msg.path = src_path
        payload = Any()
        payload.Pack(msg)

        try:
            with open(dest_path, 'wb') as f:
                responses = self._hub_client.do_server_streaming("cegal.hub.agent", "cegal.hub.agent.download_file", payload,
                                                                 connector_filter=self.connector_filter, major_version=1, minor_version=0)
                cid = ""
                for ok, resp, connector_id in responses:
                    if not ok:
                        logger.warning(f"error downloading file: {resp} on connector_id {connector_id}")
                        raise Exception(f"error from Agent download file: {resp} on connector_id {connector_id}")
                    cid = connector_id
                    data = DownloadFileResult()
                    resp.Unpack(data)
                    f.write(data.file_bytes)
                logger.debug(f"download file finished on connector_id {cid}")
        except Exception as error:
            path_exists = os.path.exists(dest_path)
            os.remove(path=dest_path)
            raise Exception(error)
        return


def _upload_message_from_file(filename, dest_path, overwrite, relative):
    one_time = False
    with open(filename, "rb") as f:
        while True:
            msg = UploadFileRequest()
            if relative:
                msg.relative_path = dest_path
            else:
                msg.absolute_path = dest_path
            msg.overwrite = overwrite
            bytes = f.read(1024)
            msg.file_bytes = bytes
            payload = Any()
            payload.Pack(msg)
            if not bytes and one_time:
                break
            one_time = True
            yield (payload)
