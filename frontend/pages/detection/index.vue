<script setup>
import {ref} from "vue";
import WebRTC from "~/composables/WebRTC";


const privacyAgreed = ref(false);
let step = ref(1);

let sender = null;
let stream = null;

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
      ideal: 20.0
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
  document.getElementById("start").style.display = "none";

  webRtc.createPeerConnection();

  try {
    stream = await getStream();
    const track = getVideoTrack(stream);

    // TODO Maybe rescale track before sending it with WebRTC
    sender = webRtc.localPeerConnection.addTrack(track, stream)

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

  document.getElementById("stop").style.display = "inline-block";
}

function stop() {
  document.getElementById("stop").style.display = "none";
  document.getElementById("start").style.display = "inline-block";

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
  const track = getVideoTrack(stream);
  if (webRtc.localPeerConnection.iceConnectionState !== "closed") {
    await sender.replaceTrack(track);
  }
}
</script>

<template>
  <div>
    <h1>Detection</h1>

    <!-- Step 1 -->
    <div v-if="step === 1">
      <div>Before using this application please read the
        <NuxtLink target="_blank" to="/privacy">data privacy policy</NuxtLink>
        . To continue, accept it by clicking on the checkbox.
      </div>
      <el-checkbox v-model="privacyAgreed" label="I read and agree to the data privacy policy." size="large"/>
      <br/>
      <el-button :disabled="privacyAgreed === false" type="primary" @click="step = 2">Start Video Recording</el-button>
    </div>

    <!-- Step 2 -->
    <div class="step-2-body">
      <video id="localVideo" ref="videoContainer" autoplay playsinline/>
    </div>

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

    <br/>

    <button id="start" @click="start()">Start</button>
    <button id="stop" style="display: none" @click="stop()">Stop</button>

    <h2>State</h2>
    <p>ICE gathering state: <span id="iceGatheringState"></span></p>
    <p>ICE connection state: <span id="iceConnectionState"></span></p>
    <p>Signaling state: <span id="signalingState"></span></p>
    <h2>Data channel</h2>
    <pre ref="dataChannel" style="height: 200px"></pre>
    <h2>SDP</h2>

    <h3>Offer</h3>
    <pre id="offerSdp"></pre>

    <h3>Answer</h3>
    <pre id="answerSdp"></pre>
  </div>
</template>

<style lang='scss'>
.step-2-body {
  display: flex;
  justify-content: center;
}

#localVideo {
  width: 640px;
  height: 480px;
  object-fit: cover;
  background: gray;
}

.video-placeholder {
  width: 640px;
  height: 480px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: gray;
}

.status-indicator {
  height: 10px;
  width: 10px;
  background-color: red;
  border-radius: 50%;
}
</style>