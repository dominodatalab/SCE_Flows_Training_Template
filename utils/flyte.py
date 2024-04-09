import os
from typing import List
from flytekit.types.file import FlyteFile
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, EnvironmentRevisionSpecification, EnvironmentRevisionType, DatasetSnapshot
from flytekit.loggers import logger
from dataclasses import dataclass
from domino import Domino

@dataclass
class Input:
    """Class for defining an input for the Domino Job task in Flyte"""
    name: str
    type: type
    value: any

@dataclass
class Output:
    """Class for defining an output for the Domino Job task in Flyte"""
    name: str
    type: type

def DominoTask(
    name: str, 
    command: str, 
    environment: str = None,
    hardware_tier: str = None, 
    dfs_commit_id: str = None,
    volume_size_gb: int = 10,
    inputs: List[Input] = None,
    outputs: List[Output] = None,
) -> DominoJobTask:

    api_key=os.environ.get('DOMINO_USER_API_KEY')
    project_owner = os.environ.get("DOMINO_PROJECT_OWNER")
    project_name = os.environ.get("DOMINO_PROJECT_NAME")

    domino = Domino(f"{project_owner}/{project_name}")

    # Get environment ID
    environmentId = None
    if environment is None:
        print(f"Environment not specified for job: {name}. Project default will be used.")
    else:
        for env in domino.environments_list()["data"]:
            if env["name"] == environment:
                environmentId = env["id"]
        if environmentId is None:
            raise Exception("Environment name does not exist")

    # Get hardware tier ID
    hardwareTierId = None
    if hardware_tier is None:
        print(f"Hardware tier not specified for job: {name}. Project default will be used.")
    else:
        hardwareTierId = domino.get_hardware_tier_id_from_name(hardware_tier)

    job_config = DominoJobConfig(
        Title=name,
        ApiKey=api_key,
        Command=command,
        CommitId=dfs_commit_id, 
        MainRepoGitRef=GitRef(Type="head"), # TODO: Allow user to change git branch and commit. For now, we will use
        EnvironmentId=environmentId,
        EnvironmentRevisionSpec=None, # TODO: Allow user to specify revision ID. For now, it just takes the active revision.
        HardwareTierId=hardwareTierId,
        VolumeSizeGiB=volume_size_gb
    )
    job_config.resolve_job_properties()

    input_types = {}
    input_values = {}
    if inputs is not None:
        for input in inputs:
            input_types[input.name] = input.type
            input_values[input.name] = input.value

    output_types = {}
    if outputs is not None:
        for output in outputs:
            output_types[output.name] = output.type

    job = DominoJobTask(
        name,
        job_config,
        inputs=input_types,
        outputs=output_types, 
    )

    results = job(**input_values)

    return results

