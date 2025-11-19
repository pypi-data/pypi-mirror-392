import asyncio
import os
import re
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from terminal_bench.agents import BaseAgent
from terminal_bench.agents.base_agent import AgentResult
from terminal_bench.agents.failure_mode import FailureMode
from terminal_bench.terminal.models import TerminalCommand
from terminal_bench.terminal.tmux_session import TmuxSession

from spoox.environment.TerminalBenchEnvironment import TerminalBenchEnvironment
from spoox.interface.LogInterface import LogInterface
from spoox.utils import setup_model_client, setup_agent_system, save_logs

"""
# run TerminalBench single task
tb run \
    --dataset terminal-bench-core==0.1.1 \
    --agent-import-path src.benchmark.terminal_bench.AgentuTerminalBench:AgentuTB \
    --task-id hello-world \
    --global-agent-timeout-sec 2000
    
# run TerminalBench entire bench
tb run \
    --dataset terminal-bench-core==0.1.1 \
    --agent-import-path src.benchmark.terminal_bench.AgentuTerminalBench:AgentuTB \
    --n-concurrent 2
    
# run 40 subset of TerminalBench 
tb run \
    --local-registry-path /Users/linus/Documents/TUM/MA/code/agentu/src/benchmark/terminal_bench/custom_registry_tb_first_half_40.json \
    --dataset terminal-bench-core-first-half-40==0.1.1 \
    --agent-import-path src.benchmark.terminal_bench.AgentuTerminalBench:AgentuTB \
    --global-agent-timeout-sec 2000 \
    --n-concurrent 2
    
# run 40 subset of TerminalBench - all default
tb run \
    --local-registry-path /Users/linus/Documents/TUM/MA/code/agentu/src/benchmark/terminal_bench/custom_registry_tb_first_half_40.json \
    --dataset terminal-bench-core-first-half-40==0.1.1 \
    --agent-import-path src.benchmark.terminal_bench.AgentuTerminalBench:AgentuTB
"""

_AGENT_ID = "mas-group-chat-m"  # "singleton",'mas-group-chat-s','mas-group-chat-m','mas-group-chat-l','mas-supervisor'
_MODEL_ID = "gpt-5-mini"  # "gpt-oss:20b","qwen3:14b","claude-sonnet-4-5","magistral:24b","gpt-5","gpt-5-mini"

class AgentuTB(BaseAgent):

    @staticmethod
    def name() -> str:
        return "agentu"

    def perform_task(
            self,
            instruction: str,
            session: TmuxSession,
            logging_dir: Path | None = None
    ) -> AgentResult:
        """
        Perform the task described by `task_description`.
        Args:
            instruction: The description of the task to perform.
            session: Optional tmux session to send commands to.
            logging_dir: The directory to optionally log your agent's output.
        Returns:
            An `AgentResult` object with the agent's token counts and optionally a
            failure mode for debugging.
        """

        # setup agent
        # setup interface
        load_dotenv()

        log_interface = LogInterface(
            logging_active=True,
            feedback_iterations_max=0,  # just a placeholder; not supported by terminal bench
            eval_file_path=f"task_eval.py",  # just a placeholder; not supported by terminal bench
            home_dir_path='.',  # just a placeholder; not supported by terminal bench
        )
        log_interface.user_delegate.user_input = [instruction, 'q']
        log_interface.user_delegate.default_user_choice = 'confirm'
        # setup environment
        model_client = setup_model_client(model_id=_MODEL_ID)
        environment = TerminalBenchEnvironment(session)
        # setup agent
        agent = setup_agent_system(_AGENT_ID, model_client, environment, log_interface)

        # uncomment for manual shell tool testing
        #asyncio.run(live_testing(environment, session))

        # unfortunately, most of the task containers do not have Python pre-installed,
        # however, the agent's python tool requires this,
        # therefore, we try to install it before triggering the agent
        session.send_command(TerminalCommand(command="apt update", block=True))
        session.send_command(TerminalCommand(command="apt install -y python3 python3-pip", block=True))
        session.send_command(TerminalCommand(command="ln -sf /usr/bin/python3 /usr/bin/python", block=True))
        session.send_command(TerminalCommand(command="ln -sf /usr/bin/pip3 /usr/bin/pip", block=True))
        session.send_command(TerminalCommand(command="python --version", block=True))
        session.send_command(TerminalCommand(command="pip --version", block=True))
        log_interface.print_shadow(session.capture_pane(), "PYTHON INSTALLATION")

        # run agent
        start_time = time.time()
        try:
            asyncio.run(agent.start())
            error = not agent.usage_stats['agent_errors']
        except Exception as e:
            log_interface.print_highlight(str(e), f"Exception during terminal bench agent system execution.")
            error = True
        exec_minutes = (time.time() - start_time) / 60

        # saving our own agentu logs
        current_dir = os.path.dirname(os.path.abspath(__file__))
        results_dir_name = f"results_tb_{_AGENT_ID}_{_MODEL_ID.replace(":", "-")}"
        results_dir_path = Path(current_dir) / results_dir_name
        results_dir_path.mkdir(parents=True, exist_ok=True)
        instruction_name = instruction[:40]
        instruction_name = re.sub(r'[^a-zA-Z0-9]', '_', instruction_name)
        instruction_name = re.sub(r'_+', '_', instruction_name)
        instruction_name = instruction_name.strip("_")
        # add a random id (cause descriptions can start with same sentences...)
        instruction_name += f"_{uuid.uuid4().hex[:4]}"
        save_logs(results_dir_path, 0, instruction_name, None, _AGENT_ID, _MODEL_ID,
                  None, None, exec_minutes, agent, log_interface, instruction)

        # fill out terminal bench AgentResult
        agent_result = AgentResult(
            total_input_tokens=sum(agent.usage_stats['prompt_tokens']),
            total_output_tokens=sum(agent.usage_stats['completion_tokens']),
            failure_mode=FailureMode.UNKNOWN_AGENT_ERROR if error else FailureMode.NONE,
        )

        session.stop()

        return agent_result
