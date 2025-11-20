# File name: create_and_insert_products.py
import sqlite3

# Connect (or create new) Database.db
conn = sqlite3.connect('Database.db')
cursor = conn.cursor()

# Step 1: Create products table (if not exists)
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT,
    subcategory TEXT,
    type TEXT,
    description TEXT,
    features TEXT,
    price_usd REAL,
    image_url TEXT,
    stock INTEGER,
    rating REAL,
    created_at TEXT,
    updated_at TEXT
);
''')

# Step 2: 30 products data
products = [
    (1, "AI Cam Pro 3000", "Hardware", "AI Tracking Camera", "Camera", "Full-field AI camera automatically tracks ball and players", "4K, Auto Tracking, Livestream, PTZ", 3499, "/images/ai_cam_pro3000.jpg", 20, 4.8, "2025-11-19", "2025-11-19"),
    (2, "AI Cam Ultra", "Hardware", "AI Tracking Camera", "Multi-camera", "AI camera system automatically records and analyzes matches", "Multi-view, AI Analytics, Livestream", 8999, "/images/ai_cam_ultra.jpg", 10, 4.7, "2025-11-19", "2025-11-19"),
    (3, "GimbalCam X2", "Hardware", "Gimbal / Webcam AI Camera", "Camera", "Compact PTZ AI gimbal camera, suitable for livestream and analysis", "4K, AI Tracking, Stabilization", 1350, "/images/gimbalcam_x2.jpg", 50, 4.8, "2025-11-19", "2025-11-19"),
    (4, "GimbalCam Link 4K", "Hardware", "Gimbal / Webcam AI Camera", "Camera", "AI gimbal 4K, livestream, automatic player tracking", "4K, AI Stabilization, Auto Framing", 700, "/images/gimbalcam_link4k.jpg", 30, 4.6, "2025-11-19", "2025-11-19"),
    (5, "AI Video Hub TS2‑08", "Hardware", "AI Video Analysis Device", "Module", "AI processor analyzes multiple camera videos, creates highlights and reports", "Multi-channel, AI Object Tracking", 3999, "/images/ai_video_hub_ts2.jpg", 5, 4.6, "2025-11-19", "2025-11-19"),
    (6, "AI Processing Unit Pro", "Hardware", "AI Video Analysis Device", "Module", "Upgrade module enhances AI processing capability for camera systems", "AI Object Detection, Multi-Stream", 850, "/images/ai_processing_unit_pro.jpg", 10, 5.0, "2025-11-19", "2025-11-19"),
    (7, "GoalTrack Sensor", "Hardware", "Sensor & VAR Devices", "Sensor", "Sensor and camera system tracks the ball, supports referees", "Goal-line, Offside, 3D Tracking", 12000, "/images/goaltrack_sensor.jpg", 3, 5.0, "2025-11-19", "2025-11-19"),
    (8, "GoalMag Sensor", "Hardware", "Sensor & VAR Devices", "Sensor", "Electromagnetic sensor accurately determines goals", "Goal-line, Magnetic Sensor", 8500, "/images/goalmag_sensor.jpg", 2, 4.9, "2025-11-19", "2025-11-19"),
    (9, "AI DualCam EO/IR", "Hardware", "Sensor & VAR Devices", "Camera", "Dual sensor EO/IR gimbal camera, AI tracking", "Dual Sensor, Night Vision, AI Tracking", 12500, "/images/ai_dualcam_eoir.jpg", 4, 4.8, "2025-11-19", "2025-11-19"),
    (10, "MatchAnalyzer Suite", "Software", "Match Analysis Software", "Software", "AI software analyzes matches, tags and provides statistics", "Tagging, Player Tracking, Reports", 499, "/images/matchanalyzer_suite.jpg", None, 4.5, "2025-11-19", "2025-11-19"),
    (11, "ProMatch Analyzer", "Software", "Match Analysis Software", "Software", "Professional match analysis software, creates detailed reports", "Multi-camera, Event Tagging, Stats", 1200, "/images/promatch_analyzer.jpg", None, 4.6, "2025-11-19", "2025-11-19"),
    (12, "AutoHighlight Editor", "Software", "Automatic Highlight & Editing", "Service", "AI service automatically edits videos and creates highlights", "Auto Edit, Multi-camera, Player Clips", 299, "/images/autohighlight_editor.jpg", None, 4.7, "2025-11-19", "2025-11-19"),
    (13, "PlayerHighlight AI", "Software", "Automatic Highlight & Editing", "Service", "Automatically creates individual player highlights from match videos", "Player Focus, AI Highlight, Multi-format", 399, "/images/playerhighlight_ai.jpg", None, 4.6, "2025-11-19", "2025-11-19"),
    (14, "MotionCapture Pro", "Software", "3D Motion Analysis", "Software", "AI software analyzes player movements", "3D Motion Tracking, 3D Skeleton, Injury Detection", 1999, "/images/motioncapture_pro.jpg", None, 4.6, "2025-11-19", "2025-11-19"),
    (15, "FootMotion Analyzer", "Software", "3D Motion Analysis", "Software", "Software analyzes player movements and techniques", "3D Motion, Performance Analysis, Reports", 899, "/images/footmotion_analyzer.jpg", None, 4.5, "2025-11-19", "2025-11-19"),
    (16, "VirtualReplay System", "Software", "VAR & Virtual Replay", "Service", "3D AI replay supports referees and coaches", "Offside Detection, 3D Replay", 1499, "/images/virtualreplay_system.jpg", None, 4.8, "2025-11-19", "2025-11-19"),
    (17, "SemiOffside AI", "Software", "VAR & Virtual Replay", "Service", "AI system assists in offside determination", "AI Tracking, Multi-camera", 1800, "/images/semi_offside_ai.jpg", None, 4.7, "2025-11-19", "2025-11-19"),
    (18, "LensAdd-on Pro", "Hardware", "AI Tracking Camera", "Accessory", "Extension lens for AI Cam Pro 3000", "Wide-angle, Improved Zoom", 250, "/images/lensaddon_pro.jpg", 15, 4.7, "2025-11-19", "2025-11-19"),
    (19, "TinyCam AI", "Hardware", "Gimbal / Webcam AI Camera", "Camera", "Compact AI camera, suitable for analysis rooms and livestream", "1080p, AI Tracking", 350, "/images/tinycam_ai.jpg", 40, 4.5, "2025-11-19", "2025-11-19"),
    (20, "TeamCam AI", "Hardware", "AI Tracking Camera", "Multi-camera", "Small club version, AI tracking and highlight", "Multi-view, Automated Analysis", 6999, "/images/teamcam_ai.jpg", 8, 4.7, "2025-11-19", "2025-11-19"),
    (21, "AI Coaching Assistant", "Software", "Match Analysis Software", "Software", "AI assists coaches with tactical suggestions", "Tactics Analysis, Event Highlights", 799, "/images/ai_coaching_assistant.jpg", None, 4.6, "2025-11-19", "2025-11-19"),
    (22, "MatchTracker Pro", "Software", "Match Analysis Software", "Software", "Professional match statistics software with AI tagging", "Event Tagging, Player Stats", 599, "/images/matchtracker_pro.jpg", None, 4.5, "2025-11-19", "2025-11-19"),
    (23, "360TrackCam", "Hardware", "AI Tracking Camera", "Camera", "360° AI camera, tracks entire field", "360° Tracking, HD, Livestream", 5999, "/images/360trackcam.jpg", 6, 4.6, "2025-11-19", "2025-11-19"),
    (24, "AI Referee Assistant", "Software", "VAR & Virtual Replay", "Service", "AI assists referees, analyzes fouls and offside", "Offside Detection, Foul Detection", 1299, "/images/ai_referee_assistant.jpg", None, 4.7, "2025-11-19", "2025-11-19"),
    (25, "MotionLab Analyzer", "Software", "3D Motion Analysis", "Software", "AI software analyzes player movements and fitness reports", "Motion Capture, 3D Analysis", 1399, "/images/motionlab_analyzer.jpg", None, 4.5, "2025-11-19", "2025-11-19"),
    (26, "AI Cam Tripod", "Hardware", "AI Tracking Camera", "Accessory", "Premium tripod for AI Cam Pro 3000", "Adjustable Height, Stable", 150, "/images/ai_cam_tripod.jpg", 25, 4.6, "2025-11-19", "2025-11-19"),
    (27, "CloudAnalytics AI", "Software", "Match Analysis Software", "Service", "AI video analysis service on cloud", "Cloud Processing, Player Stats", 399, "/images/cloudanalytics_ai.jpg", None, 4.7, "2025-11-19", "2025-11-19"),
    (28, "TrackCam AI", "Hardware", "Gimbal / Webcam AI Camera", "Camera", "AI with auto tracking, suitable for analysis rooms", "AI Tracking, 4K, Stabilization", 650, "/images/trackcam_ai.jpg", 20, 4.6, "2025-11-19", "2025-11-19"),
    (29, "MultiCam Studio Kit", "Hardware", "AI Video Analysis Device", "Module", "Multi-camera + AI kit for small clubs, livestream & highlight", "4 Cameras, AI Analytics", 2999, "/images/multicam_studio_kit.jpg", 5, 4.5, "2025-11-19", "2025-11-19"),
    (30, "CoachVision Suite", "Software", "Match Analysis Software", "Software", "AI software for coaches, statistics and tactics", "AI Tactics, Event Analysis, Player Stats", 699, "/images/coachvision_suite.jpg", None, 4.6, "2025-11-19", "2025-11-19"),
]

# Step 3: Delete old data (if you want complete refresh) - you can skip this line if you don't want to delete
cursor.execute("DELETE FROM products")

# Step 4: Insert 30 products
cursor.executemany('''
INSERT OR IGNORE INTO products 
(product_id, name, category, subcategory, type, description, features, price_usd, image_url, stock, rating, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', products)

# Save and close
conn.commit()
conn.close()

print("Table created + Successfully added 30 products to Database.db")
print("You can now run the website normally!")