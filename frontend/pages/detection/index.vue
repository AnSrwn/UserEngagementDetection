<script setup>
import {ref} from "vue";
import WebRTC from "~/composables/WebRTC";


const privacyAgreed = ref(false);
let step = ref(1);

let sender = null;
let stream = null;

let videoSrc = ref(null);
let selectedCamera = ref(null);
let cameraList = ref([]);

let connectionState = ref("disconnected");
let signalingState = ref("missing");

// Template Refs
let videoContainer = ref(null);
let cameraSelection = ref(null);
let statusIndicator = ref(null);

let webRtc = new WebRTC(videoContainer, connectionState, signalingState);

watch(step, (newValue, oldValue) => {
      if (newValue === 2) {
        start();
      }
    }
);

watch(selectedCamera, async (newValue, oldValue) => {
  if (oldValue !== null && newValue !== oldValue) {
    await onCameraChange();
  }
});

watch(connectionState, (newValue, oldValue) => {
  if (newValue === "checking") {
    statusIndicator.value.style.backgroundColor = "yellow";
  } else if (newValue === "connected") {
    statusIndicator.value.style.backgroundColor = "green";
  } else {
    statusIndicator.value.style.backgroundColor = "red";
  }
});

onDeactivated(() => {
  stop();
})

onBeforeUnmount(() => {
  stop();
})

function getActiveCameraId(stream) {
  return stream.getVideoTracks()
      .map((track) => track.getSettings().deviceId)[0];
}

function getActiveCamera(stream) {
  const activeDeviceId = getActiveCameraId(stream);
  return cameraList.value.find((camera) => camera.deviceId === activeDeviceId);
}

async function getAllCameras() {
  let devices = await navigator.mediaDevices.enumerateDevices()
  return devices.filter(device => device.kind === 'videoinput');
}

async function getStream() {
  let constraints = {}
  if (selectedCamera.value !== null) {
    constraints.video = {deviceId: {exact: selectedCamera.value.deviceId}};
  } else {
    constraints.video = true;
  }

  let newStream = await navigator.mediaDevices.getUserMedia(constraints);

  if (stream !== null) {
    stream.getTracks().forEach(function (track) {
      track.stop();
    });
  }
  stream = newStream;
  return stream;
}

function getVideoTrack(stream) {
  let constraints = {
    frameRate: {
      ideal: 10.0
    },
    facingMode: 'user', // use front camera on mobile devices
    width: {ideal: 1280},
    height: {ideal: 960}
  };

  const [track] = stream.getVideoTracks();
  track.applyConstraints(constraints);
  return track;
}

async function start() {
  webRtc.createPeerConnection();

  try {
    stream = await getStream();
    const trackForPredictions = getVideoTrack(stream, 10.0);

    // sending video stream to backend
    sender = webRtc.localPeerConnection.addTrack(trackForPredictions, stream);
    // display video stream in frontend
    videoSrc.value = stream;

    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
      console.error("enumerateDevices() not supported.");
    } else {
      cameraList.value = await getAllCameras();
      selectedCamera.value = getActiveCamera(stream);
    }

    await webRtc.negotiate();
  } catch (error) {
    console.error("Error opening video camera.", error);
  }
}

function stop() {
  if (stream !== null) {
    stream.getTracks().forEach(function (track) {
      track.stop();
    });
  }

  videoContainer.value.srcObject = null;

  webRtc.stopConnection()
}

async function onCameraChange() {
  stream = await getStream()
  const trackForPredictions = getVideoTrack(stream);
  if (webRtc.localPeerConnection.iceConnectionState !== "closed") {
    await sender.replaceTrack(trackForPredictions);
  }

  // display video stream in frontend
  videoSrc.value = stream;
}
</script>

<template>
  <div>
    <h1>Detection</h1>

    <!-- Step 1 -->
    <div v-if="step === 1" class="step-1-body">
      <el-card class="privacy-consent-card">
        <div>Before using this application please read the
          <NuxtLink target="_blank" to="/privacy">data privacy policy</NuxtLink>
          . To continue, accept it by clicking on the checkbox.
        </div>
        <el-checkbox v-model="privacyAgreed" label="I read and agree to the data privacy policy." size="large"/>
        <br/>
        <el-button :disabled="privacyAgreed === false" class="privacy-agreed-start-button" type="primary"
                   @click="step = 2">Start Session
        </el-button>
      </el-card>
    </div>

    <!-- Step 2 -->
    <div v-if="step === 2" class="step-2-body">
      <video id="localVideo" ref="videoContainer" :srcObject.prop="videoSrc" autoplay playsinline preload="none"/>

      <div class="technical-infos">
        <el-select v-if="cameraList !== null && cameraList.length > 0" ref="cameraSelection" v-model="selectedCamera"
                   class="camera-selection" placeholder="Select" size="large">
          <el-option
              v-for="camera in cameraList"
              :key="camera.deviceId"
              :label="camera.label"
              :value="camera"
          />
        </el-select>

        <el-popover :width="fit - content" placement="top" trigger="hover">
          <template #reference>
            <div ref="statusIndicator" class="status-indicator"/>
          </template>
          <div>Connection Status: {{ connectionState }}</div>
          <div>Signaling State: {{ signalingState }}</div>
        </el-popover>

      </div>

      <br/>

      <el-button v-if="connectionState !== 'connected'" type="primary" @click="start()">Restart</el-button>
      <el-button v-if="connectionState === 'connected'" type="primary" @click="stop()">Stop Session</el-button>
    </div>
  </div>
</template>

<style lang='scss'>
.step-1-body {
  display: flex;
  justify-content: center;
}

.privacy-consent-card {
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
}

.privacy-agreed-start-button {
  width: 100%;
}

.step-2-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1em;
}

#localVideo {
  width: 100%;
  max-width: 640px;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  background: darkgrey url('/images/icon_video_camera_off_64.png') 50% 50% / 10% no-repeat;
  border-radius: 8px;
}

.technical-infos {
  width: 100%;
  max-width: 640px;
  display: flex;
  justify-content: space-between;
}

.status-indicator {
  height: 10px;
  width: 10px;
  background-color: red;
  border-radius: 50%;
}
</style>