@echo OFF

rem -----------------------CONFIG-----------------------
rem Define here the path to your conda installation
set CONDAPATH=C:\Users\phili\miniconda3

rem Define here the name of the environment
set ENVNAME=esg_codebase
rem ----------------------------------------------------

rem activate base environment
if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

rem Activate specified conda environment
call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

cmd /k

