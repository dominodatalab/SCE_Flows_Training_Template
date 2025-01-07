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

Within the flow definition we use the DominoJobTask helper method to define each Flow task. This method will ultimately trigger a Domino Job with the specified parameters and return the outputs that get produced by the job.  

See the [Domino Docs]([https://docs.dominodatalab.com/en/latest/user_guide/e09156/define-flows/](https://docs.dominodatalab.com/en/latest/user_guide/e09156/define-flows/#_use_helper_methods) on all the parameters that can befiend the task helper method. 

**create_adam_data()**

This method provides a standardized interface for triggering a SAS script that produces an ADAM dataset. 

Here is a sample code snippet of how the method can be used:

```python
# Create task that generates ADSL dataset. This will run a unique Domino job and return its outputs.
adsl = create_adam_data(
    name="ADSL", 
    command="sas -stdio prod/adsl.sas",
    environment=sas_environment_name,
    hardware_tier=hardware_tier_name, 
    sdtm_data_path=sdtm_data_path 
)
# Create task that generates ADAE dataset. This takes the output from the previous task as an input.
adae = create_adam_data(
    name="ADAE", 
    command="sas -stdio prod/adae.sas",
    environment=sas_environment_name, 
    hardware_tier=hardware_tier_name,
    sdtm_data_path=sdtm_data_path, 
    dependencies=[adsl] # Note how this is the output from the previous task
)
```
Explaining the parameters in more detail:

- `name`: Name for the dataset that will be produced.
- `command`: Command that will be used when triggering the Domino job. This should point to the SAS file you want to execute.
- `environment`: Name of the compute environment to use in the job. If not specified, this will point to the default compute environment.
- `hardware_tier`: Name of the hardware tier to use in the job. If not specified, this will point to the default hardware tier.
- `sdtm_data_path`: Filepath location of the SDTM data. This parameter will be taken into the task as an input, which can be parsed and used as a parameter within the SAS script during the Domino job.
- `dependencies`: List of outputs from other create_adam_data() tasks. This task will not begin until the specified dependencies are produced. These are passed to the Domino job as inputs, which can be used within the SAS scripts.

Within the SAS script that gets executed by this method:

- You can get the `sdtm_data_path` variable by reading the contents of the file located at `/workflow/inputs/sdtm_data_path`
- You can get the `adam_dataset` dependencies by loading the contents of the file located at `/workflow/inputs/<NAME OF DATASET>`
- The output ADAM dataset must be written to `workflow/outputs/adam` in order for it to be returned, tracked properly, and passed into another task.

**create_tfl_report**

This method provides a standardized interface for triggering a SAS script that to produces aa TFL report. 

Here is a sample code snippet of how the method can be used:

```python
t_ae_rel = create_tfl_report(
    name="T_AE_REL", 
    command="sas -stdio prod/t_ae_rel.sas", 
    environment=sas_environment_name,
    hardware_tier=hardware_tier_name,
    dependencies=[adae]
)
```
Explaining the parameters in more detail:

- `name`: A name for the task
- `command`: The command that will be use when triggering the Domino job. This should point to the SAS file you want to execute.
- `environment`: Name of the compute environment to use in the job. If not specified, this will point to the default compute environment.
- `hardware_tier`: The name of the hardware tier to use in the job. If not specified, this will point to the default hardware tier.
- `dependencies`: List of outputs from other create_adam_data() tasks. This task will not begin until the specified dependencies are produced. These are passed to the Domino job as inputs, which can be used within the SAS scripts.

Within the SAS script that gets executed by this method:

- You can get the `adam_dataset` dependencies by loading the contents of the file located at `/workflow/inputs/<NAME OF DATASET>`
- The output report must be written to `workflow/outputs/report` in order for it to be returned and tracked properly.

## License
This template is licensed under Apache 2.0 and contains the following open source components: 

* Flytekit [Apache 2.0](https://github.com/flyteorg/flytekit/blob/master/LICENSE)
