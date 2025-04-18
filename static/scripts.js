// barcode_scanner.js

function initializeBarcodeScanner(inputFieldId) {
  const inputField = document.getElementById(inputFieldId);
  if (!inputField) {
    console.error(`Input field with ID '${inputFieldId}' not found.`);
    return;
  }

  let isScanning = false;
  let scanner;

  const startScanning = async () => {
    if (isScanning) return;
    isScanning = true;

    try {
      if (!("mediaDevices" in navigator && "getUserMedia" in navigator.mediaDevices)) {
          throw new Error("El navegador no soporta la captura de video");
        }
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        const video = document.createElement("video");
        document.body.appendChild(video);

        video.srcObject = stream;
        video.play();

        const Quagga = window.Quagga;

        Quagga.init(
            {
                inputStream: {
                    name: "Live",
                    type: "LiveStream",
                    target: video,
                    constraints: {
                      facingMode: "environment",
                    },
                  },
                  decoder: {
                    readers: ["ean_reader", "ean_8_reader"],
                  },
            },
            function (err) {
                if (err) {
                  console.error("Error al inicializar Quagga:", err);
                  return;
                }
                console.log("Quagga inicializado correctamente");
                Quagga.start();
            }
        );
        
        Quagga.onDetected(function (result) {
            if (result && result.codeResult && result.codeResult.code) {
              const barcodeValue = result.codeResult.code;
              inputField.value = barcodeValue;
                Quagga.stop();
                video.pause();
                document.body.removeChild(video);
                isScanning = false;
              }
        });

    } catch (error) {
      console.error("Error al acceder a la cámara:", error);
      isScanning = false;
    }
  };

  const stopScanning = () => {
    if (!isScanning) return;
    isScanning = false;
    const video = document.querySelector('video');
    if (video) {
      const tracks = video.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      video.pause();
      video.srcObject = null;
      document.body.removeChild(video);
    }
      
      Quagga.stop();
      console.log("Quagga stopped");
  };

  return { startScanning, stopScanning };
}

// Function to start scanner when page is loaded.
function loadScanner(inputFieldId, startButtonId, stopButtonId) {
  window.addEventListener("load", () => {
    const scanner = initializeBarcodeScanner(inputFieldId);

    const startButton = document.getElementById(startButtonId);
    const stopButton = document.getElementById(stopButtonId);

    if (startButton) {
      startButton.addEventListener("click", () => {
        scanner.startScanning();
      });
    }

    if (stopButton) {
      stopButton.addEventListener("click", () => {
        scanner.stopScanning();
      });
    }
  });
}