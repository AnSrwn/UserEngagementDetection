export default class WebRTC {
    config;
    stunServerUrl;

    dataChannel = ref(null);
    localPeerConnection: RTCPeerConnection | undefined;
    dc = null;

    // Template Refs
    videoElement = ref();

    constructor(videoElement: globalThis.Ref<any>) {
        this.config = useRuntimeConfig();
        this.stunServerUrl = this.config.public.stunServerUrl;

        this.localPeerConnection = undefined;

        this.videoElement = videoElement;
    }

    createPeerConnection() {
        const config = {
            sdpSemantics: "unified-plan",
        };

        if (this.stunServerUrl && this.stunServerUrl.length > 0) {
            this.config.iceServers = [{urls: [this.stunServerUrl]}];
        }

        // @ts-ignore
        this.localPeerConnection = new RTCPeerConnection(config);

        // register some listeners to help debugging
        // const iceGatheringState = document.getElementById("iceGatheringState");
        // localPeerConnection.addEventListener(
        //     "icegatheringstatechange",
        //     function () {
        //         iceGatheringState.textContent +=
        //             " -> " + localPeerConnection.iceGatheringState;
        //     },
        //     false
        // );
        // iceGatheringState.textContent = localPeerConnection.iceGatheringState;

        // const iceConnectionState = document.getElementById("iceConnectionState");
        // localPeerConnection.addEventListener(
        //     "iceconnectionstatechange",
        //     function () {
        //         iceConnectionState.textContent +=
        //             " -> " + localPeerConnection.iceConnectionState;
        //     },
        //     false
        // );
        // iceConnectionState.textContent = localPeerConnection.iceConnectionState;

        // const signalingState = document.getElementById("signalingState");
        // localPeerConnection.addEventListener(
        //     "signalingstatechange",
        //     function () {
        //         signalingState.textContent += " -> " + localPeerConnection.signalingState;
        //     },
        //     false
        // );
        // signalingState.textContent = localPeerConnection.signalingState;

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
        // const offerSdp = document.getElementById("offerSdp");
        // offerSdp.textContent = offer.sdp;

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
        // const answerSdp = document.getElementById("answerSdp");
        // answerSdp.textContent = responseValue.sdp;
        // @ts-ignore
        await this.localPeerConnection.setRemoteDescription(responseValue);
        console.debug(this.localPeerConnection)
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
        }, 500);
    }
}