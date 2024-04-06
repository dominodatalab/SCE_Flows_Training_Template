/******************************************************************************
*  This script mocks the scenario for generating a final t_ae_rel PDF report
*
* For simplicity, we will simply print the input data onto a PDF file 
*****************************************************************************/
options dlcreatedir;
libname inputs "/workflow/inputs"; /* All inputs live in this directory at workflow/inputs/<NAME OF INPUT> */ 
libname outputs "/workflow/outputs"; /* All outputs must go to this directory at workflow/inputs/<NAME OF OUTPUT>y */ 

/* TODO: Read the inputs and write the outputs properly. For now, we will just create an empty output file */
libname report "/workflow/outputs/report";