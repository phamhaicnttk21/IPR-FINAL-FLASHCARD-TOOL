import React from 'react';
import { Link } from 'react-router-dom';
import { UploadIcon, BrainIcon, BookIcon, ArrowRightIcon } from 'lucide-react';
const HomePage = () => {
  return <div className="w-full">
      {/* Hero Section */}
      <section className="bg-blue-600 text-white py-16">
        <div className="container mx-auto px-4 flex flex-col md:flex-row items-center">
          <div className="md:w-1/2 mb-8 md:mb-0">
            <h1 className="text-4xl font-bold mb-4">
              Learn Faster with Interactive Flashcards
            </h1>
            <p className="text-xl mb-8">
              Create, study, and master any subject with our powerful flashcard
              platform.
            </p>
            <Link to="/create" className="bg-white text-blue-600 px-6 py-3 rounded-md font-medium inline-flex items-center">
              Get Started
              <ArrowRightIcon className="ml-2 h-5 w-5" />
            </Link>
          </div>
          <div className="md:w-1/2 md:pl-10">
              <img src="https://images.unsplash.com/photo-1434030216411-0b793f4b4173?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80" alt="Student studying with flashcards" className="rounded-lg shadow-xl" />
            </div>
        </div>
      </section>
      {/* Features Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">
            Create Flashcards Your Way
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-lg shadow-md text-center">
              <div className="bg-blue-100 h-16 w-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <UploadIcon className="h-8 w-8 text-blue-500" />
              </div>
              <h3 className="text-xl font-semibold mb-2">
                Upload Existing Files
              </h3>
              <p className="text-gray-600 mb-6">
                Import your vocabulary lists from Excel, CSV, or our template
                files to quickly create flashcard decks.
              </p>
              <Link to="/create" className="text-blue-600 font-medium inline-flex items-center">
                Upload File
                <ArrowRightIcon className="ml-1 h-4 w-4" />
              </Link>
            </div>
            <div className="bg-white p-8 rounded-lg shadow-md text-center">
              <div className="bg-blue-100 h-16 w-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <BrainIcon className="h-8 w-8 text-blue-500" />
              </div>
              <h3 className="text-xl font-semibold mb-2">
                AI-Generated Vocabulary
              </h3>
              <p className="text-gray-600 mb-6">
                Let our AI create vocabulary sets based on your topics,
                difficulty level, and learning goals.
              </p>
              <Link to="/create" className="text-blue-600 font-medium inline-flex items-center">
                Use AI Generator
                <ArrowRightIcon className="ml-1 h-4 w-4" />
              </Link>
            </div>
            <div className="bg-white p-8 rounded-lg shadow-md text-center">
              <div className="bg-blue-100 h-16 w-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <BookIcon className="h-8 w-8 text-blue-500" />
              </div>
              <h3 className="text-xl font-semibold mb-2">
                Interactive Learning
              </h3>
              <p className="text-gray-600 mb-6">
                Study with interactive flashcards featuring words,
                pronunciations, images, and meanings.
              </p>
              <Link to="/library" className="text-blue-600 font-medium inline-flex items-center">
                Browse Library
                <ArrowRightIcon className="ml-1 h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>
      {/* How It Works Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="bg-blue-600 text-white h-12 w-12 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Create</h3>
              <p className="text-gray-600">
                Upload a file or use our AI to generate vocabulary flashcards
              </p>
            </div>
            <div className="text-center">
              <div className="bg-blue-600 text-white h-12 w-12 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Preview</h3>
              <p className="text-gray-600">
                Review your flashcards and make any necessary adjustments
              </p>
            </div>
            <div className="text-center">
              <div className="bg-blue-600 text-white h-12 w-12 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Save</h3>
              <p className="text-gray-600">
                Save your flashcard deck to your library for future studying
              </p>
            </div>
            <div className="text-center">
              <div className="bg-blue-600 text-white h-12 w-12 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-xl font-bold">4</span>
              </div>
              <h3 className="text-xl font-semibold mb-2">Study</h3>
              <p className="text-gray-600">
                Learn with interactive flashcards featuring words and visuals
              </p>
            </div>
          </div>
          <div className="text-center mt-12">
            <Link to="/create" className="bg-blue-600 text-white px-6 py-3 rounded-md font-medium">
              Create Your First Deck
            </Link>
          </div>
        </div>
      </section>
    </div>;
};
export default HomePage;