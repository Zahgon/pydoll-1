from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional

from pydoll.protocol.base import Command
from pydoll.protocol.page.methods import (
    AddCompilationCacheParams,
    AddScriptToEvaluateOnNewDocumentParams,
    CaptureScreenshotParams,
    CaptureSnapshotParams,
    CreateIsolatedWorldParams,
    EnableParams,
    GenerateTestReportParams,
    GetAdScriptAncestryIdsParams,
    GetAppIdParams,
    GetAppManifestParams,
    GetOriginTrialsParams,
    GetPermissionsPolicyStateParams,
    GetResourceContentParams,
    HandleJavaScriptDialogParams,
    NavigateParams,
    NavigateToHistoryEntryParams,
    PageMethod,
    PrintToPDFParams,
    ProduceCompilationCacheParams,
    ReloadParams,
    RemoveScriptToEvaluateOnNewDocumentParams,
    ScreencastFrameAckParams,
    SearchInResourceParams,
    SetAdBlockingEnabledParams,
    SetBypassCSPParams,
    SetDocumentContentParams,
    SetFontFamiliesParams,
    SetFontSizesParams,
    SetInterceptFileChooserDialogParams,
    SetLifecycleEventsEnabledParams,
    SetPrerenderingAllowedParams,
    SetRPHRegistrationModeParams,
    SetSPCTransactionModeParams,
    SetWebLifecycleStateParams,
    StartScreencastParams,
)
from pydoll.protocol.page.types import (
    CompilationCacheParams,
    FontFamilies,
    FontSizes,
    ScriptFontFamilies,
)

if TYPE_CHECKING:
    from pydoll.protocol.page.methods import (
        AddCompilationCacheCommand,
        AddScriptToEvaluateOnNewDocumentCommand,
        BringToFrontCommand,
        CaptureScreenshotCommand,
        CaptureSnapshotCommand,
        ClearCompilationCacheCommand,
        CloseCommand,
        CrashCommand,
        CreateIsolatedWorldCommand,
        DisableCommand,
        EnableCommand,
        GenerateTestReportCommand,
        GetAdScriptAncestryIdsCommand,
        GetAppIdCommand,
        GetAppManifestCommand,
        GetFrameTreeCommand,
        GetInstallabilityErrorsCommand,
        GetLayoutMetricsCommand,
        GetNavigationHistoryCommand,
        GetOriginTrialsCommand,
        GetPermissionsPolicyStateCommand,
        GetResourceContentCommand,
        GetResourceTreeCommand,
        HandleJavaScriptDialogCommand,
        NavigateCommand,
        NavigateToHistoryEntryCommand,
        PrintToPDFCommand,
        ProduceCompilationCacheCommand,
        ReloadCommand,
        RemoveScriptToEvaluateOnNewDocumentCommand,
        ResetNavigationHistoryCommand,
        ScreencastFrameAckCommand,
        SearchInResourceCommand,
        SetAdBlockingEnabledCommand,
        SetBypassCSPCommand,
        SetDocumentContentCommand,
        SetFontFamiliesCommand,
        SetFontSizesCommand,
        SetInterceptFileChooserDialogCommand,
        SetLifecycleEventsEnabledCommand,
        SetPrerenderingAllowedCommand,
        SetRPHRegistrationModeCommand,
        SetSPCTransactionModeCommand,
        SetWebLifecycleStateCommand,
        StartScreencastCommand,
        StopLoadingCommand,
        StopScreencastCommand,
        WaitForDebuggerCommand,
    )
    from pydoll.protocol.page.types import (
        AutoResponseMode,
        ReferrerPolicy,
        ScreencastFormat,
        ScreenshotFormat,
        TransferMode,
        TransitionType,
        Viewport,
        WebLifecycleState,
    )


