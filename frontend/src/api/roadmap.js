import api from './axios';

export const generateRoadmap = () =>
  api.post('/roadmap/generate-roadmap');

export const submitFeedback = (data) =>
  api.post('/roadmap/feedback', data);
