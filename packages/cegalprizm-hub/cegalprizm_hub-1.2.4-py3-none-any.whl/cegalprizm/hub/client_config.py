# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.

import os


class ClientConfig():
    """Global configuration for the Python client communicating with a running Cegal Hub Server. This is used primarily with ConnectionParameters objects.
    When a ConnectionParameters object is created but no values are provided, the ConnectionParameters object will rely on the ClientConfig and ServerConfig
    global configurations for defaults.
    """

    __use_auth: bool = None

    @staticmethod
    def set_use_auth(use_auth: bool):
        """Update the ClientConfig to use auth or not.

        Args:
            use_auth (bool): True to indicate authentication should be used, False otherwise.
        """
        ClientConfig.__use_auth = use_auth

    @staticmethod
    def get_use_auth():
        """Get the configuration for whether or not to use authentication. This will look for an environment variable called CEGAL_HUB_USE_AUTH
        which it will expect to be set to True or False.

        Returns:
            [bool]: Whether or not to use authentication.
        """
        if ClientConfig.__use_auth is None:
            val = ClientConfig.__get_envvar("CEGAL_HUB_USE_AUTH")
            if val[0]:
                return val[1].lower() == "true"
            else:
                return False
        else:
            return ClientConfig.__use_auth

    @staticmethod
    def is_user_impersonation_active() -> bool:
        """Is a user impersonation token defined.

        Returns:
            [bool]: True if active, false otherwise
        """
        val = ClientConfig.__get_envvar("CEGAL_HUB_IMPERSONATION_TOKEN")
        if val[0]:
            return len(val[1]) > 0 and not val[1].isspace()
        else:
            return False

    @staticmethod
    def set_user_impersonation_token(token: str):
        """Set the predefined impersonation token.

        Args:
            token (str): The impersonation token to use. Set to None to clear the user impersonation token and restore the default behaviour
        """
        if token:
            ClientConfig.__set_envvar("CEGAL_HUB_IMPERSONATION_TOKEN", token)
        else:
            ClientConfig.__set_envvar("CEGAL_HUB_IMPERSONATION_TOKEN", "")

    @staticmethod
    def get_user_impersonation_token() -> str:
        """Get a predefined user impersonation token if defined.

        Returns:
            [str]: The impersonation token, if None no user impersonation token is defined
        """
        val = ClientConfig.__get_envvar("CEGAL_HUB_IMPERSONATION_TOKEN")
        if val[0]:
            return val[1]
        else:
            return None

    @staticmethod
    def __get_envvar(key: str):
        try:
            return (True, os.environ[key])
        except Exception:
            return (False, "")

    @staticmethod
    def __set_envvar(key: str, value: str):
        os.environ[key] = value

    @staticmethod
    def __repr__():
        return "use auth:" + repr(ClientConfig.get_use_auth())
