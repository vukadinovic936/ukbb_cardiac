import nibabel as nib
import numpy as np
import os #traversal folder
import imageio #convert to image
import matplotlib.pyplot as plt
import cv2
import numpy as np
import os

def nifti4d_to_avi(original_image_path = "demo_image/1/ao.nii.gz",segmented_image_path="demo_image/1/seg_ao.nii.gz"):
    """" 
        creates videos from nifti so it's human readable
        Args:
            original_image_path string
                path to the original unsegmented nifti image
            segmented_image path string 
                path to the segmented nifti image
        Return
            True/False boolean
    """"

    nim = nib.load(original_image_path)
    seg_nim = nib.load(segmented_image_path)
    image = nim.get_data()
    seg_image = seg_nim.get_data()
    X, Y, Z, T = image.shape

    print(f"Nifti image dimensions are ({X},{Y},{Z},{T})")
    for i in range(Z):
        img_array = []
        size=0
        if(not os.path.isdir("images/")): 
            os.mkdir("images")
        if(not os.path.isdir(f"images/{i+1}")):
            os.mkdir(f"images/{i+1}")
        for j in range(T):
            # if images doesn't exist make images 
            # if number folder doesnt exist make it
            filename = f"images/{i+1}/frame{j+1}.png"
            fig,ax = plt.subplots()
            ax.imshow(image[:,:,i,j],cmap='gray')
            data_masked = np.ma.masked_where(seg_image == 0, seg_image)
            ax.imshow(data_masked[:,:,i,j], interpolation='none', vmin = 0, alpha=0.6)

            fig.savefig(filename)
            img = cv2.imread(filename)
            height, width, layers = img.shape
            size = (width,height)
            plt.plot()
            img_array.append(img)
        out = cv2.VideoWriter(f'images/{i+1}/res.avi', cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
        for img in img_array:
            out.write(img)
        out.release()
        # delete pngs if u don't want frames
        #os.system(f"rm -r images/{i}*.png") 
    return True

if __name__ == "__main__":
    nifti4d_to_avi()