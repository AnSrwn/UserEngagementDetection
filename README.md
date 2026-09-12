# UserEngagementDetection
<p align="justify">

This project uses video-based detection to analyze user engagement and visualizes the results on a real-time dashboard. It focuses on supporting instructors during online training sessions and was developed as part of my master's thesis.


<img src="https://github.com/AnSrwn/UserEngagementDetection/assets/38131809/34b59fe6-298b-458d-a0dc-b476c3f38a0c" width="400"/>
<img src="https://github.com/AnSrwn/UserEngagementDetection/assets/38131809/523122d7-76b1-49a4-a8a0-895c7d54aaff" width="400"/>


Two examples of the analysis dashboard.

<br>

## Features ##
<p align="justify">

* Video streaming from participants to the backend via WebRTC.
* Frame-based analysis of engagement, frustration, confusion and boredom using an existing TensorFlow/Keras model (https://github.com/The-revolutionary-army/Engagement-and-comprehension-level-detection/tree/master/Models) trained on the DAiSEE dataset (https://arxiv.org/pdf/1609.01885).
* Parallel processing of analysis jobs using local Dask worker processes.
* Adaptive frame sampling based on the number of pending analysis jobs to reduce processing load.
* Persistent storage of analysis results using PostgreSQL and provision through REST APIs.
* Interactive visualization of current and historical engagement data using D3.js.

<br>

## Technologies
* Backend: FastAPI, PostgreSQL with sqlmodel, Dask and Tensorflow.
* Frontend: Nuxt 3 and D3.js for visualization.
* Communication: WebRTC with aiortc and REST.

<br>

## Architecture
<p align="justify">
  
![Architektur](https://github.com/AnSrwn/UserEngagementDetection/assets/38131809/0766ffb3-31b3-427e-9dc5-55229f56f6e8)


## Setup
Setup instructions can be found in the frontend and backend folders.
