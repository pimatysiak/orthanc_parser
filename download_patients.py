import base64
import sys
import os

import sqlite3
from tqdm import tqdm

from pyorthanc import Orthanc, Instance
from pyorthanc.filtering import find, _build_patient

from encoding_orthanc import *


# Read list of patients from external text file given as input and download all data related to these
# Currently does not allow to select which data are downloaded
def downloadAllInstancesFromPatients():
    # Read patient list file (given as argument) and parse each line to obtain list of patients
    # patientIDs = ["Prostate-AEC-001", "Prostate-AEC-002", "Prostate-AEC-003"]
    if len(sys.argv) < 2:
        print("Error: need to input patient list file as argument")
        print("Example call: download_patients.py list.txt")
        return  

    patient_list_file = sys.argv[1]
    with open(patient_list_file) as file:
        patientIDs = [line.rstrip() for line in file]

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

    inst = 0 #
    for patient in tqdm(patient_list):
        pID = patient.get_main_information()['MainDicomTags']['PatientID']
        for study in patient._studies:
            stID = study.get_main_information()['MainDicomTags']['StudyInstanceUID']
            desc = study.get_main_information()['MainDicomTags']['StudyDescription']
            suID = desc + '_' + stID[-5:]
            for series in study._series:
                srID = series.get_main_information()['MainDicomTags']['SeriesInstanceUID']
                body = series.get_main_information()['MainDicomTags']['BodyPartExamined']
                seID = body + '_' + srID[-5:]
                for instance in tqdm(series._instances):
                    dicom_file = instance.get_dicom_file_content()
                    folder_name = "dump/" + pID + '/' + suID + '/' + seID + '/'
                    os.makedirs(folder_name, exist_ok=True)
                    file_name = '%0*d' % (3,inst)
                    with open(folder_name + file_name, 'wb') as file_handler:
                        file_handler.write(dicom_file)
                        inst = inst + 1
                inst = 0
        
        # Also download patient data in a zip file, formatted similarly to the original data
        zip_content = patient.get_zip()
        zip_fold_name = "dump/" + pID + '/'
        os.makedirs(zip_fold_name, exist_ok=True)
        with open(zip_fold_name + pID + ".zip", 'wb') as file_handler:
            file_handler.write(zip_content)
    print("Great success!")

downloadAllInstancesFromPatients()