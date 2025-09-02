from flytekit import workflow
from flytekit.types.file import FlyteFile
from typing import TypeVar, NamedTuple
from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, EnvironmentRevisionSpecification, EnvironmentRevisionType, DatasetSnapshot
from flytekitplugins.domino.artifact import Artifact, DATA, MODEL, REPORT, ExportArtifactToDatasetsSpec, run_launch_export_artifacts_task

"""
    This script mocks a sample clinical trial using Domino Flows. 

    The input to this flow is the path to your SDTM data. You can point this to either your SDTM-BLIND dataset or your SDTM-UNBLIND dataset. The output to this flow are a series of TFL reports.

    To the run the workflow remotely, execute the following code in your terminal:
    
    pyflyte run --remote flow_1_prod.py ADaM_TFL --sdtm_dataset_snapshot /mnt/code/data/sdtm-blind

    """

# As this is considered a PROD Flow definition, we do not the use_project_defaults_for_omitted parameter
# and explictly set every required parameter in the task defintion to ensure reproducability.
# These are all the parameters required to be explicitly set of each task. 

sas_environment_name = "SAS Analytics Pro"                    # Change to the name of your deployments SAS Environment name
environment_revision_id="68792679a33fd917266afcbf"            # Change to the latest revision ID of your deployments SAS Environment
hardware_tier_name = "Small"                                  # Change to the name of one of your Domino's hardware tiers
GitRef_type="commitId"                                     
GitRef_value="ae2b61b09125271b5478c53fe06e96c278547769"       # Change to the commitId of main Git repository 
volume_size_gib=10
dfs_repo_commit_id="93326b183a6dd5ec24035b570337c08108658617"  # Change to the latest commit ID of the Artifacts file system in your project
cache = False

# Define Flow Artifacts for your ADaM Datasets and TFL Reports to gather in
DataArtifact = Artifact("ADaM Datasets", DATA)
ReportArtifact = Artifact("TFL Reports", DATA)

# Add the ID of the Dataset you want to export your ADaM Datasets to 
dataset_id="685a8797c7e1254245082ff7"

@workflow
def ADaM_TFL(sdtm_dataset_snapshot: str):
    # Create task that generates ADSL dataset. This will run a unique Domino job and return its outputs.
    adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="prod/adam/adsl.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot)],
        output_specs=[Output(name="adsl", type=DataArtifact.File(name="adsl.sas7bdat"))],
        environment_name=sas_environment_name,
        environment_revision_id=environment_revision_id,
        hardware_tier_name=hardware_tier_name,
        dataset_snapshots=[],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        volume_size_gib=volume_size_gib,
        dfs_repo_commit_id=dfs_repo_commit_id,
        external_data_volumes=[],
        cache=cache,
        cache_version="1.0"
    )

     # Create task that generates ADAE dataset. 
    adae_task = run_domino_job_task(
        flyte_task_name="Create ADAE Dataset",
        command="prod/adam/adae.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
        Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"])],
        output_specs=[Output(name="adae", type=DataArtifact.File(name="adae.sas7bdat"))],
        environment_name=sas_environment_name,
        environment_revision_id=environment_revision_id,
        hardware_tier_name=hardware_tier_name,
        dataset_snapshots=[],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        volume_size_gib=volume_size_gib,
        dfs_repo_commit_id=dfs_repo_commit_id,
        external_data_volumes=[],
        cache=cache,
        cache_version="1.0"
    )

     # Create task that generates ADVS dataset. 
    advs_task = run_domino_job_task(
        flyte_task_name="Create ADVS Dataset",
        command="prod/adam/advs.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=sdtm_dataset_snapshot),
        Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"]),
        Input(name="adae", type=FlyteFile[TypeVar("sas7bdat")], value=adae_task["adae"])],
        output_specs=[Output(name="advs", type=DataArtifact.File(name="advs.sas7bdat"))],
        environment_name=sas_environment_name,
        environment_revision_id=environment_revision_id,
        hardware_tier_name=hardware_tier_name,
        dataset_snapshots=[],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        volume_size_gib=volume_size_gib,
        dfs_repo_commit_id=dfs_repo_commit_id,
        external_data_volumes=[],
        cache=cache,
        cache_version="1.0"
    )

    # Create task that generates the AE report. 
    t_ae_rel_task = run_domino_job_task(
        flyte_task_name="Create T_AE_REL Report",
        command="prod/tfl/t_ae_rel.sas",
        inputs=[Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"]),
        Input(name="adae", type=FlyteFile[TypeVar("sas7bdat")], value=adae_task["adae"])],
        output_specs=[Output(name="t_ae_rel", type=ReportArtifact.File(name="t_ae_rel.pdf"))],
        environment_name=sas_environment_name,
        environment_revision_id=environment_revision_id,
        hardware_tier_name=hardware_tier_name,
        dataset_snapshots=[],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        volume_size_gib=volume_size_gib,
        dfs_repo_commit_id=dfs_repo_commit_id,
        external_data_volumes=[],
        cache=cache,
        cache_version="1.0"
    )
    # Create task that generates the VSCAT report. 
    t_vscat_task = run_domino_job_task(
        flyte_task_name="Create T_VSCAT Report",
        command="prod/tfl/t_vscat.sas",
        inputs=[Input(name="advs", type=FlyteFile[TypeVar("sas7bdat")], value=advs_task["advs"])],
        output_specs=[Output(name="t_vscat", type=ReportArtifact.File(name="t_vscat.pdf"))],
        environment_name=sas_environment_name,
        environment_revision_id=environment_revision_id,
        hardware_tier_name=hardware_tier_name,
        dataset_snapshots=[],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        volume_size_gib=volume_size_gib,
        dfs_repo_commit_id=dfs_repo_commit_id,
        external_data_volumes=[],
        cache=cache,
        cache_version="1.0"
    )

    run_launch_export_artifacts_task(
        spec_list=[
            ExportArtifactToDatasetsSpec(
                artifact=DataArtifact,
                dataset_id=dataset_id,
            ),
        ],
        environment_name="Domino Standard Environment Py3.10 R4.5 - Latest Cloud",
        hardware_tier_name=hardware_tier_name,
        use_project_defaults_for_omitted=True
    )
    
    return
