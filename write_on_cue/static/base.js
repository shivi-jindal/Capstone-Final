"use strict"

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown"
}

let fluteRecorder, bgRecorder;
let fluteChunks = [], bgChunks = [];

// Function to start recording
async function startRecording(type) {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    
    if (type === "flute") {
        fluteRecorder = recorder;
        fluteChunks = [];
        document.getElementById("fluteUpload").disabled = true; // Disable upload
    } else {
        bgRecorder = recorder;
        bgChunks = [];
        document.getElementById("backgroundUpload").disabled = true; // Disable upload
    }

    recorder.start();

    // Disable start recording, enable stop button
    document.getElementById(`${type}StartRecord`).disabled = true;
    document.getElementById(`${type}StopRecord`).disabled = false;

    recorder.ondataavailable = (event) => {
        if (type === "flute") {
            fluteChunks.push(event.data);
        } else {
            bgChunks.push(event.data);
        }
    };

    recorder.onstop = async () => {
        const audioBlob = new Blob(type === "flute" ? fluteChunks : bgChunks, { type: "audio/wav" });
        const formData = new FormData();
        formData.append("audio_file", audioBlob, `${type}_recording.wav`);

        // Send to Django backend
        await fetch("/upload-audio/", {
            method: "POST",
            body: formData
        });

        // Play recorded audio
        const audioURL = URL.createObjectURL(audioBlob);
        document.getElementById(`${type}AudioPlayer`).src = audioURL;

        // Disable upload button until redo is clicked
        document.getElementById(`${type}Upload`).disabled = true;
        document.getElementById(`${type}StartRecord`).disabled = false;
        document.getElementById(`${type}StopRecord`).disabled = true;
        document.getElementById(`${type}Redo`).disabled = false; // Enable redo button
    };
}

// Function to handle file upload
function handleFileUpload(event, type) {
    const file = event.target.files[0];
    if (file) {
        // Disable recording buttons
        document.getElementById(`${type}StartRecord`).disabled = true;
        document.getElementById(`${type}StopRecord`).disabled = true;

        // Play uploaded file
        const fileURL = URL.createObjectURL(file);
        document.getElementById(`${type}AudioPlayer`).src = fileURL;

        // Enable redo button
        document.getElementById(`${type}Redo`).disabled = false;
    }
}

// Function to reset both options
function resetOptions(type) {
    document.getElementById(`${type}Upload`).disabled = false; // Re-enable upload
    document.getElementById(`${type}StartRecord`).disabled = false;
    document.getElementById(`${type}AudioPlayer`).src = "";
    document.getElementById(`${type}Redo`).disabled = true; // Disable redo until another action is taken
}

// Event Listeners
document.getElementById("fluteStartRecord").addEventListener("click", () => startRecording("flute"));
document.getElementById("fluteStopRecord").addEventListener("click", () => fluteRecorder.stop());
document.getElementById("fluteUpload").addEventListener("change", (event) => handleFileUpload(event, "flute"));
document.getElementById("fluteRedo").addEventListener("click", () => resetOptions("flute"));

document.getElementById("backgroundStartRecord").addEventListener("click", () => startRecording("background"));
document.getElementById("backgroundStopRecord").addEventListener("click", () => bgRecorder.stop());
document.getElementById("backgroundUpload").addEventListener("change", (event) => handleFileUpload(event, "background"));
document.getElementById("backgroundRedo").addEventListener("click", () => resetOptions("background"));