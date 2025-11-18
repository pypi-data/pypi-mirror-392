# Face Anonymizer

| Original Frame | `faceblur` output (using default options)|
|--------|-------|
| ![Before](https://raw.githubusercontent.com/ayusrjn/face-anonymizer/refs/heads/video-support/images/target2.jpg) | ![After](https://raw.githubusercontent.com/ayusrjn/face-anonymizer/refs/heads/video-support/images/target2_blurred.jpg) |


This repository contains roboust solution for detecting and anonymizing human faces in photos and videos and video streams. The primary goal is to protect privacy of individuals while retaining the overall structure of the media

This toolkit is designed for researchers, developers, and organizations handling visual data that requires privacy compliance (e.g., GPDR, CCPA)

## Features
- Real Time Detection - Utilizes state-of-the-art models Currently Custom Trained YOLO model for accurate face localization.
- Multiple Anonymization Methods : Supports several techniques to obscure faces:
	+ Gaussian Blur : Applies a strong, customizable blur filter.
	+ Pixelation/Mosaic : Divides the face into large, indistinguisable blocks.
- Video Processing : Processes sequential frames from video files or live camera feeds.
- Configurable Parameters : Allows users to adjust the strength of the blur or the size of the pixelation block.