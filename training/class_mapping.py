"""Auto-generated class mapping for AgroSentinel model"""

CLASSES = ['pepper_bacterial_spot', 'pepper_healthy', 'potato_early_blight', 'potato_healthy', 'potato_late_blight', 'tomato_bacterial_spot', 'tomato_early_blight', 'tomato_healthy', 'tomato_late_blight', 'tomato_leaf_mold', 'tomato_mosaic_virus', 'tomato_septoria_leaf_spot', 'tomato_spider_mites', 'tomato_target_spot', 'tomato_yellow_leaf_curl_virus']

NUM_CLASSES = 15

CLASS_TO_IDX = {
    "pepper_bacterial_spot": 0,
    "pepper_healthy": 1,
    "potato_early_blight": 2,
    "potato_healthy": 3,
    "potato_late_blight": 4,
    "tomato_bacterial_spot": 5,
    "tomato_early_blight": 6,
    "tomato_healthy": 7,
    "tomato_late_blight": 8,
    "tomato_leaf_mold": 9,
    "tomato_mosaic_virus": 10,
    "tomato_septoria_leaf_spot": 11,
    "tomato_spider_mites": 12,
    "tomato_target_spot": 13,
    "tomato_yellow_leaf_curl_virus": 14,
}

IDX_TO_CLASS = {
    0: "pepper_bacterial_spot",
    1: "pepper_healthy",
    2: "potato_early_blight",
    3: "potato_healthy",
    4: "potato_late_blight",
    5: "tomato_bacterial_spot",
    6: "tomato_early_blight",
    7: "tomato_healthy",
    8: "tomato_late_blight",
    9: "tomato_leaf_mold",
    10: "tomato_mosaic_virus",
    11: "tomato_septoria_leaf_spot",
    12: "tomato_spider_mites",
    13: "tomato_target_spot",
    14: "tomato_yellow_leaf_curl_virus",
}

DISEASE_INFO = {
    "pepper_bacterial_spot": {"crop": "Pepper", "disease": "Bacterial Spot", "severity": "medium"},
    "pepper_healthy": {"crop": "Pepper", "disease": "Healthy", "severity": "none"},
    "potato_early_blight": {"crop": "Potato", "disease": "Early Blight", "severity": "high"},
    "potato_healthy": {"crop": "Potato", "disease": "Healthy", "severity": "none"},
    "potato_late_blight": {"crop": "Potato", "disease": "Late Blight", "severity": "critical"},
    "tomato_bacterial_spot": {"crop": "Tomato", "disease": "Bacterial Spot", "severity": "medium"},
    "tomato_early_blight": {"crop": "Tomato", "disease": "Early Blight", "severity": "high"},
    "tomato_healthy": {"crop": "Tomato", "disease": "Healthy", "severity": "none"},
    "tomato_late_blight": {"crop": "Tomato", "disease": "Late Blight", "severity": "critical"},
    "tomato_leaf_mold": {"crop": "Tomato", "disease": "Leaf Mold", "severity": "medium"},
    "tomato_mosaic_virus": {"crop": "Tomato", "disease": "Mosaic Virus", "severity": "high"},
    "tomato_septoria_leaf_spot": {"crop": "Tomato", "disease": "Septoria Leaf Spot", "severity": "medium"},
    "tomato_spider_mites": {"crop": "Tomato", "disease": "Spider Mites", "severity": "medium"},
    "tomato_target_spot": {"crop": "Tomato", "disease": "Target Spot", "severity": "medium"},
    "tomato_yellow_leaf_curl_virus": {"crop": "Tomato", "disease": "Yellow Leaf Curl Virus", "severity": "critical"},
}
