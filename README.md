### AFNI Brain Co-Registration

This Flywheel gear warps the supplied `warp_target` nifti image into the same space as the `functional` nifti image.
The input `warp_target` should already be warped correctly to the `anatomical`. This gear generates a warp from the
`functional` to the `anatomical` by using AFNI's `align_epi_anat.py`. The inverse of warp is applied to the `warp_target`.

Inputs:
  - `functional`: an fMRI image.
  - `anatomical`: a T1 image.
  - `warp_target`: a segmentation in the same space as `anatomical` that should be warped to the same space as `functional`.

Outputs (for `functional` input called `functional.nii.gz` and `anatomical` input called `anatomical.nii.gz`):
  - `functional.nii.gz`: a version of `functional` with some NIFTI header issues addressed (see `fix_nifti.py` for more details).
  - `functional_seg.nii.gz`: a version of `warp_target` that is warped into `functional`-space.
  - `functional_shft_func2anat_mat.aff12.1D`: transform matrix from shifted `functional` to `anatomical`. See code for more details on how to use this matrix.
  - `functional_shft_anat2func_mat.aff12.1D`: transform matrix from `anatomical` to shifted `functional`. See code for more details on how to use this matrix.
  - `stdout.log`: a log file that contains stdout from the script execution.
  - `stderr.log`: a log file that contains stderr from the script execution.
