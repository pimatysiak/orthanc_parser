PREPARATION/INSTALLATION

Required python packages to be installed additionally:

- zipfile (if the files need to be downloaded in zip format, still in current version)
- pyorthanc
- hashlib

Before running ensure these files are all in the working folder:

- download_patients_xlsl.py
- encoding_orthanc.py
(more to come for additional download option, e.g. specific instances per patient)

Additionally ensure that the Orthanc server is already running (assuming localhost:8042)


USAGE

In a terminal, call the following command:

download_patients_xlsx.py orthanc_spreadsheet.xlsx

Where orthanc_spreadsheet.xlsx is the full file used to compute the "tableau croisé dynamique"
The script will automatically parse the sheet in the file containing the result of the manual
filtering, the one containing the list of patients.


RESULT

In theory, if parsing was executed properly, all the selected patients' data (in full) will be downloaded
into a folder named "Output" created in the working directory, generally the one where the python
script reside. If necessary an option can be added to give the desired output directory as argument
to the script.