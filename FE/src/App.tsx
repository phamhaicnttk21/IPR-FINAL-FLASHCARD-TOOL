import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import CreatePage from './pages/CreatePage';
import PreviewPage from './pages/PreviewPage';
import SlideshowPage from './pages/SlideshowPage';
import VideoPage from './pages/VideoPage';
export function App() {
  return <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/create" element={<CreatePage />} />
          <Route path="/preview" element={<PreviewPage />} />
          <Route path="/slideshow" element={<SlideshowPage />} />
          <Route path="/video" element={<VideoPage />} />
        </Routes>
      </Layout>
    </Router>;
}