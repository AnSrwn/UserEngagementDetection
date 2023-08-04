export default class WebRTC {
    runtimeConfig;
    stunServerUrl;

    dataChannel = ref(null);
    localPeerConnection: RTCPeerConnection | undefined;

    connectionState = ref();
    signalingState = ref();

    // Template Refs
    videoElement = ref();

    constructor(videoElement: globalThis.Ref<any>, connectionState: globalThis.Ref<any>, signalingState: globalThis.Ref<any>) {
        this.runtimeConfig = useRuntimeConfig();
        this.stunServerUrl = this.runtimeConfig.public.stunServerUrl;

        this.localPeerConnection = undefined;

        this.connectionState = connectionState;
        this.signalingState = signalingState;

        this.videoElement = videoElement;
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
        }, false);

        this.localPeerConnection.addEventListener("signalingstatechange", () => {
            this.signalingState.value = this.localPeerConnection?.signalingState;
        }, false);

        // connect video
        this.localPeerConnection.addEventListener("track", (evt) => {
            if (evt.track.kind === "video") { // @ts-ignore
                this.videoElement.value.srcObject = evt.streams[0];
            }
        });

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
        let {data: response, error} = await useApiFetch("offer", {
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