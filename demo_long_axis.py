"""
    This script demonstrates a pipeline for cardiac MR image analysis on long axis
"""
import os
import urllib.request
import shutil


if __name__ == '__main__':
    # The GPU device id
    CUDA_VISIBLE_DEVICES = 0

    # The URL for downloading demo data
    URL = 'https://www.doc.ic.ac.uk/~wbai/data/ukbb_cardiac/'

    # Download demo images
    print('Downloading demo images ...')
    for i in [1]:
        if not os.path.exists('demo_image/{0}'.format(i)):
            os.makedirs('demo_image/{0}'.format(i))
        for seq_name in ['la_4ch']:
            f = 'demo_image/{0}/{1}.nii.gz'.format(i, seq_name)
            urllib.request.urlretrieve(URL + f, f)

    # Download information spreadsheet
    print('Downloading information spreadsheet ...')
    if not os.path.exists('demo_csv'):
        os.makedirs('demo_csv')

    # Download trained models
    print('Downloading trained models ...')
    if not os.path.exists('trained_model'):
        os.makedirs('trained_model')

    for model_name in ['FCN_la_4ch_seg4']:
        for f in ['trained_model/{0}.meta'.format(model_name),
                  'trained_model/{0}.index'.format(model_name),
                  'trained_model/{0}.data-00000-of-00001'.format(model_name)]:
            urllib.request.urlretrieve(URL + f, f)

    # Deploy the segmentation network
    print('Deploying the segmentation network ...')
    os.system('CUDA_VISIBLE_DEVICES={0} python3 common/deploy_network.py --seq_name la_4ch --data_dir demo_image '
              '--seg4 --model_path trained_model/FCN_la_4ch_seg4'.format(CUDA_VISIBLE_DEVICES))

    print('Done.')
