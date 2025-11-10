#import packages, verify if they are all installed in your python
import numpy as np
import nibabel as nib
import pydicom as pyd
import argparse
from matplotlib import pyplot as plt
import matplotlib as mpl
import glob
import os
import sys

# =====================================================================
# Interfile to NIfTI conversion tool for CASToR-reconstructed images
# =====================================================================
# Supports: 
#   - 3D volumes
#   - 3D + Time (Dynamic)
#   - 3D + Gating (Respiratory or Cardiac)
#   - 3D + Time + Gating
#
# Notes:
#   - Only some Interfile/NIfTI types are supported.
#   - Default: NIfTI version 1 (more widely compatible).
#   - Time frames: time info stored in DICOM tags (used by PMOD).
# =====================================================================

description = """
CASToR Interfile → NIfTI Conversion Tool

This script converts images reconstructed with CASToR from Interfile (.hdr/.img) format 
to NIfTI (.nii) format.

Supports:
  • 3D static images
  • 3D + time (dynamic)
  • 3D + respiratory or cardiac gating
  • 3D + time + gating

By default, NIfTI version 1 is used for maximum compatibility.

⚠️ For time-framed images:
Since NIfTI has no native dynamic support, time info is embedded in DICOM fields 
(works with PMOD but may be unreliable).

──────────────────────────────────────────────────────────────
Required Input:
  • CASToR Interfile image without extensions (.hdr/.img)

Optional Inputs:
  • Number of time frames, respiratory gates, or cardiac gates
  • Output folder
  • NIfTI version (1 or 2)
  • Option to convert float → uint16 (with slope/intercept) - convert voxels intensities

Example:
  python3 CASToR_Interfile_to_Nifti_converter_tool.py 
      -Castorfilepath CASToRImage_it10 
      -nbFrames 10 -nbRgates 1 -nbCgates 1 -niftiVersion 1 -outFolder /path/to/folder
──────────────────────────────────────────────────────────────
"""

# Create parser (suppress automatic help so we can control behavior)
parser = argparse.ArgumentParser(
    description=description,
    add_help=False,
    formatter_class=argparse.RawTextHelpFormatter,
)

# -------------------------------------------------------------------
# Define arguments (hidden until user calls --helper)
# -------------------------------------------------------------------
parser.add_argument(
    "-Castorfilepath",
    type=str,
    required=True,
    metavar="CASTORFILEPATH",
    help=("Path and base name of the CASToR Interfile image (without extensions). "
          "Example: /path/to/CASToRImage_it10"),
)

parser.add_argument(
    "-nbFrames",
    type=int,
    default=1,
    metavar="NBFRAMES",
    help=("Number of time frames to convert. "
          "Input: one Interfile file per frame. "
          "Output: one 4D NIfTI file (compatible with PMOD)."),
)

parser.add_argument(
    "-nbRgates",
    type=int,
    default=1,
    metavar="NBRGATES",
    help=("Number of respiratory gates. "
          "Input: one Interfile file per gate. "
          "Output: one NIfTI file per gate."),
)

parser.add_argument(
    "-nbCgates",
    type=int,
    default=1,
    metavar="NBCGATES",
    help=("Number of cardiac gates. "
          "Input: one Interfile file per gate. "
          "Output: one NIfTI file per gate."),
)

parser.add_argument(
    "-niftiVersion",
    type=int,
    default=1,
    choices=[1, 2],
    metavar="{1,2}",
    help="NIfTI version (1 or 2). Default: 1",
)

parser.add_argument(
    "-convertFloatToInt",
    action="store_true",
    help=("Convert float voxel values to uint16. "
          "Applies rescale slope/intercept to preserve dynamic range."),
)

parser.add_argument(
    "-outFolder",
    type=str,
    default="",
    metavar="OUTFOLDER",
    help="Output folder (default: same as input path CASToR Image).",
)

# -------------------------------------------------------------------
# Custom help flags
# -------------------------------------------------------------------
parser.add_argument(
    "--help",
    action="store_true",
    help="show this message and exit (short help)",
)

parser.add_argument(
    "--helper",
    action="store_true",
    help="show full detailed help (includes options)",
)

