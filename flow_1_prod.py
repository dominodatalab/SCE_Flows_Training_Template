from flytekit import workflow
from flytekit.types.file import FlyteFile
from typing import TypeVar, NamedTuple
from flytekitplugins.domino.helpers import Input, Output, run_domino_job_task
from flytekitplugins.domino.task import DominoJobConfig, DominoJobTask, GitRef, EnvironmentRevisionSpecification, EnvironmentRevisionType, DatasetSnapshot, NetAppVolumeSnapshot
from flytekitplugins.domino.artifact import Artifact, DATA, MODEL, REPORT, ExportArtifactToDatasetsSpec, ExportArtifactToNetAppVolumesSpec, run_launch_export_artifacts_task
"""
    This script mocks a simple clinical trial using Domino Flows. 

    The input to this flow is the path to your SDTM data. You can point this to either your SDTMBLIND dataset or your SDTM-UNBLIND dataset stored in seperate NetApp Volumes. The output to this flow are a series of TFL reports.

    To the run the workflow remotely, execute the following code in your terminal:
    
    pyflyte run --remote flow_1_prod.py ADaM_TFL --netapp_volume_snapshot /mnt/netapp-volumes/CDISC01_SDTMBLIND

    """

# Define common Job config parameters across your seperate Flow tasks

sas_environment_name = "SAS Analytics Pro"                    # Change to the name of your deployments SAS Environment name
environment_revision_id="690a9ac36416b01c67c07e75"            # Change to the latest revision ID of your deployments SAS Environment
hardware_tier_name = "Small"                                  # Change to the name of one of your Domino's hardware tiers
GitRef_type="commitId"                                     
GitRef_value="4d76513dc0623e3898f191253967715414d00cf0"       # Change to the commitId of main Git repository 
netapp_volume_id="43d47cd8-af02-4d8e-8d0b-ab046102c03b"       # Change to the ID of the Netapp Volume containing your SDTM data
dfs_repo_commit_id="773b62fa7a6f41063056982a1c93646e6b4db727"  # Change to the latest commit ID of the Artifacts file system in your project
cache = False

# Add the ID of the NetApp Volume you want to export your ADaM Datasets to 
netapp_volume_export_id="c76a99a0-7659-4164-869a-ab397ac10cc6"

# Define Flow Artifacts for your ADaM Datasets and TFL Reports to gather in
DataArtifact = Artifact("ADaM Datasets", DATA)
ReportArtifact = Artifact("TFL Reports", DATA)

@workflow
def ADaM_TFL(netapp_volume_snapshot: str):
    # Create task that generates ADSL dataset. This will run a unique Domino job and return its outputs.
    adsl_task = run_domino_job_task(
        flyte_task_name="Create ADSL Dataset",
        command="prod/adam/adsl.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot)],
        output_specs=[Output(name="adsl", type=DataArtifact.File(name="adsl.sas7bdat"))],
        environment_name=sas_environment_name,
        hardware_tier_name=hardware_tier_name,
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id=netapp_volume_id, Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

     # Create task that generates ADAE dataset. 
    adae_task = run_domino_job_task(
        flyte_task_name="Create ADAE Dataset",
        command="prod/adam/adae.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot),
        Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"])],
        output_specs=[Output(name="adae", type=DataArtifact.File(name="adae.sas7bdat"))],
        environment_name=sas_environment_name,
        hardware_tier_name=hardware_tier_name,
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id=netapp_volume_id, Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

     # Create task that generates ADVS dataset. 
    advs_task = run_domino_job_task(
        flyte_task_name="Create ADVS Dataset",
        command="prod/adam/advs.sas",
        inputs=[Input(name="sdtm_snapshot_task_input", type=str, value=netapp_volume_snapshot),
        Input(name="adsl", type=FlyteFile[TypeVar("sas7bdat")], value=adsl_task["adsl"]),
        Input(name="adae", type=FlyteFile[TypeVar("sas7bdat")], value=adae_task["adae"])],
        output_specs=[Output(name="advs", type=DataArtifact.File(name="advs.sas7bdat"))],
        environment_name=sas_environment_name,
        hardware_tier_name=hardware_tier_name,
        netapp_volume_snapshots=[NetAppVolumeSnapshot(Id=netapp_volume_id, Version=1)],
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
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
        hardware_tier_name=hardware_tier_name,
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
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
        hardware_tier_name=hardware_tier_name,
        main_git_repo_ref=GitRef(Type=GitRef_type, Value=GitRef_value),
        use_project_defaults_for_omitted=True,
        cache=cache,
        cache_version="1.0"
    )

    run_launch_export_artifacts_task(
        spec_list=[
            ExportArtifactToNetAppVolumesSpec(
                artifact=DataArtifact,
                netapp_volume_id=netapp_volume_export_id,
                target_relative_path="ADaM_Datasets",
            ),
        ],
        environment_name="Domino Standard Environment Py3.10 R4.5",
        hardware_tier_name=hardware_tier_name,
        use_project_defaults_for_omitted=True
    )
    return


