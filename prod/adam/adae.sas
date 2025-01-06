/******************************************************************************
* This is a dummy script that mocks the following use case:
*  1. Loading in the original SDTM ts.sas7bdat data & a processed ADSL data
*  2. Using that data to create the ADAE dataset
* 
*  For simplcity, we will simply merging the datasets together
*****************************************************************************/
options dlcreatedir;
libname inputs "/workflow/inputs"; /* All inputs live in this directory at workflow/inputs/<NAME OF INPUT> */ 
libname outputs "/workflow/outputs"; /* All outputs must go to this directory at workflow/inputs/<NAME OF OUTPUT>y */ 

/* Mandatory step to add sas7bdat file extension to inputs */
x "mv /workflow/inputs/adsl_dataset /workflow/inputs/adsl_dataset.sas7bdat";

/* Read in the SDTM data path input */
data _null__;
    infile '/workflow/inputs/sdtm_snapshot_task_input' truncover;
    input data_path $CHAR100.;
    call symputx('data_path', data_path, 'G');
run;
libname dataset "&data_path.";

/* Write the final ADAM output */
data outputs.adae_dataset;
    merge dataset.ts inputs.adsl_dataset;
run;


