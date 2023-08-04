<script setup>
import {ref} from "vue";

// TODO: Selection of camera
// TODO: Handling change of camera
// TODO: Start and Stop buttons
// TODO: Stop on page change

const privacyAgreed = ref(false);
let step = ref(1);

// WebRTC
const dataChannel = ref(null);

// peer connection
let localPeerConnection = null;

// data channel
const dc = null;

let sender = null;
let stream = null;
const config = useRuntimeConfig();
const stunServerUrl = config.public.stunServerUrl;

let selectedCamera = ref(null);
let cameraList = ref([]);

// Template Refs
let videoContainer = ref(null);
let cameraSelection = ref(null);

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

onDeactivated(() => {
  stop();
})

onBeforeUnmount(() => {
  stop();
})

function createPeerConnection() {
  const config = {
    sdpSemantics: "unified-plan",
  };

  if (stunServerUrl && stunServerUrl.length > 0) {
    config.iceServers = [{urls: [stunServerUrl]}];
  }

  localPeerConnection = new RTCPeerConnection(config);

  // register some listeners to help debugging
  const iceGatheringState = document.getElementById("iceGatheringState");
  localPeerConnection.addEventListener(
      "icegatheringstatechange",
      function () {
        iceGatheringState.textContent +=
            " -> " + localPeerConnection.iceGatheringState;
      },
      false
  );
  iceGatheringState.textContent = localPeerConnection.iceGatheringState;

  const iceConnectionState = document.getElementById("iceConnectionState");
  localPeerConnection.addEventListener(
      "iceconnectionstatechange",
      function () {
        iceConnectionState.textContent +=
            " -> " + localPeerConnection.iceConnectionState;
      },
      false
  );
  iceConnectionState.textContent = localPeerConnection.iceConnectionState;

  const signalingState = document.getElementById("signalingState");
  localPeerConnection.addEventListener(
      "signalingstatechange",
      function () {
        signalingState.textContent += " -> " + localPeerConnection.signalingState;
      },
      false
  );
  signalingState.textContent = localPeerConnection.signalingState;

  // connect video
  const videoElement = document.querySelector("video#localVideo");
  localPeerConnection.addEventListener("track", function (evt) {
    if (evt.track.kind === "video") videoElement.srcObject = evt.streams[0];
  });

  return localPeerConnection;
}

async function negotiate() {
  const localDescription = await localPeerConnection.createOffer();
  await localPeerConnection.setLocalDescription(localDescription);
  console.debug("LocalDescription set");

  // wait for ICE gathering to complete
  await iceGatheringCompleted();

  const offer = localPeerConnection.localDescription;

  console.debug("Offer:");
  console.debug(offer);
  const offerSdp = document.getElementById("offerSdp");
  offerSdp.textContent = offer.sdp;

  console.debug("Send offer");
  let {data: response, error} = await useApiFetch("offer", {
    method: "POST",
    body: offer,
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (error.value) {
    alert(error.value);
  }

  response = response.value;

  console.debug("Received Answer:");
  console.debug(response);
  const answerSdp = document.getElementById("answerSdp");
  answerSdp.textContent = response.sdp;
  await localPeerConnection.setRemoteDescription(response);
}

async function iceGatheringCompleted() {
  return new Promise(function (resolve) {
    if (localPeerConnection.iceGatheringState === "complete") {
      resolve();
    } else {
      function checkState() {
        if (localPeerConnection.iceGatheringState === "complete") {
          localPeerConnection.removeEventListener(
              "icegatheringstatechange",
              checkState
          );
          resolve();
        }
      }

      localPeerConnection.addEventListener("icegatheringstatechange", checkState);
    }
  });
}

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

  localPeerConnection = createPeerConnection();

  try {
    stream = await getStream();
    const track = getVideoTrack(stream);

    // TODO Maybe rescale track before sending it with WebRTC
    sender = localPeerConnection.addTrack(track, stream)


    if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
      console.error("enumerateDevices() not supported.");
    } else {
      cameraList.value = await getAllCameras();
      selectedCamera.value = getActiveCamera(stream);
    }

    await negotiate();
    console.debug(localPeerConnection);
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

  // close data channel
  if (dc) {
    dc.close();
  }

  // close transceivers
  if (localPeerConnection.getTransceivers) {
    localPeerConnection.getTransceivers().forEach(function (transceiver) {
      if (transceiver.stop) {
        transceiver.stop();
      }
    });
  }

  // close peer connection
  setTimeout(function () {
    localPeerConnection.close();
  }, 500);
}

async function onCameraChange() {
  stream = await getStream()
  const track = getVideoTrack(stream);
  await sender.replaceTrack(track);
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
  background: gray;
}

.video-placeholder {
  height: 480px;
  width: 640px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: gray;
}
</style>