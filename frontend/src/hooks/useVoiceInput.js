import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  extensionForMimeType,
  pickRecordingMimeType,
  resolveVoiceMode,
} from '../utils/voiceSupport';

/** Errors that should not show a scary banner (browser Speech API only). */
const QUIET_ERRORS = new Set(['aborted', 'interrupted']);

/**
 * Voice input with two modes:
 * - Server (Whisper): record audio → transcribe via backend (Safari, Edge, Chrome — needs OPENAI_API_KEY)
 * - Browser (Speech API): live captions (Chrome/Edge when no API key)
 */
export const useVoiceInput = ({
  onResult,
  onInterim,
  onError,
  lang = 'en-IN',
  transcribeAudio = null,
  serverTranscriptionEnabled = false,
}) => {
  const voiceMode = useMemo(
    () => resolveVoiceMode({ serverTranscriptionEnabled }),
    [serverTranscriptionEnabled],
  );
  const useServerMode = voiceMode.mode === 'server';

  const [listening, setListening] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const supported = voiceMode.supported;

  const recognitionRef = useRef(null);
  const listeningRef = useRef(false);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const chunksRef = useRef([]);
  const transcribeRef = useRef(transcribeAudio);
  const onResultRef = useRef(onResult);
  const onInterimRef = useRef(onInterim);
  const onErrorRef = useRef(onError);

  useEffect(() => {
    transcribeRef.current = transcribeAudio;
  }, [transcribeAudio]);

  useEffect(() => {
    onResultRef.current = onResult;
  }, [onResult]);

  useEffect(() => {
    onInterimRef.current = onInterim;
  }, [onInterim]);

  useEffect(() => {
    onErrorRef.current = onError;
  }, [onError]);

  // Browser Speech API setup (Chrome/Edge fallback when no server transcribe)
  useEffect(() => {
    if (useServerMode) return undefined;

    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return undefined;

    const recognition = new SpeechRecognition();
    const hasStandardApi = Boolean(window.SpeechRecognition);
    recognition.continuous = hasStandardApi;
    recognition.interimResults = true;
    recognition.lang = lang;

    recognition.onresult = (event) => {
      let interim = '';
      let finalChunk = '';
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const text = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalChunk += text;
        } else {
          interim += text;
        }
      }
      if (interim.trim() && onInterimRef.current) {
        onInterimRef.current(interim.trim());
      }
      if (finalChunk.trim() && onResultRef.current) {
        onResultRef.current(finalChunk.trim());
      }
    };

    recognition.onerror = (event) => {
      const code = event.error || 'unknown';
      setListening(false);
      listeningRef.current = false;
      if (QUIET_ERRORS.has(code)) return;
      onErrorRef.current?.(code);
    };

    recognition.onend = () => {
      setListening(false);
      listeningRef.current = false;
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.onresult = null;
      recognition.onerror = null;
      recognition.onend = null;
      try {
        recognition.abort();
      } catch {
        // ignore
      }
      recognitionRef.current = null;
    };
  }, [lang, useServerMode]);

  const stopMediaStream = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  }, []);

  const startServerRecording = useCallback(async () => {
    if (listeningRef.current || !transcribeRef.current) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      chunksRef.current = [];

      const mimeType = pickRecordingMimeType();
      const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        stopMediaStream();
        const blobType = recorder.mimeType || mimeType || 'audio/webm';
        const blob = new Blob(chunksRef.current, { type: blobType });
        chunksRef.current = [];

        if (!blob.size || !transcribeRef.current) {
          setTranscribing(false);
          return;
        }

        setTranscribing(true);
        try {
          const text = await transcribeRef.current(blob);
          if (text?.trim()) {
            onResultRef.current?.(text.trim());
          } else {
            onErrorRef.current?.('empty-transcript');
          }
        } catch {
          onErrorRef.current?.('transcribe-failed');
        } finally {
          setTranscribing(false);
        }
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setListening(true);
      listeningRef.current = true;
      onInterimRef.current?.('Recording… tap mic again when done speaking');
    } catch (err) {
      stopMediaStream();
      setListening(false);
      listeningRef.current = false;
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        onErrorRef.current?.('not-allowed');
      } else {
        onErrorRef.current?.('audio-capture');
      }
    }
  }, [stopMediaStream]);

  const stopServerRecording = useCallback(() => {
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== 'inactive') {
      recorder.stop();
    } else {
      stopMediaStream();
    }
    mediaRecorderRef.current = null;
    setListening(false);
    listeningRef.current = false;
  }, [stopMediaStream]);

  const startBrowserListening = useCallback(() => {
    const recognition = recognitionRef.current;
    if (!recognition || listeningRef.current) return;

    const tryStart = () => {
      try {
        recognition.start();
        setListening(true);
        listeningRef.current = true;
      } catch (err) {
        if (err.name === 'InvalidStateError') {
          try {
            recognition.stop();
          } catch {
            // ignore
          }
          window.setTimeout(() => {
            try {
              recognition.start();
              setListening(true);
              listeningRef.current = true;
            } catch (retryErr) {
              setListening(false);
              listeningRef.current = false;
              onErrorRef.current?.(retryErr.name || 'start-failed');
            }
          }, 150);
          return;
        }
        setListening(false);
        listeningRef.current = false;
        onErrorRef.current?.(err.name || 'start-failed');
      }
    };

    tryStart();
  }, []);

  const stopBrowserListening = useCallback(() => {
    const recognition = recognitionRef.current;
    if (!recognition) return;
    try {
      recognition.stop();
    } catch {
      try {
        recognition.abort();
      } catch {
        // ignore
      }
    }
    setListening(false);
    listeningRef.current = false;
  }, []);

  const startListening = useCallback(() => {
    if (!supported) {
      onErrorRef.current?.(voiceMode.reason || 'unsupported');
      return;
    }
    if (useServerMode && transcribeRef.current) {
      startServerRecording();
    } else {
      startBrowserListening();
    }
  }, [startBrowserListening, startServerRecording, supported, useServerMode, voiceMode.reason]);

  const stopListening = useCallback(() => {
    if (useServerMode && transcribeRef.current) {
      stopServerRecording();
    } else {
      stopBrowserListening();
    }
  }, [stopBrowserListening, stopServerRecording, useServerMode]);

  const toggleListening = useCallback(() => {
    if (listeningRef.current) {
      stopListening();
    } else {
      startListening();
    }
  }, [startListening, stopListening]);

  return {
    listening,
    transcribing,
    supported,
    useServerMode,
    voiceMode: voiceMode.mode,
    toggleListening,
    stopListening,
    startListening,
  };
};
