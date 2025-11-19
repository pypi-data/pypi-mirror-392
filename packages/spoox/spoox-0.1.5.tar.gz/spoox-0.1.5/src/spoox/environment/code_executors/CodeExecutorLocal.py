import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import List, Optional, ClassVar

from autogen_core import CancellationToken, Component
from autogen_core.code_executor import CodeExecutor, CodeBlock, CodeResult
from pydantic import BaseModel


class CodeExecutorLocalConfig(BaseModel):
    """Configuration for PermanentCommandLineCodeExecutor"""

    timeout: int = 90
    work_dir: Optional[str] = None


class CodeExecutorLocal(CodeExecutor, Component[CodeExecutorLocalConfig]):
    component_config_schema = CodeExecutorLocalConfig

    SUPPORTED_LANGUAGES: ClassVar[List[str]] = [
        "python",
        "bash",
    ]

    def __init__(self, timeout: int = 90, work_dir: Optional[Path] = None, user: Optional[str] = None):
        super().__init__()

        if timeout < 1:
            raise ValueError("Timeout must be greater than or equal to 1.")
        self.timeout = timeout

        self._started = False
        self._runs_count = 0
        self._local_code_dir = None
        self._local_code_dir_path = None

        self.work_dir = work_dir or Path.cwd()
        self.user = user or os.environ.get("USER") or os.environ.get("USERNAME")

    @property
    def runs_count(self) -> int:
        """Counter of executed code blocks."""
        return self._runs_count

    async def execute_code_blocks(self, code_blocks: List[CodeBlock],
                                  cancellation_token: CancellationToken) -> CodeResult:

        if len(code_blocks) != 1:
            raise RuntimeError(f"CodeExecutorLocal `code_blocks` must exactly contain one code block.")
        code_block = code_blocks[0]

        if not self._started:
            raise RuntimeError(f"CodeExecutorLocal must be started. Make sure `.start()` is called.")

        if code_block.language.lower() not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Language '{code_block.language}' not supported by CodeExecutorLocal.")

        # setup code block language dependents
        type_of_file = ".py" if code_block.language.lower() == "python" else ".sh"
        caller_keyword = "python" if code_block.language.lower() == "python" else "bash"

        # write code block to the py or sh file
        rand_id = uuid.uuid4().hex[:8]
        code_block_file = self._local_code_dir_path / f"code_block_{self._runs_count}_{rand_id}{type_of_file}"
        code_block_file.write_text(f"{code_block.code}\n")
        code_block_file.chmod(0o755)

        # exec code file
        try:
            result = subprocess.run(
                [caller_keyword, str(code_block_file)],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                user=self.user,
                cwd=str(self.work_dir)
            )
        except subprocess.TimeoutExpired:
            return CodeResult(1, "Command execution failed - timeout error")

        # format exec output
        if result.stdout and result.stderr:
            return CodeResult(result.returncode, f"<stdout>\n{result.stdout}\n</stdout>\n\n<stderr>\n{result.stderr}\n</stderr>")
        elif result.stdout:
            return CodeResult(result.returncode, result.stdout)
        elif result.stderr:
            return CodeResult(result.returncode, result.stderr)
        return CodeResult(result.returncode, "")

    async def start(self) -> None:
        if not self._started:
            # setup local temp code dir
            self._local_code_dir = tempfile.TemporaryDirectory(dir=Path("/tmp"))
            self._local_code_dir_path = Path(self._local_code_dir.name)
            # others
            self._runs_count = 0
            self._started = True

    async def stop(self) -> None:
        if self._started:
            self._local_code_dir.cleanup()
            self._started = False

    async def restart(self) -> None:
        if self._started:
            await self.stop()
        await self.start()
