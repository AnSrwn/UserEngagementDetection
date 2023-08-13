export default class WebRTC {
    runtimeConfig;
    stunServerUrl;

    localPeerConnection: RTCPeerConnection | undefined;

    connectionState = ref();
    signalingState = ref();

    dataChannel = undefined;
    dataChannelInterval = undefined;

    // Template Refs
    videoElement = ref();

    onDisconnected: () => void;

    constructor(videoElement: globalThis.Ref<any>, connectionState: globalThis.Ref<any>, signalingState: globalThis.Ref<any>, onDisconnected: () => void) {
        this.runtimeConfig = useRuntimeConfig();
        this.stunServerUrl = this.runtimeConfig.public.stunServerUrl;

        this.localPeerConnection = undefined;

        this.connectionState = connectionState;
        this.signalingState = signalingState;

        this.videoElement = videoElement;
        this.onDisconnected = onDisconnected;
    }

    createPeerConnection() {
        const config = {
            sdpSemantics: "unified-plan",
        };

        if (this.stunServerUrl && this.stunServerUrl.length > 0) {
            // @ts-ignore
            config.iceServers = [{urls: [this.stunServerUrl]}];
        }

        // @ts-ignore
        this.localPeerConnection = new RTCPeerConnection(config);

        this.localPeerConnection.addEventListener("iceconnectionstatechange", () => {
            this.connectionState.value = this.localPeerConnection?.iceConnectionState;

            // in case the connection stops unexpectedly
            if (this.connectionState.value === "disconnected") {
                // TODO
                // The goal of this code is to switch off the local video when the connection is disconnected.
                // But sometimes the connections has some "hiccups": status is changed to disconnected, but it reconnects again...
                // this.onDisconnected();
            }
        }, false);

        this.localPeerConnection.addEventListener("signalingstatechange", () => {
            this.signalingState.value = this.localPeerConnection?.signalingState;
        }, false);

        // connect video
        // this.localPeerConnection.addEventListener("track", (evt) => {
        //     if (evt.track.kind === "video") { // @ts-ignore
        //         this.videoElement.value.srcObject = evt.streams[0];
        //     }
        // });

        // dataChannel to keep connection alive
        this.dataChannel = this.localPeerConnection.createDataChannel('chat', {
            "ordered": true,
            "maxPacketLifetime": 500
        });

        this.dataChannel.onclose = () => {
            if (this.dataChannelInterval) clearInterval(this.dataChannelInterval);
        };

        this.dataChannel.onopen = () => {
            this.dataChannelInterval = setInterval(() => {
                const message = 'client_keep_alive';
                if (this.dataChannel) this.dataChannel.send(message);
            }, 1000);
        };

        this.dataChannel.onmessage = (evt) => {
            if (evt.data === 'server_keep_alive') {
                console.debug("WebRTC: connection alive.")
            }
        };

        return this.localPeerConnection;
    }

    async negotiate() {
        if (this.localPeerConnection === undefined) return;

        const localDescription = await this.localPeerConnection.createOffer();
        await this.localPeerConnection.setLocalDescription(localDescription);
        console.debug("LocalDescription set");

        // wait for ICE gathering to complete
        await this.iceGatheringCompleted();

        const offer = this.localPeerConnection.localDescription;

        console.debug("Offer:");
        console.debug(offer);

        console.debug("Send offer");
        let {data: response, error} = await useApiFetch("webrtc/offer", {
            method: "POST", body: offer, headers: {
                "Content-Type": "application/json",
            },
        });

        if (error.value) {
            // TODO: custom Error Dialog
            alert(error.value);
        }

        let responseValue = response.value;

        console.debug("Received Answer:");
        console.debug(responseValue);

        // @ts-ignore
        await this.localPeerConnection.setRemoteDescription(responseValue);
        console.debug(this.localPeerConnection)
    }

    stopConnection() {
        // close transceivers
        if (this.localPeerConnection === undefined) return;
        if (this.dataChannel) this.dataChannel.close();
        if (this.localPeerConnection.getTransceivers) {
            this.localPeerConnection.getTransceivers().forEach((transceiver) => {
                if (transceiver.stop) {
                    if (this.localPeerConnection === undefined) return;
                    transceiver.stop();
                }
            });
        }

        // close peer connection
        setTimeout(() => {
            if (this.localPeerConnection === undefined) return;
            this.localPeerConnection.close();
            this.connectionState.value = "disconnected"
        }, 500);
    }

    private async iceGatheringCompleted() {
        return new Promise<void>((resolve) => {
            if (this.localPeerConnection === undefined || this.localPeerConnection.iceGatheringState === "complete") {
                resolve();
            } else {
                const checkState = () => {
                    if (this.localPeerConnection === undefined) resolve();

                    // @ts-ignore
                    if (this.localPeerConnection.iceGatheringState === "complete") {
                        // @ts-ignore
                        this.localPeerConnection.removeEventListener("icegatheringstatechange", checkState);
                        resolve();
                    }
                }

                this.localPeerConnection.addEventListener("icegatheringstatechange", checkState);
            }
        });
    }
}