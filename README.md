# Clincial Trial Workflow

This repo mocks a sample SCE clinical trial using Domino Flows. The example flow:

1. Takes your raw SDTM data as an `input`.
2. Produces a series of ADAM datasets.
3. Uses the ADAM datasets to generate a collection of TFL report as the `outputs`.

To run the flow:

1. Startup a workspace using the Domino Standard Environment.
2. Execute the command below through a terminal in your workspace.

```
pyflyte run --remote workflow.py sce_workflow --sdtm_data_path "/mnt/code/data/sdtm-blind"
```
- The `pyflyte run` command will register the flow and trigger an execution.
- The `--remote` option enables running the execution remotely (outside of the workspace).
- `workflow.py` / `sce_workflow` specifies the file and method that contains the flow definition.
- The `--sdtm_data_path` parameter specifies the location of your raw SDTM data. To use use a different dataset as your input, change this parameter to a different folder path.

Once you run the command, a direct link to the Flyte console should be returned:

![Execution Link](https://github.com/dominodatalab/domino-sce-flows/blob/b45fde19fe69246d2d54985ef4f5c6c6772eed07/screenshots/execution-link.png)

Upon clicking on the link, you should be navigated to a page where you can monitor the execution:

![Monitor](https://github.com/dominodatalab/domino-sce-flows/blob/b45fde19fe69246d2d54985ef4f5c6c6772eed07/screenshots/monitor.png)

## Flow Breakdown

The flow definition is located in the file named `workflow.py` under a method called `sce_workflow`. Notice how the SDTM dataset path that was specified through the command line gets taken in as parameter to this method.

Within the flow definition, there are two helper methods that are used for defining common tasks that are used in clinical trial studies. These methods will utltimately trigger a Domino Job with the specified parameters and return the outputs that get produced by the job.  

**create_adam_data()**

This method provides a standardized interface for triggering a SAS script that produces an ADAM dataset. 

Here is a sample code snippet of how the method can be used:

```
# Create task that generates ADSL dataset. This will run a unique Domino job and return its outputs.
adsl = create_adam_data(
    name="ADSL", 
    command="sas -stdio prod/adsl.sas",
    hardware_tier= "Small", 
    sdtm_data_path=sdtm_data_path 
)
# Create task that generates ADAE dataset. This takes the output from the previous task as an input.
adae = create_adam_data(
    name="ADAE", 
    command="sas -stdio prod/adae.sas", 
    hardware_tier= "Small",
    sdtm_data_path=sdtm_data_path, 
    dependencies=[adsl] # Note how this is the output from the previous task
)
```
Explaining the parameters in more detail:

- `name`: Name for the dataset that will be produced.
- `command`: Command that will be used when triggering the Domino job. This should point to the SAS file you want to execute.
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

```
t_ae_rel = create_tfl_report(
    name="T_AE_REL", 
    command="sas -stdio prod/t_ae_rel.sas", 
    hardware_tier="small-k8s",
    dependencies=[adae]
)
```
Explaining the parameters in more detail:

- `name`: A name for the task
- `command`: The command that will be use when triggering the Domino job. This should point to the SAS file you want to execute.
- `hardware_tier`: The name of the hardware tier to use in the job. If not specified, this will point to the default hardware tier.
- `dependencies`: List of outputs from other create_adam_data() tasks. This task will not begin until the specified dependencies are produced. These are passed to the Domino job as inputs, which can be used within the SAS scripts.

Within the SAS script that gets executed by this method:

- You can get the `adam_dataset` dependencies by loading the contents of the file located at `/workflow/inputs/<NAME OF DATASET>`
- The output report must be written to `workflow/outputs/report` in order for it to be returned and tracked properly.

# Environment Requirements

The project requires two environments:

1. The `Domino Standard Environment` which contains the necessary packages to trigger the flow.
2. A `SAS Analytics Pro` environment which contains the necessary packages to run the SAS jobs that get triggered by the flow. The environment definition is included in this template and will be automatically created in the deployment if it doesn't already exist.

# Hardware Requirements

This project works with a standard small-sized hardware tier, such as the small-k8s tier on all Domino deployments.
