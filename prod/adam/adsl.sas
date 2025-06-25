/******************************************************************************
* This scripts mocks the following use case:
*  1. Loading in the original SDTM tv.sas7bdat data 
*  2. Using that data to create the ADAM ADSL dataset
* 
*  For simplicity, we are going to just return the same dataset back
*  and assume some data processing happened.
*****************************************************************************/
options dlcreatedir;
libname inputs "/workflow/inputs"; /* All inputs live in this directory at workflow/inputs/<NAME OF INPUT> */ 
libname outputs "/workflow/outputs"; /* All outputs must go to this directory at workflow/inputs/<NAME OF OUTPUT>y */ 

/* Read in the SDTM data path input */
data _null__;   
    infile '/workflow/inputs/sdtm_snapshot_task_input' truncover;  /* Open the file that Flyte creates from the Launch Parameter value. 
                                                                      This file contains a single string that is the path to the input dataset */
    input data_path $CHAR100.;  /* Read the string from that file into a SAS variable called data_path.*/
    call symputx('data_path', data_path, 'G');  /* Take that value and store it in a global macro variable called &data_path */
run;

libname dataset "&data_path."; /* Assign a lib to this path */

/* Write the final ADAM output */
data outputs.adsl_dataset;
    set dataset.tv;
run;