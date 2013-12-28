#! /usr/bin/env python
'''
Created on 2012/04/20

@author: nic

This is a Gimp plugin

Updated: 
	Guy West (gywst) 2013/10/12
	http://github.com/gywst
	- added support for xxhdpi 
	- see http://developer.android.com/design/style/iconography.html

Updated: 
	Thomas Koch (Skywave) 2013/12/28
	http://github.com/skywave
	- added support for xxxhdpi 
	- see http://developer.android.com/design/style/iconography.html


Actions: 
    - Save Visible Selection to android drawables into 
        - res/drawable-ldpi 
        - res/drawable-mdpi 
        - res/drawable-hdpi 
        - res/drawable-xhdpi
        - res/drawable-xxhdpi 
        - res/drawable-xxxhdpi 
        
    - You can select a new width for the drawable and select the target density.
    - Drawables for other densities will be scaled accordingly

Installation: 
    - Put this file into your gimp plugin directory, ie: ~/.gimp-2.6/plug-ins/gimpfu_android_xdpi.py
    - Restart Gimp
    - Run script via Filters/Android/Write Android XDPIs...
'''

import gimpfu
import gimp
import os

DEFAULT_OUTPUT_DIR = os.getcwd()
DEFAULT_OUTPUT_EXT = 'png'
DEFAULT_OUTPUT_DPI = 'drawable-mdpi'

UPSCALE_WARN_MESSAGE = '\nQuality of your application could be seriously affected when using upscaled bitmaps !'

dpi_ratios = (('drawable-ldpi',0.75),
              ('drawable-mdpi',1),
              ('drawable-hdpi',1.5),
              ('drawable-xhdpi',2),
              ('drawable-xxhdpi',3)
              ('drawable-xxxhdpi',4))



def write_xdpi(img, layer, res_folder, image_basename, target_width, target_dpi, image_extension):
    '''
    Resize and write images for all android density folders 
    
    @param img: gimp image
    @param layer: gimp layer (or drawable)
    @param res_folder: output directory : basically res folder of your android project 
    @param image_basename: basename of your image, ex: icon
    @param target_width: new width for your image
    @param target_dpi: reference density for your target width
    @param image_extension: output format
    '''
    
    warnings = list()
    
    # reference density requested by the user
    target_density_ratio = dict(dpi_ratios).get(target_dpi)
    
    gimpfu.pdb.gimp_edit_copy_visible(img); #@UndefinedVariable
    
    for dpi_ratio in dpi_ratios:
        new_img = gimpfu.pdb.gimp_edit_paste_as_new(); #@UndefinedVariable
        
        # resize requested by the user
        resize_ratio = float(target_width) / float(new_img.width)

        target_res_folder = os.path.join(res_folder, dpi_ratio[0])
        if (os.path.exists(res_folder) and not os.path.exists(target_res_folder)):
            os.makedirs(target_res_folder)
            
        target_res_filename = os.path.join(target_res_folder, image_basename+'.'+image_extension)
        
        # Compute new dimensions for the image
        density_ratio = dpi_ratio[1]
        
        new_width = round(float(new_img.width) / target_density_ratio * density_ratio * resize_ratio)
        new_height = round(float(new_img.height) / target_density_ratio * density_ratio * resize_ratio)
        
        print('%s : %f, %f, %f' % (dpi_ratio[0], target_density_ratio, density_ratio, resize_ratio))
        
        if (new_width>new_img.width):
            warnings.append('Resource for %s has been upscaled by %0.2f' % 
                            (dpi_ratio[0], new_width/new_img.width))
        
        # Save the new Image
        gimpfu.pdb.gimp_image_scale_full( #@UndefinedVariable
            new_img, new_width, new_height, gimpfu.INTERPOLATION_CUBIC)
        
        gimpfu.pdb.gimp_file_save( #@UndefinedVariable
            new_img, new_img.layers[0], target_res_filename, target_res_filename)
        
        gimpfu.pdb.gimp_image_delete(new_img) #@UndefinedVariable
        
    # Show warning message
    if warnings: 
        warnings.append(UPSCALE_WARN_MESSAGE)
        gimp.message('\n'.join(warnings))

gimpfu.register("python_fu_android_xdpi", 
                "Write Android drawables for all DPI folders", 
                "Write images for all android densities", 
                "Nic", "Nicolas CORNETTE", "2012", 
                "<Image>/Filters/Android/Write Android XDPIs...", 
                "*", [
#                    (gimpfu.PF_IMAGE, "image", "Input image", None),
#                    (gimpfu.PF_DRAWABLE, "drawable", "Input drawable", None),
                    (gimpfu.PF_DIRNAME, "res-folder",     "Project res Folder", DEFAULT_OUTPUT_DIR), #os.getcwd()),
                    (gimpfu.PF_STRING, "image-basename", "Image Base Name", 'icon'),
                    (gimpfu.PF_INT, "target-width", "Target Width", 48),
                    (gimpfu.PF_RADIO, "target-dpi", "Base Density", DEFAULT_OUTPUT_DPI, (("ldpi", "drawable-ldpi"), ("mdpi", "drawable-mdpi"), ("hdpi", "drawable-hdpi"), ("xhdpi", "drawable-xhdpi"), ("xxhdpi", "drawable-xxhdpi"),("xxxhdpi", "drawable-xxxhdpi"))),
                    (gimpfu.PF_RADIO, "image-extension", "Image Format", DEFAULT_OUTPUT_EXT, (("gif", "gif"), ("png", "png"), ("jpg", "jpg"))),
                      ], 
                [], 
                write_xdpi) #, menu, domain, on_query, on_run)

gimpfu.main()
