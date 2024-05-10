import os
from .flyte import DominoTask, Input, Output
from typing import List, TypeVar
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask
from flytekit import workflow, task
from flytekit.types.file import FlyteFile
from flytekit.types.directory import FlyteDirectory
from dataclasses import dataclass

@dataclass
class ADAM:
    """Class for defining an ADAM dataset"""
    filename: str
    data: FlyteFile[TypeVar("sas7bdat")]

def create_adam_data(
    name: str, 
    command: str, 
    environment: str = None, 
    hardware_tier: str = None, 
    sdtm_data_path: str = None, 
    dependencies: List[ADAM] = None
) -> ADAM:
    """
    This method provides a standard interface for creating an ADAM dataset 

    :param name: The name in which to give the dataset. This is used to generate the step name.
    :param command: The command to execute for generating the dataset
    :param environment: The name of the environment you want to use. If not specified, the project default will be used.
    :param hardware_tier: The name of the hardware tier you want to use. If not specified, the project default will be used.
    :param sdtm_data_path: The root directory to the SDTM data
    :param adam_dataset: Any processed ADAM dataset to use in the generation.
    :return: An ADAM dataset
    """
    # Define inputs
    inputs=[]
    inputs.append(Input(name="sdtm_data_path", type=str, value=sdtm_data_path))
    if dependencies:
        for dataset in dependencies:
            inputs.append(Input(name=dataset.filename, type=FlyteFile[TypeVar("sas7bdat")], value=dataset.data))

    # Define outputs
    outputs = [Output(name="adam", type=FlyteFile[TypeVar("sas7bdat")])]

    results = DominoTask(
        name=f"Create {name} dataset",
        command=command, 
        environment=environment,
        hardware_tier=hardware_tier,
        inputs=inputs,
        outputs=outputs
    )

    return ADAM(filename=f"{name}.sas7bdat".lower(), data=results["adam"])


 