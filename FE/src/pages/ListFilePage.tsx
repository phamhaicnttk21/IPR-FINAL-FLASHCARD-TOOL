import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import { motion, AnimatePresence } from 'framer-motion';
import { FileSpreadsheet, RefreshCw, ArrowLeft, Trash2 } from 'lucide-react'; // Added Trash2 icon

const ListFilePage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [files, setFiles] = useState<string[]>(location.state?.files || []);
  const [loading, setLoading] = useState<boolean>(false);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  // Fetch the list of files from the server
  const fetchFiles = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/listFiles');
      console.log('Fetched files from server:', response.data);
      setFiles(response.data);
    } catch (error) {
      console.error('Failed to fetch files:', error);
      toast.error('Failed to load file list.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleFileClick = async (filename: string) => {
    console.log('Clicked filename:', filename);
    if (!filename || filename === 'string' || !filename.endsWith('.xlsx')) {
      toast.error('Invalid filename selected.');
      return;
    }

    try {
      const response = await axios.get(`http://localhost:8000/home/viewDoc?filename=${filename}`);
      console.log('Fetched file data:', response.data);
      navigate('/preview', {
        state: {
          source: 'file',
          fileData: response.data,
          filename,
        },
      });
    } catch (error) {
      console.error('Failed to fetch file contents:', error);
      if (axios.isAxiosError(error) && error.response) {
        const { status, data } = error.response;
        toast.error(data.detail || `Failed to fetch file (Status: ${status})`);
      } else {
        toast.error('Failed to fetch file: Network error or server unreachable.');
      }
    }
  };

  const handleDeleteFile = async (filename: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the file click event
    if (!window.confirm(`Are you sure you want to delete ${filename}?`)) {
      return;
    }

    try {
      await axios.delete(`http://localhost:8000/home/deleteDoc?filename=${filename}`);
      toast.success(`File ${filename} deleted successfully.`);
      setFiles(files.filter((file) => file !== filename)); // Update UI immediately
    } catch (error) {
      console.error('Failed to delete file:', error);
      if (axios.isAxiosError(error) && error.response) {
        const { status, data } = error.response;
        toast.error(data.detail || `Failed to delete file (Status: ${status})`);
      } else {
        toast.error('Failed to delete file: Network error or server unreachable.');
      }
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchFiles();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-8">
      <div className="container mx-auto">
        {/* Header Section */}
        <div className="flex flex-col sm:flex-row justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-indigo-800 flex items-center mb-4 sm:mb-0">
            <FileSpreadsheet className="mr-3 h-8 w-8 text-indigo-600" />
            Uploaded Files
          </h1>
          <div className="flex space-x-3">
            <button
              onClick={handleRefresh}
              className={`flex items-center px-4 py-2 rounded-lg text-white font-semibold transition-all duration-300 ${
                refreshing
                  ? 'bg-indigo-400 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-700'
              }`}
              disabled={refreshing}
            >
              <RefreshCw
                className={`h-5 w-5 mr-2 ${refreshing ? 'animate-spin' : ''}`}
              />
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </button>
            <button
              onClick={() => navigate('/create')}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition-all duration-300"
            >
              <ArrowLeft className="h-5 w-5 mr-2" />
              Back to Create
            </button>
          </div>
        </div>

        {/* File List Section */}
        <div className="max-w-4xl mx0 mx-auto">
          {loading && files.length === 0 ? (
            <div className="flex justify-center items-center py-10">
              <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-600 border-solid"></div>
            </div>
          ) : files.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              <AnimatePresence>
                {files.map((file: string, index: number) => (
                  <motion.div
                    key={file}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="bg-white rounded-xl shadow-lg p-5 hover:shadow-xl transition-all duration-300 cursor-pointer border border-indigo-100 hover:border-indigo-300 relative"
                    onClick={() => handleFileClick(file)}
                  >
                    <div className="flex items-center space-x-3">
                      <FileSpreadsheet className="h-8 w-8 text-indigo-500" />
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-800 truncate">
                          {file}
                        </h3>
                        <p className="text-sm text-gray-500 mt-1">
                          Excel File (.xlsx)
                        </p>
                      </div>
                    </div>
                    <div className="mt-4 flex justify-end items-center space-x-2">
                      <span className="inline-block bg-indigo-50 text-indigo-700 text-xs font-medium px-3 py-1 rounded-full">
                        View Details
                      </span>
                      <button
                        onClick={(e) => handleDeleteFile(file, e)}
                        className="text-red-500 hover:text-red-700 transition-colors duration-200"
                        title="Delete File"
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          ) : (
            <div className="text-center py-10 bg-white rounded-xl shadow-md p-6">
              <FileSpreadsheet className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 text-lg">
                No files uploaded yet.
              </p>
              <p className="text-gray-500 mt-2">
                Upload an Excel file to get started.
              </p>
              <button
                onClick={() => navigate('/create')}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition-all duration-300"
              >
                Upload a File
              </button>
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>© 2025 Flashcard Learning Platform by Group 03.</p>
        </footer>
      </div>
    </div>
  );
};

export default ListFilePage;