/** Detect Safari (desktop or iOS) — browser Speech API is unreliable there. */
export const isSafari = () => {
  if (typeof navigator === 'undefined') return false;
  const ua = navigator.userAgent;
  return (
    /iPhone|iPad|iPod/.test(ua)
    || (ua.includes('Safari') && !ua.includes('Chrome') && !ua.includes('Chromium') && !ua.includes('Edg'))
  );
};

export const canUseMediaRecorder = () => {
  if (typeof window === 'undefined') return false;
  return Boolean(navigator.mediaDevices?.getUserMedia && window.MediaRecorder);
};

export const canUseSpeechRecognition = () => {
  if (typeof window === 'undefined') return false;
  return Boolean(window.SpeechRecognition || window.webkitSpeechRecognition);
};

/** Prefer server-side Whisper on Safari; Chrome/Edge can use live browser captions when no API key. */
export const prefersServerTranscription = () => isSafari();

export const pickRecordingMimeType = () => {
  if (typeof MediaRecorder === 'undefined') return '';
  const types = isSafari()
    ? ['audio/mp4', 'audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus']
    : ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg;codecs=opus'];
  return types.find((t) => MediaRecorder.isTypeSupported(t)) || '';
};

export const extensionForMimeType = (mimeType = '') => {
  const mime = mimeType.toLowerCase();
  if (mime.includes('mp4') || mime.includes('m4a')) return 'm4a';
  if (mime.includes('ogg')) return 'ogg';
  if (mime.includes('wav')) return 'wav';
  return 'webm';
};

export const resolveVoiceMode = ({ serverTranscriptionEnabled }) => {
  const hasRecorder = canUseMediaRecorder();
  const hasSpeech = canUseSpeechRecognition();
  const preferServer = prefersServerTranscription();

  if (serverTranscriptionEnabled && hasRecorder) {
    return { mode: 'server', supported: true };
  }
  if (preferServer && hasRecorder && !serverTranscriptionEnabled) {
    return { mode: 'unavailable', supported: true, reason: 'safari-needs-server' };
  }
  if (hasSpeech) {
    return { mode: 'browser', supported: true };
  }
  if (hasRecorder && serverTranscriptionEnabled) {
    return { mode: 'server', supported: true };
  }
  return { mode: 'unavailable', supported: false, reason: 'unsupported' };
};
