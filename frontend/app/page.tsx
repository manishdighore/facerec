'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import { api, DetectedFace } from '@/lib/api';
import styles from './page.module.css';

export default function Home() {
  const webcamRef = useRef<Webcam>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [detectedFaces, setDetectedFaces] = useState<DetectedFace[]>([]);
  const [error, setError] = useState<string>('');
  const [mode, setMode] = useState<'recognize' | 'register' | 'gallery'>('recognize');
  const [registerName, setRegisterName] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerEmployeeId, setRegisterEmployeeId] = useState('');
  const [registeredPeople, setRegisteredPeople] = useState<any[]>([]);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [uploadPreview, setUploadPreview] = useState<string | null>(null);
  const [isRealTime, setIsRealTime] = useState(false);
  const realTimeIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    checkBackendStatus();
    loadPeople();
  }, []);

  useEffect(() => {
    if (isRealTime && mode === 'recognize') {
      startRealTimeDetection();
    } else {
      stopRealTimeDetection();
    }
    return () => stopRealTimeDetection();
  }, [isRealTime, mode]);

  const checkBackendStatus = async () => {
    try {
      await api.healthCheck();
      setBackendStatus('online');
    } catch (err) {
      setBackendStatus('offline');
    }
  };

  const loadPeople = async () => {
    try {
      const people = await api.getPeople();
      setRegisteredPeople(people || []);
    } catch (err) {
      console.error('Error loading people:', err);
      setRegisteredPeople([]);
    }
  };

  const drawBoundingBoxes = useCallback((faces: DetectedFace[], videoElement: HTMLVideoElement) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size to match video
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw each face
    faces.forEach((face) => {
      const { bbox, recognized, person } = face;
      
      // Scale coordinates from detection resolution to video resolution
      const scaleX = videoElement.videoWidth / 640;
      const scaleY = videoElement.videoHeight / 480;
      
      const x = bbox.x * scaleX;
      const y = bbox.y * scaleY;
      const w = bbox.w * scaleX;
      const h = bbox.h * scaleY;

      // Set color based on recognition
      const color = recognized ? '#00ff00' : '#ff0000';
      
      // Draw rectangle
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, w, h);

      // Draw name label
      const label = person?.name || 'Unknown';
      const subLabel = person?.employee_id ? `ID: ${person.employee_id}` : '';
      
      // Background for text
      ctx.fillStyle = color;
      const labelHeight = subLabel ? 50 : 30;
      ctx.fillRect(x, y - labelHeight, w, labelHeight);

      // Draw text
      ctx.fillStyle = '#000';
      ctx.font = 'bold 16px Arial';
      ctx.fillText(label, x + 5, y - labelHeight + 20);
      
      if (subLabel) {
        ctx.font = '12px Arial';
        ctx.fillText(subLabel, x + 5, y - labelHeight + 40);
      }

      // Draw confidence if recognized
      if (recognized && person?.confidence) {
        ctx.font = '12px Arial';
        ctx.fillText(`${person.confidence.toFixed(1)}%`, x + w - 50, y - 10);
      }
    });
  }, []);

  const processFrame = useCallback(async () => {
    if (!webcamRef.current || isProcessing) return;

    const videoElement = webcamRef.current.video;
    if (!videoElement) return;

    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    setIsProcessing(true);
    try {
      const result = await api.detectAndRecognize(imageSrc);
      setDetectedFaces(result.faces);
      drawBoundingBoxes(result.faces, videoElement);
      setError('');
    } catch (err: any) {
      console.error('Detection error:', err);
      setError('Detection failed');
    } finally {
      setIsProcessing(false);
    }
  }, [isProcessing, drawBoundingBoxes]);

  const startRealTimeDetection = () => {
    stopRealTimeDetection();
    realTimeIntervalRef.current = setInterval(() => {
      processFrame();
    }, 1000); // Process every second
  };

  const stopRealTimeDetection = () => {
    if (realTimeIntervalRef.current) {
      clearInterval(realTimeIntervalRef.current);
      realTimeIntervalRef.current = null;
    }
  };

  const captureAndDetect = useCallback(async () => {
    if (!webcamRef.current) return;

    setIsProcessing(true);
    setError('');
    setDetectedFaces([]);

    try {
      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) {
        setError('Failed to capture image from webcam');
        return;
      }

      const result = await api.detectAndRecognize(imageSrc);
      setDetectedFaces(result.faces);
      
      const videoElement = webcamRef.current.video;
      if (videoElement) {
        drawBoundingBoxes(result.faces, videoElement);
      }
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Detection failed');
    } finally {
      setIsProcessing(false);
    }
  }, [drawBoundingBoxes]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setUploadPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const captureAndRegister = useCallback(async () => {
    if (!registerName.trim()) {
      setError('Please enter a name');
      return;
    }

    setIsProcessing(true);
    setError('');

    try {
      let imageSrc: string | null = null;

      // Use uploaded image if available, otherwise capture from webcam
      if (uploadedImage) {
        const reader = new FileReader();
        imageSrc = await new Promise<string>((resolve, reject) => {
          reader.onloadend = () => resolve(reader.result as string);
          reader.onerror = reject;
          reader.readAsDataURL(uploadedImage);
        });
      } else if (webcamRef.current) {
        imageSrc = webcamRef.current.getScreenshot();
      }

      if (!imageSrc) {
        setError('Failed to capture or upload image');
        return;
      }

      const response = await api.registerFace(registerName, imageSrc, registerEmail, registerEmployeeId);
      alert(`Successfully registered ${response.person.name}!`);
      setRegisterName('');
      setRegisterEmail('');
      setRegisterEmployeeId('');
      setUploadedImage(null);
      setUploadPreview(null);
      await loadPeople();
      setMode('gallery');
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Registration failed');
    } finally {
      setIsProcessing(false);
    }
  }, [registerName, registerEmail, registerEmployeeId, uploadedImage]);

  const deletePerson = async (personId: string) => {
    if (!confirm('Are you sure you want to delete this person?')) return;
    
    try {
      await api.deletePerson(personId);
      loadPeople();
    } catch (err: any) {
      alert('Failed to delete person');
    }
  };

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>🎭 Multi-Face Recognition System</h1>
        <div className={styles.statusBadge}>
          <span className={`${styles.statusDot} ${styles[backendStatus]}`}></span>
          Backend: {backendStatus}
        </div>
      </header>

      <div className={styles.mainContent}>
        <div className={styles.leftPanel}>
          <div className={styles.modeSelector}>
            <button
              className={`${styles.modeButton} ${mode === 'recognize' ? styles.active : ''}`}
              onClick={() => setMode('recognize')}
            >
              🔍 Recognize
            </button>
            <button
              className={`${styles.modeButton} ${mode === 'register' ? styles.active : ''}`}
              onClick={() => setMode('register')}
            >
              ➕ Register
            </button>
            <button
              className={`${styles.modeButton} ${mode === 'gallery' ? styles.active : ''}`}
              onClick={() => setMode('gallery')}
            >
              👥 Gallery
            </button>
          </div>

          {(mode === 'recognize' || mode === 'register') && (
            <div className={styles.videoContainer}>
              <div className={styles.webcamWrapper}>
                <Webcam
                  ref={webcamRef}
                  audio={false}
                  screenshotFormat="image/jpeg"
                  className={styles.webcam}
                  videoConstraints={{
                    width: 640,
                    height: 480,
                    facingMode: 'user',
                  }}
                />
                <canvas ref={canvasRef} className={styles.canvas} />
              </div>
            </div>
          )}

          {mode === 'recognize' && (
            <div className={styles.controls}>
              <div className={styles.toggleContainer}>
                <label className={styles.toggleLabel}>
                  <input
                    type="checkbox"
                    checked={isRealTime}
                    onChange={(e) => setIsRealTime(e.target.checked)}
                    className={styles.toggleCheckbox}
                  />
                  <span className={styles.toggleText}>
                    {isRealTime ? '🔴 Real-time ON' : '⚪ Real-time OFF'}
                  </span>
                </label>
              </div>
              
              {!isRealTime && (
                <button
                  onClick={captureAndDetect}
                  disabled={isProcessing || backendStatus !== 'online'}
                  className={styles.captureButton}
                >
                  {isProcessing ? '🔄 Detecting...' : '📸 Detect & Recognize'}
                </button>
              )}
              
              <div className={styles.stats}>
                <p>Detected Faces: <strong>{detectedFaces.length}</strong></p>
                <p>Recognized: <strong>{detectedFaces.filter(f => f.recognized).length}</strong></p>
                <p>Unknown: <strong>{detectedFaces.filter(f => !f.recognized).length}</strong></p>
              </div>
            </div>
          )}

          {mode === 'register' && (
            <div className={styles.registerForm}>
              <input
                type="text"
                placeholder="Full Name *"
                value={registerName}
                onChange={(e) => {
                  setRegisterName(e.target.value);
                  setError('');
                }}
                className={styles.input}
              />
              <input
                type="text"
                placeholder="Employee ID"
                value={registerEmployeeId}
                onChange={(e) => {
                  setRegisterEmployeeId(e.target.value);
                  setError('');
                }}
                className={styles.input}
              />
              <input
                type="email"
                placeholder="Email (optional)"
                value={registerEmail}
                onChange={(e) => {
                  setRegisterEmail(e.target.value);
                  setError('');
                }}
                className={styles.input}
              />
              
              <div className={styles.uploadSection}>
                <label className={styles.uploadLabel}>
                  📁 Or upload an image
                </label>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className={styles.fileInput}
                />
                {uploadPreview && (
                  <div className={styles.uploadPreview}>
                    <img src={uploadPreview} alt="Upload preview" />
                    <button
                      onClick={() => {
                        setUploadedImage(null);
                        setUploadPreview(null);
                        if (fileInputRef.current) fileInputRef.current.value = '';
                      }}
                      className={styles.clearUpload}
                    >
                      ✕ Clear
                    </button>
                  </div>
                )}
              </div>

              <button
                onClick={captureAndRegister}
                disabled={isProcessing || !registerName.trim() || backendStatus !== 'online'}
                className={styles.registerButton}
              >
                {isProcessing ? '🔄 Registering...' : uploadedImage ? '✅ Register with Upload' : '✅ Capture & Register'}
              </button>
            </div>
          )}

          {mode === 'gallery' && (
            <div className={styles.galleryView}>
              <div className={styles.galleryHeader}>
                <h2>📋 Registered Faces ({registeredPeople?.length || 0})</h2>
                <button onClick={loadPeople} className={styles.refreshButton}>
                  🔄 Refresh
                </button>
              </div>
              <div className={styles.galleryGrid}>
                {!registeredPeople || registeredPeople.length === 0 ? (
                  <p className={styles.emptyState}>No people registered yet</p>
                ) : (
                  registeredPeople.map((person) => (
                    <div key={person.id} className={styles.galleryCard}>
                      <div className={styles.galleryImage}>
                        <img 
                          src={api.getPersonImageUrl(person.id)} 
                          alt={person.name}
                          onError={(e) => {
                            (e.target as HTMLImageElement).src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect fill="%23ddd" width="200" height="200"/><text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="%23999" font-size="60">?</text></svg>';
                          }}
                        />
                      </div>
                      <div className={styles.galleryInfo}>
                        <h3>{person.name}</h3>
                        {person.employee_id && (
                          <p className={styles.employeeId}>ID: {person.employee_id}</p>
                        )}
                        {person.email && <p className={styles.email}>{person.email}</p>}
                        <p className={styles.date}>
                          Added: {new Date(person.added_date).toLocaleDateString()}
                        </p>
                        <button
                          onClick={() => deletePerson(person.id)}
                          className={styles.deleteButton}
                        >
                          🗑️ Delete
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {error && (
            <div className={styles.error}>
              ⚠️ {error}
            </div>
          )}
        </div>

        {mode === 'recognize' && detectedFaces.length > 0 && (
          <div className={styles.rightPanel}>
            <h2>Detected Faces</h2>
            <div className={styles.facesList}>
              {detectedFaces.map((face, index) => (
                <div 
                  key={index} 
                  className={`${styles.faceCard} ${face.recognized ? styles.recognized : styles.unknown}`}
                >
                  <div className={styles.faceCardHeader}>
                    {face.recognized ? '✅' : '❌'} Face #{index + 1}
                  </div>
                  <div className={styles.faceCardBody}>
                    <p><strong>Name:</strong> {face.person?.name || 'Unknown'}</p>
                    {face.person?.employee_id && (
                      <p><strong>ID:</strong> {face.person.employee_id}</p>
                    )}
                    {face.recognized && face.person?.confidence && (
                      <p><strong>Confidence:</strong> {face.person.confidence.toFixed(2)}%</p>
                    )}
                    <p><strong>Position:</strong> ({face.bbox.x}, {face.bbox.y})</p>
                    <p><strong>Size:</strong> {face.bbox.w}x{face.bbox.h}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
