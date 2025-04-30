import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import VocabularyTable from '../components/VocabularyTable';
import axios from 'axios';
import { toast, ToastContent } from 'react-toastify';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Volume2, Image, Video, ArrowLeft, Save, X } from 'lucide-react';

interface Vocabulary {
  id: number;
  word: string;
  meaning: string;
  language: string;
}

const PreviewPage: React.FC = () => {
  const navigate = useNavigate();
  const { state } = useLocation() as {
    state: {
      source: string;
      filename?: string;
      fileData?: Array<{ Word: string; Meaning: string }>;
      aiData?: Vocabulary[];
    };
  };

  const [vocabularyList, setVocabularyList] = useState<Vocabulary[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [audioLoading, setAudioLoading] = useState<boolean>(false);
  const [flashcardLoading, setFlashcardLoading] = useState<boolean>(false);
  const [videoLoading, setVideoLoading] = useState<boolean>(false);
  const [showFlashcardModal, setShowFlashcardModal] = useState<boolean>(false);
  const [flashcardStatus, setFlashcardStatus] = useState<'success' | 'failure' | null>(null);
  const [filename, setFilename] = useState<string | null>(null);
  const [showVideoSuccess, setShowVideoSuccess] = useState<boolean>(false);

  useEffect(() => {
    const storedFilename = localStorage.getItem('previewFilename');
    console.log('Location state:', state);
    console.log('Stored filename from localStorage:', storedFilename);

    if (state?.filename && state.filename !== 'string' && state.filename.endsWith('.xlsx')) {
      const normalizedFilename = state.filename.toLowerCase();
      console.log('Setting filename from state:', normalizedFilename);
      setFilename(normalizedFilename);
      localStorage.setItem('previewFilename', normalizedFilename);
    } else if (storedFilename && storedFilename !== 'string' && storedFilename.endsWith('.xlsx')) {
      const normalizedFilename = storedFilename.toLowerCase();
      console.log('Setting filename from localStorage:', normalizedFilename);
      setFilename(normalizedFilename);
    } else {
      console.warn('No valid filename available in state or localStorage.');
      toast.warn('No valid file selected. Please upload a file.');
      navigate('/list-files');
      return;
    }

    if (state?.source === 'file' && state?.fileData) {
      console.log('Raw state.fileData:', JSON.stringify(state.fileData, null, 2));
      const transformedData = state.fileData
        .map((item, index) => {
          if (!item || typeof item.Word !== 'string' || typeof item.Meaning !== 'string') {
            console.warn('Invalid fileData item:', item);
            return null;
          }
          return {
            id: Date.now() + index,
            word: item.Word.trim(),
            meaning: item.Meaning.trim(),
            language: '',
          };
        })
        .filter((item): item is Vocabulary => item !== null);
      console.log('Transformed data (file source):', transformedData);
      setVocabularyList(transformedData);
    } else if (state?.source === 'ai' && state?.aiData) {
      const transformedData = state.aiData.map((item, index) => ({
        id: Date.now() + index,
        word: typeof item.word === 'string' ? item.word.trim() : '',
        meaning: typeof item.meaning === 'string' ? item.meaning.trim() : '',
        language: item.language || '',
      }));
      console.log('Transformed data (ai source):', transformedData);
      setVocabularyList(transformedData);
    } else if ((state?.source === 'upload' || !state?.source) && filename) {
      setLoading(true);
      axios
        .get(`http://localhost:8000/home/viewDoc?filename=${filename}`)
        .then(res => {
          console.log('Raw API response (upload source):', JSON.stringify(res.data, null, 2));
          const transformedData = res.data
            .map((item: any, index: number) => {
              if (!item || typeof item.Word !== 'string' || typeof item.Meaning !== 'string') {
                console.warn('Invalid API item:', item);
                return null;
              }
              return {
                id: Date.now() + index,
                word: item.Word.trim(),
                meaning: item.Meaning.trim(),
                language: '',
              };
            })
            .filter((item): item is Vocabulary => item !== null);
          console.log('Transformed data (upload source):', transformedData);
          setVocabularyList(transformedData);
        })
        .catch(err => {
          console.error('Error fetching uploaded vocab:', err);
          if (axios.isAxiosError(err) && err.response?.status === 404) {
            toast.error('File no longer exists on the server. Please upload a new file.');
            localStorage.removeItem('previewFilename');
            navigate('/list-files');
          } else {
            toast.error('Failed to load vocabulary data.');
            navigate('/list-files');
          }
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      console.warn('No vocab data provided.');
      toast.warn('No vocabulary data available.');
      navigate('/list-files');
    }
  }, [state, navigate]);

  const handleAddRow = () => {
    const newRow: Vocabulary = {
      id: Date.now(),
      word: '',
      meaning: '',
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
    if (!filename) {
      toast.error('No filename provided for saving updates.');
      return;
    }

    const updates = vocabularyList
      .map(item => ({
        Word: item.word.trim(),
        Meaning: item.meaning.trim(),
      }))
      .filter(item => item.Word && item.Meaning);

    if (updates.length === 0) {
      toast.error('No valid entries to save. Ensure all rows have a Word and Meaning.');
      return;
    }

    console.log('Saving updates:', JSON.stringify(updates, null, 2));

    try {
      const response = await axios.put(
        `http://localhost:8000/home/updateDoc?filename=${filename}`,
        { updates },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      console.log('Update response:', response.data);

      toast.success(
        (({ closeToast }) => (
          <div className="flex items-center justify-between w-full">
            <span>Flashcards updated successfully!</span>
            <button onClick={closeToast} className="ml-4">
              <X className="h-5 w-5 text-gray-600 hover:text-gray-800" />
            </button>
          </div>
        )) as ToastContent,
        {
          autoClose: 5000,
        }
      );
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
    if (!filename) {
      toast.error('No filename provided for generating audio.');
      return;
    }

    if (filename === 'string' || !filename.endsWith('.xlsx')) {
      toast.error('Invalid filename for generating audio.');
      localStorage.removeItem('previewFilename');
      navigate('/list-files');
      return;
    }

    console.log('Generating audio for filename:', filename);
    console.log('Request payload:', { filename, language: 'en' });

    setAudioLoading(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/home/generate_audio_for_file`,
        new URLSearchParams({
          filename: filename,
          language: 'en',
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
          },
        }
      );
      console.log('Audio generation response:', response.data);
      toast.success('Audio files generated successfully!');
    } catch (error) {
      console.error('Audio generation failed:', error);
      if (axios.isAxiosError(error) && error.response) {
        const { status, data } = error.response;
        console.log('Error response data:', data);
        if (status === 404) {
          toast.error('File not found on the server. Please upload the file again.');
          localStorage.removeItem('previewFilename');
          navigate('/list-files');
        } else {
          toast.error(`Audio generation failed: ${data.detail || 'Unknown error'} (Status: ${status})`);
        }
      } else {
        toast.error('Audio generation failed: Network error or server unreachable.');
      }
    } finally {
      setAudioLoading(false);
    }
  };

  const handlePlayAudio = async (word: string) => {
    try {
      const safeWord = word.replace(/[^a-zA-Z0-9]/g, '_');
      const audioUrl = `http://localhost:8000/audio_uploadfile/${safeWord}.mp3`;
      const audio = new Audio(audioUrl);
      await audio.play();
    } catch (error) {
      console.error(`Failed to play audio for word "${word}":`, error);
      toast.error(`Failed to play audio for "${word}". Ensure audio has been generated.`);
    }
  };

  const handleGenerateFlashcards = async () => {
    if (vocabularyList.length === 0) {
      toast.error('No vocabulary data to generate flashcards.');
      return;
    }

    setFlashcardLoading(true);
    const generatedFlashcards: { word: string; meaning: string }[] = [];
    const failedEntries: { item: Vocabulary; reason: string }[] = [];

    try {
      console.log('Generating flashcards for:', JSON.stringify(vocabularyList, null, 2));

      for (const item of vocabularyList) {
        const word = item.word.trim();
        const meaning = item.meaning.trim();

        if (!word || !meaning) {
          toast.warn(`Skipping invalid entry: Word: ${word}, Meaning: ${meaning}`);
          failedEntries.push({ item, reason: 'Empty word or meaning' });
          continue;
        }

        console.log(`Generating flashcard for Word: ${word}, Meaning: ${meaning}`);

        try {
          const response = await axios.get(`http://localhost:8000/home/generate_flashcard`, {
            params: {
              word,
              meaning,
            },
          });
          console.log(`Flashcard generated for ${word}:`, response.data);
          generatedFlashcards.push({ word, meaning });
        } catch (error) {
          console.error(`Failed to generate flashcard for ${word}:`, error);
          if (axios.isAxiosError(error) && error.response) {
            failedEntries.push({ item, reason: error.response.data.detail || error.message });
          } else {
            failedEntries.push({ item, reason: error.message });
          }
        }
      }

      if (generatedFlashcards.length === vocabularyList.length) {
        toast.success('All flashcards generated successfully!');
        setFlashcardStatus('success');
      } else {
        toast.warn(
          `Generated ${generatedFlashcards.length} of ${vocabularyList.length} flashcards. Check console for details.`
        );
        console.log('Failed entries:', failedEntries);
        setFlashcardStatus('failure');
      }
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
    if (!filename) {
      toast.error('No filename provided for generating video.');
      return;
    }

    if (filename === 'string' || !filename.endsWith('.xlsx')) {
      toast.error('Invalid filename for generating video.');
      localStorage.removeItem('previewFilename');
      navigate('/list-files');
      return;
    }

    setVideoLoading(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/home/generate_flashcard_video_with_audio`,
        new URLSearchParams({
          filename: filename,
          language: 'English',
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'video/mp4',
          },
          responseType: 'blob',
        }
      );
      console.log('Video generation response:', response);

      const videoBlob = new Blob([response.data], { type: 'video/mp4' });
      const videoUrl = window.URL.createObjectURL(videoBlob);

      const link = document.createElement('a');
      link.href = videoUrl;
      link.download = `flashcard_video_${Date.now()}.mp4`;
      document.body.appendChild(link);
      link.click();

      document.body.removeChild(link);
      window.URL.revokeObjectURL(videoUrl);

      toast.success('Video generated and download started!');
      setShowVideoSuccess(true);
      setTimeout(() => setShowVideoSuccess(false), 3000);
    } catch (error) {
      console.error('Video generation failed:', error);
      if (axios.isAxiosError(error) && error.response) {
        const { status, data } = error.response;
        if (data instanceof Blob) {
          const errorText = await data.text();
          const errorJson = JSON.parse(errorText);
          toast.error(`Video generation failed: ${errorJson.detail || 'Unknown error'} (Status: ${status})`);
        } else {
          toast.error(`Video generation failed: ${data.detail || 'Unknown error'} (Status: ${status})`);
        }
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-8 relative">
      <div className="container mx-auto">
        <h1 className="text-4xl font-bold text-indigo-800 mb-4">Review Vocabulary</h1>
        <p className="text-gray-600 mb-8">
          Review and edit your vocabulary list before creating flashcards.
        </p>

        <div className="bg-white rounded-xl shadow-lg p-6 mb-6 border border-indigo-100">
          {loading ? (
            <div className="flex justify-center items-center py-10">
              <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-600 border-solid"></div>
            </div>
          ) : vocabularyList.length > 0 ? (
            <VocabularyTable
              words={vocabularyList}
              onDelete={handleDelete}
              onEdit={handleEdit}
              onPlayAudio={handlePlayAudio}
            />
          ) : (
            <div className="text-center py-10">
              <p className="text-gray-600 text-lg">No vocabulary data available.</p>
              <p className="text-gray-500 mt-2">Add some words to get started.</p>
            </div>
          )}
        </div>

        <div className="flex flex-wrap gap-4 mb-4">
          <button
            className="flex items-center px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-400 transition-all duration-300"
            onClick={handleAddRow}
            disabled={loading || audioLoading || flashcardLoading || videoLoading}
          >
            <Plus className="h-5 w-5 mr-2" />
            Add New Row
          </button>
          <button
            className="flex items-center px-6 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600 disabled:bg-purple-300 transition-all duration-300"
            onClick={handleGenerateAudio}
            disabled={audioLoading || flashcardLoading || videoLoading}
          >
            <Volume2 className="h-5 w-5 mr-2" />
            {audioLoading ? 'Generating Audio...' : 'Generate Audio'}
          </button>
          <button
            className="flex items-center px-6 py-2 bg-indigo-500 text-white rounded-md hover:bg-indigo-600 disabled:bg-indigo-300 transition-all duration-300"
            onClick={handleGenerateFlashcards}
            disabled={audioLoading || flashcardLoading || videoLoading}
          >
            <Image className="h-5 w-5 mr-2" />
            {flashcardLoading ? 'Generating Flashcards...' : 'Generate Flashcards'}
          </button>
          <button
            className="flex items-center px-6 py-2 bg-teal-500 text-white rounded-md hover:bg-teal-600 disabled:bg-teal-300 transition-all duration-300"
            onClick={handleGenerateVideo}
            disabled={audioLoading || flashcardLoading || videoLoading}
          >
            <Video className="h-5 w-5 mr-2" />
            {videoLoading ? 'Generating Video...' : 'Generate Video'}
          </button>
        </div>

        <div className="flex justify-between">
          <button
            className="flex items-center px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:bg-gray-300 transition-all duration-300"
            onClick={() => navigate(state?.source === 'file' ? '/list-files' : '/create')}
            disabled={loading || audioLoading || flashcardLoading || videoLoading}
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Back
          </button>
          <button
            className="flex items-center px-6 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 disabled:bg-green-300 transition-all duration-300"
            onClick={handleSaveFlashcards}
            disabled={loading || audioLoading || flashcardLoading || videoLoading}
          >
            <Save className="h-5 w-5 mr-2" />
            Save Flashcards
          </button>
        </div>

        {showFlashcardModal && (
          <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
            <div className="bg-white rounded-lg p-6 shadow-lg max-w-sm w-full">
              <h2
                className={`text-xl font-semibold mb-4 ${
                  flashcardStatus === 'success' ? 'text-green-600' : 'text-red-600'
                }`}
              >
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

        <AnimatePresence>
          {showVideoSuccess && (
            <motion.div
              className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none"
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.5 }}
              transition={{ duration: 0.5 }}
            >
              <div className="relative flex items-center justify-center">
                <motion.div
                  className="absolute w-64 h-64 bg-gradient-to-r from-orange-400 to-yellow-400 rounded-full"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1.5, opacity: 0 }}
                  transition={{ duration: 1, repeat: 1 }}
                />
                {[...Array(20)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-3 h-3 rounded-full"
                    style={{
                      backgroundColor: `hsl(${Math.random() * 360}, 70%, 60%)`,
                    }}
                    initial={{ x: 0, y: 0, opacity: 1 }}
                    animate={{
                      x: (Math.random() - 0.5) * 300,
                      y: (Math.random() - 0.5) * 300,
                      opacity: 0,
                    }}
                    transition={{ duration: 1.5, delay: Math.random() * 0.5 }}
                  />
                ))}
                <motion.div
                  className="text-center"
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.2, duration: 0.5 }}
                >
                  <h2 className="text-6xl font-bold text-red-600 drop-shadow-lg">Yeah!</h2>
                  <p className="text-4xl font-semibold text-red-600 drop-shadow-lg mt-2">
                    Successful!
                  </p>
                </motion.div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>© 2025 Flashcard Learning Platform by Group 03.</p>
        </footer>
      </div>
    </div>
  );
};

export default PreviewPage;