import React from 'react';
import { FaVolumeUp, FaTrash } from 'react-icons/fa';

interface Vocabulary {
  id: number;
  word: string;
  meaning: string;
  pronunciation: string;
  language: string;
}

interface VocabularyTableProps {
  words: Vocabulary[];
  onDelete: (id: number) => void;
  onEdit: (id: number, field: keyof Vocabulary, value: string) => void;
  onPlayAudio: (word: string) => void;
}

const VocabularyTable: React.FC<VocabularyTableProps> = ({ words, onDelete, onEdit, onPlayAudio }) => {
  return (
    <table className="w-full border-collapse border border-gray-300">
      <thead>
        <tr className="bg-gray-100">
          <th className="border border-gray-300 p-2">Word</th>
          <th className="border border-gray-300 p-2">Meaning</th>
          <th className="border border-gray-300 p-2">Pronunciation</th>
          <th className="border border-gray-300 p-2">Audio</th>
          <th className="border border-gray-300 p-2">Actions</th>
        </tr>
      </thead>
      <tbody>
        {words.map(({ id, word, meaning, pronunciation }) => (
          <tr key={id}>
            {/* Ô nhập liệu cho Word */}
            <td className="border border-gray-300 p-2">
              <input
                type="text"
                value={word}
                onChange={(e) => onEdit(id, 'word', e.target.value)}
                className="w-full px-2 py-1 border border-blue-500 rounded-md focus:outline-none"
              />
            </td>
            {/* Ô nhập liệu cho Meaning */}
            <td className="border border-gray-300 p-2">
              <input
                type="text"
                value={meaning}
                onChange={(e) => onEdit(id, 'meaning', e.target.value)}
                className="w-full px-2 py-1 border border-blue-500 rounded-md focus:outline-none"
              />
            </td>
            {/* Ô nhập liệu cho Pronunciation */}
            <td className="border border-gray-300 p-2">
              <input
                type="text"
                value={pronunciation}
                onChange={(e) => onEdit(id, 'pronunciation', e.target.value)}
                className="w-full px-2 py-1 border border-blue-500 rounded-md focus:outline-none"
              />
            </td>
            {/* Nút Audio với icon */}
            <td className="border border-gray-300 p-2 text-center">
              <button
                className="px-3 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                onClick={() => onPlayAudio(word)}
              >
                <FaVolumeUp />
              </button>
            </td>
            {/* Nút Delete với icon */}
            <td className="border border-gray-300 p-2 text-center">
              <button
                className="px-3 py-1 bg-red-500 text-white rounded-md hover:bg-red-600"
                onClick={() => onDelete(id)}
              >
                <FaTrash />
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default VocabularyTable;
