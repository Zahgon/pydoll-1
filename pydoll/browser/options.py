from contextlib import suppress

from pydoll.browser.interfaces import Options
from pydoll.constants import PageLoadState
from pydoll.exceptions import (
    ArgumentAlreadyExistsInOptions,
    ArgumentNotFoundInOptions,
    WrongPrefsDict,
)


class ChromiumOptions(Options):
    """
    A class to manage command-line options for a browser instance.

    This class allows the user to specify command-line arguments and
    the binary location of the browser executable.
    """

    def __init__(self):
        """
        Initializes the Options instance.

        Sets up an empty list for command-line arguments and a string
        for the binary location of the browser.
        """
        self._arguments = []
        self._binary_location = ''
        self._start_timeout = 10
        self._browser_preferences = {}
        self._headless = False
        self._webrtc_leak_protection = False
        self._page_load_state = PageLoadState.COMPLETE

    @property
    def arguments(self) -> list[str]:
        """
        Gets the list of command-line arguments.

        Returns:
            list: A list of command-line arguments added to the options.
        """
        pass

    @arguments.setter
    def arguments(self, args_list: list[str]):
        """
        Sets the list of command-line arguments.

        Args:
            args_list (list): A list of command-line arguments.
        """
        pass

    @property
    def binary_location(self) -> str:
        """
        Gets the location of the browser binary.

        Returns:
            str: The file path to the browser executable.
        """
        pass

    @binary_location.setter
    def binary_location(self, location: str):
        """
        Sets the location of the browser binary.

        Args:
            location (str): The file path to the browser executable.
        """
        pass

    @property
    def start_timeout(self) -> int:
        """
        Gets the timeout to verify the browser's running state.

        Returns:
            int: The timeout in seconds.
        """
        pass

    @start_timeout.setter
    def start_timeout(self, timeout: int):
        """
        Sets the timeout to verify the browser's running state.

        Args:
            timeout (int): The timeout in seconds.
        """
        pass

    def add_argument(self, argument: str):
        """
        Adds a command-line argument to the options.

        Args:
            argument (str): The command-line argument to be added.

        Raises:
            ArgumentAlreadyExistsInOptions: If the argument is already in the list of arguments.
        """
        if argument not in self._arguments:
            self._arguments.append(argument)
        else:
            raise ArgumentAlreadyExistsInOptions(f'Argument already exists: {argument}')

    def remove_argument(self, argument: str):
        """
        Removes a command-line argument from the options.

        Args:
            argument (str): The command-line argument to be removed.

        Raises:
            ArgumentNotFoundInOptions: If the argument is not in the list of arguments.
        """
        pass

    @property
    def browser_preferences(self) -> dict:
        pass

    @browser_preferences.setter
    def browser_preferences(self, preferences: dict):
        pass

    def _set_pref_path(self, path: list, value):
        """
        Safely sets a nested value in self._browser_preferences,
        creating intermediate dicts as needed.

        Arguments:
            path -- List of keys representing the nested
                    path (e.g., ['plugins', 'always_open_pdf_externally'])
            value -- The value to set at the given path
        """
        pass

    def _get_pref_path(self, path: list):
        """
        Safely gets a nested value from self._browser_preferences.

        Arguments:
            path -- List of keys representing the nested
                    path (e.g., ['plugins', 'always_open_pdf_externally'])

        Returns:
            The value at the given path, or None if path doesn't exist
        """
        pass

    def set_default_download_directory(self, path: str):
        """
        Set the default directory where downloaded files will be saved.

        Usage: Sets the 'download.default_directory' preference for Chrome.

        Arguments:
            path: Absolute path to the download destination folder.
        """
        pass

    def set_accept_languages(self, languages: str):
        """
        Set the accepted languages for the browser.

        Usage: Sets the 'intl.accept_languages' preference.

        Arguments:
            languages: A comma-separated string of language codes (e.g., 'pt-BR,pt,en-US,en').
        """
        pass

    @property
    def prompt_for_download(self) -> bool:
        pass

    @prompt_for_download.setter
    def prompt_for_download(self, enabled: bool):
        """
        Enable or disable download prompt confirmation.

        Usage: Sets the 'download.prompt_for_download' preference.

        Arguments:
            enabled: If True, Chrome will ask for confirmation before downloading.
        """
        pass

    @property
    def block_popups(self) -> bool:
        pass

    @block_popups.setter
    def block_popups(self, block: bool):
        """
        Block or allow pop-up windows.

        Usage: Sets the 'profile.default_content_setting_values.popups' preference.

        Arguments:
            block: If True, pop-ups will be blocked (value = 0); otherwise allowed (value = 1).
        """
        pass

    @property
    def password_manager_enabled(self) -> bool:
        pass

    @password_manager_enabled.setter
    def password_manager_enabled(self, enabled: bool):
        """
        Enable or disable Chrome's password manager.

        Usage: Sets the 'profile.password_manager_enabled' preference.

        Arguments:
            enabled: If True, the password manager is active.
        """
        pass

    @property
    def block_notifications(self) -> bool:
        pass

    @block_notifications.setter
    def block_notifications(self, block: bool):
        """
        Block or allow site notifications.

        Usage: Sets the 'profile.default_content_setting_values.notifications' preference.

        Arguments:
            block: If True, notifications will be blocked (value = 2);
            otherwise allowed (value = 1).
        """
        pass

    @property
    def allow_automatic_downloads(self) -> bool:
        pass

    @allow_automatic_downloads.setter
    def allow_automatic_downloads(self, allow: bool):
        """
        Allow or block automatic multiple downloads.

        Usage: Sets the 'profile.default_content_setting_values.automatic_downloads' preference.

        Arguments:
            allow: If True, automatic downloads are allowed (value = 1);
            otherwise blocked (value = 2).
        """
        pass

    @property
    def open_pdf_externally(self) -> bool:
        pass

    @open_pdf_externally.setter
    def open_pdf_externally(self, enabled: bool):
        """
        Block or allow geolocation access.

        Usage: Sets the 'profile.managed_default_content_settings.geolocation' preference.

        Arguments:
            block: If True, location access is blocked (value = 2); otherwise allowed (value = 1).
        """
        pass

    @property
    def headless(self) -> bool:
        pass

    @headless.setter
    def headless(self, headless: bool):
        pass

    @property
    def webrtc_leak_protection(self) -> bool:
        pass

    @webrtc_leak_protection.setter
    def webrtc_leak_protection(self, enabled: bool):
        pass

    @property
    def page_load_state(self) -> PageLoadState:
        pass

    @page_load_state.setter
    def page_load_state(self, state: PageLoadState):
        pass
