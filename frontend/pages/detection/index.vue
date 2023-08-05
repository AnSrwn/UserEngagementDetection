<script setup>
import {ref} from "vue";
import WebRTC from "~/composables/WebRTC";
import {useApiFetch} from "~/composables/useApiFetch";


const privacyAgreed = ref(false);
let step = ref(1);

let connectedUsers = ref(0);

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

const {data, refresh} = await useApiFetch(`engagement/connections-count`, {
  transform: (data) => {
    connectedUsers.value = data;
    return data;
  },
});

function refreshing() {
  refresh();
}

let requestInterval;

onMounted(() => {
  refreshing();
  requestInterval = setInterval(refreshing, 30000);
})

onDeactivated(() => {
  clearInterval(requestInterval);
  stop();
})

onBeforeUnmount(() => {
  clearInterval(requestInterval);
  stop();
})

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
    refreshing();
  } else {
    statusIndicator.value.style.backgroundColor = "red";
    refreshing();
  }
});

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

  if (videoContainer.value) {
    videoContainer.value.srcObject = null;
  }

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
    <h1>{{ $t('detection.title') }}</h1>

    <!-- Step 1 -->
    <div v-if="step === 1" class="step-1-body">
      <el-card class="privacy-consent-card">
        <div>{{ $t('detection.privacy-text-1') }}
          <NuxtLink target="_blank" to="/privacy">{{ $t('detection.privacy-text-link') }}</NuxtLink>
          .<br/>
          {{ $t('detection.privacy-text-2') }}
        </div>
        <el-checkbox v-model="privacyAgreed" :label="$t('detection.privacy-checkbox-label')" size="large"/>
        <br/>
        <el-button :disabled="privacyAgreed === false" class="privacy-agreed-start-button" type="primary"
                   @click="step = 2">{{ $t('detection.privacy-button') }}
        </el-button>
      </el-card>
    </div>

    <!-- Step 2 -->
    <div v-if="step === 2" class="step-2-body">
      <video id="localVideo" ref="videoContainer" :srcObject.prop="videoSrc" autoplay playsinline preload="none"/>

      <div class="technical-infos">
        <el-select v-if="cameraList !== null && cameraList.length > 0" ref="cameraSelection" v-model="selectedCamera"
                   :placeholder="$t('general.select-placeholder')" class="camera-selection" size="large">
          <el-option
              v-for="camera in cameraList"
              :key="camera.deviceId"
              :label="camera.label"
              :value="camera"
          />
        </el-select>

        <el-popover class="tooltip" placement="top" trigger="hover">
          <template #reference>
            <div ref="statusIndicator" class="status-indicator"/>
          </template>
          <div>{{ $t('detection.connection-status') }}: {{ connectionState }}</div>
          <div>{{ $t('detection.signaling-state') }}: {{ signalingState }}</div>
          <div>{{ $t('detection.connected-users') }}: {{ connectedUsers }}</div>
        </el-popover>

      </div>

      <br/>

      <el-button v-if="connectionState !== 'connected'" type="primary" @click="start()">
        {{ $t('detection.session-restart-button') }}
      </el-button>
      <el-button v-if="connectionState === 'connected'" type="primary" @click="stop()">
        {{ $t('detection.session-stop-button') }}
      </el-button>
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
  max-width: 460px;
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

.tooltip {
  width: fit-content;
}
</style>