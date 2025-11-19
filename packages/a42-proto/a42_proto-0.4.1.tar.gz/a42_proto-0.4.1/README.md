# 📦 A42 Protobuf Bindings (`a42-proto`)

Dieses Python-Paket enthält die **Protobuf-Bindings für Sensordaten im A42-Format**. Es erlaubt das einfache Einlesen und Verarbeiten von LiDAR-Scans und zugehörigen Objektinformationen.

---

## 🔽 Datendownload

👉 [KIT Sync & Share Download](https://bwsyncandshare.kit.edu/s/6pLYbjB9Etxe3gY)

---

## 📥 Installation

```bash
pip install a42-proto
```

---

## 🧪 Beispielskripte

- [`analyze_proto.py`](https://github.com/HSE-VSV/DataReaderA42/blob/581dea222b6871f6ef4e66ad9e998c3d5a60af08/scripts/analyze_proto.py) – aggregierte Auswertung über Frames, Scans, Punkte, Objekte  
- [`visualize_pointcloud.py`](https://github.com/HSE-VSV/DataReaderA42/blob/581dea222b6871f6ef4e66ad9e998c3d5a60af08/scripts/visualize_pointcloud.py) – zeigt eine Punktwolke in Open3D

---

## 📄 Data Structure

### Frame
- `frame_timestamp_ns` – global timestamp in nanoseconds  
- `lidars[]` – list of `LidarScan` messages  
- `frame_id` - unique identifier for the frame

**Example:**
```python
first_scan = frame.lidars[0]
```

---

### LidarScan
- `laser_name` – sensor identifier (`LaserName` enum)  
- `scan_timestamp_ns` – timestamp of this scan (ns)  
- `pointcloud` – LiDAR point cloud (`PointCloud`)  
- `calibration` – sensor calibration (`SensorCalibration`)  
- `object_list[]` – detected objects (`ObjectBBox`)  

**Example:**
```python
objects = scan.object_list[0]
```

---

### PointCloud

All fields are stored as **byte arrays** and must be decoded into NumPy arrays.

- `cartesian` – XYZ coordinates (`float32`, shape N×3)  
- `intensity` – intensity values (`uint16`)  
- `ambient` – ambient light / signal quality (`uint16`)  
- `velocity` – point-wise velocity (`float32`)  
- `reflectivity` – reflectivity values (`uint16`)  
- `timestamp_offset` – per‑point timestamp offset (`uint64` ns)  
- `channel_id` – channel index (`uint16`)  

**Example decoding:**
```python
import numpy as np
xyz = np.frombuffer(pc.cartesian, dtype=np.float32).reshape(-1, 3)
intensity = np.frombuffer(pc.intensity, dtype=np.uint16)
```

---

### ObjectBBox
- `id` – object ID  
- `timestamp_ns` – timestamp of the object (ns)  
- `position {x,y,z}` – center position  
- `dimension {x,y,z}` – object size  
- `orientation {x,y,z,w}` – quaternion orientation  
- `velocity {x,y,z}` – velocity vector  
- `pointcloud` – sub‑pointcloud inside the bounding box  
- `obj_class` – semantic class  
- `obj_class_score` – classification confidence  

**Example:**
```python
pos = obj.position
```

---

### SensorCalibration
- `sensor_name` – sensor identifier  
- `extrinsic[]` – 4×4 row‑major extrinsic matrix  
- `vertical_fov`, `horizontal_fov` – field of view  
- `vertical_scanlines`, `horizontal_scanlines` – resolution  
- `horizontal_angle_spacing` – angle spacing (deg)  
- `beam_altitude_angles[]` – altitude angles  
- `beam_azimuth_angles[]` – azimuth angles  
- `frame_mode` – scan mode  
- `scan_pattern` – scan pattern identifier  

**Example:**
```python
vfov = scan.calibration.vertical_fov
```

---