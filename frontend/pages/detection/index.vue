<script setup>
import { ref, onMounted } from 'vue'

// TODO: Selection of camera
// TODO: Handling change of camera
// TODO: Start and Stop buttons
// TODO: Stop on page change

// WebRTC
const dataChannel = ref(null)

// peer connection
var peerConnection = null;

// data channel
var dc = null, dcInterval = null;

function createPeerConnection() {
    var config = {
        sdpSemantics: 'unified-plan'
    };

    // config.iceServers = [{ urls: ['stun:stun.l.google.com:19302'] }];
    // config.iceServers = [{
    //     urls: ['turn:localhost:3478'],
    //     username: 'test',
    //     credential: 'test123'
    // }];
    config.iceServers = [{
        urls: ['turn:a.relay.metered.ca:80'],
        username: '6e1209436b4e7050772c1c01',
        credential: 'XXyU9+35T0piBKe1'
    }];

    peerConnection = new RTCPeerConnection(config);

    // register some listeners to help debugging
    const iceGatheringState = document.getElementById('iceGatheringState');
    peerConnection.addEventListener('icegatheringstatechange', function () {
        iceGatheringState.textContent += ' -> ' + peerConnection.iceGatheringState;
    }, false);
    iceGatheringState.textContent = peerConnection.iceGatheringState;

    const iceConnectionState = document.getElementById('iceConnectionState');
    peerConnection.addEventListener('iceconnectionstatechange', function () {
        iceConnectionState.textContent += ' -> ' + peerConnection.iceConnectionState;
    }, false);
    iceConnectionState.textContent = peerConnection.iceConnectionState;

    const signalingState = document.getElementById('signalingState');
    peerConnection.addEventListener('signalingstatechange', function () {
        signalingState.textContent += ' -> ' + peerConnection.signalingState;
    }, false);
    signalingState.textContent = peerConnection.signalingState;

    // connect video
    const videoElement = document.querySelector('video#localVideo');
    peerConnection.addEventListener('track', function(evt) {
        if (evt.track.kind == 'video')
            videoElement.srcObject = evt.streams[0];
    });

    return peerConnection;
}

async function negotiate() {
    const offer = await peerConnection.createOffer()
    await peerConnection.setLocalDescription(offer)

    const offerSdp = document.getElementById('offerSdp');
    offerSdp.textContent = offer.sdp;

    // wait for ICE gathering to complete
    // await new Promise(function (resolve) {
    //     if (pc.iceGatheringState === 'complete') {
    //         resolve();
    //     } else {
    //         function checkState() {
    //             if (pc.iceGatheringState === 'complete') {
    //                 pc.removeEventListener('icegatheringstatechange', checkState);
    //                 resolve();
    //             }
    //         }
    //         pc.addEventListener('icegatheringstatechange', checkState);
    //     }
    // })

    let response = await $fetch('offer', {
        method: 'POST',
        baseURL: 'http://localhost:8000',
        body: offer,
        headers: {
            'Content-Type': 'application/json'
        },
    }).catch((error) => {
        alert(error);
    })

    const answerSdp = document.getElementById('answerSdp');
    answerSdp.textContent = response.sdp;
    peerConnection.setRemoteDescription(response);
}

async function start() {
    document.getElementById('start').style.display = 'none';

    peerConnection = createPeerConnection();

    try {
        const constraints = { 'video': true, 'audio': false };
        // video: {
        // width: {min: 640, ideal: 1280, max: 1920},
        // height: {min: 480, ideal: 720, max: 1080}
        // }
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        stream.getTracks().forEach(function (track) {
            peerConnection.addTrack(track, stream);
        })

        // const videoElement = document.querySelector('video#localVideo');
        // videoElement.srcObject = stream;

        await negotiate();
        console.log(peerConnection)
    } catch (error) {
        console.error('Error opening video camera.', error);
    }

    document.getElementById('stop').style.display = 'inline-block';
}

function stop() {
    document.getElementById('stop').style.display = 'none';
    document.getElementById('start').style.display = 'inline-block';

    // close data channel
    if (dc) {
        dc.close();
    }

    // close transceivers
    if (peerConnection.getTransceivers) {
        peerConnection.getTransceivers().forEach(function (transceiver) {
            if (transceiver.stop) {
                transceiver.stop();
            }
        });
    }

    // close local audio / video
    peerConnection.getSenders().forEach(function (sender) {
        sender.track.stop();
    });

    // close peer connection
    setTimeout(function () {
        peerConnection.close();
    }, 500);
}

</script>

<template>
    <div>
        <h1>Detection</h1>
        <div>
            <video id="localVideo" autoplay playsinline controls="false" />
        </div>

        <button id="start" @click="start()">Start</button>
        <button id="stop" style="display: none" @click="stop()">Stop</button>


        <h2>State</h2>
        <p>
            ICE gathering state: <span id="iceGatheringState"></span>
        </p>
        <p>
            ICE connection state: <span id="iceConnectionState"></span>
        </p>
        <p>
            Signaling state: <span id="signalingState"></span>
        </p>
        <h2>Data channel</h2>
        <pre ref="dataChannel" style="height: 200px;"></pre>
        <h2>SDP</h2>

        <h3>Offer</h3>
        <pre id="offerSdp"></pre>

        <h3>Answer</h3>
        <pre id="answerSdp"></pre>
    </div>
</template>

<style lang='scss'></style>