import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeftIcon, ChevronRightIcon, VolumeIcon } from 'lucide-react';
import AudioPlayer from '../components/AudioPlayer';
const SlideshowPage = () => {
  const navigate = useNavigate();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showFront, setShowFront] = useState(true);
  const vocabulary = [{
    id: 1,
    word: 'Hello',
    meaning: 'Xin chào',
    pronunciation: '/həˈləʊ/',
    language: 'English'
  }, {
    id: 2,
    word: 'Thank you',
    meaning: 'Cảm ơn',
    pronunciation: '/θæŋk juː/',
    language: 'English'
  }];
  const handleFlip = () => setShowFront(!showFront);
  const handleNext = () => {
    if (currentIndex < vocabulary.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setShowFront(true);
    }
  };
  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setShowFront(true);
    }
  };
  return <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-2">Interactive Flashcards</h1>
      <p className="text-gray-600 mb-8">Click the card to flip it</p>
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-8 mb-8 relative min-h-[300px] flex items-center justify-center">
          <button className="absolute top-4 right-4 text-gray-500 hover:text-gray-700" onClick={() => {}}>
            <VolumeIcon className="h-6 w-6" />
          </button>
          <AudioPlayer text={vocabulary[currentIndex].word} language={vocabulary[currentIndex].language} autoPlay={false} />
          <div className="text-center w-full cursor-pointer" onClick={handleFlip}>
            {showFront ? <>
                <h2 className="text-4xl font-bold mb-2">
                  {vocabulary[currentIndex].word}
                </h2>
                <p className="text-xl text-gray-600">
                  {vocabulary[currentIndex].pronunciation}
                </p>
              </> : <p className="text-2xl">{vocabulary[currentIndex].meaning}</p>}
          </div>
        </div>
        <div className="flex justify-between items-center mb-8">
          <button className="flex items-center text-gray-700" onClick={handlePrevious} disabled={currentIndex === 0}>
            <ChevronLeftIcon className="h-5 w-5 mr-1" />
            Previous
          </button>
          <div className="text-gray-600">
            Card {currentIndex + 1} of {vocabulary.length}
          </div>
          <button className="flex items-center text-gray-700" onClick={handleNext} disabled={currentIndex === vocabulary.length - 1}>
            Next
            <ChevronRightIcon className="h-5 w-5 ml-1" />
          </button>
        </div>
        <div className="flex justify-between">
          <button className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md" onClick={() => navigate('/preview')}>
            Back to Preview
          </button>
          <button className="px-6 py-2 bg-blue-600 text-white rounded-md" onClick={() => navigate('/video')}>
            Create Video
          </button>
        </div>
      </div>
    </div>;
};
export default SlideshowPage;