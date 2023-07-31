import base64
import sys
import os

import sqlite3
from tqdm import tqdm

from pyorthanc import Orthanc, Instance
from pyorthanc.filtering import find, _build_patient

from encoding_orthanc import *


# Given an external text file listing one (1) patient, download all subsequently listed instances
def downloadSpecificInstancesFromSinglePatient():
    # Read patient list file (given as argument) and parse each line to obtain list of patients
    if len(sys.argv) < 2:
        print("Error: need to input patient list file as argument")
        print("Example call: download_patients.py list.txt")
        return  

    patient_list_file = sys.argv[1]
    with open(patient_list_file) as file:
        file_list = [line.rstrip() for line in file]

    patient_uuid = file_list[0]
    instanceIDs = file_list[1:]

    # Need to convert human-readable patient ID into Orthanc-specific encrypted ID
    patient_UUID = encodePatientID(patient_uuid)
    
    # Create and orthanc instance that will communicate with the (assumedly already open) server 
    orthanc = Orthanc('http://localhost:8042', username='orthanc', password='orthanc')

    # Build the patient database, including all appropriate tags and list of studies, series, instances
    patient = _build_patient(patient_identifier=patient_UUID, orthanc=orthanc, patient_filter=None,
                                       study_filter=None, series_filter=None, instance_filter=None)

    inst = 0 #
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
                instUID = instance.get_main_information()['MainDicomTags']['SOPInstanceUID']
                if(instUID in instanceIDs):
                    dicom_file = instance.get_dicom_file_content()
                    folder_name = "dump2/" + pID + '/' + suID + '/' + seID + '/'
                    os.makedirs(folder_name,exist_ok=True)
                    file_name = str(inst) + '-' + instUID[-5:]
                    with open(folder_name + file_name, 'wb') as file_handler:
                        file_handler.write(dicom_file)
                        inst = inst + 1
            inst = 0
    print("Great success!")

downloadSpecificInstancesFromSinglePatient()