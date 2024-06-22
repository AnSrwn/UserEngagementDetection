# UserEngagementDetection
<p align="justify">
  
This project uses video-based detection to analyze user engagement and visualizes it on a real-time dashboard. It focuses on the use-case of online trainings with a teacher. The project was part of my master-thesis.

<img src="https://github.com/AnSrwn/UserEngagementDetection/assets/38131809/34b59fe6-298b-458d-a0dc-b476c3f38a0c" width="400"/>
<img src="https://github.com/AnSrwn/UserEngagementDetection/assets/38131809/523122d7-76b1-49a4-a8a0-895c7d54aaff" width="400"/>


Two examples of the analysis dashboard.

<br>

## Features ##
<p align="justify">
  
* Video Stream with WebRTC.
* Analyzing images of the video stream with a KI model to detect the user engagement attributes engagement, frustration, confusion und boredom. An existing model was used (https://github.com/The-revolutionary-army/Engagement-and-comprehension-level-detection/tree/master/Models), which was trained on the DAiSEE dataset (https://arxiv.org/pdf/1609.01885).
* Visualization of the data with the help of D3.js.

<br>

## Technologies
* Backend: FastAPI, PostgreSQL with sqlmodel and Tensorflow.
* Frontend: Nuxt 3 and D3.js for visualization.
* Communication: WebRTC and REST.

<br>

## Architecture
<p align="justify">
  
![Architektur](https://github.com/AnSrwn/UserEngagementDetection/assets/38131809/0766ffb3-31b3-427e-9dc5-55229f56f6e8)


## Setup
Setup instructions can be found in the frontend and backend folders.
