import React from 'react'

interface FlashcardDisplayProps {
  word: string
  meaning: string
  imageUrl: string
}

const FlashcardDisplay: React.FC<FlashcardDisplayProps> = ({
  word,
  meaning,
  imageUrl,
}) => {
  return (
    <div className="text-center p-4">
      <img
        src={imageUrl}
        alt={word}
        className="w-full h-64 object-cover rounded-lg shadow-md"
      />
      <h2 className="text-2xl font-bold mt-4">{word}</h2>
      <p className="text-lg text-gray-600">{meaning}</p>
    </div>
  )
}

export default FlashcardDisplay;