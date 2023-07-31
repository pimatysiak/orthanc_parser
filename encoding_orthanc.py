import hashlib

# Obtaining Orthanc instance IDs, which are the concatenation of patientID, StudyInstanceUID,
# SeriesInstanceUID and SOPInstanceUID with pipes in between, all hashed using SHA-1, before segmenting
# the 40-character hash into 5 8-character sections separated by colons 
def encodePatientID(patientID):
    patient_id_sha1 = hashlib.sha1(patientID.encode())
    hex_patient = patient_id_sha1.hexdigest()
    orthancPatientID = hex_patient[0:8] + '-' + hex_patient[8:16] + '-' +\
                       hex_patient[16:24] + '-' + hex_patient[24:32] + '-' +\
                       hex_patient[32:40]
    return orthancPatientID

def encodeStudyID(patientID, studyInstanceUID):
    concatenated_ID = patientID + '|' + studyInstanceUID
    concatenated_ID_sha1 = hashlib.sha1(concatenated_ID.encode())
    hex_concat_sha1 = concatenated_ID_sha1.hexdigest() # hexadecimal encoding of the hash
    orthancStudyUID = hex_concat_sha1[0:8] + '-' + hex_concat_sha1[8:16] + '-' +\
                      hex_concat_sha1[16:24] + '-' + hex_concat_sha1[24:32] + '-' +\
                      hex_concat_sha1[32:40]
    return orthancStudyUID

def encodeSeriesID(patientID, studyInstanceUID, seriesInstanceUID):
    concatenated_ID = patientID + '|' + studyInstanceUID + '|' + seriesInstanceUID
    concatenated_ID_sha1 = hashlib.sha1(concatenated_ID.encode())
    hex_concat_sha1 = concatenated_ID_sha1.hexdigest() # hexadecimal encoding of the hash
    orthancSeriesUID = hex_concat_sha1[0:8] + '-' + hex_concat_sha1[8:16] + '-' +\
                       hex_concat_sha1[16:24] + '-' + hex_concat_sha1[24:32] + '-' +\
                       hex_concat_sha1[32:40]
    return orthancSeriesUID

def encodeInstanceID(patientID, studyInstanceUID, seriesInstanceUID, SOPInstanceUID):
    concatenated_ID = patientID + '|' + studyInstanceUID + '|' + seriesInstanceUID + '|' + SOPInstanceUID
    concatenated_ID_sha1 = hashlib.sha1(concatenated_ID.encode())
    hex_concat_sha1 = concatenated_ID_sha1.hexdigest() # hexadecimal encoding of the hash
    orthancInstanceID = hex_concat_sha1[0:8] + '-' + hex_concat_sha1[8:16] + '-' +\
                        hex_concat_sha1[16:24] + '-' + hex_concat_sha1[24:32] + '-' +\
                        hex_concat_sha1[32:40]
    return orthancInstanceID
