from terminal_bench.terminal.tmux_session import TmuxSession

from spoox.environment.TerminalBenchEnvironment import TerminalBenchEnvironment
from spoox.environment.tools.TerminalTool import TerminalInput

"""
# run this test with the following command; also make sure to uncomment the function in AgentuTerminalBench
tb run \
    --dataset terminal-bench-core==0.1.1 \
    --agent-import-path src.benchmark.terminal_bench.AgentuTerminalBench:AgentuTB \
    --task-id fix-git \
    --global-agent-timeout-sec 240 
"""


async def live_testing(env: TerminalBenchEnvironment, session: TmuxSession):
    env.code_executor.timeout = 5
    await env.start()
    """
    # ---------------
    # timeout testing
    # come commands open a page that need to be closed with "q"
    print(await env.code_executor.execute_code_blocks(
        [CodeBlock(language="bash", code="git show 857d654")]))  # can be tested with fix-git task
    # problem here: the sleep 6 sets the -S done flag -> the waiting for echo 6done emmediately exists -> no 6done as output
    print(await env.code_executor.execute_code_blocks(
        [CodeBlock(language="bash", code="sleep 3 && echo 3done")]))
    print(await env.code_executor.execute_code_blocks(
        [CodeBlock(language="bash", code="sleep 6 && echo 6done")]))
    print(await env.code_executor.execute_code_blocks(
        [CodeBlock(language="bash", code="sleep 4 && echo 4done")]))
    # another problem: if one command timed out the other one is still blocked and times out as well
    print(await env.code_executor.execute_code_blocks(
        [CodeBlock(language="bash", code="sleep 50000 && echo timeo")]))
    print(await env.code_executor.execute_code_blocks(
        [CodeBlock(language="bash", code="echo no-timeo")]))
    # ---------------
    """
    """
    # ---------------------------
    # interactive program testing
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInteractiveProgramInput(start_command="pwd")))  # should fail to open interactive program
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInteractiveProgramInput(start_command="git log")))  # should start interactive program
    print("--------")
    print(await env.code_executor.execute_code_blocks(
        [CodeBlock(language="bash", code="echo it_works")]))  # should be completely independent -> should not fail
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInteractiveProgramInput(interaction_command="i")))  # should do nothing in the git log program
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInteractiveProgramInput(interaction_command="h")))  # should open the help page in the git log program
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInteractiveProgramInput(interaction_command="q")))  # should quit the git log program
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInteractiveProgramInput(close_it="true")))  # does nothing but should work
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInteractiveProgramInput(close_it="true")))  # does nothing but should work
    print("--------")
    # ---------------------------
    """

    """
    # ---------------------------
    # terminal tool testing
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInput(command="pwd")))
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInput(command="mkdir test_dir && cd test_dir")))  # checking if terminal is persistent
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInput(command="pwd")))
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInput(command="git log")))  # should start interactive program
    print("--------")
    print(await env.code_executor.execute_code_blocks(
        [CodeBlock(language="bash", code="echo it_works")]))  # should be completely independent -> should not fail
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInput(command="i", enter="false")))  # should do nothing in the git log program
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInput(command="h", enter="false")))  # should open the help page in the git log program
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInput(command="q", enter="false")))  # should quit the git log program
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInput(command="q", enter="false")))  # should quit the git log program
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInput(command="pwd")))
    print("--------")
    await env.reset()
    print(await env.terminal_tool.run(
        TerminalInput(command="pwd")))
    # ---------------------------
    """

    """
    # ---------------------------
    # terminal tool testing
    # should be executed using the task blind-maze-explorer-algorithm
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInput(command="./maze_game.sh 1")))
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInput(command="move N")))
    print("--------")
    await env.reset()
    print(await env.terminal_tool.run(
        TerminalInput(command="move N", enter="false")))
    print("--------")
    """


    # ---------------------------
    # terminal tool testing
    # should be executed using the task vim-terminal-task
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInput(command="vim")))
    print("--------")
    print(await env.terminal_tool.run(
        TerminalInput(command="i", enter="false")))
    print("--------")
    await env.reset()
    print(await env.terminal_tool.run(
        TerminalInput(command="hallo", enter="false")))
    print("--------")
    await env.reset()
    print(await env.terminal_tool.run(
        TerminalInput(command="Escape", enter="false")))
    print("--------")
    await env.reset()
    print(await env.terminal_tool.run(
        TerminalInput(command=":qa!", enter="true")))
    print("--------")
