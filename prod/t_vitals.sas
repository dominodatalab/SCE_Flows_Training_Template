/******************************************************************************
*  This script mocks the scenario for generating a final t_demog PDF report
*
*  For simplicity, we will simply print the input data onto a PDF file.
*  Dependant on ADVS
*****************************************************************************/
options dlcreatedir;
libname inputs "/workflow/inputs"; /* All inputs live in this directory at workflow/inputs/<NAME OF INPUT> */ 
libname outputs "/workflow/outputs"; /* All outputs must go to this directory at workflow/inputs/<NAME OF OUTPUT>y */ 

/* TODO: Read the inputs and write the outputs properly. For now, we will just create an empty output file
libname report "/workflow/outputs/report";
*/

ods pdf file='/workflow/outputs/report' pdftoc=2;
title 'T_VITALS report';
title2 '(this space left blank)';
ods text="(this space left intentionally blank)";
run;
ods pdf close;
