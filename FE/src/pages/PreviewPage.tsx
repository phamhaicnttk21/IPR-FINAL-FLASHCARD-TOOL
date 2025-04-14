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

  useEffect(() => {
    if (state?.source === 'file' && state?.fileData) {
      const transformedData = state.fileData.map((item, index) => ({
        id: Date.now() + index,
        word: item.Word || '',
        meaning: item.Meaning || '',
        pronunciation: '',
        language: '',
      }));
      setVocabularyList(transformedData);
    } else if (state?.source === 'ai' && state?.aiData) {
      setVocabularyList(state.aiData);
    } else if (state?.source === 'upload' && state?.filename) {
      setLoading(true);
      axios
        .get(`http://localhost:8000/home/viewDoc?filename=${state.filename}`)
        .then(res => {
          const transformedData = res.data.map((item: any, index: number) => ({
            id: Date.now() + index,
            word: item.Word || '',
            meaning: item.Meaning || '',
            pronunciation: '',
            language: '',
          }));
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

    const updates = vocabularyList.map(item => ({
      Word: item.word,
      Meaning: item.meaning,
    }));

    const validUpdates = updates.filter(item => item.Word.trim() && item.Meaning.trim());

    if (validUpdates.length === 0) {
      toast.error('No valid entries to save. Ensure all rows have a Word and Meaning.');
      return;
    }

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

  const closeModal = () => {
    setShowSuccessModal(false);
    navigate('/list-files'); // Navigate back to list after closing modal
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

      <div className="flex justify-between mb-4">
        <button
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          onClick={handleAddRow}
        >
          Add New Row
        </button>
      </div>

      <div className="flex justify-between">
        <button
          className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          onClick={() => navigate(state?.source === 'file' ? '/list-files' : '/create')}
        >
          Back
        </button>
        <button
          className="px-6 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
          onClick={handleSaveFlashcards}
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
    </div>
  );
};

export default PreviewPage;