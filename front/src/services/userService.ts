import axios from 'axios';
import type { User, UserUpdate, PasswordChange } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api/v1';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const userService = {
  // Get current user
  getCurrentUser: async () => {
    const response = await axiosInstance.get<User>('/users/me');
    return response.data;
  },

  // Get user by ID
  getById: async (id: string) => {
    const response = await axiosInstance.get<User>(`/users/${id}`);
    return response.data;
  },

  // Update user profile
  update: async (data: UserUpdate) => {
    const response = await axiosInstance.put<User>('/users/me', data);
    return response.data;
  },

  // Change password
  changePassword: async (data: PasswordChange) => {
    await axiosInstance.post('/users/change-password', data);
  },

  // Delete account
  delete: async () => {
    await axiosInstance.delete('/users/me');
  },
};
