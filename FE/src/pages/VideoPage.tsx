import React, { useState, useEffect, useRef } from 'react';
import { PlayIcon, PauseIcon, DownloadIcon, ChevronLeftIcon, InfoIcon } from 'lucide-react';

interface Flashcard {
  id: number;
  word: string;
  meaning: string;
  pronunciation: string;
  imageUrl: string;
  audioUrl: string;
}

const flashcards: Flashcard[] = [
  {
    id: 1,
    word: 'Apple',
    meaning: 'Quả táo',
    pronunciation: '/ˈæp.əl/',
    imageUrl: 'https://cdn-images.vtv.vn/Uploaded/nguyetmai/2013_03_29/apples_00412559.jpg',
    audioUrl: 'https://ssl.gstatic.com/dictionary/static/sounds/20200429/apple--_gb_1.mp3',
  },
  {
    id: 2,
    word: 'Book',
    meaning: 'Quyển sách',
    pronunciation: '/bʊk/',
    imageUrl: 'https://megaweb.vn/blog/uploads/images/anybook-la-gi-su-khac-nhau-giau-any-book-va-any-books.jpg',
    audioUrl: 'https://ssl.gstatic.com/dictionary/static/sounds/20200429/book--_gb_1.mp3',
  },
  {
    id: 3,
    word: 'Car',
    meaning: 'Xe hơi',
    pronunciation: '/kɑːr/',
    imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdfThvF_AiBSkjP-qj3K1lJpn-Z9WmPq8Vaw&s',
    audioUrl: 'https://ssl.gstatic.com/dictionary/static/sounds/20200429/car--_gb_1.mp3',
  },
  {
    id: 4,
    word: 'Car',
    meaning: 'Xe hơi',
    pronunciation: '/kɑːr/',
    imageUrl: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdfThvF_AiBSkjP-qj3K1lJpn-Z9WmPq8Vaw&s',
    audioUrl: 'https://ssl.gstatic.com/dictionary/static/sounds/20200429/car--_gb_1.mp3',
  },
];

const VideoPage: React.FC = () => {
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const videoDuration = flashcards.length * 5;
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        setProgress((prev) => {
          if (prev >= videoDuration) {
            setIsPlaying(false);
            return videoDuration;
          }
          return prev + 1;
        });
      }, 700);
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isPlaying]);

  useEffect(() => {
    const newIndex = Math.floor(progress / 5);
    if (newIndex !== currentIndex && newIndex < flashcards.length) {
      setCurrentIndex(newIndex);
      if (audioRef.current) {
        audioRef.current.src = flashcards[newIndex].audioUrl;
        audioRef.current.play();
      }
    }
  }, [progress]);

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newProgress = parseInt(e.target.value, 10);
    setProgress(newProgress);
  };

  // Hàm download video
  const handleDownload = () => {
    const videoUrl = '/video.mp4'; // Đường dẫn đến file video trong public folder
    const a = document.createElement('a');
    a.href = videoUrl;
    a.download = 'video_flashcard.mp4';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-3xl font-bold text-center mb-4">Video Flashcards</h1>
      <div className="relative w-full aspect-video bg-black flex items-center justify-center">
        <img
          src={flashcards[currentIndex].imageUrl}
          alt={flashcards[currentIndex].word}
          className="w-full h-full object-cover absolute opacity-70"
        />
        <div className="absolute text-center text-white p-8">
          <h2 className="text-4xl font-bold">{flashcards[currentIndex].word}</h2>
          <p className="text-xl mt-2">{flashcards[currentIndex].pronunciation}</p>
          <p className="text-2xl mt-4">{flashcards[currentIndex].meaning}</p>
        </div>
        <div className="absolute bottom-4 left-0 right-0 flex justify-center">
          <button onClick={() => setIsPlaying(!isPlaying)} className="bg-white/30 rounded-full p-3">
            {isPlaying ? <PauseIcon className="h-8 w-8 text-white" /> : <PlayIcon className="h-8 w-8 text-white" />}
          </button>
        </div>
      </div>
      <audio ref={audioRef} />
      <input
        type="range"
        min="0"
        max={videoDuration}
        value={progress}
        onChange={handleSeek}
        className="w-full mt-4"
      />
      <div className="bg-white rounded-lg shadow-md p-6 mt-4">
        <div className="flex items-start mb-4">
          <InfoIcon className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
          <p className="text-gray-600 text-sm">
            Your video flashcard will not be stored on our servers. Please download your video to save it.
          </p>
        </div>
        <button
          onClick={handleDownload}
          className="bg-blue-600 text-white px-6 py-3 rounded-md w-full flex items-center justify-center"
        >
          <DownloadIcon className="h-5 w-5 mr-2" />
          Download Video Flashcard
        </button>
      </div>
      <div className="flex justify-between">
        <button
          className="text-gray-700 flex items-center"
          onClick={() => (window.location.href = '/slideshow')}
        >
          <ChevronLeftIcon className="h-20 w-5 mr-1" />
          Back to Slideshow
        </button>
        <button className="text-blue-600" onClick={() => (window.location.href = '/create')}>
          Create New Flashcards
        </button>
      </div>
    </div>
  );
};

export default VideoPage;
