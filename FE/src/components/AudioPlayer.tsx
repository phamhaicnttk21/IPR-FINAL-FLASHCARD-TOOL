import React, { useEffect, useRef, Component } from 'react';
interface AudioPlayerProps {
  text: string;
  language: string;
  autoPlay?: boolean;
  onPlayComplete?: () => void;
}
const AudioPlayer = ({
  text,
  language,
  autoPlay = false,
  onPlayComplete
}: AudioPlayerProps) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const supportedLanguages = ['Vietnamese', 'Chinese', 'English', 'German'];
  useEffect(() => {
    if (autoPlay && supportedLanguages.includes(language)) {
      playAudio();
    }
  }, [text, language, autoPlay]);
  const playAudio = () => {
    if (audioRef.current) {
      audioRef.current.play();
    }
  };
  if (!supportedLanguages.includes(language)) {
    return null;
  }
  // In a real app, we would use a proper TTS service
  const audioUrl = `https://api.example.com/tts?text=${encodeURIComponent(text)}&lang=${language}`;
  return <audio ref={audioRef} src={audioUrl} onEnded={onPlayComplete} className="hidden" />;
};
export default AudioPlayer;