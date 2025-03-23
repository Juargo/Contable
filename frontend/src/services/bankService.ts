import axios from 'axios';
import { API_URL } from '../config/constants';

export interface Bank {
  id: number;
  name: string;
  code?: string;
}

export const getBanks = async (): Promise<Bank[]> => {
  try {
    const response = await axios.get(`${API_URL}/banks`);
    return response.data;
  } catch (error) {
    console.error('Error al obtener los bancos:', error);
    return [];
  }
};
