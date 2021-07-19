# Copyright 2017, Wenjia Bai. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

# Milos Vukadinovic 6/4/2021
# Adaptation of the script

import os
import glob
import pandas as pd
from tqdm import tqdm
from biobank_utils import *
import dateutil.parser

def convert_zip_to_nifti(patients_csv = "/workspace/Milos/TestNifti/patients.csv",  
                         data_root = "/workspace/Milos/TestNifti/",
                         output_dir = "/workspace/Milos/UKBB_nifti",
                         util_dir = '/workspace/Milos/UKBB/', 
                         ukbkey = '/workspace/Milos/UKBB/.ukbkey',
                         start=0,
                         end=10000):

    """ for each patient creates a folder:
        patient_id
            saa.nii.gz
            la_2ch.nii.gz
            la_3ch.nii.gz
            la_4ch.nii.gz
            lvot.nii.gz

        Args:
            patient_csv : string
                a text file containing ids of patients that we want to process
            data_root : string 
                directory with all the UKBB zip files
            output_dir : string 
                directory where we can write output
            util_dir : string
                directory where you installed UKBB utils from  http://biobank.ctsu.ox.ac.uk/crystal/download.cgi
            ukbkey : string
                the auth key you received in the email

        Return:
            True/False based on if it was able to execute the task
    """
    with open(patients_csv) as f:
        lines = [line.rstrip() for line in f]
    end = min(end,len(lines))
    lines=lines[start:end]
    for eid in tqdm(lines):
        # Destination directories
        data_dir = os.path.join(output_dir,eid)
        print(data_dir)
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        dicom_dir = os.path.join(data_dir, 'dicom')
        fileList = glob.glob(f"{data_dir}/*.gz")

        if (not os.path.exists(dicom_dir)) and ( len(fileList) ==0 ) : 
            os.mkdir(dicom_dir)
            files = glob.glob(data_root+'*{0}_*2_0.zip'.format(eid))
            for f in files:
                os.system('unzip -o {0} -d {1}'.format(f, dicom_dir))
                ## Process the manifest file
                if os.path.exists(os.path.join(dicom_dir, 'manifest.cvs')):
                    os.system('cp {0} {1}'.format(os.path.join(dicom_dir, 'manifest.cvs'),
                                                os.path.join(dicom_dir, 'manifest.csv')))
                process_manifest(os.path.join(dicom_dir, 'manifest.csv'),
                                os.path.join(dicom_dir, 'manifest2.csv'))
                df2 = pd.read_csv(os.path.join(dicom_dir, 'manifest2.csv'), error_bad_lines=False)

                ## Patient ID and acquisition date
                pid = df2.at[0, 'patientid']
                date = dateutil.parser.parse(df2.at[0, 'date'][:11]).date().isoformat()

                ## Organise the dicom files
                ## Group the files into subdirectories for each imaging series
                for series_name, series_df in df2.groupby('series discription'):
                    series_dir = os.path.join(dicom_dir, series_name)
                    if not os.path.exists(series_dir):
                        os.mkdir(series_dir)
                    series_files = [os.path.join(dicom_dir, x) for x in series_df['filename']]
                    os.system('mv {0} {1}'.format(' '.join(series_files), series_dir))
            ## Convert dicom files and annotations into nifti images

        if(len(fileList) ==0):
            try:
                dset = Biobank_Dataset(dicom_dir)
                dset.read_dicom_images()
                dset.convert_dicom_to_nifti(data_dir)
                os.system('rm -rf {0}'.format(dicom_dir))
            except:
                print("SKIPPING ONE")


if __name__ == '__main__':

    convert_zip_to_nifti(patients_csv="/workspace/Milos/UKBB/bulk_files/patients.csv",
                         data_root="/workspace/data/NAS/UKBB/",
                         output_dir="/workspace/data/NAS/UKBB_NIFTI",
                         start=40000,
                         end=50000)

#    convert_zip_to_nifti()