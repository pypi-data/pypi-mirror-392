from typing import Optional

from autogen_core import CancellationToken, Component, ComponentModel
from autogen_core.code_executor import CodeBlock, CodeExecutor
from autogen_core.tools import BaseTool
from pydantic import BaseModel, Field, model_serializer
from typing_extensions import Self

from spoox.environment._utils import output_truncat


class CodeExecutionInput(BaseModel):
    code: str = Field(description="The Python code block that should be executed.")


class CodeExecutionResult(BaseModel):
    output: str
    exit_code: Optional[int] = None

    @model_serializer
    def ser_model(self) -> str:
        if self.exit_code is None:
            return f"<output> {self.output} </output>"
        return f"<exit-code> {self.exit_code} </exit-code>  \n  <output> {self.output} </output>"


class PythonToolConfig(BaseModel):
    """Configuration for PythonTool"""

    executor: ComponentModel
    output_max: int
    description: str = "Run a Python code block once in the users current directory."


class PythonTool(
    BaseTool[CodeExecutionInput, CodeExecutionResult], Component[PythonToolConfig]
):
    """
    A tool that executes Python code blocks in a code executor and returns output.

    Args:
        executor: The code executor that will be used to execute the code blocks.
    """

    component_config_schema = PythonToolConfig

    def __init__(self, executor: CodeExecutor, output_max: int = 20000):
        super().__init__(
            CodeExecutionInput,
            CodeExecutionResult,
            "PythonExecutor",
            "Run a Python code block once in the users current directory."
        )
        self._executor = executor
        self._output_max = output_max

    async def run(self, args: CodeExecutionInput, cancellation_token: CancellationToken) -> CodeExecutionResult:
        # execute code
        code_block = CodeBlock(code=args.code, language="python")
        result = await self._executor.execute_code_blocks(
            code_blocks=[code_block], cancellation_token=cancellation_token
        )
        # make sure the output is cut when too long
        output = output_truncat(result.output, self._output_max)
        return CodeExecutionResult(exit_code=result.exit_code, output=output)

    def _to_config(self) -> PythonToolConfig:
        """Convert current instance to config object"""
        return PythonToolConfig(executor=self._executor.dump_component(), output_max=self._output_max)

    @classmethod
    def _from_config(cls, config: PythonToolConfig) -> Self:
        """Create instance from config object"""
        executor = CodeExecutor.load_component(config.executor)
        return cls(executor=executor, output_max=config.output_max)
