/**
 * Frontend-side index metadata (mirrors backend INDEX_META).
 * Used for labels, color scales, and UI hints without an API call.
 */

export const INDEX_META = {
  NDVI: {
    label:       'NDVI',
    fullName:    'Normalized Difference Vegetation Index',
    range:       [-1, 1],
    goodRange:   [0.2, 1],
    colorVar:    '--ndvi-color',
    color:       '#5deb9b',
    unit:        '',
    description: 'Measures live green vegetation density. Values above 0.5 indicate dense, healthy vegetation.',
    bands:       'B08 (NIR) & B04 (Red)',
    useCases:    ['Agriculture', 'Forestry', 'Land cover'],
  },
  NDWI: {
    label:       'NDWI',
    fullName:    'Normalized Difference Water Index',
    range:       [-1, 1],
    goodRange:   [0, 1],
    colorVar:    '--ndwi-color',
    color:       '#3a9be8',
    unit:        '',
    description: 'Highlights open water bodies and moisture. Values above 0 indicate water presence.',
    bands:       'B03 (Green) & B08 (NIR)',
    useCases:    ['Water bodies', 'Drought monitoring', 'Flood mapping'],
  },
  EVI: {
    label:       'EVI',
    fullName:    'Enhanced Vegetation Index',
    range:       [-1, 1],
    goodRange:   [0.2, 1],
    colorVar:    '--evi-color',
    color:       '#a78bfa',
    unit:        '',
    description: 'Improved vegetation index that corrects for atmospheric distortion and canopy background signals.',
    bands:       'B08 (NIR), B04 (Red) & B02 (Blue)',
    useCases:    ['Dense forests', 'Tropical vegetation', 'Biomass estimation'],
  },
  SAVI: {
    label:       'SAVI',
    fullName:    'Soil-Adjusted Vegetation Index',
    range:       [-1.5, 1.5],
    goodRange:   [0.1, 1],
    colorVar:    '--savi-color',
    color:       '#fbbf24',
    unit:        '',
    description: 'Minimises soil brightness influence. Especially useful in arid and sparsely vegetated areas.',
    bands:       'B08 (NIR) & B04 (Red)',
    useCases:    ['Arid regions', 'Rangelands', 'Semi-arid agriculture'],
  },
  NDMI: {
    label:       'NDMI',
    fullName:    'Normalized Difference Moisture Index',
    range:       [-1, 1],
    goodRange:   [0.2, 1],
    colorVar:    '--ndmi-color',
    color:       '#34d399',
    unit:        '',
    description: 'Sensitive to moisture content in vegetation canopy. High values indicate well-watered vegetation.',
    bands:       'B8A (NIR narrow) & B11 (SWIR1)',
    useCases:    ['Drought stress', 'Irrigation monitoring', 'Fire risk'],
  },
}

export const PRESET_CONFIGS = {
  agriculture: {
    label:       '🌾 Agriculture',
    description: 'Monitor crop health and field conditions',
    indices:     ['NDVI', 'SAVI', 'NDMI'],
    cloudMax:    20,
    temporal:    '16D',
  },
  forestry: {
    label:       '🌲 Forestry',
    description: 'Analyze forest cover and canopy health',
    indices:     ['NDVI', 'EVI', 'NDMI'],
    cloudMax:    30,
    temporal:    '1M',
  },
  water: {
    label:       '💧 Water Bodies',
    description: 'Map and monitor surface water extent',
    indices:     ['NDWI', 'NDVI'],
    cloudMax:    20,
    temporal:    '16D',
  },
  drought: {
    label:       '☀️ Drought Monitor',
    description: 'Track vegetation stress and moisture deficit',
    indices:     ['NDMI', 'NDVI', 'SAVI'],
    cloudMax:    40,
    temporal:    '16D',
  },
}

export const ALL_INDICES = Object.keys(INDEX_META)

export function getIndexColor(indexName) {
  return INDEX_META[indexName]?.color ?? '#fff'
}

export function getIndexRange(indexName) {
  return INDEX_META[indexName]?.range ?? [-1, 1]
}
