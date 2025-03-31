import React from 'react'
import { PlayIcon, PauseIcon, DownloadIcon } from 'lucide-react'

interface VideoControlsProps {
  isPlaying: boolean
  onTogglePlay: () => void
  onDownload: () => void
}

const VideoControls: React.FC<VideoControlsProps> = ({
  isPlaying,
  onTogglePlay,
  onDownload,
}) => {
  return (
    <div className="flex items-center justify-center space-x-4 p-4">
      <button
        onClick={onTogglePlay}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg flex items-center"
      >
        {isPlaying ? <PauseIcon className="w-5 h-5" /> : <PlayIcon className="w-5 h-5" />}
        <span className="ml-2">{isPlaying ? 'Pause' : 'Play'}</span>
      </button>
      <button
        onClick={onDownload}
        className="px-4 py-2 bg-green-600 text-white rounded-lg flex items-center"
      >
        <DownloadIcon className="w-5 h-5" />
        <span className="ml-2">Download</span>
      </button>
    </div>
  )
}

export default VideoControls;