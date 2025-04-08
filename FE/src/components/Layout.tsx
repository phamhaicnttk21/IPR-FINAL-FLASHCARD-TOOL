import React, { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import {
  BookOpenIcon,
  PlusCircleIcon,
  HomeIcon,
  LibraryIcon,
  UsersIcon,
} from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <header className="bg-white border-b border-gray-200 py-4">
        <div className="container mx-auto px-4 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <Link
              to="/"
              className="flex items-center text-blue-600 font-semibold"
            >
              <BookOpenIcon className="h-6 w-6 mr-2" />
              <span className="text-xl">FlashCard</span>
            </Link>
          </div>
          {/* Các mục và nút Create Flashcards đặt cạnh nhau */}
          <div className="flex items-center space-x-6">
            <Link
              to="/"
              className="flex items-center space-x-1 text-gray-700 hover:text-gray-900"
            >
              <HomeIcon className="h-5 w-5" />
              <span>Home</span>
            </Link>
            <Link
              to="/library"
              className="flex items-center space-x-1 text-gray-700 hover:text-gray-900"
            >
              <LibraryIcon className="h-5 w-5" />
              <span>Library</span>
            </Link>
            <Link
              to="/group3"
              className="flex items-center space-x-1 text-gray-700 hover:text-gray-900"
            >
              <UsersIcon className="h-5 w-5" />
              <span>Group3</span>
            </Link>
            <Link
              to="/create"
              className="bg-blue-600 text-white px-4 py-2 rounded-md flex items-center"
            >
              <PlusCircleIcon className="h-5 w-5 mr-1" />
              <span>Create Flashcards</span>
            </Link>
          </div>
        </div>
      </header>
      <main className="flex-grow">{children}</main>
      <footer className="py-4 text-center text-sm text-gray-500">
        © 2025 Flashcard Learning Platform by Group 03.
      </footer>
    </div>
  )
}

export default Layout
