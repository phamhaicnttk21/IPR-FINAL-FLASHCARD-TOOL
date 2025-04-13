import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast, ToastContainer } from 'react-toastify';
import { Volume2Icon, SaveIcon, ArrowLeftIcon, PlusIcon, DownloadIcon } from 'lucide-react';

interface FileDataItem {
  Word: string;
  Meaning: string;
  audio_path?: string | null;
}

const PreviewPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { state } = location as { state: { source: string; filename: string; fileData: FileDataItem[] } };
  
  const [data, setData] = useState<FileDataItem[]>([]);
  const [loadingAudio, setLoadingAudio] = useState<boolean>(false);
  const [loadingSave, setLoadingSave] = useState<boolean>(false);
  const [loadingVideo, setLoadingVideo] = useState<boolean>(false);
  const [videoPath, setVideoPath] = useState<string | null>(null);
  const [videoFilename, setVideoFilename] = useState<string | null>(null);

  const BASE_URL = 'http://localhost:8000'; // Backend base URL

  useEffect(() => {
    if (state?.source === 'file' && state?.fileData) {
      // Ensure audio_path is a full URL
      const updatedFileData = state.fileData.map(item => ({
        ...item,
        audio_path: item.audio_path ? `${BASE_URL}${item.audio_path}` : null,
      }));
      setData(updatedFileData);
    } else if (state?.source === 'ai' && state?.aiData?.data) {
      // Handle AI-generated data if needed
      const updatedAiData = state.aiData.data.map((item: { word: string; meaning: string }) => ({
        Word: item.word,
        Meaning: item.meaning,
        audio_path: null, // AI data may have audio_path if generated
      }));
      setData(updatedAiData);
    } else {
      toast.error("No data available to preview.");
      navigate('/create');
    }
  }, [state, navigate]);

  const handleInputChange = (index: number, field: 'Word' | 'Meaning', value: string) => {
    const newData = [...data];
    newData[index] = { ...newData[index], [field]: value };
    setData(newData);
  };

  const handleAddRow = () => {
    if (state?.source !== 'file') {
      toast.error("Cannot add rows to AI-generated data.");
      return;
    }

    setData([...data, { Word: "", Meaning: "", audio_path: null }]);
  };

  const handleGenerateVideo = async () => {
    if (state?.source !== 'file' || !state?.filename) {
      toast.error("Cannot generate video: Invalid source or filename.");
      return;
    }

    setLoadingVideo(true);
    try {
      const formData = new FormData();
      formData.append('filename', state.filename);
      const response = await axios.post(
        'http://localhost:8000/home/generate_video_for_file',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      console.log(`Video generation for ${state.filename}:`, response.data);
      setVideoPath(response.data.video_path);
      setVideoFilename(`${state.filename.split('.')[0]}_video.mp4`);
      toast.success(`Video generated successfully for ${state.filename}!`);
    } catch (error) {
      console.error(`Failed to generate video for ${state.filename}:`, error);
      if (axios.isAxiosError(error) && error.response) {
        const { status, data } = error.response;
        toast.error(`Failed to generate video: ${data.detail || 'Unknown error'} (Status: ${status})`);
      } else {
        toast.error("Failed to generate video: Network error or server unreachable.");
      }
    } finally {
      setLoadingVideo(false);
    }
  };

  const handleGenerateAudio = async () => {
    if (state?.source !== 'file' || !state?.filename) {
      toast.error("Cannot generate audio: Invalid source or filename.");
      return;
    }

    setLoadingAudio(true);
    try {
      const formData = new FormData();
      formData.append('filename', state.filename);
      formData.append('language', 'en'); // Default language; you can make this configurable
      const response = await axios.post(
        'http://localhost:8000/home/generate_audio_for_file',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      console.log(`Audio generation for ${state.filename}:`, response.data);

      // Update the data with the new audio paths, prefixing with BASE_URL
      const updatedData = data.map((item) => {
        const safeWord = item.Word.replace(/[^a-zA-Z0-9]/g, '_');
        const audioPath = response.data.audio_files.find((path: string) =>
          path.includes(safeWord)
        );
        return {
          ...item,
          audio_path: audioPath ? `${BASE_URL}${audioPath}` : item.audio_path,
        };
      });
      setData(updatedData);

      toast.success(`Audio generated successfully for ${state.filename}!`);

      // Generate video after audio
      await handleGenerateVideo();
    } catch (error) {
      console.error(`Failed to generate audio for ${state.filename}:`, error);
      if (axios.isAxiosError(error) && error.response) {
        const { status, data } = error.response;
        toast.error(`Failed to generate audio: ${data.detail || 'Unknown error'} (Status: ${status})`);
      } else {
        toast.error("Failed to generate audio: Network error or server unreachable.");
      }
    } finally {
      setLoadingAudio(false);
    }
  };

  const handleSaveChanges = async () => {
    if (state?.source !== 'file' || !state?.filename) {
      toast.error("Cannot save changes: Invalid source or filename.");
      return;
    }

    // Validate that all rows have non-empty Word and Meaning
    for (const item of data) {
      if (!item.Word.trim() || !item.Meaning.trim()) {
        toast.error("All rows must have non-empty Word and Meaning values.");
        return;
      }
    }

    setLoadingSave(true);
    try {
      // Step 1: Save the changes
      const updates = data.map((item) => ({
        Word: item.Word,
        Meaning: item.Meaning,
      }));
      const updateResponse = await axios.put(`http://localhost:8000/home/updateDoc?filename=${state.filename}`, {
        updates,
      });
      console.log('Update successful:', updateResponse.data);
      toast.success("File updated successfully!");

      // Step 2: Generate audio for the updated file
      await handleGenerateAudio();
    } catch (error) {
      console.error('Update failed:', error);
      if (axios.isAxiosError(error) && error.response) {
        const { status, data } = error.response;
        toast.error(`Update failed: ${data.detail || 'Unknown error'} (Status: ${status})`);
      } else {
        toast.error("Update failed: Network error or server unreachable.");
      }
    } finally {
      setLoadingSave(false);
    }
  };

  const handlePlayAudio = (audioPath: string | null | undefined) => {
    if (!audioPath) {
      console.error("No audio path provided for playback.");
      toast.error("No audio available for this word.");
      return;
    }

    console.log("Attempting to play audio from:", audioPath);

    try {
      const audio = new Audio(audioPath);
      audio.oncanplaythrough = () => {
        console.log("Audio can play through, starting playback...");
        audio.play().catch((error) => {
          console.error("Audio playback failed:", error);
          toast.error("Failed to play audio: " + error.message);
        });
      };
      audio.onerror = (error) => {
        console.error("Audio loading failed:", error);
        toast.error("Failed to load audio file.");
      };
    } catch (error) {
      console.error("Error creating Audio object:", error);
      toast.error("Failed to initialize audio playback.");
    }
  };

  const handleDownloadVideo = async () => {
    if (!videoFilename) {
      toast.error("No video available to download.");
      return;
    }

    try {
      const response = await axios.get(
        `http://localhost:8000/home/download_video?filename=${videoFilename}`,
        {
          responseType: 'blob',
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', videoFilename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success("Video downloaded successfully!");
    } catch (error) {
      console.error('Video download failed:', error);
      toast.error("Failed to download video.");
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">
          Preview {state?.source === 'file' ? state?.filename : 'AI Generated Data'}
        </h1>
        <div className="flex space-x-4">
          <button
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-md flex items-center hover:bg-gray-300"
            onClick={() => navigate(state?.source === 'file' ? '/list-files' : '/create')}
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Back
          </button>
          {state?.source === 'file' && (
            <>
              <button
                className="bg-green-600 text-white px-4 py-2 rounded-md flex items-center hover:bg-green-700"
                onClick={handleAddRow}
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Add Row
              </button>
              <button
                className={`bg-blue-600 text-white px-4 py-2 rounded-md flex items-center hover:bg-blue-700 ${loadingSave ? 'opacity-50 cursor-not-allowed' : ''}`}
                onClick={handleSaveChanges}
                disabled={loadingSave}
              >
                <SaveIcon className="h-5 w-5 mr-2" />
                {loadingSave ? "Saving..." : "Save Changes"}
              </button>
              <button
                className={`bg-purple-600 text-white px-4 py-2 rounded-md flex items-center hover:bg-purple-700 ${loadingAudio ? 'opacity-50 cursor-not-allowed' : ''}`}
                onClick={handleGenerateAudio}
                disabled={loadingAudio}
              >
                <Volume2Icon className="h-5 w-5 mr-2" />
                {loadingAudio ? "Generating..." : "Generate Audio"}
              </button>
              {videoPath && (
                <button
                  className="bg-yellow-600 text-white px-4 py-2 rounded-md flex items-center hover:bg-yellow-700"
                  onClick={handleDownloadVideo}
                >
                  <DownloadIcon className="h-5 w-5 mr-2" />
                  Download Video
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {data.length > 0 ? (
        <div className="bg-white rounded-lg shadow-md p-6">
          <table className="w-full table-auto">
            <thead>
              <tr className="bg-gray-100">
                <th className="p-3 text-left">Word</th>
                <th className="p-3 text-left">Meaning</th>
                <th className="p-3 text-left">Audio</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item, index) => (
                <tr key={index} className="border-b">
                  <td className="p-3">
                    <input
                      type="text"
                      className="w-full p-2 border border-gray-300 rounded-md"
                      value={item.Word}
                      onChange={(e) => handleInputChange(index, 'Word', e.target.value)}
                      disabled={state?.source !== 'file'} // Disable editing for AI data
                    />
                  </td>
                  <td className="p-3">
                    <input
                      type="text"
                      className="w-full p-2 border border-gray-300 rounded-md"
                      value={item.Meaning}
                      onChange={(e) => handleInputChange(index, 'Meaning', e.target.value)}
                      disabled={state?.source !== 'file'} // Disable editing for AI data
                    />
                  </td>
                  <td className="p-3">
                    {item.audio_path ? (
                      <button
                        className="text-blue-600 hover:underline"
                        onClick={() => handlePlayAudio(item.audio_path)}
                      >
                        Play Audio
                      </button>
                    ) : (
                      <span className="text-gray-500">No audio</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-gray-500">No data to display.</p>
      )}

      <ToastContainer
        position="top-center"
        autoClose={2000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        pauseOnHover
        draggable
      />
    </div>
  );
};

export default PreviewPage;