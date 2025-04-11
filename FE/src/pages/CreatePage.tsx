import React, { useState, ChangeEvent, DragEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadIcon,
  BrainIcon,
  DownloadIcon,
  AlertCircleIcon,
} from 'lucide-react';

const CreatePage: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'upload' | 'ai'>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [aiPrompt, setAiPrompt] = useState<string>('');
  const [wordLanguage, setWordLanguage] = useState<string>('English');
  const [meaningLanguage, setMeaningLanguage] = useState<string>('Vietnamese');
  const [difficultyLevel, setDifficultyLevel] = useState<string>('Beginner');
  const [wordCount, setWordCount] = useState<string>('10 words');
  const [showSuccessPopup, setShowSuccessPopup] = useState<boolean>(false); // Thêm state cho popup
  const supportedVoiceLanguages: string[] = ['Vietnamese', 'Chinese', 'English', 'German'];

  const handleFileUpload = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setShowSuccessPopup(true);
      setTimeout(() => {
        setShowSuccessPopup(false);
        navigate('/preview', {
          state: {
            source: 'upload',
            file: file,
          },
        });
      }, 2000);
    }
  };

  const handleDragDrop = (e: DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file);
      setShowSuccessPopup(true);
      setTimeout(() => {
        setShowSuccessPopup(false);
        navigate('/preview', {
          state: {
            source: 'upload',
            file,
          },
        });
      }, 2000);
    }
  };

  const handleDownloadTemplate = () => {
    const csvContent = [
      ['Word', 'Meaning'],
      ['Apple', 'A fruit'],
      ['Table', 'A piece of furniture'],
      ['Dog', 'A domestic animal'],
      ['Computer', 'An electronic device'],
      ['Book', 'A set of written pages'],
      ['Sun', 'The star in our solar system'],
      ['Water', 'A liquid essential for life'],
      ['Car', 'A four-wheeled vehicle'],
      ['Phone', 'A communication device'],
      ['Mountain', 'A large natural elevation'],
    ];
    const blob = new Blob([csvContent.map(row => row.join(',')).join('\n')], {
      type: 'text/csv',
    });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'flashcard_template.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const handleGenerateAI = () => {
    navigate('/preview', {
      state: {
        source: 'ai',
        settings: {
          prompt: aiPrompt,
          wordLanguage,
          meaningLanguage,
          difficultyLevel,
          wordCount,
        },
      },
    });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Create Flashcards</h1>
      <div className="max-w-2xl mx-auto">
        <div className="mb-6 grid grid-cols-2 gap-4">
          <button
            className={`p-4 flex items-center justify-center ${activeTab === 'upload' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'}`}
            onClick={() => setActiveTab('upload')}
          >
            <UploadIcon className="h-5 w-5 mr-2" />
            Upload File
          </button>
          <button
            className={`p-4 flex items-center justify-center ${activeTab === 'ai' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'}`}
            onClick={() => setActiveTab('ai')}
          >
            <BrainIcon className="h-5 w-5 mr-2" />
            AI Generator
          </button>
        </div>
        {activeTab === 'upload' ? (
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Upload Vocabulary File</h2>
              <button
                className="text-blue-600 flex items-center"
                onClick={handleDownloadTemplate}
              >
                <DownloadIcon className="h-5 w-5 mr-1" />
                Download Template
              </button>
            </div>
            <p className="text-gray-600 mb-6">
              Upload a CSV or Excel file with your vocabulary words. Make sure
              it follows our template format.
            </p>
            <label
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 block text-center cursor-pointer hover:border-blue-500"
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDragDrop}
            >
              <div className="flex flex-col items-center">
                <UploadIcon className="h-12 w-12 text-gray-400 mb-4" />
                <p className="text-gray-500 mb-4">
                  Drag and drop your file here, or click to select
                </p>
                <input
                  type="file"
                  className="hidden"
                  accept=".csv,.xlsx,.xls"
                  onChange={handleFileUpload}
                />
              </div>
            </label>
          </div>
        ) : (
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold mb-6">
              AI Vocabulary Generator
            </h2>
            <div className="mb-6">
              <label className="block mb-2 text-gray-700">
                What would you like to learn?
              </label>
              <input
                type="text"
                className="w-full p-3 border border-gray-300 rounded-md"
                placeholder="e.g. I want to learn about animals and nature"
                value={aiPrompt}
                onChange={(e: ChangeEvent<HTMLInputElement>) =>
                  setAiPrompt(e.target.value)
                }
              />
            </div>
            <div className="grid grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block mb-2 text-gray-700">
                  Word Language
                </label>
                <select
                  className="w-full p-3 border border-gray-300 rounded-md"
                  value={wordLanguage}
                  onChange={(e: ChangeEvent<HTMLSelectElement>) =>
                    setWordLanguage(e.target.value)
                  }
                >
                  {[
                    'English',
                    'Vietnamese',
                    'Chinese',
                    'German',
                    'French',
                    'Spanish',
                    'Japanese',
                  ].map((lang) => (
                    <option key={lang} value={lang}>
                      {lang}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block mb-2 text-gray-700">
                  Meaning Language
                </label>
                <select
                  className="w-full p-3 border border-gray-300 rounded-md"
                  value={meaningLanguage}
                  onChange={(e: ChangeEvent<HTMLSelectElement>) =>
                    setMeaningLanguage(e.target.value)
                  }
                >
                  {[
                    'Vietnamese',
                    'English',
                    'Chinese',
                    'German',
                    'French',
                    'Spanish',
                    'Japanese',
                  ].map((lang) => (
                    <option key={lang} value={lang}>
                      {lang}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block mb-2 text-gray-700">
                  Difficulty Level
                </label>
                <select
                  className="w-full p-3 border border-gray-300 rounded-md"
                  value={difficultyLevel}
                  onChange={(e: ChangeEvent<HTMLSelectElement>) =>
                    setDifficultyLevel(e.target.value)
                  }
                >
                  {['Beginner', 'Intermediate', 'Advanced'].map((level) => (
                    <option key={level} value={level}>
                      {level}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block mb-2 text-gray-700">
                  Number of Words
                </label>
                <select
                  className="w-full p-3 border border-gray-300 rounded-md"
                  value={wordCount}
                  onChange={(e: ChangeEvent<HTMLSelectElement>) =>
                    setWordCount(e.target.value)
                  }
                >
                  {[
                    '10 words',
                    '15 words',
                    '20 words',
                    '25 words',
                    '30 words',
                  ].map((count) => (
                    <option key={count} value={count}>
                      {count}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            {(!supportedVoiceLanguages.includes(wordLanguage) ||
              !supportedVoiceLanguages.includes(meaningLanguage)) && (
              <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-md flex items-start mb-6">
                <AlertCircleIcon className="h-5 w-5 text-yellow-600 mr-2 mt-0.5" />
                <p className="text-yellow-800">
                  Note: Audio is only available for Vietnamese, Chinese,
                  English, and German languages.
                </p>
              </div>
            )}
            <div className="flex justify-end">
              <button
                className="bg-blue-600 text-white px-6 py-2 rounded-md disabled:bg-gray-300"
                onClick={handleGenerateAI}
                disabled={!aiPrompt}
              >
                Generate Flashcards
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Popup thông báo upload thành công */}
      {showSuccessPopup && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white rounded-lg p-6 shadow-lg max-w-sm w-full text-center">
            <h3 className="text-lg font-semibold text-green-600 mb-4">Upload Successful!</h3>
            <p className="text-gray-600 mb-4">Your file has been selected successfully.</p>
            <button
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              onClick={() => setShowSuccessPopup(false)}
            >
              OK
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CreatePage;