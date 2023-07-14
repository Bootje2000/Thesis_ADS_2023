// Load the Hansen Global Forest Change dataset
var hansen = ee.Image('UMD/hansen/global_forest_change_2015');

// Select the forest cover band
var forestCover = hansen.select('treecover2000');

// Define a forest mask based on the tree cover threshold
var forestMask = forestCover.gt(30); // Adjust the threshold as needed

// Convert the forest mask to a binary mask (0 for non-forest, 1 for forest)
var binaryMask = forestMask.updateMask(forestMask);

// Convert the binary mask to a geometry object representing forest areas
var forestGeometry = binaryMask.reduceToVectors({
  geometry: geometry,
  scale: 30,
  geometryType: 'polygon',
  eightConnected: false,
  labelProperty: 'binaryMask',
});

// Load Landsat 5, 7, and 8 surface reflectance collections (C02/T1_L2)
var l5L2 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
  .filterBounds(geometry);
var l7L2 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2')
  .filterBounds(geometry);

// Merge the collections into a single collection
var mergedCollection = l5L2.merge(l7L2);

// Select a specific image from the collection
var image = ee.Image(mergedCollection.first());

// Clip the image to the study area
var clippedImage = image.clip(geometry);

// Apply the forest mask to the clipped image
var forestImage = clippedImage.updateMask(binaryMask);

// Get the image's band names
var bandNames = image.bandNames();
var seedValue = 124;
// Generate random points within the forest geometry
var randomPoints = ee.FeatureCollection.randomPoints({
  region: forestGeometry,
  points: 3000,
  seed: seedValue
});

// Sample the forest image at the random points
var sampledData = forestImage.sampleRegions({
  collection: randomPoints,
  properties: bandNames.getInfo(), // Convert bandNames to a plain list of strings
  scale: 30, // Specify the pixel scale
});

var coordinates = randomPoints.geometry().coordinates();
print('Random Points Coordinates:', coordinates);

var assetPath = 'users/hondjuuhx/ee-thesis-uu-2023/'
// Export the FeatureCollection to the asset
Export.table.toAsset({
  collection: randomPoints,
  description: 'FeatureCollection to Asset',
  assetId: assetPath
});

// Display the forest image
Map.addLayer(forestImage, {bands: ['SR_B4', 'SR_B3', 'SR_B2'], max: 3000}, 'Forest Image');

// Display the sample area (random points)
Map.addLayer(randomPoints, {color: 'red'}, 'Sample Area');

print('Sampled Data:', sampledData); // Print the sampled pixel values

Map.centerObject(geometry, 10);
