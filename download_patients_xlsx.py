import base64
import sys
import os

import pandas as pd
import sqlite3
from tqdm import tqdm
import zipfile

from pyorthanc import Orthanc, Instance
from pyorthanc.filtering import find, _build_patient

from encoding_orthanc import *


# Read list of patients from external text file given as input and download all data related to these
# Currently does not allow to select which data are downloaded
def downloadAllInstancesFromPatients():
    # Read patient list file (given as argument) and parse each line to obtain list of patients
    if len(sys.argv) < 2:
        print("Error: need to input patient list file as argument")
        print("Example call: python download_patients_xlsx.py orthanc_db.xlsx")
        return  

    # Open patient list file and read/parse its data with pandas
    # Extract relevant information (here patient IDs) from the file
    # Formatting is ugly and assumes Excel will always format the tab in a specific manner
    # Namely the relevant tab is always called "Tableau croisé dyn.", as well the relevant list of patients is
    # assumed to always be in the first column, in which the first cell (for which pandas requires the content
    # since it uses it as the column title, to extract the column data) and finally the cell just above the
    # actual list of patients, contains de phrase "Étiquettes de lignes". If the formatting for any of this
    # were not consistent or were to change in the future, this file would need to be addressed
    
    patient_list_file = sys.argv[1]
    xlsx_data = pd.read_excel(patient_list_file, usecols="A", sheet_name="Tableau croisé dyn.")

    patientIDs = xlsx_data["Unnamed: 0"].values.tolist()
    while(patientIDs[0] != "Étiquettes de lignes"):
        patientIDs.pop(0)
    patientIDs.pop(0)
    del patientIDs[-7:] # we delete the last parts of the list (again assuming the formatting is consistent) 
    print("Patient list to download:", patientIDs)

    # Need to convert human-readable patient IDs into Orthanc-specific encrypted IDs
    patient_UUIDs = []
    for patientID in patientIDs:
        patient_UUID = encodePatientID(patientID)
        patient_UUIDs.append(patient_UUID)
    
    # Create and orthanc instance that will communicate with the (assumedly already open) server 
    orthanc = Orthanc('http://localhost:8042', username='orthanc', password='orthanc')

    patient_list = []
    for patient_uuid in patient_UUIDs:
        patient = _build_patient(patient_identifier=patient_uuid, orthanc=orthanc, patient_filter=None,
                                       study_filter=None, series_filter=None, instance_filter=None)
        patient_list.append(patient)

    # For debug purpose, check number of found patients 
    # print("Size list: ", len(patient_list))

    # Uncommenting all the zip-related lines will, in addition to downloading the files in separate folders,
    # also create zip archives with the same data neatly organised. Could be added as --option
    inst = 0 #
    for patient in tqdm(patient_list):
        pID = patient.get_main_information()['MainDicomTags']['PatientID']
        # patient_zip = zipfile.ZipFile("Output/" + pID + '.gz', mode='w', compression = zipfile.ZIP_DEFLATED)
        # patient_zip.mkdir(pID + '/', 'w')
        for study in patient._studies:
            stID = study.get_main_information()['MainDicomTags']['StudyInstanceUID']
            desc = study.get_main_information()['MainDicomTags']['StudyDescription']
            suID = desc + '_' + stID[-5:]
            # patient_zip.mkdir(pID + '/' + suID + '/', 'w')
            for series in study._series:
                srID = series.get_main_information()['MainDicomTags']['SeriesInstanceUID']
                body = series.get_main_information()['MainDicomTags']['BodyPartExamined']
                seID = body + '_' + srID[-5:]
                # patient_zip.mkdir(pID + '/' + suID + '/' + seID + '/', 'w')
                for instance in tqdm(series._instances):
                    instUID = instance.get_main_information()['MainDicomTags']['SOPInstanceUID']
                    dicom_file = instance.get_dicom_file_content()
                    folder_name = pID + '/' + suID + '/' + seID + '/'
                    os.makedirs('Output/' + folder_name, exist_ok=True)
                    file_name = str(inst) + '-' + instUID[-5:]
                    # patient_zip.writestr(folder_name + file_name + '.dcm', dicom_file)
                    with open('Output/' + folder_name + file_name + '.dcm', 'wb') as file_handler:
                        file_handler.write(dicom_file)
                        inst = inst + 1
                inst = 0
    print("Great success!")

downloadAllInstancesFromPatients()