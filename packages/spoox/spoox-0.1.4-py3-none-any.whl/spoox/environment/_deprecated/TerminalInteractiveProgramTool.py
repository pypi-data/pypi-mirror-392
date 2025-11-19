from typing import Union

from autogen_core import CancellationToken, Component
from autogen_core.tools import BaseTool
from pydantic import BaseModel, Field, model_serializer
from terminal_bench.terminal.tmux_session import TmuxSession
from typing_extensions import Self


_TMUX_SESSION: dict[str, TmuxSession] = {}


def set_tmux_session(key: str, session: TmuxSession) -> None:
    global _TMUX_SESSION
    _TMUX_SESSION[key] = session


def get_tmux_session(key: str) -> TmuxSession:
    if key not in _TMUX_SESSION:
        raise ValueError(f"TerminalInteractiveProgramResult: no global Tmux session set for key {key}.")
    return _TMUX_SESSION[key]


class TerminalInteractiveProgramInput(BaseModel):
    start_command: str = Field(
        default="",
        description="The Bash command for starting the interactive program in the terminal. "
                    "It must only be specified in the first tool call that should start the interactive program.")
    interaction_command: str = Field(
        default="",
        description="The command that is executed in the interactive program in the terminal. "
                    "Ensure the tool is first called with a start_command. "
                    "After that, you may call the tool with the interactive_command "
                    "as many times as needed to interact with the running terminal program. "
                    "Use this field to also send general terminal interactive commands to the program "
                    "(following tmux keys), for example: C-a, C-d, Tab, Up, Down, Left, Right, Escape ...")
    close_it: Union[bool, str] = Field(
        default="false",
        description="Set to 'true' to close the interactive program. "
                    "This releases the tool, allowing it to be restarted with a new start_command.")


class TerminalInteractiveProgramResult(BaseModel):

    success: bool
    start_command: str
    interaction_history: list[str]
    running_program: bool
    current_screen: str

    @model_serializer
    def ser_model(self) -> str:
        return (f"<success> {self.success} </success>  "
                f"\n  <start-command> {self.start_command} </start-command>"
                f"\n  <interaction-history> {self.interaction_history} </interaction-history>"
                f"\n  <running-program> {self.running_program} </running-program>"
                f"\n  <current-screen>  \n  {self.current_screen}  \n  </current-screen>")


class TerminalInteractiveProgramConfig(BaseModel):
    """Configuration for TerminalInteractiveProgramTool"""

    tmux_session_key: str
    description: str = ("Start, interact and stop an interactive program in the terminal. "
                        "First, call the tool with a start_command that starts the interactive program in the terminal. "
                        "After that, you may call the tool with the interactive_command as many times as needed "
                        "to interact with the running interactive program. "
                        "When finished set close_it to true to releases the tool, allowing it to be restarted with a new start_command.")


class TerminalInteractiveProgramTool(
    BaseTool[TerminalInteractiveProgramInput, TerminalInteractiveProgramResult],
    Component[TerminalInteractiveProgramConfig]
):
    """
    A tool that can start, interact and stop an interactive program in the terminal.
    Developed for the TmuxSession and the terminal benchmark.

    Args:
        tmux_session_key: The terminal bench TmuxSession key.
    """

    component_config_schema = TerminalInteractiveProgramConfig

    def __init__(self, tmux_session_key: str):
        super().__init__(
            TerminalInteractiveProgramInput,
            TerminalInteractiveProgramResult,
            "TerminalInteractiveProgram",
            ("Start, interact and stop an interactive program in the terminal. "
             "First, call the tool with a start_command that starts the interactive program in the terminal. "
             "After that, you may call the tool with the interactive_command as many times as needed "
             "to interact with the running interactive program. "
             "When finished set close_it to true to releases the tool, allowing it to be restarted with a new start_command. "
             "In general, only fill one of start_command, interactive_command, or close_it per tool call, and leave all other fields empty.")
        )
        self._tmux_session_key = tmux_session_key
        self._running_program = False
        self._start_command = ""
        self._interaction_history = list()
        self._session = get_tmux_session(tmux_session_key)

    async def run(self, args: TerminalInteractiveProgramInput,
                  cancellation_token: CancellationToken = None) -> TerminalInteractiveProgramResult:

        current_screen: str = ""
        error_message: str = ""

        # check if it is a 'close_it' call
        if str(args.close_it).strip().lower() in ["true", "'true'", "t", "yes", "y", "close_it", "close-it", "close"]:
            self._running_program, current_screen = self._session.send_stop_command_interactive_program()
            self._start_command = ""
            self._interaction_history = list()

        elif args.start_command:
            # make sure previous programs are closed and the screen is cleared
            self._session.send_stop_command_interactive_program()
            # start program
            command = args.start_command
            self._running_program, current_screen = self._session.send_start_interactive_program(command)
            self._start_command = command
            self._interaction_history = list()
            if not self._running_program:
                error_message = ("The provided start_command did not start a terminal program. "
                                 "Do only use this tool for an interactive terminal program.")

        elif args.interaction_command:
            if not self._running_program:
                error_message = ("Call the tool with start_command to start the program first, "
                                 "then use interactive_command to interact with it.")
            else:
                # run interaction command
                command = args.interaction_command
                self._running_program, current_screen = self._session.send_command_interactive_program(command)
                self._interaction_history.append(command)
        else:
            error_message = ("Please fill one of start_command, interactive_command, or close_it per tool call, "
                             "and leave all other fields empty.")

        # tool call failure
        if error_message:
            return TerminalInteractiveProgramResult(
                success=False,
                start_command=self._start_command,
                interaction_history=self._interaction_history,
                running_program=self._running_program,
                current_screen=error_message
            )

        # success
        return TerminalInteractiveProgramResult(
            success=True,
            start_command=self._start_command,
            interaction_history=self._interaction_history,
            running_program=self._running_program,
            current_screen=current_screen
        )

    async def reset(self):
        """reset makes sure that active program is closed"""
        await self.run(TerminalInteractiveProgramInput(close_it="true"))

    def _to_config(self) -> TerminalInteractiveProgramConfig:
        """Convert current instance to config object"""
        return TerminalInteractiveProgramConfig(tmux_session_key=self._tmux_session_key)

    @classmethod
    def _from_config(cls, config: TerminalInteractiveProgramConfig) -> Self:
        """Create instance from config object"""
        return cls(tmux_session_key=config.tmux_session_key)
