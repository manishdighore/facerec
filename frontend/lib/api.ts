import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export interface Person {
  id: string;
  name: string;
  email?: string;
  employee_id?: string;
  added_date: string;
  image_count: number;
}

export interface BoundingBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface RecognizedPerson {
  name: string;
  id: string | null;
  employee_id?: string;
  distance?: number;
  confidence?: number;
}

export interface DetectedFace {
  bbox: BoundingBox;
  detection_confidence: number;
  recognized: boolean;
  person: RecognizedPerson;
}

export interface DetectionResult {
  faces: DetectedFace[];
  count: number;
  message?: string;
}

export interface RegisterResponse {
  message: string;
  person: Person;
}

export const api = {
  async detectAndRecognize(imageBase64: string): Promise<DetectionResult> {
    const response = await axios.post(`${API_BASE_URL}/api/detect-and-recognize`, {
      image: imageBase64,
    });
    return response.data;
  },

  async registerFace(name: string, imageBase64: string, email?: string, employeeId?: string): Promise<RegisterResponse> {
    const response = await axios.post(`${API_BASE_URL}/api/register`, {
      name,
      email,
      employee_id: employeeId,
      image: imageBase64,
    });
    return response.data;
  },

  async healthCheck() {
    const response = await axios.get(`${API_BASE_URL}/api/health`);
    return response.data;
  },

  async getPeople(): Promise<Person[]> {
    const response = await axios.get(`${API_BASE_URL}/api/people`);
    return response.data.people;
  },

  async deletePerson(personId: string) {
    const response = await axios.delete(`${API_BASE_URL}/api/people/${personId}`);
    return response.data;
  },

  getPersonImageUrl(personId: string): string {
    return `${API_BASE_URL}/api/people/${personId}/image`;
  },
};
