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
    
    pyflyte run --remote flow_1.py ADaM_TFL --sdtm_dataset_snapshot /mnt/code/data/sdtm-blind
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
    adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="prod/adam/adsl.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="adsl_dataset", type=DataArtifact.File(name="adsl.sas7bdat"))],
        environment_name=sas_environment_name,
        hardware_tier_name=hardware_tier_name,
        use_project_defaults_for_omitted=True,
        cache=True,
        cache_version="1.0"
    )

     # Create task that generates ADAE dataset. 
    adae_task = run_domino_job_task(
        flyte_task_name="Create ADAE Dataset",
        command="prod/adam/adae.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
        Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"])],
        output_specs=[Output(name="adae_dataset", type=DataArtifact.File(name="adae.sas7bdat"))],
        environment_name=sas_environment_name,
        hardware_tier_name=hardware_tier_name,
        use_project_defaults_for_omitted=True,
        cache=True,
        cache_version="1.0"
    )

     # Create task that generates ADVS dataset. 
    advs_task = run_domino_job_task(
        flyte_task_name="Create ADVS Dataset",
        command="prod/adam/advs.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
        Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"]),
        Input(name="adae_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adae_task["adae_dataset"])],
        output_specs=[Output(name="advs_dataset", type=DataArtifact.File(name="advs.sas7bdat"))],
        environment_name=sas_environment_name,
        hardware_tier_name=hardware_tier_name,
        use_project_defaults_for_omitted=True,
        cache=True,
        cache_version="1.0"
    )

    # Create task that generates the AE report. 
    t_ae_rel_task = run_domino_job_task(
        flyte_task_name="Create T_AE_REL Report",
        command="prod/tfl/t_ae_rel.sas",
        inputs=[Input(name="adsl_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl_dataset"]),
        Input(name="adae_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=adae_task["adae_dataset"])],
        output_specs=[Output(name="t_ae_rel", type=ReportArtifact.File(name="t_ae_rel.pdf"))],
        environment_name=sas_environment_name,
        hardware_tier_name=hardware_tier_name,
        use_project_defaults_for_omitted=True,
        cache=True,
        cache_version="1.0"
    )
    # Create task that generates the VSCAT report. 
    t_vscat_task = run_domino_job_task(
        flyte_task_name="Create T_VSCAT Report",
        command="prod/tfl/t_vscat.sas",
        inputs=[Input(name="advs_dataset", type=FlyteFile[TypeVar("sas7bdat")], value=advs_task["advs_dataset"])],
        output_specs=[Output(name="t_vscat", type=ReportArtifact.File(name="t_vscat.pdf"))],
        environment_name=sas_environment_name,
        hardware_tier_name=hardware_tier_name,
        use_project_defaults_for_omitted=True,
        cache=True,
        cache_version="1.0"
    )
    return
