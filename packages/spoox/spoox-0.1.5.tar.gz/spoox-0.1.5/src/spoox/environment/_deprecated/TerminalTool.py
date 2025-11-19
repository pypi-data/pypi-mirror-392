from typing import Union

from autogen_core import CancellationToken, Component
from autogen_core.tools import BaseTool
from pydantic import BaseModel, Field, model_serializer
from terminal_bench.terminal.tmux_session import TmuxSession
from typing_extensions import Self


_TMUX_SESSION: dict[str, TmuxSession] = {}


def set_terminal_tmux_session(key: str, session: TmuxSession) -> None:
    global _TMUX_SESSION
    _TMUX_SESSION[key] = session


def get_terminal_tmux_session(key: str) -> TmuxSession:
    if key not in _TMUX_SESSION:
        raise ValueError(f"TerminalTool: no global Tmux session set for key {key}.")
    return _TMUX_SESSION[key]


class TerminalInput(BaseModel):
    command: str = Field(description="The command that should be executed in the persistent terminal instance.")
    enter: Union[bool, str] = Field(
        default="true",
        description="Set to 'true' to simulate pressing the Enter key after the command, ensuring it is submitted to the terminal. "
                    "Set to 'false' if the command should only be typed into the terminal without executing Enter. "
                    "Typically, set this to 'true' when submitting Bash commands, and to 'false' when sending tmux keys (e.g., C-b, Tab, Up). "
                    "This field is optional, the default is set to 'true'.")


class TerminalResult(BaseModel):
    running_program: str
    current_screen: str

    @model_serializer
    def ser_model(self) -> str:
        return (f"<running-program> {self.running_program} </running-program>  "
                f"\n  <current-screen>  \n  {self.current_screen}  \n  </current-screen>")


class TerminalToolConfig(BaseModel):
    """Configuration for TerminalTool"""

    tmux_session_key: str
    description: str = ("Execute commands in a persistent terminal session and receive the updated visible terminal screen buffer. "
                        "Supports both shell commands and interactive commands that follow the tmux key format, "
                        "for example: C-a, C-b, C-l, Tab, Space, Home, End, Insert, Delete, Up, Down, Left, Right, Escape. "
                        "Especially ideal for running and controlling interactive terminal programs such as 'top' or 'vim'.")

class TerminalTool(
    BaseTool[TerminalInput, TerminalResult],
    Component[TerminalToolConfig]
):
    """
    A tool that runs an active terminal can execute commands and returns the entire terminal screen.
    Developed for the TmuxSession and the terminal benchmark.

    Args:
        tmux_session_key: The terminal bench TmuxSession key.
    """

    component_config_schema = TerminalToolConfig

    def __init__(self, tmux_session_key: str):
        super().__init__(
            TerminalInput,
            TerminalResult,
            "Terminal",
            ("Execute commands in a persistent terminal session and receive the updated visible terminal screen buffer. "
             "Supports both shell commands and interactive commands that follow the tmux key format, "
             "for example: C-a, C-b, C-l, Tab, Space, Home, End, Insert, Delete, Up, Down, Left, Right, Escape. "
             "Especially ideal for running and controlling interactive terminal programs such as 'top' or 'vim'.")
        )
        self._tmux_session_key = tmux_session_key
        self._session = get_terminal_tmux_session(tmux_session_key)

    async def run(self, args: TerminalInput,
                  cancellation_token: CancellationToken = None) -> TerminalResult:

        keys = [args.command]
        if str(args.enter).strip().lower() in ["true", "'true'", "t", "yes", "y", "enter"]:
            keys.append("Enter")
        running_program, current_screen = self._session.send_command_terminal(keys)

        return TerminalResult(
            running_program=running_program,
            current_screen=current_screen
        )

    async def reset(self):
        """reset makes sure that active program is closed"""
        await self.run(TerminalInput(command="q", enter="false"))
        await self.run(TerminalInput(command="q", enter="true"))
        await self.run(TerminalInput(command="C-c", enter="false"))
        await self.run(TerminalInput(command="C-c", enter="true"))
        await self.run(TerminalInput(command="clear", enter="true"))

    def _to_config(self) -> TerminalToolConfig:
        """Convert current instance to config object"""
        return TerminalToolConfig(tmux_session_key=self._tmux_session_key)

    @classmethod
    def _from_config(cls, config: TerminalToolConfig) -> Self:
        """Create instance from config object"""
        return cls(tmux_session_key=config.tmux_session_key)
