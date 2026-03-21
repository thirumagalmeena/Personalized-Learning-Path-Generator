import api from './axios';

export const generateRoadmap = () =>
  api.post('/roadmap/generate-roadmap');

export const getSavedRoadmaps = () =>
  api.get('/roadmap/saved');

export const getSavedRoadmap = (goalId) =>
  api.get(`/roadmap/${goalId}`);

export const submitFeedback = (data) =>
  api.post('/roadmap/feedback', data);
