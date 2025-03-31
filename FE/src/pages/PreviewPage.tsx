import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import VocabularyTable from '../components/VocabularyTable';

interface Vocabulary {
  id: number;
  word: string;
  meaning: string;
  pronunciation: string;
  language: string;
}

const PreviewPage: React.FC = () => {
  const navigate = useNavigate();
  const [vocabularyList, setVocabularyList] = useState<Vocabulary[]>([
    {
      id: 1,
      word: 'Hello',
      meaning: 'Xin chào',
      pronunciation: '/həˈləʊ/',
      language: 'English',
    },
    {
      id: 2,
      word: 'Thank you',
      meaning: 'Cảm ơn',
      pronunciation: '/θæŋk juː/',
      language: 'English',
    },
  ]);

  const handleAddRow = () => {
    const newRow: Vocabulary = {
      id: Date.now(), // Tạo ID duy nhất
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
        <VocabularyTable 
          words={vocabularyList} 
          onDelete={handleDelete} 
          onEdit={(id: number, field: keyof Vocabulary, value: string) => {
            handleEdit(id, field, value);
          }} 
          onPlayAudio={(word) => {}} 
        />
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
        <button className="px-6 py-2 bg-blue-600 text-white rounded-md" onClick={() => navigate('/slideshow')}>
          Continue to Slideshow
        </button>
      </div>
    </div>
  );
};

export default PreviewPage;