# -------------------------------------------------------------------
# Behavior: show short description if no args
# -------------------------------------------------------------------
if len(sys.argv) == 1:
    print(description)
    print("Run with '--helper' to see available options.\n")
    sys.exit(0)

# -------------------------------------------------------------------
# Behavior: show full help if requested
# -------------------------------------------------------------------
if "--helper" in sys.argv:
    parser.print_help()
    sys.exit(0)

# -------------------------------------------------------------------
# Parse normally
# -------------------------------------------------------------------
args = parser.parse_args()

nbFrames = args.nbFrames
Castorfilepath = args.Castorfilepath
nbRgates = args.nbRgates
nbCgates = args.nbCgates
niftiVersion = args.niftiVersion
convertFloatToInt = args.convertFloatToInt
outFolder = args.outFolder

if niftiVersion!=1 and niftiVersion!=2:
  print("NIfTI version either 1 or 2")
  quit()

# loop on respiratory and cardiac gates if any
for rg in range(1,nbRgates+1):
  for cg in range(1,nbCgates+1):

    # automatic CASToR file name suffix in presence of gating
    suffix = ''
    if nbRgates>1:
      suffix += '_rg{:d}'.format(rg)
    if nbCgates>1:
      suffix += '_cg{:d}'.format(cg)

    # if dynamic image series (time frames), initialize additional variables and 
    # read all header information except the framing information from the first frame
    if nbFrames>1:
      # information on frame start times and frame duration for all frames
      frameStartTime = []
      frameDuration = []

      # paths to Interfile header and binary image for the first frame
      hdrPath = Castorfilepath+'_fr1'+suffix+'.hdr'
      imgPath = Castorfilepath+'_fr1'+suffix+'.img'
    else:
      # paths to Interfile header and binary image
      hdrPath = Castorfilepath+suffix+'.hdr'
      imgPath = Castorfilepath+suffix+'.img'

    # parse the Interfile header into a dictionary
    header = dict()
    with open (hdrPath) as f:
      l = f.readline()
      while l:
        l = f.readline()
        # split keys from values
        s = l.split(':=')
        if len(s)>1:
          # store key-value pair, trim any white spaces
          header[s[0].strip().replace('!','')]=s[1].strip()

    # check some fields, only simple 3D volume Interfile files are supported currently
    if 'number of frame groups' in header.keys() and int(header['number of frame groups'])>1:
      print ('Number of frame groups > 1, not supported yet!')
      quit()

    # number format for voxel values
    if header['number format']=='short float' and header['number of bytes per pixel']=='4':
      precision = np.float32
    elif header['number format']=='long float' and header['number of bytes per pixel']=='8':
      precision = np.double
    else:
      print ('Number format not supported, only floating point number formats are supported!')

    # image dimensions (X Y Z)
    nbDim = int(header['number of dimensions'])
    # number of voxels for each dimension
    dimNbVox = np.zeros(nbDim, np.int32)
    # voxel size in mm for each dimension
    dimVoxSize = np.zeros(nbDim, np.float32)
    # offset for the field-of-view in mm
    offset = np.zeros(nbDim, np.float32)
    for d in range(0,nbDim):
      dimNbVox[d]=int(header['matrix size [{:d}]'.format(d+1)])
      dimVoxSize[d]=float(header['scaling factor (mm/pixel) [{:d}]'.format(d+1)])
      offset[d]=float(header['first pixel offset (mm) [{:d}]'.format(d+1)])

    # bed offset in Z, if available (if available in the CASToR datafile used for reconstruction, it should correspond to the DICOM positioning fields in the raw data)
    # TODO not sure this always works correctly
    if 'horizontal bed relative position (mm)' in header.keys():
      offset[2] -= float(header['horizontal bed relative position (mm)'])

    # Affine transform for NIfTI
    affine=np.array([[-dimVoxSize[0],0,0,0.5*(dimNbVox[0]-1)*dimVoxSize[0]+offset[0]],
    [0,dimVoxSize[1],0,-0.5*(dimNbVox[1]-1)*dimVoxSize[1]-offset[1]],
    [0,0,dimVoxSize[2],-0.5*(dimNbVox[2]-1)*dimVoxSize[2]-offset[2]],
    [0,0,0,1]])

    # read dynamic (time frame) information and images from other frames
    if nbFrames>1:
      # Actual image matrix (X Y Z T)
      im = np.zeros((dimNbVox[0], dimNbVox[1], dimNbVox[2], nbFrames),np.float32)  

      # load each frame and store the image matrix and the frame start time and duration 
      # the order of dimensions of the image matrix is inverted to match NIfTI
      for fr in range(0,nbFrames):
        # name of the frame files
        hdrPath = Castorfilepath+'_fr{:d}'.format(fr+1)+suffix+'.hdr'
        imgPath = Castorfilepath+'_fr{:d}'.format(fr+1)+suffix+'.img'

        # parse the Interfile header into a dictionary
        header = dict()
        with open (hdrPath) as f:
          l = f.readline()
          while l:
            l = f.readline()
            # split keys from values
            s = l.split(':=')
            if len(s)>1:
              # store key-value pair, trim any white spaces
              header[s[0].strip().replace('!','')]=s[1].strip()
        
        # load image matrix from the binary .img Interfile file and invert the order of dimensions to match NIfTI
        im[:,:,:,fr] = np.transpose(np.fromfile(imgPath, dtype=precision, count=-1).reshape(dimNbVox[::-1].tolist()))
        # frame start time information in s
        frameStartTime.append(float(header['image start time (sec)']))
        # frame start duration in ms, apparently required by Pmod
        frameDuration.append(float(header['image duration (sec)'])*1000.)
    else:
      # load image matrix from the binary .img Interfile file and invert the order of dimensions to match NIfTI
      im = np.transpose(np.fromfile(imgPath, dtype=precision, count=-1).reshape(dimNbVox[::-1].tolist()))


    # convert voxel values from float to uint16
    # compute rescale slope/intercept
    rescaleSlope=1.
    rescaleIntercept=0.
    if convertFloatToInt:
      print ("Initial range of image voxel values (format {}): min={:g} max={:g}".format(precision, np.min(im), np.max(im)))
      rescaleIntercept = np.min(im)
      im = im-rescaleIntercept

      rescaleSlope = np.max(im)/65535.
      if rescaleSlope>2.:
        print("Warning! The rescale slope is surprisingly high ({:g}), so the conversion from float to uint16 might compromise image voxel values. Check if your CASToR image has some very noisy values, at image edges for instance. If this is the case, apply a mask or similar to avoid very high unnecessary voxel values! ".format(rescaleSlope))
      im = im/rescaleSlope
      #convert image to uint16
      im = np.uint16(im) 
      print ("Final range of image voxel values (format uint16): min={:d} max={:d}".format(np.min(im), np.max(im)))
      
    # create the final NIfTI image
    if niftiVersion==1:
      niftiIm = nib.Nifti1Image(im, affine)
    elif niftiVersion==2:
      niftiIm = nib.Nifti2Image(im, affine)

    # set units
    niftiIm.header.set_xyzt_units('mm', 'sec')
    niftiIm.header.set_slope_inter(rescaleSlope,rescaleIntercept)
      
    # store information for the time dimension in DICOM extension, used by Pmod
    if nbFrames>1 and niftiVersion==1:    
      dicomds = pyd.Dataset()
      dicomds.add_new((0x0054,0x1001),'CS','Bq/ml')
      print("Warning! The unit for voxel values is set to Bq/ml by default, but we can't know if this is true from the current Interfile!")
      dicomds.add_new((0x0055,0x0010),'LO','PMOD_1')
      dicomds.add_new((0x0055,0x1001),'FD',frameStartTime)
      dicomds.add_new((0x0055,0x1004),'FD',frameDuration)
      dcmext = nib.nifti1.Nifti1DicomExtension(2, dicomds) # Use DICOM ecode 2
      niftiIm.header.extensions.append(dcmext)

    # save the final NIfTI image to .nii file
    if outFolder:
      inFolderName, inFileName = os.path.split(Castorfilepath)
      output_path = outFolder+inFileName+suffix+'.nii'
      nib.save(niftiIm, output_path)
    else:
      output_path = Castorfilepath+suffix+'.nii'
      nib.save(niftiIm, output_path)
    
    print(f"Successfully converted to NIfTI: {output_path}")

