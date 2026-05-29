import React, { useState, useEffect, useRef, useCallback } from 'react';
import api from '../services/api';
import { useVoiceInput } from '../hooks/useVoiceInput';
import JeevesIcon from '../components/JeevesIcon';
import { renderAssistantData } from '../components/assistant/AssistantResults';
import '../components/JeevesIcon.css';
import '../components/assistant/AssistantResults.css';
import './Assistant.css';

const renderMarkdownLite = (text) => {
  if (!text) return '';
  return text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
};

const welcomeMessage = (helpText) => ({
  id: 'welcome',
  role: 'assistant',
  content: helpText,
  type: 'text',
  data: null,
});

const Assistant = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [starters, setStarters] = useState([]);
  const [llmEnabled, setLlmEnabled] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [error, setError] = useState('');
  const [voiceError, setVoiceError] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const clarificationContextRef = useRef(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const voiceBaseRef = useRef('');

  const handleVoiceInterim = useCallback((transcript) => {
    setVoiceError('');
    if (transcript.startsWith('Recording…')) {
      return;
    }
    const base = voiceBaseRef.current;
    setInput(base ? `${base} ${transcript}` : transcript);
  }, []);

  const handleVoiceResult = useCallback((transcript) => {
    if (transcript) {
      setVoiceError('');
      setInput((prev) => {
        const next = prev ? `${prev} ${transcript}` : transcript;
        voiceBaseRef.current = next;
        return next;
      });
      inputRef.current?.focus();
    }
  }, []);

  const handleVoiceError = useCallback((err) => {
    switch (err) {
      case 'not-allowed':
      case 'service-not-allowed':
        setVoiceError('Microphone permission denied. Allow mic access for this site in browser settings.');
        break;
      case 'no-speech':
        // Soft hint — not a hard failure
        setVoiceError("Didn't hear anything — tap the mic and speak clearly.");
        break;
      case 'network':
        setVoiceError(
          'Browser speech service unreachable (Chrome sends audio to Google, separate from normal internet). '
          + 'Add OPENAI_API_KEY to .env for reliable server-side voice, or type your question.',
        );
        break;
      case 'transcribe-failed':
        setVoiceError('Could not transcribe audio. Check OPENAI_API_KEY and try again.');
        break;
      case 'empty-transcript':
        setVoiceError("Didn't catch speech — tap mic, speak, then tap again to finish.");
        break;
      case 'audio-capture':
        setVoiceError('No microphone detected. Check your audio input device.');
        break;
      case 'start-failed':
        setVoiceError('Could not start the microphone. Try again.');
        break;
      default:
        if (err !== 'aborted' && err !== 'interrupted') {
          setVoiceError(`Voice error (${err}). You can type your question instead.`);
        }
        break;
    }
  }, []);

  const transcribeAudio = useCallback(async (blob) => {
    const form = new FormData();
    form.append('audio', blob, 'recording.webm');
    const res = await api.post('/assistant/transcribe/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data.text;
  }, []);

  const { listening, transcribing, supported, useServerMode, toggleListening, stopListening } = useVoiceInput({
    onResult: handleVoiceResult,
    onInterim: handleVoiceInterim,
    onError: handleVoiceError,
    transcribeAudio: voiceEnabled ? transcribeAudio : null,
  });

  const handleToggleVoice = useCallback(() => {
    if (!listening) {
      voiceBaseRef.current = input.trim();
      setVoiceError('');
    }
    toggleListening();
  }, [input, listening, toggleListening]);

  useEffect(() => {
    loadMeta();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const loadMeta = async (selectedSessionId = null) => {
    try {
      const url = selectedSessionId
        ? `/assistant/chat/?session_id=${selectedSessionId}`
        : '/assistant/chat/';
      const res = await api.get(url);
      setStarters(res.data.starters || []);
      setLlmEnabled(res.data.llm_enabled);
      setVoiceEnabled(res.data.voice_transcription_enabled ?? res.data.llm_enabled);
      setSessionId(res.data.session_id);
      setSessions(res.data.sessions || []);

      if (res.data.messages?.length) {
        setMessages(res.data.messages);
      } else {
        setMessages([welcomeMessage(res.data.help)]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const getPendingContext = (messageList) => {
    const fromMessages = [...messageList]
      .reverse()
      .find((m) => m.role === 'assistant' && m.pendingContext)?.pendingContext;
    return fromMessages || clarificationContextRef.current;
  };

  const buildHistoryPayload = (messageList) =>
    messageList
      .filter((m) => m.role === 'user' || m.role === 'assistant')
      .slice(-12)
      .map((m) => ({
        role: m.role,
        content: m.content,
        ...(m.pendingContext ? { pending_context: m.pendingContext } : {}),
      }));

  const sendMessage = async (text) => {
    const trimmed = (text || input).trim();
    if (!trimmed || loading) return;

    stopListening();
    setError('');
    setVoiceError('');
    setInput('');

    const userMsg = {
      id: `u-${Date.now()}`,
      role: 'user',
      content: trimmed,
    };

    const priorMessages = [...messages.filter((m) => m.id !== 'welcome'), userMsg];
    setMessages((prev) => [...prev.filter((m) => m.id !== 'welcome'), userMsg]);
    setLoading(true);

    try {
      const pendingContext = getPendingContext(messages);

      const res = await api.post('/assistant/chat/', {
        message: trimmed,
        history: buildHistoryPayload(priorMessages),
        clarification_context: pendingContext,
        session_id: sessionId,
      });

      const nextContext = res.data.clarification_context || null;
      clarificationContextRef.current = nextContext;
      if (res.data.session_id) setSessionId(res.data.session_id);

      setMessages((prev) => [
        ...prev,
        {
          id: `a-${Date.now()}`,
          role: 'assistant',
          content: res.data.message,
          type: res.data.type,
          data: res.data.data,
          options: res.data.type === 'clarification' ? res.data.data?.options : null,
          pendingContext: nextContext,
        },
      ]);

      api.get('/assistant/sessions/').then((r) => setSessions(r.data.sessions || [])).catch(() => {});
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleNewChat = async () => {
    try {
      stopListening();
      const res = await api.post('/assistant/reset/');
      clarificationContextRef.current = null;
      setMessages([]);
      setError('');
      setVoiceError('');
      if (res.data.session_id) setSessionId(res.data.session_id);
      loadMeta(res.data.session_id);
    } catch (err) {
      console.error(err);
    }
  };

  const handleLoadSession = async (id) => {
    setShowHistory(false);
    clarificationContextRef.current = null;
    await loadMeta(id);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleOptionClick = (option) => {
    sendMessage(option);
  };

  const showStarters = messages.length <= 1 && !loading;

  return (
    <div className="assistant-page">
      <div className="assistant-header">
        <div>
          <div className="assistant-title-row">
            <h2>Ask Jeeves</h2>
            <JeevesIcon size={44} title="At your service — ask about orders, customers, and menu" />
          </div>
          <p className="assistant-subtitle">
            Your business valet — plain English answers about orders, customers, and your menu
            {llmEnabled && <span className="ai-badge">AI enhanced</span>}
            {voiceEnabled && supported && <span className="ai-badge voice-badge">Voice</span>}
          </p>
        </div>
        <div className="assistant-header-actions">
          <button
            type="button"
            className="btn-secondary btn-sm"
            onClick={() => setShowHistory((v) => !v)}
            title="Chat history"
          >
            History
          </button>
          <button type="button" className="btn-secondary btn-sm" onClick={handleNewChat}>
            New chat
          </button>
        </div>
      </div>

      {showHistory && sessions.length > 0 && (
        <div className="session-history-panel">
          {sessions.map((s) => (
            <button
              key={s.id}
              type="button"
              className={`session-item ${s.id === sessionId ? 'active' : ''}`}
              onClick={() => handleLoadSession(s.id)}
            >
              <span className="session-title">{s.title}</span>
              <span className="session-meta">{s.message_count} msgs</span>
            </button>
          ))}
        </div>
      )}

      <div className="assistant-layout">
        <div className="chat-panel">
          <div className="chat-messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`chat-message ${msg.role}`}>
                <div className="message-avatar jeeves-avatar">
                  {msg.role === 'user' ? 'You' : <JeevesIcon size={28} />}
                </div>
                <div className="message-body">
                  <div
                    className="message-text"
                    dangerouslySetInnerHTML={{
                      __html: renderMarkdownLite(msg.content),
                    }}
                  />
                  {msg.options?.length > 0 && (
                    <div className="clarification-options">
                      {msg.options.map((opt) => (
                        <button
                          key={opt}
                          type="button"
                          className="option-chip"
                          onClick={() => handleOptionClick(opt)}
                        >
                          {opt}
                        </button>
                      ))}
                    </div>
                  )}
                  {msg.role === 'assistant' && renderAssistantData(msg.type, msg.data)}
                </div>
              </div>
            ))}

            {loading && (
              <div className="chat-message assistant">
                <div className="message-avatar jeeves-avatar">
                  <JeevesIcon size={28} />
                </div>
                <div className="message-body">
                  <div className="typing-indicator">
                    <span /><span /><span />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {showStarters && starters.length > 0 && (
            <div className="starter-prompts">
              {starters.map((prompt) => (
                <button
                  key={prompt}
                  type="button"
                  className="starter-chip"
                  onClick={() => sendMessage(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>
          )}

          {error && <div className="assistant-error">{error}</div>}
          {voiceError && <div className="assistant-error voice-error">{voiceError}</div>}
          {listening && !voiceError && (
            <div className="listening-hint">
              {useServerMode
                ? 'Recording… speak your question, then tap the mic again to transcribe.'
                : 'Listening… speak your question. Words appear as you talk.'}
            </div>
          )}
          {transcribing && (
            <div className="listening-hint">Transcribing your speech…</div>
          )}

          <div className="chat-composer">
            {supported && (
              <button
                type="button"
                className={`mic-btn ${listening ? 'listening' : ''} ${transcribing ? 'transcribing' : ''}`}
                onClick={handleToggleVoice}
                disabled={loading || transcribing}
                aria-label={listening ? 'Stop recording' : 'Start voice input'}
                title={
                  useServerMode
                    ? (listening ? 'Stop & transcribe' : 'Record voice (server transcription)')
                    : (listening ? 'Stop listening' : 'Speak your question')
                }
              >
                {transcribing ? '…' : listening ? '◉' : '🎤'}
              </button>
            )}
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                transcribing
                  ? 'Transcribing…'
                  : listening
                    ? (useServerMode ? 'Recording… tap mic when done' : 'Listening… speak now')
                    : 'Ask anything… or tap the mic'
              }
              rows={1}
              disabled={loading}
            />
            <button
              type="button"
              className="send-btn"
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              aria-label="Send"
            >
              ↑
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Assistant;
