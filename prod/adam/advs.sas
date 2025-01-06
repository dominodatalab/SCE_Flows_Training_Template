/******************************************************************************
* This scripts mocks the following use case:
*  1. Loading in the original SDTM ta.sas7bdat data & a processed ADSL data
*  2. Using that data to create the ADVS dataset
* 
*  For simplcity, we will simply merging the datasets together
*****************************************************************************/
options dlcreatedir;
libname inputs "/workflow/inputs"; /* All inputs live in this directory at workflow/inputs/<NAME OF INPUT> */ 
libname outputs "/workflow/outputs"; /* All outputs must go to this directory at workflow/inputs/<NAME OF OUTPUT>y */ 

/* Mandatory steps to add sas7bdat file extension to inputs */
x "mv /workflow/inputs/adsl_sas7bdat /workflow/inputs/adsl.sas7bdat";
x "mv /workflow/inputs/adae_sas7bdat /workflow/inputs/adae.sas7bdat";

/* Read in the SDTM data path input */
data _null__;
    infile '/workflow/inputs/sdtm_data_path' truncover;
    input data_path $CHAR100.;
    call symputx('data_path', data_path, 'G');
run;
libname dataset "&data_path.";

/* Write the final ADAM output */
data outputs.adam;
    merge dataset.ta inputs.adsl inputs.adae;
run;

