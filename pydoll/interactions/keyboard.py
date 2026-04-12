from __future__ import annotations

import asyncio
import logging
import random
import warnings
from dataclasses import dataclass
from typing import Any, Optional, Protocol, cast

from pydoll.commands import InputCommands
from pydoll.constants import (
    CHAR_TO_KEY_INFO,
    DEFAULT_TYPO_PROBABILITY,
    QWERTY_NEIGHBORS,
    Key,
    TypoType,
)
from pydoll.protocol.input.types import KeyEventType, KeyModifier

logger = logging.getLogger(__name__)


class CommandExecutor(Protocol):
    """Protocol for objects that can execute CDP commands."""

    async def _execute_command(self, command: Any) -> Any: ...


@dataclass(frozen=True)
class TypoResult:
    """Result of a typo generation."""

    typo_type: TypoType
    wrong_char: str = ''


@dataclass(frozen=True)
class TimingConfig:
    """Configuration for realistic typing timing."""

    keystroke_min: float = 0.03
    keystroke_max: float = 0.12
    punctuation_min: float = 0.08
    punctuation_max: float = 0.18
    thinking_probability: float = 0.02
    thinking_min: float = 0.3
    thinking_max: float = 0.7
    distraction_probability: float = 0.005
    distraction_min: float = 0.5
    distraction_max: float = 1.2
    mistake_realize_min: float = 0.1
    mistake_realize_max: float = 0.25
    after_correction_min: float = 0.03
    after_correction_max: float = 0.08
    double_press_min: float = 0.02
    double_press_max: float = 0.05
    hesitation_min: float = 0.15
    hesitation_max: float = 0.3


@dataclass(frozen=True)
class TypoConfig:
    """Configuration for typo generation weights."""

    adjacent_weight: float = 0.55
    transpose_weight: float = 0.20
    double_weight: float = 0.12
    skip_weight: float = 0.08
    missed_space_weight: float = 0.05


class Keyboard:
    """
    Keyboard input controller for Tab and WebElement.

    Provides methods for:
    - Tab: Public keyboard simulation (press, down, up, hotkey)
    - WebElement: Private text typing with optional humanization
    """

    PAUSE_CHARS = frozenset(' .,!?;:\n')

    def __init__(
        self,
        executor: CommandExecutor,
        timing: Optional[TimingConfig] = None,
        typo_config: Optional[TypoConfig] = None,
    ):
        """
        Initialize keyboard controller.

        Args:
            executor: Object with _execute_command method (Tab or WebElement).
            timing: Optional custom timing configuration.
            typo_config: Optional custom typo weights configuration.
        """
        self._executor = executor
        self._timing = timing or TimingConfig()
        self._typo_config = typo_config or TypoConfig()
        self._has_focus = hasattr(executor, 'focus')

    async def _ensure_focus(self):
        """Re-focus the executor element before a keystroke if it supports focus."""
        pass

    async def press(
        self,
        key: Key,
        modifiers: Optional[KeyModifier] = None,
        interval: float = 0.1,
    ):
        """
        Press and release a key (down + wait + up).

        Args:
            key: Key to press (from Key enum).
            modifiers: Optional key modifiers (Alt=1, Ctrl=2, Meta=4, Shift=8).
            interval: Time to hold the key down in seconds.

        Example:
            await tab.keyboard.press(Key.ENTER)
            await tab.keyboard.press(Key.A, modifiers=KeyModifier.CTRL)
        """
        pass

    async def down(self, key: Key, modifiers: Optional[KeyModifier] = None):
        """
        Press a key down (without releasing).

        Args:
            key: Key to press down (from Key enum).
            modifiers: Optional key modifiers.
        """
        pass

    async def up(self, key: Key):
        """
        Release a key (key up event).

        Args:
            key: Key to release (from Key enum).
        """
        pass

    async def hotkey(self, key1: Key, key2: Key, key3: Optional[Key] = None):
        """
        Execute a key combination (hotkey) with up to 3 keys.

        Args:
            key1: First key (usually a modifier like Ctrl, Shift, Alt).
            key2: Second key.
            key3: Optional third key.

        Example:
            await tab.keyboard.hotkey(Key.CONTROL, Key.C)  # Ctrl+C
        """
        pass

    async def type_text(
        self,
        text: str,
        humanize: bool = False,
        interval: Optional[float] = None,
    ):
        """
        Type text character by character.

        Args:
            text: Text to type.
            humanize: When True, simulates human-like typing with
                variable delays and occasional typos (~2%).
            interval: Deprecated. Use humanize=True instead.

        Example:
            await tab.keyboard.type_text("Hello World", humanize=True)
            await tab.keyboard.type_text("Hello World")
        """
        pass

    async def _type_text_humanized(self, text: str):
        """Type text with realistic human-like behavior."""
        pass

    async def _type_char(self, char: str):
        """Type a single character, re-focusing the element before each keystroke."""
        pass

    async def _type_backspace(self):
        """Send backspace keypress."""
        pass

    async def _process_char_with_typo(
        self,
        current_char: str,
        next_char: Optional[str],
    ) -> bool:
        """Process character, potentially with typo. Returns True if next should be skipped."""
        pass

    async def _handle_typo(
        self,
        current_char: str,
        next_char: Optional[str],
        typo: TypoResult,
    ) -> bool:
        """Handle typo. Returns True if next char should be skipped."""
        pass

    async def _do_adjacent_typo(self, correct_char: str, wrong_char: str):
        """Type wrong adjacent key, pause, backspace, correct."""
        pass

    async def _do_transpose_typo(self, current_char: str, next_char: str):
        """Type chars in wrong order, then fix."""
        pass

    async def _do_double_typo(self, current_char: str):
        """Type character twice, then backspace."""
        pass

    async def _do_skip_typo(self, current_char: str):
        """Hesitate, then type normally."""
        pass

    async def _do_missed_space_typo(self, space_char: str, next_char: str):
        """Miss space, type next char, realize, go back and fix."""
        pass

    async def _apply_realistic_delay(self, typed_char: str):
        """Apply realistic delay after typing a character."""
        pass

    @staticmethod
    def _should_make_typo() -> bool:
        """Determine if a typo should occur."""
        pass

    def _generate_typo(self, current_char: str, next_char: Optional[str]) -> TypoResult:
        """Generate a realistic typo based on QWERTY layout."""
        pass

    def _select_typo_type(self) -> TypoType:
        """Select typo type based on weights."""
        pass

    def _create_typo(
        self,
        typo_type: TypoType,
        current_char: str,
        next_char: Optional[str],
    ) -> TypoResult:
        """Create typo result based on type."""
        pass

    def _create_transpose_typo(self, current_char: str, next_char: Optional[str]) -> TypoResult:
        """Create transpose typo, falling back to adjacent if not possible."""
        pass

    def _create_missed_space_typo(self, current_char: str) -> TypoResult:
        """Create missed space typo, falling back to adjacent if not a space."""
        pass

    @staticmethod
    def _create_adjacent_typo(original_char: str) -> TypoResult:
        """Create adjacent key typo."""
        pass

    @staticmethod
    def _split_modifiers_and_keys(keys: list[Key]) -> tuple[list[Key], list[Key]]:
        """Split keys into modifiers and non-modifiers."""
        pass

    @staticmethod
    def _calculate_modifier_value(modifiers: list[Key]) -> Optional[KeyModifier]:
        """Calculate KeyModifier value from modifier keys."""
        pass


KeyboardAPI = Keyboard
