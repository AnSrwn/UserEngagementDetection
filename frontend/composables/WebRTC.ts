import {useApiFetch} from "~/composables/useApiFetch";

export default class WebRTC {
    runtimeConfig;
    stunServerUrl;

    localPeerConnection: RTCPeerConnection | undefined;
    peerConnectionId: string | undefined;

    connectionState = ref();
    signalingState = ref();
    isRestarting = ref(false);
    dataChannel = undefined;
    dataChannelInterval = undefined;
    // Template Refs
    videoElement = ref();
    onDisconnected: () => void;
    private internalConnectionState = ref();

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
            this.internalConnectionState.value = this.localPeerConnection?.iceConnectionState;
            console.debug(`internalConnectionState: ${this.internalConnectionState.value}`);

            // in case the connection stops unexpectedly
            if (this.internalConnectionState.value === "disconnected") {
                this.isRestarting.value = true;
                setTimeout(() => {
                    if (this.internalConnectionState.value === "disconnected" && this.isRestarting.value) {
                        console.debug("WebRTC: Connection disconnected -> Reconnecting...");
                        this.onDisconnected();
                    } else {
                        this.isRestarting.value = false;
                    }
                }, 10 * 1000);

                return;
            }

            if (!this.isRestarting.value) {
                this.connectionState.value = this.internalConnectionState.value;
            }
        }, false);

        this.localPeerConnection.addEventListener("signalingstatechange", () => {
            this.signalingState.value = this.localPeerConnection?.signalingState;
        }, false);

        // dataChannel to keep connection alive
        this.dataChannel = this.localPeerConnection.createDataChannel('chat', {
            "ordered": true, "maxPacketLifetime": 500
        });

        this.dataChannel.onclose = () => {
            if (this.dataChannelInterval) clearInterval(this.dataChannelInterval);
        };

        this.dataChannel.onopen = () => {
            this.dataChannelInterval = setInterval(() => {
                const message = 'client_keep_alive';
                try {
                    if (this.dataChannel) this.dataChannel.send(message);
                } catch (e) {
                    console.error("WebRTC: Cannot send message. DataChannel already closed.", e)
                }
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

        let responseValue = response.value.description;
        this.peerConnectionId = response.value.pc_id;

        console.debug("Received Answer:");
        console.debug(responseValue);

        // @ts-ignore
        await this.localPeerConnection.setRemoteDescription(responseValue);
        console.debug(this.localPeerConnection)
        this.isRestarting.value = false;
    }

    async stopConnection() {
        try {
            // close transceivers
            if (this.localPeerConnection === undefined) return;
            if (this.dataChannelInterval) clearInterval(this.dataChannelInterval);
            if (this.dataChannel) this.dataChannel.close();
            if (this.localPeerConnection.getTransceivers) {
                this.localPeerConnection.getTransceivers().forEach((transceiver) => {
                    if (transceiver.stop) {
                        if (this.localPeerConnection === undefined) return;
                        transceiver.stop();
                    }
                });
            }

            await useApiFetch("webrtc/close", {
                method: "POST", query: {pc_id: this.peerConnectionId}
            });

            // close peer connection
            await new Promise(resolve => setTimeout(resolve, 500)).then(() => {
                if (this.localPeerConnection === undefined) return;
                this.localPeerConnection.close();
            })
        } catch (e) {
            console.error("WebRTC: Failed to stop connection", e);
        }
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