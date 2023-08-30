<script setup>
import {ref} from "vue";
import WebRTC from "~/composables/WebRTC";
import {useApiFetch} from "~/composables/useApiFetch";


const privacyAgreed = ref(false);
let step = ref(1);

let connectedUsers = ref(0);

let sender = null;
let globalStream = null;

let videoSrc = ref(null);
let selectedCamera = ref(null);
let cameraList = ref([]);

let connectionState = ref("disconnected");
let signalingState = ref("missing");

// Template Refs
let videoContainer = ref(null);
let cameraSelection = ref(null);
let statusIndicator = ref(null);

let webRtc = new WebRTC(videoContainer, connectionState, signalingState, () => {
  restart();
});

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
  if (webRtc.isRestarting.value) {
    statusIndicator.value.style.backgroundColor = "green";
  } else if (newValue === "checking") {
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

  if (globalStream !== null) {
    globalStream.getTracks().forEach(function (track) {
      track.stop();
    });
  }
  return newStream;
}

function getVideoTrack(stream) {
  let constraints = {
    frameRate: {
      ideal: 30.0
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
    if (globalStream === null) {
      globalStream = await getStream();
    }
    const trackForPredictions = getVideoTrack(globalStream, 10.0);

    // sending video stream to backend
    webRtc.localPeerConnection.addTransceiver('video', {kind: 'sendonly', sendEncodings: [{maxFramerate: 1}]});
    sender = webRtc.localPeerConnection.addTrack(trackForPredictions, globalStream);
    // display video stream in frontend
    if (videoSrc.value === null) {
      videoSrc.value = globalStream;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
      console.error("enumerateDevices() not supported.");
    } else {
      if (!webRtc.isRestarting.value) {
        cameraList.value = await getAllCameras();
        selectedCamera.value = getActiveCamera(globalStream);
      }
    }

    await webRtc.negotiate();
  } catch (e) {
    console.error("Error opening video camera.", e);
  }
}

async function stop() {
  console.debug("DetectionIndex: Stopping Connection ...");
  webRtc.isRestarting.value = false;
  if (globalStream !== null) {
    globalStream.getTracks().forEach(function (track) {
      track.stop();
    });
    globalStream = null;
    videoSrc.value = null;
  }

  if (videoContainer.value) {
    videoContainer.value.srcObject = null;
  }

  await webRtc.stopConnection();
  webRtc.connectionState.value = "disconnected"
  console.debug("DetectionIndex: Connection stopped");
}

async function restart() {
  webRtc.isRestarting.value = true;
  await webRtc.stopConnection();
  console.debug("DetectionIndex: Connection stopped");
  await start();
}

async function onCameraChange() {
  globalStream = await getStream();
  const trackForPredictions = getVideoTrack(globalStream);
  if (webRtc.localPeerConnection.iceConnectionState !== "closed") {
    await sender.replaceTrack(trackForPredictions);
  }

  // display video stream in frontend
  videoSrc.value = globalStream;
}
</script>

<template>
  <div>
    <h1>{{ $t('detection.title') }}</h1>

    <!-- Step 1 -->
    <div v-if="step === 1" class="step-1-body">
      <el-card class="privacy-consent-card">
        <p>{{ $t('detection.privacy-text-1') }}
          <br/><br/>
          {{ $t('detection.privacy-text-2') }}
          <NuxtLink target="_blank" to="/privacy">{{ $t('detection.privacy-text-link') }}</NuxtLink>
          {{ $t('detection.privacy-text-3') }}
        </p>
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

        <el-popover :width="230" class="tooltip" placement="top" trigger="hover">
          <template #reference>
            <div ref="statusIndicator" class="status-indicator"/>
          </template>
          <div>{{ $t('detection.connection-status') }}: {{ connectionState }}</div>
          <div>{{ $t('detection.signaling-state') }}: {{ signalingState }}</div>
          <div>{{ $t('detection.connected-users') }}: {{ connectedUsers }}</div>
        </el-popover>

      </div>

      <br/>

      <el-button v-if="connectionState === 'connected' || connectionState === 'checking' || webRtc.isRestarting.value" type="primary" @click="stop()">
        {{ $t('detection.session-stop-button') }}
      </el-button>
      <el-button v-else type="primary" @click="start()">
        {{ $t('detection.session-restart-button') }}
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
  background: darkgrey url('/images/icon_video_camera_off_mirrored_64.png') 50% 50% / 10% no-repeat;
  border-radius: 8px;
}

video {
  transform: scale(-1, 1);
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