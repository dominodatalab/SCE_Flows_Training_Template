# Clincial Trial Workflow

This repo mocks a sample SCE clinical trial using Domino Flows. The example flow:

1. Takes your raw SDTM data as an `Launch Parameter`.
2. Produces a series of ADAM datasets that are collected together as Flow Artifact with type `DATA`.
3. Uses the ADAM datasets to generate a 2 TFL report that are collected together as Flow Artifact with type `REPORT`.
N.B. This does not contain real ADaM and TFL programs. They are dummy programs. 

## Environment Requirements

The project requires two environments:

1. The `Domino Standard Environment` which contains the necessary packages to trigger the flow.
2. A SAS-enabled environment for running the SAS jobs that get triggered by the flow. This must be created manually before running the flow in this template. Follow the instructions [here](https://docs.dominodatalab.com/en/latest/user_guide/e7805a/sas-on-domino/#_sas_analytics_for_containers_on_domino) for how to create a SAS environment. To have the template work out-of-the-box, the environment must be named `SAS Analytics Pro`. Otherwise, replace the `sas_environment_name` in variable in the `flow_1.py` files before running the flow.

## Hardware Requirements

This project works with the default `small-k8s` hardware tier named `Small` that comes with all Domino deployments. To use a different hardware tier, rename the `hardware_tier_name` variable in the `flow_1.py` file.

## Running The Flow

To run the flow:

1. Startup a VS Code workspace using the Domino Standard Environment.
2. Open the terminal and cd into `/mnt/code` in your directory. 
3. Execute the command below through a terminal in your workspace.

```
pyflyte run --remote flow_1.py ADaM_TFL --sdtm_dataset_snapshot /mnt/code/data/sdtm-blind
```
- The `pyflyte run` command will register the flow and trigger an execution.
- The `--remote` option enables running the execution remotely (outside of the workspace and in Flows). 
- `flow_1.py` / `ADaM_TFL` specifies the file and method that contains the flow definition.
- The `--sdtm_dataset_snapshot` parameter specifies the location of your raw SDTM data. To use use a different dataset as your input, change this parameter to a different folder path. 

Once you run the command, a link to the running Flow in the Project UI will be returned in the terminal.

Upon clicking on the link, you should be navigated to a page where you can monitor the execution:

![Monitor](https://github.com/dominodatalab/SCE_Flows_Training_Template/blob/13d705d8326c0e789f152580bfed8cdd846bdbc4/screenshots/monitor.jpg?raw=true)

## Flow Breakdown

The flow definition is located in the file named `flow_1.py` under a method called `ADaM_TFL`. Notice how the SDTM dataset path that was specified through the command line gets taken in as parameter to this method. In this example, we have stored the SDTM dataset inside of the Git repo. In reality, this would likely exist in a Domino Dataset snapshot which your parameter would point to instead.

Within the flow definition we use the `run_domino_job_task` helper method to define both the Domino Job and the Flow task together in one. This method will ultimately trigger a Domino Job with the specified parameters and return the outputs that get produced by the job.  

See the [[Domino Docs]](https://docs.dominodatalab.com/en/latest/user_guide/e09156/define-flows/#use-base-classes) view the base class methods of `DominoJobConfig` and `DominoJobTask`.

**run_domino_job_task()**

This method provides a standardized interface for both configuring the Flow task and the Job it will run. 

Here is a sample code snippet of how the method can be used:

```python
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
```
Explaining the parameters in more detail:

- `flyte_task_name`: Name of both the Flow Task and the corresponding Domino Job.
- `command`: Command that will be used when triggering the Domino job. This point to the underlying program you want to execute.
- `inputs`: The strongly typed inputs that the underlying program ingests. This can be combination of external Launch Parameters such as Domino Datasets and outputs from other Flow tasks. 
- `output_specs`: The strongly typed outputs produced by my underlying task program. In this example we are giving the outputs the type DataArtifact in order to group them as Flow Artifacts.
- `environment_name`: Name of the compute environment to use in the job. If not specified, this will point to the default compute environment.
- `hardware_tier_name`: Name of the hardware tier to use in the job. If not specified, this will point to the default hardware tier.
- `use_project_defaults_for_omitted`: Setting this to true means that any Job config that has not been explictly defined as a parameter will use the project default.
- `cache`: Setting this to true enables caching for this task.
- `cache_version`: A user defined value that specifies a version identifier for a task's cached results. It ensures that cached results are reused only if the task's logic and version remain consistent. Changing this allows users to force a rerun of the task. 



## License
This template is licensed under Apache 2.0 and contains the following open source components: 

* Flytekit [Apache 2.0](https://github.com/flyteorg/flytekit/blob/master/LICENSE)
