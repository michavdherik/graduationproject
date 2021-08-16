# Retrieve Sentinel-2 imagery as raster objects.
# Derive indices (e.g. NDVI) from the bands and reproject them 
# to the desired output raster crs and dimensions.
#
# Intialork by Melanie Arp & adapted by Micha van den Herik. 


# Import GIS libraries
library(raster)
library(rgdal)
library(sp)
library(leaflet)
# Import other
library(tidyverse)
library(ggplot2)
library(Rfast)
library(matrixStats)

# Set working directory
setwd("C:/Users/micha/OneDrive - TU Eindhoven/00. Studie Relevant/00. 2IMC00 Thesis/graduationproject")

# Read pre-made Polygon geometry of area of interest
aoi <- readOGR('data/geometries')
# Convert to raster of certain geometry.
out <- raster(aoi)

#------------------------------------------------------------
# create indices from Sentinel-2 imagery (from EO browser)
#------------------------------------------------------------
folder <- 'data/Sentinel-2/'

# function to retrieve Sentinel-2 images and create an index (e.g. NDVI)
sentinel2_index <- function(name1, name2, sent2_path, cloudmask = FALSE){
  # IMPORTANT: index is executed: (name1 - name2) / (name1 + name2)
  
  # load Sentinel-2 images (retrieved from EO browser)
  stack1 <- stack(paste0(folder, list.files(folder, name1)))
  stack2 <- stack(paste0(folder, list.files(folder, name2)))
  
  # check equal nlayers()
  if (nlayers(stack1) != nlayers(stack2)){
    warning('Sentinel-2 images are missing, check the designated folder.')
  }
  
  if (cloudmask){
    classified_stack <- stack(paste0(folder, list.files(folder, 'classification')), bands = 1)
    if (nlayers(stack1) != nlayers(classified_stack)){
      warning('Sentinel-2 scene classification images are missing, check the designated folder.')
    }
  }
  
  index_stack <- stack()
  date_names <- NULL # Use date as unique name
  for (i in 1:length(names(stack1))) {
    date1 <- str_sub(names(stack1[[i]]), start = 2, end = 11)
    date2 <- str_sub(names(stack2[[i]]), start = 2, end = 11)
    if (date1 == date2) {
      print(paste0(i, ' out of ', length(names(stack1))))
      date_names <- c(date_names, date1)
      layer <- (stack1[[i]] - stack2[[i]])/(stack1[[i]] + stack2[[i]])
      
      if (cloudmask){
        # using sentinel classification to replace cloud pixels with NA value for NDVI
        # value 65535 = cloud high probability
        # value 49345 = cloud medium probability
        cl <- classified_stack[[i]]
        cl[cl == 65535] <- NA
        cl[cl == 49345] <- NA
        layer <- mask(layer, cl)
      }
      index_stack <- addLayer(index_stack, layer)
    }
  }
  names(index_stack) <- date_names
  return(index_stack)
}

# Calculate vegetation index (NDVI) 
ndvi_stack <- sentinel2_index('L2A_B08', 'L2A_B04', sent2_path = folder)

# Flip raster to have north up, south down
ndvi_stack <- flip(t(ndvi_stack), direction='y')

# Extract layer from stack
ndvi_layer <- subset(ndvi_stack, 1, drop=TRUE)


# Aggregate to resolution:
# From sentinel-2: latitude degree/pixel = 0.0023898 
# multiplied by number of pixels vertically *1422,  times ~km per latitude degree *111 = number of km vertically on picture.
# That divided by 1470 = km/pixel vertically = 0.2652678
# resolution we want: E.g.: 0.023898 -> equals # dimensions of (126, 167), ncells: 21042
# resolution of source data: (1422, 1250), 1777500.
# aggregation factor then equals 1422/126, 1250/167 ~= 10
ndvi_layer <- aggregate(ndvi_layer, fact=10)

# Crop to output polygon                       
ndvi_layer <- crop(ndvi_layer, extent(out))

# Write to file.
writeRaster(ndvi_layer, 'data/output/ndvi_2017_CMtAGG10.tiff', 'overwrite'=TRUE)