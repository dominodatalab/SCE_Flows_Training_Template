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
    infile '/workflow/inputs/sdtm_data_path' truncover;
    input data_path $CHAR100.;
    call symputx('data_path', data_path, 'G');
run;
libname dataset "&data_path.";

/* Write the final ADAM output */
data outputs.adam;
    set dataset.tv;
run;