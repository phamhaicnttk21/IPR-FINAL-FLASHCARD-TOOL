import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import VocabularyTable from '../components/VocabularyTable';
import axios from 'axios';
import { toast } from 'react-toastify';

interface Vocabulary {
  id: number;
  word: string;
  meaning: string;
  pronunciation: string;
  language: string;
}

const PreviewPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { state } = location as {
    state: {
      source: string;
      filename?: string;
      fileData?: Array<{ Word: string; Meaning: string }>;
      aiData?: Vocabulary[];
    };
  };

  const [vocabularyList, setVocabularyList] = useState<Vocabulary[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [showSuccessModal, setShowSuccessModal] = useState<boolean>(false);
  const [audioLoading, setAudioLoading] = useState<boolean>(false);
  const [flashcardLoading, setFlashcardLoading] = useState<boolean>(false);
  const [videoLoading, setVideoLoading] = useState<boolean>(false);
  const [showFlashcardModal, setShowFlashcardModal] = useState<boolean>(false);
  const [flashcardStatus, setFlashcardStatus] = useState<'success' | 'failure' | null>(null);

  useEffect(() => {
    console.log('Location state:', state);

    // Helper function to extract vocabulary from a string like "('Word', 'hello')"
    const extractVocabulary = (value: string): string => {
      if (typeof value !== 'string') return '';
      const match = value.match(/^\('[^']*',\s*'([^']*)'\)$/);
      return match ? match[1].trim() : value.trim();
    };

    if (state?.source === 'file' && state?.fileData) {
      const transformedData = state.fileData.map((item, index) => {
        const word = extractVocabulary(item.Word);
        const meaning = extractVocabulary(item.Meaning);
        return {
          id: Date.now() + index,
          word,
          meaning,
          pronunciation: '',
          language: '',
        };
      });
      console.log('Transformed data (file source):', transformedData);
      setVocabularyList(transformedData);
    } else if (state?.source === 'ai' && state?.aiData) {
      const transformedData = state.aiData.map((item, index) => ({
        id: Date.now() + index,
        word: typeof item.word === 'string' ? item.word.trim() : '',
        meaning: typeof item.meaning === 'string' ? item.meaning.trim() : '',
        pronunciation: item.pronunciation || '',
        language: item.language || '',
      }));
      console.log('Transformed data (ai source):', transformedData);
      setVocabularyList(transformedData);
    } else if (state?.source === 'upload' && state?.filename) {
      setLoading(true);
      axios
        .get(`http://localhost:8000/home/viewDoc?filename=${state.filename}`)
        .then(res => {
          console.log('Raw API response (upload source):', res.data);
          const transformedData = res.data.map((item: any, index: number) => {
            const word = extractVocabulary(item.Word);
            const meaning = extractVocabulary(item.Meaning);
            return {
              id: Date.now() + index,
              word,
              meaning,
              pronunciation: '',
              language: '',
            };
          });
          console.log('Transformed data (upload source):', transformedData);
          setVocabularyList(transformedData);
        })
        .catch(err => {
          console.error('Error fetching uploaded vocab:', err);
          toast.error('Failed to load vocabulary data.');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      console.warn('No vocab data provided.');
      toast.warn('No vocabulary data available.');
    }
  }, [state]);

  const handleAddRow = () => {
    const newRow: Vocabulary = {
      id: Date.now(),
      word: '',
      meaning: '',
      pronunciation: '',
      language: '',
    };
    setVocabularyList([...vocabularyList, newRow]);
  };

  const handleEdit = (id: number, field: keyof Vocabulary, value: string) => {
    setVocabularyList(vocabularyList.map(word =>
      word.id === id ? { ...word, [field]: value } : word
    ));
  };

  const handleDelete = (id: number) => {
    setVocabularyList(vocabularyList.filter(word => word.id !== id));
  };

  const handleSaveFlashcards = async () => {
    if (!state?.filename) {
      toast.error('No filename provided for saving updates.');
      return;
    }

    // Helper function to extract vocabulary from a string like "('Word', 'hello')"
    const extractVocabulary = (value: string): string => {
      if (typeof value !== 'string') return '';
      const match = value.match(/^\('[^']*',\s*'([^']*)'\)$/);
      return match ? match[1].trim() : value.trim();
    };

    // Create the updates array with clean strings
    const updates = vocabularyList.map(item => ({
      Word: extractVocabulary(item.word),
      Meaning: extractVocabulary(item.meaning),
    }));

    // Filter out invalid entries
    const validUpdates = updates.filter(item => item.Word && item.Meaning);

    if (validUpdates.length === 0) {
      toast.error('No valid entries to save. Ensure all rows have a Word and Meaning.');
      return;
    }

    // Log the updates to debug
    console.log('Saving updates:', validUpdates);

    try {
      const response = await axios.put(
        `http://localhost:8000/home/updateDoc?filename=${state.filename}`,
        { updates: validUpdates },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      console.log('Update response:', response.data);

      // Reload the updated data
      const reloadResponse = await axios.get(`http://localhost:8000/home/viewDoc?filename=${state.filename}`);
      const transformedData = reloadResponse.data.map((item: any, index: number) => {
        const word = extractVocabulary(item.Word);
        const meaning = extractVocabulary(item.Meaning);
        return {
          id: Date.now() + index,
          word,
          meaning,
          pronunciation: '',
          language: '',
        };
      });
      console.log('Reloaded data:', transformedData);
      setVocabularyList(transformedData);

      toast.success('Flashcards updated successfully!');
      setShowSuccessModal(true);
    } catch (error) {
      console.error('Update failed:', error);
      if (axios.isAxiosError(error) && error.response) {
        const { status, data } = error.response;
        toast.error(`Update failed: ${data.detail || 'Unknown error'} (Status: ${status})`);
      } else {
        toast.error('Update failed: Network error or server unreachable.');
      }
    }
  };

  const handleGenerateAudio = async () => {
    if (!state?.filename) {
      toast.error('No filename provided for generating audio.');
      return;
    }

    setAudioLoading(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/generate_audio_for_file`,
        new URLSearchParams({
          filename: state.filename,
          language: 'en',
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );
      console.log('Audio generation response:', response.data);
      toast.success('Audio files generated successfully!');
    } catch (error) {
      console.error('Audio generation failed:', error);
      if (axios.isAxiosError(error) && error.response) {
        const { status, data } = error.response;
        toast.error(`Audio generation failed: ${data.detail || 'Unknown error'} (Status: ${status})`);
      } else {
        toast.error('Audio generation failed: Network error or server unreachable.');
      }
    } finally {
      setAudioLoading(false);
    }
  };

  const handleGenerateFlashcards = async () => {
    if (vocabularyList.length === 0) {
      toast.error('No vocabulary data to generate flashcards.');
      return;
    }

    setFlashcardLoading(true);
    try {
      // Helper function to extract vocabulary from a string like "('Word', 'hello')"
      const extractVocabulary = (value: string): string => {
        if (typeof value !== 'string') return '';
        const match = value.match(/^\('[^']*',\s*'([^']*)'\)$/);
        return match ? match[1].trim() : value.trim();
      };

      for (const item of vocabularyList) {
        const word = extractVocabulary(item.word);
        const meaning = extractVocabulary(item.meaning);

        if (!word || !meaning) {
          toast.warn(`Skipping invalid entry: Word: ${word}, Meaning: ${meaning}`);
          continue;
        }

        console.log(`Generating flashcard for Word: ${word}, Meaning: ${meaning}`);

        const response = await axios.get(`http://localhost:8000/home/generate_flashcard`, {
          params: {
            word: word,
            meaning: meaning,
          },
        });
        console.log(`Flashcard generated for ${word}:`, response.data);
      }
      setFlashcardStatus('success');
      setShowFlashcardModal(true);
    } catch (error) {
      console.error('Flashcard generation failed:', error);
      setFlashcardStatus('failure');
      setShowFlashcardModal(true);
      if (axios.isAxiosError(error) && error.response) {
        const { status, data } = error.response;
        toast.error(`Flashcard generation failed: ${data.detail || 'Unknown error'} (Status: ${status})`);
      } else {
        toast.error('Flashcard generation failed: Network error or server unreachable.');
      }
    } finally {
      setFlashcardLoading(false);
    }
  };

  const handleGenerateVideo = async () => {
    setVideoLoading(true);
    try {
      const response = await axios.post(`http://localhost:8000/home/generate_flashcard_video`, null, { responseType: 'blob' });
      console.log('Video generation response:', response);
      
      // Create a blob URL from the response data
      const videoBlob = new Blob([response.data], { type: 'video/mp4' });
      const videoUrl = window.URL.createObjectURL(videoBlob);
      
      // Create a temporary link element to trigger download
      const link = document.createElement('a');
      link.href = videoUrl;
      link.download = `flashcard_video_${Date.now()}.mp4`; // Dynamic filename with timestamp
      document.body.appendChild(link);
      link.click();
      
      // Clean up
      document.body.removeChild(link);
      window.URL.revokeObjectURL(videoUrl);
      
      toast.success('Video generated and download started!');
    } catch (error) {
      console.error('Video generation failed:', error);
      if (axios.isAxiosError(error) && error.response) {
        const { status, data } = error.response;
        toast.error(`Video generation failed: ${data.detail || 'Unknown error'} (Status: ${status})`);
      } else {
        toast.error('Video generation failed: Network error or server unreachable.');
      }
    } finally {
      setVideoLoading(false);
    }
};

  const closeFlashcardModal = () => {
    setShowFlashcardModal(false);
    setFlashcardStatus(null);
  };

  const handleGenerateVideoFromModal = () => {
    closeFlashcardModal();
    handleGenerateVideo();
  };

  const closeModal = () => {
    setShowSuccessModal(false);
    navigate('/list-files');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Review Vocabulary</h1>
      <p className="text-gray-600 mb-8">
        Review and edit your vocabulary list before creating flashcards.
      </p>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        {loading ? (
          <p className="text-gray-500">Loading vocabulary...</p>
        ) : vocabularyList.length > 0 ? (
          <VocabularyTable
            words={vocabularyList}
            onDelete={handleDelete}
            onEdit={handleEdit}
            onPlayAudio={() => {}}
          />
        ) : (
          <p className="text-gray-500">No vocabulary data available.</p>
        )}
      </div>

      <div className="flex flex-wrap gap-4 mb-4">
        <button
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          onClick={handleAddRow}
          disabled={loading || audioLoading || flashcardLoading || videoLoading}
        >
          Add New Row
        </button>
        <button
          className="px-6 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600 disabled:bg-purple-300"
          onClick={handleGenerateAudio}
          disabled={audioLoading || flashcardLoading || videoLoading}
        >
          {audioLoading ? 'Generating Audio...' : 'Generate Audio'}
        </button>
        <button
          className="px-6 py-2 bg-indigo-500 text-white rounded-md hover:bg-indigo-600 disabled:bg-indigo-300"
          onClick={handleGenerateFlashcards}
          disabled={audioLoading || flashcardLoading || videoLoading}
        >
          {flashcardLoading ? 'Generating Flashcards...' : 'Generate Flashcards'}
        </button>
        <button
          className="px-6 py-2 bg-teal-500 text-white rounded-md hover:bg-teal-600 disabled:bg-teal-300"
          onClick={handleGenerateVideo}
          disabled={audioLoading || flashcardLoading || videoLoading}
        >
          {videoLoading ? 'Generating Video...' : 'Generate Video'}
        </button>
      </div>

      <div className="flex justify-between">
        <button
          className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          onClick={() => navigate(state?.source === 'file' ? '/list-files' : '/create')}
          disabled={loading || audioLoading || flashcardLoading || videoLoading}
        >
          Back
        </button>
        <button
          className="px-6 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:bg-green-300"
          onClick={handleSaveFlashcards}
          disabled={loading || audioLoading || flashcardLoading || videoLoading}
        >
          Save Flashcards
        </button>
      </div>

      {showSuccessModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white rounded-lg p-6 shadow-lg max-w-sm w-full">
            <h2 className="text-xl font-semibold mb-4 text-green-600">Success!</h2>
            <p className="text-gray-700 mb-6">
              Flashcards updated successfully!
            </p>
            <div className="flex justify-end">
              <button
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                onClick={closeModal}
              >
                OK
              </button>
            </div>
          </div>
        </div>
      )}

      {showFlashcardModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white rounded-lg p-6 shadow-lg max-w-sm w-full">
            <h2 className={`text-xl font-semibold mb-4 ${flashcardStatus === 'success' ? 'text-green-600' : 'text-red-600'}`}>
              {flashcardStatus === 'success' ? 'Success!' : 'Failed!'}
            </h2>
            <p className="text-gray-700 mb-4">
              {flashcardStatus === 'success'
                ? 'Flashcard images generated successfully!'
                : 'Flashcard generation failed. Please try again.'}
            </p>
            {flashcardStatus === 'success' && (
              <p className="text-gray-700 mb-4">
                Would you like to generate a video from these flashcards?
              </p>
            )}
            <div className="flex justify-end gap-4">
              {flashcardStatus === 'success' && (
                <>
                  <button
                    className="px-4 py-2 bg-teal-500 text-white rounded-md hover:bg-teal-600"
                    onClick={handleGenerateVideoFromModal}
                  >
                    Yes, Generate Video
                  </button>
                  <button
                    className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                    onClick={closeFlashcardModal}
                  >
                    No, Close
                  </button>
                </>
              )}
              {flashcardStatus === 'failure' && (
                <button
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  onClick={closeFlashcardModal}
                >
                  Close
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PreviewPage;