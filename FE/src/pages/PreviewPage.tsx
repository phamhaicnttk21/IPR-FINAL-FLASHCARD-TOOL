import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import VocabularyTable from '../components/VocabularyTable';
import axios from 'axios';

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
  const { state } = location as { state: { source: string; filename?: string; aiData?: Vocabulary[] } };

  const [vocabularyList, setVocabularyList] = useState<Vocabulary[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (state?.source === 'upload' && state?.filename) {
      setLoading(true);
      axios
        .get(`https://generally-known-civet.ngrok-free.app/home/viewDoc?filename=${state.filename}`)
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
        })
        .finally(() => {
          setLoading(false);
        });
    } else if (state?.source === 'ai' && state?.aiData) {
      setVocabularyList(state.aiData);
    } else {
      console.warn('No vocab data provided.');
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

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Review Vocabulary</h1>
      <p className="text-gray-600 mb-8">
        Review and edit your vocabulary list before creating flashcards.
      </p>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        {loading ? (
          <p className="text-gray-500">Loading vocabulary...</p>
        ) : (
          <VocabularyTable 
            words={vocabularyList} 
            onDelete={handleDelete} 
            onEdit={handleEdit}
            onPlayAudio={() => {}} 
          />
        )}
      </div>

      <div className="flex justify-between mb-4">
        <button className="px-6 py-2 bg-blue-600 text-white rounded-md" onClick={handleAddRow}>
          Add New Row
        </button>
      </div>

      <div className="flex justify-between">
        <button className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md" onClick={() => navigate('/create')}>
          Back
        </button>
        <button className="px-6 py-2 bg-green-500 text-white rounded-md" onClick={() => alert('Flashcards saved!')}>
          Save Flashcards
        </button>
      </div>
    </div>
  );
};

export default PreviewPage;
