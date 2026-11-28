/**
 * static/mediapipe/proctoring.js
 * Browser-only MediaPipe Tasks Vision proctoring (no video upload).
 * Self-hosted WASM + .task models under /static/mediapipe/.
 */

function computeAverageLuma(videoEl, canvas) {
  const ctx = canvas.getContext('2d', { willReadFrequently: true });
  canvas.width = 96;
  canvas.height = 72;
  ctx.drawImage(videoEl, 0, 0, 96, 72);
  const data = ctx.getImageData(0, 0, 96, 72).data;
  let sum = 0;
  for (let i = 0; i < data.length; i += 4) {
    sum += 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
  }
  return sum / (96 * 72);
}

function captureSmallJpeg(videoEl) {
  const c = document.createElement('canvas');
  c.width = 320;
  c.height = 240;
  const ctx = c.getContext('2d');
  ctx.drawImage(videoEl, 0, 0, 320, 240);
  return c.toDataURL('image/jpeg', 0.6);
}

export async function initCameraCheck({
  videoEl, statusEl, wasmBase, bundleUrl, faceModelUrl, onPass, onUnavailable
}) {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    onUnavailable('Camera API is not supported in this browser.');
    return;
  }

  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
      audio: false,
    });
    videoEl.srcObject = stream;
    await videoEl.play();
  } catch (err) {
    onUnavailable('Camera permission denied or camera unavailable.');
    return;
  }

  try {
    const vision = await import(bundleUrl);
    const fileset = await vision.FilesetResolver.forVisionTasks(wasmBase);
    const faceLandmarker = await vision.FaceLandmarker.createFromOptions(fileset, {
      baseOptions: { modelAssetPath: faceModelUrl, delegate: 'GPU' },
      runningMode: 'VIDEO',
      numFaces: 3,
    });

    const probeCanvas = document.createElement('canvas');
    let passed = false;

    const timer = setInterval(() => {
      if (passed || videoEl.readyState < 2) return;
      const luma = computeAverageLuma(videoEl, probeCanvas);
      if (luma < 35) {
        statusEl.className = 'alert alert-warning small mb-2';
        statusEl.textContent = 'Lighting is too dark. Please move to a brighter area.';
        return;
      }
      const res = faceLandmarker.detectForVideo(videoEl, performance.now());
      const faces = res.faceLandmarks || [];
      if (faces.length === 0) {
        statusEl.className = 'alert alert-warning small mb-2';
        statusEl.textContent = 'No face detected. Please center your face in the camera.';
      } else if (faces.length > 1) {
        statusEl.className = 'alert alert-danger small mb-2';
        statusEl.textContent = 'Multiple faces detected. Only one person is allowed.';
      } else {
        const nose = faces[0][1];
        if (nose && (nose.x < 0.22 || nose.x > 0.78 || nose.y < 0.15 || nose.y > 0.85)) {
          statusEl.className = 'alert alert-warning small mb-2';
          statusEl.textContent = 'Please center your face inside the frame.';
        } else {
          passed = true;
          clearInterval(timer);
          onPass();
        }
      }
    }, 350);
  } catch (err) {
    // If WASM fails to load in a restricted environment, still report cleanly
    onUnavailable('Could not initialize camera face verification.');
  }
}

export async function startExamProctoring({
  videoEl, wasmBase, bundleUrl, faceModelUrl, poseModelUrl, objectModelUrl,
  snapshotsEnabled, onEvent
}) {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) return;

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { ideal: 480 }, height: { ideal: 360 } },
      audio: false,
    });
    videoEl.srcObject = stream;
    await videoEl.play();
  } catch (_) {
    return;
  }

  let faceLandmarker = null;
  let poseLandmarker = null;
  let objectDetector = null;

  try {
    const vision = await import(bundleUrl);
    const fileset = await vision.FilesetResolver.forVisionTasks(wasmBase);

    faceLandmarker = await vision.FaceLandmarker.createFromOptions(fileset, {
      baseOptions: { modelAssetPath: faceModelUrl },
      runningMode: 'VIDEO',
      numFaces: 3,
    });
    poseLandmarker = await vision.PoseLandmarker.createFromOptions(fileset, {
      baseOptions: { modelAssetPath: poseModelUrl },
      runningMode: 'VIDEO',
      numPoses: 1,
    });
    if (objectModelUrl) {
      objectDetector = await vision.ObjectDetector.createFromOptions(fileset, {
        baseOptions: { modelAssetPath: objectModelUrl },
        runningMode: 'VIDEO',
        scoreThreshold: 0.6,
        maxResults: 5,
      });
    }
  } catch (_) {
    return;
  }

  const activeSince = {};
  const lastReported = {};
  const COOLDOWN_MS = 10000;

  function checkRule(type, violated, minMs) {
    const now = Date.now();
    if (violated) {
      if (!activeSince[type]) activeSince[type] = now;
      const elapsed = now - activeSince[type];
      if (elapsed >= minMs && (!lastReported[type] || now - lastReported[type] > COOLDOWN_MS)) {
        lastReported[type] = now;
        const snap = snapshotsEnabled ? captureSmallJpeg(videoEl) : '';
        onEvent(type, Math.round(elapsed / 100) / 10, snap);
      }
    } else {
      activeSince[type] = null;
    }
  }

  // Detection loop ~4 fps, paused when tab is hidden
  setInterval(() => {
    if (document.hidden || videoEl.readyState < 2) return;
    const ts = performance.now();

    if (faceLandmarker) {
      const fRes = faceLandmarker.detectForVideo(videoEl, ts);
      const faces = fRes.faceLandmarks || [];
      checkRule('no_face', faces.length === 0, 3000);
      checkRule('multiple_faces', faces.length > 1, 1000);

      if (faces.length === 1) {
        const lm = faces[0];
        const nose = lm[1];
        const leftCheek = lm[234];
        const rightCheek = lm[454];
        let headTurned = false;
        if (nose && leftCheek && rightCheek) {
          const span = Math.abs(rightCheek.x - leftCheek.x) || 0.001;
          const ratio = (nose.x - leftCheek.x) / span;
          if (ratio < 0.22 || ratio > 0.78) headTurned = true;
        }
        checkRule('head_turn', headTurned, 3000);
      } else {
        activeSince['head_turn'] = null;
      }
    }

    if (poseLandmarker) {
      const pRes = poseLandmarker.detectForVideo(videoEl, ts);
      const poses = pRes.landmarks || [];
      let bodyOut = poses.length === 0;
      if (poses.length > 0) {
        const leftSh = poses[0][11];
        const rightSh = poses[0][12];
        if (leftSh && rightSh) {
          const midX = (leftSh.x + rightSh.x) / 2;
          if (midX < 0.15 || midX > 0.85) bodyOut = true;
        }
      }
      checkRule('body_out', bodyOut, 3000);
    }

    if (objectDetector) {
      const oRes = objectDetector.detectForVideo(videoEl, ts);
      const dets = oRes.detections || [];
      const phoneFound = dets.some(d =>
        (d.categories || []).some(c =>
          c.categoryName && c.categoryName.toLowerCase().includes('cell phone') && c.score > 0.6
        )
      );
      checkRule('phone_detected', phoneFound, 2000);
    }
  }, 250);
}
