import os
from .adam import ADAM
from typing import List, TypeVar
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask
from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task
from flytekit import workflow, task
from flytekit.types.file import FlyteFile
from flytekit.types.directory import FlyteDirectory

def create_tfl_report(
    name: str, 
    command: str, 
    dependencies: List[ADAM],
    environment: str = None,
    hardware_tier: str = None
) -> FlyteFile[TypeVar("pdf")]:
    """
    This method provides a standard interface for creating a TFL report 

    :param name: The name in which to give the report. This is used to generate the step name.
    :param command: The command to execute for generating the report
    :param environment: The name of the environment you want to use. If not specified, the project default will be used.
    :param hardware_tier: The name of the hardware tier you want to use. If not specified, the project default will be used.
    :param adam_dataset: The processed ADAM dataset to use for generating the report
    :return: A PDF files containing the final TFL report
    """
    # Define inputs
    inputs = []
    for dataset in dependencies:
        inputs.append(Input(name=dataset.filename, type=FlyteFile[TypeVar("sas7bdat")], value=dataset.data))

    # Define outputs
    outputs = [Output(name="report", type=FlyteFile[TypeVar("pdf")])]

    results = run_domino_job_task(
        flyte_task_name=f"Create {name} report",
        command=command, 
        environment_name=environment,
        hardware_tier_name=hardware_tier,
        inputs=inputs,
        output_specs=outputs,
        use_project_defaults_for_omitted=True
    )

    return results["report"]



 