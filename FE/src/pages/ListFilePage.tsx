import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FileTextIcon } from 'lucide-react';

const ListFilePage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { state } = location as { state: { files?: string[] } };
  const [files, setFiles] = useState<string[]>([]);

  useEffect(() => {
    if (state?.files) {
      setFiles(state.files);
    } else {
      fetchFiles();
    }
  }, [state]);

  const fetchFiles = async () => {
    try {
      const response = await axios.get('http://localhost:8000/home/listFiles');
      setFiles(response.data.files);
    } catch (error) {
      console.error('Failed to fetch files:', error);
      toast.error("Failed to fetch files.");
    }
  };

  const handleFileClick = async (filename: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/home/viewDoc?filename=${filename}`);
      const fileData = response.data;
      navigate('/preview', { state: { source: 'file', filename, fileData } });
    } catch (error) {
      console.error(`Failed to fetch file data for ${filename}:`, error);
      if (axios.isAxiosError(error) && error.response) {
        const { status, data } = error.response;
        toast.error(`Failed to fetch file data: ${data.detail || 'Unknown error'} (Status: ${status})`);
      } else {
        toast.error("Failed to fetch file data: Network error or server unreachable.");
      }
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Uploaded Files</h1>
      <div className="mb-6 flex justify-between">
        <button
          className="bg-gray-200 text-gray-700 px-4 py-2 rounded-md"
          onClick={() => navigate('/create')}
        >
          Back to Create
        </button>
      </div>
      {files.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {files.map((file, index) => (
            <div
              key={index}
              className="bg-white p-4 rounded-lg shadow-md flex justify-between items-center cursor-pointer hover:bg-gray-100"
              onClick={() => handleFileClick(file)}
            >
              <div className="flex items-center">
                <FileTextIcon className="h-6 w-6 text-blue-600 mr-2" />
                <span className="text-gray-800">{file}</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500">No files found.</p>
      )}
    </div>
  );
};

export default ListFilePage;