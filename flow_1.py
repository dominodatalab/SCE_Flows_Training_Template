from flytekit import workflow
from flytekit.types.file import FlyteFile
from typing import TypeVar, NamedTuple
from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, EnvironmentRevisionSpecification, EnvironmentRevisionType, DatasetSnapshot
from flytekitplugins.domino.artifact import Artifact, DATA, MODEL, REPORT

"""
    This script mocks a sample clinical trial using Domino Flows. 

    The input to this flow is the path to your SDTM data. You can point this to either your SDTM-BLIND dataset or your SDTM-UNBLIND dataset. The output to this flow are a series of TFL reports.

    To the run the workflow remotely, execute the following code in your terminal:
    
    pyflyte run --remote workflow.py ADaM_TFL --sdtm_dataset_snapshot /mnt/code/data/sdtm-blind
    """

# Define variables for the hardware tier and compute enviroment
sas_environment_name = "SAS Analytics Pro"
hardware_tier_name = "Small"

# Define Flow Artifacts for your ADaM Datasets and TFL Reports to gather in
DataArtifact = Artifact("ADaM Datasets", DATA)
ReportArtifact = Artifact("TFL Reports", REPORT)

@workflow
def ADaM_TFL(sdtm_dataset_snapshot: str):
    # Create task that generates ADSL dataset. This will run a unique Domino job and return its outputs.
    adsl = create_adam_data(
        name="ADSL", 
        command="prod/adsl.sas",
        environment=sas_environment_name,
        hardware_tier= hardware_tier_name, # Optional parameter. If not set, then the default for the project will be used.
        sdtm_data_path=sdtm_data_path # Note this this is simply the input value taken in from the command line argument
    )

     adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="prod/adam/adsl.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="adsl_dataset", type=DataArtifact.File(name="adsl.sas7bdat"))],
        environment_name=sas_environment_name,
        hardware_tier=hardware_tier_name,
        use_project_defaults_for_omitted=True
    ) 
    return
