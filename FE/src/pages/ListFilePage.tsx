import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const ListFilePage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const files = location.state?.files || []; // Get the files from state

  const handleFileClick = async (filename: string) => {
    try {
      const response = await axios.get(`http://localhost:8000/home/viewDoc?filename=${filename}`);
      console.log('File contents:', response.data);
      navigate('/preview', {
        state: {
          source: 'file', // New source to indicate navigation from ListFilePage
          fileData: response.data, // Pass the file contents
          filename: filename, // Pass the filename for reference
        },
      });
    } catch (error) {
      console.error('Failed to fetch file contents:', error);
      if (axios.isAxiosError(error) && error.response) {
        const { status, data } = error.response;
        toast.error(`Failed to fetch file contents: ${data.detail || 'Unknown error'} (Status: ${status})`);
      } else {
        toast.error("Failed to fetch file contents: Network error or server unreachable.");
      }
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Uploaded Files</h1>
      <div className="max-w-2xl mx-auto">
        {files.length > 0 ? (
          <ul className="list-disc pl-5">
            {files.map((file: string, index: number) => (
              <li
                key={index}
                className="text-blue-600 hover:underline cursor-pointer mb-2"
                onClick={() => handleFileClick(file)}
              >
                {file}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500">No files uploaded yet.</p>
        )}
        <div className="mt-6">
          <button
            className="bg-blue-600 text-white px-4 py-2 rounded-md"
            onClick={() => navigate('/create')}
          >
            Back to Create
          </button>
        </div>
      </div>
    </div>
  );
};

export default ListFilePage;