class PageCommands:
    """
    This class encapsulates the page commands of the Chrome DevTools Protocol (CDP).

    CDP's Page domain allows for interacting with browser pages, including navigation,
    content manipulation, and page state monitoring. These commands provide powerful
    capabilities for web automation, testing, and debugging.

    The commands defined in this class provide functionality for:
    - Navigating to URLs and managing page history
    - Capturing screenshots and generating PDFs
    - Handling JavaScript dialogs
    - Enabling and controlling page events
    - Managing download behavior
    - Manipulating page content and state
    """

    @staticmethod
    def add_script_to_evaluate_on_new_document(
        source: str,
        world_name: Optional[str] = None,
        include_command_line_api: Optional[bool] = None,
        run_immediately: Optional[bool] = None,
    ) -> AddScriptToEvaluateOnNewDocumentCommand:
        """
        Creates a command to add a script that will be evaluated when a new document is created.

        Args:
            source (str): Script source to be evaluated when a new document is created.
            world_name (Optional[str]): If specified, creates an isolated world with the given name.
            include_command_line_api (Optional[bool]): Whether to include command line API.
            run_immediately (Optional[bool]): Whether to run the script immediately on
                existing contexts.

        Returns:
            AddScriptToEvaluateOnNewDocumentCommand: Command object with the identifier
                of the added script.
        """
        params = AddScriptToEvaluateOnNewDocumentParams(source=source)
        if world_name is not None:
            params['worldName'] = world_name
        if include_command_line_api is not None:
            params['includeCommandLineAPI'] = include_command_line_api
        if run_immediately is not None:
            params['runImmediately'] = run_immediately

        return Command(method=PageMethod.ADD_SCRIPT_TO_EVALUATE_ON_NEW_DOCUMENT, params=params)

    @staticmethod
    def bring_to_front() -> BringToFrontCommand:
        """
        Brings the page to front.
        """
        pass

    @staticmethod
    def capture_screenshot(
        format: Optional[ScreenshotFormat] = None,
        quality: Optional[int] = None,
        clip: Optional[Viewport] = None,
        from_surface: Optional[bool] = None,
        capture_beyond_viewport: Optional[bool] = None,
        optimize_for_speed: Optional[bool] = None,
    ) -> CaptureScreenshotCommand:
        """
        Creates a command to capture a screenshot of the current page.

        Args:
            format (Optional[str]): Image compression format (jpeg, png, or webp).
            quality (Optional[int]): Compression quality from 0-100 (jpeg only).
            clip (Optional[Viewport]): Region of the page to capture.
            from_surface (Optional[bool]): Capture from the surface, not the view.
            capture_beyond_viewport (Optional[bool]): Capture beyond the viewport.
            optimize_for_speed (Optional[bool]): Optimize for speed, not for size.

        Returns:
            CaptureScreenshotCommand: Command object with base64-encoded image data.
        """
        pass

    @staticmethod
    def close() -> CloseCommand:
        """
        Creates a command to close the current page.

        Returns:
            CloseCommand: Command object to close the page.
        """
        return Command(method=PageMethod.CLOSE)

    @staticmethod
    def create_isolated_world(
        frame_id: str,
        world_name: Optional[str] = None,
        grant_universal_access: Optional[bool] = None,
    ) -> CreateIsolatedWorldCommand:
        """
        Creates a command to create an isolated world for the given frame.

        Args:
            frame_id (str): ID of the frame in which to create the isolated world.
            world_name (Optional[str]): Name to be reported in the Execution Context.
            grant_universal_access (Optional[bool]): Whether to grant universal access.

        Returns:
            CreateIsolatedWorldCommand: Command object with the execution context ID.
        """
        pass

    @staticmethod
    def disable() -> DisableCommand:
        """
        Creates a command to disable page domain notifications.

        Returns:
            DisableCommand: Command object to disable the Page domain.
        """
        return Command(method=PageMethod.DISABLE)

    @staticmethod
    def enable(
        enable_file_chooser_opened_event: Optional[bool] = None,
    ) -> EnableCommand:
        """
        Creates a command to enable page domain notifications.

        Args:
            enable_file_chooser_opened_event (Optional[bool]): Whether to emit
                Page.fileChooserOpened event.

        Returns:
            EnableCommand: Command object to enable the Page domain.
        """
        params = EnableParams()
        if enable_file_chooser_opened_event is not None:
            params['enableFileChooserOpenedEvent'] = enable_file_chooser_opened_event

        return Command(method=PageMethod.ENABLE, params=params)

    @staticmethod
    def get_app_manifest(
        manifest_id: Optional[str] = None,
    ) -> GetAppManifestCommand:
        """
        Creates a command to get the manifest for the current document.

        Returns:
            GetAppManifestCommand: Command object with manifest information.
        """
        pass

    @staticmethod
    def get_frame_tree() -> GetFrameTreeCommand:
        """
        Creates a command to get the frame tree for the current page.

        Returns:
            GetFrameTreeCommand: Command object with frame tree information.
        """
        pass

    @staticmethod
    def get_layout_metrics() -> GetLayoutMetricsCommand:
        """
        Creates a command to get layout metrics for the page.

        Returns:
            GetLayoutMetricsCommand: Command object with layout metrics.
        """
        pass

    @staticmethod
    def get_navigation_history() -> GetNavigationHistoryCommand:
        """
        Creates a command to get the navigation history for the current page.

        Returns:
            GetNavigationHistoryCommand: Command object with navigation history.
        """
        pass

    @staticmethod
    def handle_javascript_dialog(
        accept: bool, prompt_text: Optional[str] = None
    ) -> HandleJavaScriptDialogCommand:
        """
        Creates a command to handle a JavaScript dialog.

        Args:
            accept (bool): Whether to accept or dismiss the dialog.
            prompt_text (Optional[str]): Text to enter in prompt dialogs.

        Returns:
            HandleJavaScriptDialogCommand: Command object to handle a JavaScript dialog.
        """
        pass

    @staticmethod
    def navigate(
        url: str,
        referrer: Optional[str] = None,
        transition_type: Optional[TransitionType] = None,
        frame_id: Optional[str] = None,
        referrer_policy: Optional[ReferrerPolicy] = None,
    ) -> NavigateCommand:
        """
        Creates a command to navigate to a specific URL.

        Args:
            url (str): URL to navigate to.
            referrer (Optional[str]): Referrer URL.
            transition_type (Optional[str]): Intended transition type.
            frame_id (Optional[str]): Frame ID to navigate.
            referrer_policy (Optional[str]): Referrer policy.

        Returns:
            NavigateCommand: Command object to navigate to a URL.
        """
        pass

    @staticmethod
    def navigate_to_history_entry(entry_id: int) -> NavigateToHistoryEntryCommand:
        """
        Creates a command to navigate to a specific history entry.

        Args:
            entry_id (int): ID of the history entry to navigate to.

        Returns:
            NavigateToHistoryEntryCommand: Command object to navigate to a history entry.
        """
        pass

    @staticmethod
    def print_to_pdf(  # noqa: PLR0912
        landscape: Optional[bool] = None,
        display_header_footer: Optional[bool] = None,
        print_background: Optional[bool] = None,
        scale: Optional[float] = None,
        paper_width: Optional[float] = None,
        paper_height: Optional[float] = None,
        margin_top: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_right: Optional[float] = None,
        page_ranges: Optional[str] = None,
        header_template: Optional[str] = None,
        footer_template: Optional[str] = None,
        prefer_css_page_size: Optional[bool] = None,
        transfer_mode: Optional[TransferMode] = None,
        generate_tagged_pdf: Optional[bool] = None,
        generate_document_outline: Optional[bool] = None,
    ) -> PrintToPDFCommand:
        """
        Creates a command to print the current page to PDF.

        Args:
            landscape (Optional[bool]): Paper orientation.
            display_header_footer (Optional[bool]): Display header and footer.
            print_background (Optional[bool]): Print background graphics.
            scale (Optional[float]): Scale of the webpage rendering.
            paper_width (Optional[float]): Paper width in inches.
            paper_height (Optional[float]): Paper height in inches.
            margin_top (Optional[float]): Top margin in inches.
            margin_bottom (Optional[float]): Bottom margin in inches.
            margin_left (Optional[float]): Left margin in inches.
            margin_right (Optional[float]): Right margin in inches.
            page_ranges (Optional[str]): Paper ranges to print, e.g., '1-5, 8, 11-13'.
            header_template (Optional[str]): HTML template for the print header.
            footer_template (Optional[str]): HTML template for the print footer.
            prefer_css_page_size (Optional[bool]): Whether to prefer page size as defined by CSS.
            transfer_mode (Optional[str]): Transfer mode.

        Returns:
            PrintToPDFCommand: Command object to print the page to PDF.
        """
        pass

    @staticmethod
    def reload(
        ignore_cache: Optional[bool] = None,
        script_to_evaluate_on_load: Optional[str] = None,
        loader_id: Optional[str] = None,
    ) -> ReloadCommand:
        """
        Creates a command to reload the current page.

        Args:
            ignore_cache (Optional[bool]): If true, browser cache is ignored.
            script_to_evaluate_on_load (Optional[str]): Script to be injected into the page on load.

        Returns:
            ReloadCommand: Command object to reload the page.
        """
        pass

    @staticmethod
    def reset_navigation_history() -> ResetNavigationHistoryCommand:
        """
        Creates a command to reset the navigation history.
        """
        pass

    @staticmethod
    def remove_script_to_evaluate_on_new_document(
        identifier: str,
    ) -> RemoveScriptToEvaluateOnNewDocumentCommand:
        """
        Creates a command to remove a script that was added to be evaluated on new documents.

        Args:
            identifier (str): Identifier of the script to remove.

        Returns:
            RemoveScriptToEvaluateOnNewDocumentCommand: Command object to remove a script.
        """
        pass

    @staticmethod
    def set_bypass_csp(enabled: bool) -> SetBypassCSPCommand:
        """
        Creates a command to toggle bypassing page CSP.

        Args:
            enabled (bool): Whether to bypass page CSP.

        Returns:
            SetBypassCSPCommand: Command object to toggle bypassing page CSP.
        """
        pass

    @staticmethod
    def set_document_content(frame_id: str, html: str) -> SetDocumentContentCommand:
        """
        Creates a command to set the document content of a frame.

        Args:
            frame_id (str): Frame ID to set the document content for.
            html (str): HTML content to set.

        Returns:
            SetDocumentContentCommand: Command object to set the document content.
        """
        pass

    @staticmethod
    def set_intercept_file_chooser_dialog(enabled: bool) -> SetInterceptFileChooserDialogCommand:
        """
        Creates a command to set whether to intercept file chooser dialogs.

        Args:
            enabled (bool): Whether to intercept file chooser dialogs.

        Returns:
            SetInterceptFileChooserDialogCommand: Command object to set file chooser dialog
                interception.
        """
        pass

    @staticmethod
    def set_lifecycle_events_enabled(enabled: bool) -> SetLifecycleEventsEnabledCommand:
        """
        Creates a command to enable/disable lifecycle events.

        Args:
            enabled (bool): Whether to enable lifecycle events.

        Returns:
            SetLifecycleEventsEnabledCommand: Command object to enable/disable lifecycle events.
        """
        pass

    @staticmethod
    def stop_loading() -> StopLoadingCommand:
        """
        Creates a command to stop loading the page.

        Returns:
            StopLoadingCommand: Command object to stop loading the page.
        """
        pass

    @staticmethod
    def add_compilation_cache(url: str, data: str) -> AddCompilationCacheCommand:
        """
        Creates a command to add a compilation cache entry.

        Experimental: This method is experimental and may be subject to change.

        Args:
            url (str): URL for which to add the compilation cache entry.
            data (str): Base64-encoded data.

        Returns:
            AddCompilationCacheCommand: Command object to add a compilation cache entry.
        """
        pass

    @staticmethod
    def capture_snapshot(
        format: Literal['mhtml'] = 'mhtml',
    ) -> CaptureSnapshotCommand:
        """
        Creates a command to capture a snapshot of the page.

        Experimental: This method is experimental and may be subject to change.

        Args:
            format (Literal['mhtml']): Format of the snapshot (only 'mhtml' is supported).

        Returns:
            CaptureSnapshotCommand: Command object to capture a snapshot.
        """
        pass

    @staticmethod
    def clear_compilation_cache() -> ClearCompilationCacheCommand:
        """
        Creates a command to clear the compilation cache.
        """
        pass

    @staticmethod
    def crash() -> CrashCommand:
        """
        Creates a command to crash the page.
        """
        pass

    @staticmethod
    def generate_test_report(
        message: str, group: Optional[str] = None
    ) -> GenerateTestReportCommand:
        """
        Creates a command to generate a test report.

        Experimental: This method is experimental and may be subject to change.

        Args:
            message (str): Message to be displayed in the report.
            group (Optional[str]): Group label for the report.

        Returns:
            GenerateTestReportCommand: Command object to generate a test report.
        """
        pass

    @staticmethod
    def get_ad_script_ancestry_ids(
        frame_id: str,
    ) -> GetAdScriptAncestryIdsCommand:
        """
        Creates a command to get the ad script ancestry IDs for a given frame.

        Experimental: This method is experimental and may be subject to change.

        Args:
            frame_id (str): ID of the frame to get ad script ancestry IDs for.

        Returns:
            GetAdScriptAncestryIdsCommand: Command object to get ad script ancestry IDs.
        """
        pass

    @staticmethod
    def get_app_id(
        app_id: Optional[str] = None, recommended_id: Optional[str] = None
    ) -> GetAppIdCommand:
        """
        Creates a command to get the app ID.

        Experimental: This method is experimental and may be subject to change.

        Args:
            app_id (Optional[str]): App ID for verification.
            recommended_id (Optional[str]): Recommended app ID.

        Returns:
            GetAppIdCommand: Command object to get the app ID.
        """
        pass

    @staticmethod
    def get_installability_errors() -> GetInstallabilityErrorsCommand:
        """
        Creates a command to get the installability errors.
        """
        pass

    @staticmethod
    def get_origin_trials(frame_id: str) -> GetOriginTrialsCommand:
        """
        Creates a command to get origin trials for a given origin.

        Experimental: This method is experimental and may be subject to change.

        Args:
            frame_id (Optional[str]): Frame ID to get trials for.

        Returns:
            GetOriginTrialsCommand: Command object to get origin trials.
        """
        pass

    @staticmethod
    def get_permissions_policy_state(
        frame_id: str,
    ) -> GetPermissionsPolicyStateCommand:
        """
        Creates a command to get the permissions policy state.
        """
        pass

    @staticmethod
    def get_resource_content(
        frame_id: str,
        url: str,
    ) -> GetResourceContentCommand:
        """
        Creates a command to get the resource content.
        """
        pass

    @staticmethod
    def get_resource_tree() -> GetResourceTreeCommand:
        """
        Creates a command to get the resource tree.
        """
        pass

    @staticmethod
    def produce_compilation_cache(
        scripts: list[CompilationCacheParams],
    ) -> ProduceCompilationCacheCommand:
        """
        Creates a command to produce a compilation cache entry.
        """
        pass

    @staticmethod
    def screencast_frame_ack(
        session_id: int,
    ) -> ScreencastFrameAckCommand:
        """
        Creates a command to acknowledge a screencast frame.
        """
        pass

    @staticmethod
    def search_in_resource(
        frame_id: str,
        url: str,
        query: str,
        case_sensitive: Optional[bool] = None,
        is_regex: Optional[bool] = None,
    ) -> SearchInResourceCommand:
        """
        Creates a command to search for a string in a resource.
        """
        pass

    @staticmethod
    def set_ad_blocking_enabled(
        enabled: bool,
    ) -> SetAdBlockingEnabledCommand:
        """
        Creates a command to set ad blocking enabled.
        """
        pass

    @staticmethod
    def set_font_families(
        font_families: FontFamilies,
        for_scripts: list[ScriptFontFamilies],
    ) -> SetFontFamiliesCommand:
        """
        Creates a command to set font families.
        """
        pass

    @staticmethod
    def set_font_sizes(
        font_sizes: FontSizes,
    ) -> SetFontSizesCommand:
        """
        Creates a command to set font sizes.
        """
        pass

    @staticmethod
    def set_prerendering_allowed(
        is_allowed: bool,
    ) -> SetPrerenderingAllowedCommand:
        """
        Creates a command to set prerendering allowed.
        """
        pass

    @staticmethod
    def set_rph_registration_mode(
        mode: AutoResponseMode,
    ) -> SetRPHRegistrationModeCommand:
        """
        Creates a command to set the RPH registration mode.
        """
        pass

    @staticmethod
    def set_spc_transaction_mode(
        mode: AutoResponseMode,
    ) -> SetSPCTransactionModeCommand:
        """
        Creates a command to set the SPC transaction mode.
        """
        pass

    @staticmethod
    def set_web_lifecycle_state(
        state: WebLifecycleState,
    ) -> SetWebLifecycleStateCommand:
        """
        Creates a command to set the web lifecycle state.
        """
        pass

    @staticmethod
    def start_screencast(
        format: ScreencastFormat,
        quality: Optional[int] = None,
        max_width: Optional[int] = None,
        max_height: Optional[int] = None,
        every_nth_frame: Optional[int] = None,
    ) -> StartScreencastCommand:
        """
        Creates a command to start a screencast.
        """
        pass

    @staticmethod
    def stop_screencast() -> StopScreencastCommand:
        """
        Creates a command to stop a screencast.
        """
        pass

    @staticmethod
    def wait_for_debugger() -> WaitForDebuggerCommand:
        """
        Creates a command to wait for a debugger.
        """
        pass
