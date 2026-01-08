'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import { api, DetectedFace, DetectionResult } from '@/lib/api';
import styles from './page.module.css';

export default function Home() {
  const webcamRef = useRef<Webcam>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const videoCanvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [detectedFaces, setDetectedFaces] = useState<DetectedFace[]>([]);
  const [videoDetectedFaces, setVideoDetectedFaces] = useState<DetectedFace[]>([]);
  const [error, setError] = useState<string>('');
  const [mode, setMode] = useState<'recognize' | 'register' | 'gallery' | 'video'>('recognize');
  const [registerName, setRegisterName] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerEmployeeId, setRegisterEmployeeId] = useState('');
  const [registeredPeople, setRegisteredPeople] = useState<any[]>([]);
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [uploadPreview, setUploadPreview] = useState<string | null>(null);
  const [isRealTime, setIsRealTime] = useState(false);
  const realTimeIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const [detectionInterval, setDetectionInterval] = useState(50); // Default 50ms = 20fps
  
  // Detection region (draggable box)
  const [detectionRegion, setDetectionRegion] = useState({ x: 50, y: 50, width: 400, height: 300 });
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [enableRegionFilter, setEnableRegionFilter] = useState(false);
  
  // Video processing state
  const [uploadedVideo, setUploadedVideo] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const [isVideoProcessing, setIsVideoProcessing] = useState(false);
  const videoProcessingRef = useRef<boolean>(false);

  useEffect(() => {
    checkBackendStatus();
    loadPeople();
  }, []);

  // Clear canvas function
  const clearCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Reset canvas size to force a full clear
    canvas.width = canvas.width;
  }, []);

  // Clear canvas and faces when mode changes away from recognize
  useEffect(() => {
    if (mode !== 'recognize') {
      clearCanvas();
      setDetectedFaces([]);
    }
  }, [mode, clearCanvas]);

  useEffect(() => {
    if (isRealTime && mode === 'recognize') {
      startRealTimeDetection();
    } else {
      stopRealTimeDetection();
      clearCanvas();
      setDetectedFaces([]);
    }
    return () => stopRealTimeDetection();
  }, [isRealTime, mode]);

  // Draw detection region overlay when enabled (even without face detection)
  useEffect(() => {
    if (!enableRegionFilter) return;
    
    let animationFrameId: number;
    
    const drawRegionOnly = () => {
      const canvas = mode === 'recognize' ? canvasRef.current : 
                     mode === 'video' ? videoCanvasRef.current : null;
      if (!canvas) return;
      
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      
      const videoElement = mode === 'recognize' ? webcamRef.current?.video : 
                          mode === 'video' ? videoRef.current : null;
      if (!videoElement) return;
      
      const videoRect = videoElement.getBoundingClientRect();
      if (canvas.width !== videoRect.width || canvas.height !== videoRect.height) {
        canvas.width = videoRect.width;
        canvas.height = videoRect.height;
      }
      
      // Only draw if we're not actively processing (to avoid flicker)
      // The region will be drawn by drawBoundingBoxes during detection
      if (!isProcessing && !isRealTime && !isVideoProcessing) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw detection region
        ctx.strokeStyle = '#00ffff';
        ctx.lineWidth = 3;
        ctx.setLineDash([10, 5]);
        ctx.strokeRect(detectionRegion.x, detectionRegion.y, detectionRegion.width, detectionRegion.height);
        ctx.setLineDash([]);
        
        // Draw 4 corner resize handles
        const handleSize = 12;
        ctx.fillStyle = '#00ffff';
        ctx.fillRect(detectionRegion.x - handleSize/2, detectionRegion.y - handleSize/2, handleSize, handleSize);
        ctx.fillRect(detectionRegion.x + detectionRegion.width - handleSize/2, detectionRegion.y - handleSize/2, handleSize, handleSize);
        ctx.fillRect(detectionRegion.x - handleSize/2, detectionRegion.y + detectionRegion.height - handleSize/2, handleSize, handleSize);
        ctx.fillRect(detectionRegion.x + detectionRegion.width - handleSize/2, detectionRegion.y + detectionRegion.height - handleSize/2, handleSize, handleSize);
        
        // Draw label
        ctx.fillStyle = 'rgba(0, 255, 255, 0.3)';
        ctx.fillRect(detectionRegion.x, detectionRegion.y - 25, 150, 25);
        ctx.fillStyle = '#00ffff';
        ctx.font = 'bold 14px Arial';
        ctx.fillText('Detection Region', detectionRegion.x + 5, detectionRegion.y - 8);
      }
      
      animationFrameId = requestAnimationFrame(drawRegionOnly);
    };
    
    drawRegionOnly();
    
    return () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, [enableRegionFilter, detectionRegion, mode, isProcessing, isRealTime, isVideoProcessing]);

  // Detection region is now drawn directly in drawBoundingBoxes, no separate effect needed

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

  const drawBoundingBoxes = useCallback((
    faces: DetectedFace[], 
    videoElement: HTMLVideoElement,
    imageWidth?: number,
    imageHeight?: number
  ) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Get the actual displayed size of the video element using getBoundingClientRect
    const videoRect = videoElement.getBoundingClientRect();
    const displayWidth = videoRect.width;
    const displayHeight = videoRect.height;
    
    // Set canvas internal resolution to match display size
    canvas.width = displayWidth;
    canvas.height = displayHeight;
    
    // The image sent to backend has dimensions imageWidth x imageHeight
    // We need to scale coordinates from image space to display space
    const srcWidth = imageWidth || videoElement.videoWidth;
    const srcHeight = imageHeight || videoElement.videoHeight;
    
    const scaleX = displayWidth / srcWidth;
    const scaleY = displayHeight / srcHeight;
    
    // Debug logging
    if (faces.length > 0) {
      console.log(`Source: ${srcWidth}x${srcHeight}, Display: ${displayWidth.toFixed(0)}x${displayHeight.toFixed(0)}, Scale: ${scaleX.toFixed(3)}x${scaleY.toFixed(3)}`);
      const bbox = faces[0].bbox;
      const scaledX = bbox.x * scaleX;
      const scaledY = bbox.y * scaleY;
      console.log(`Original bbox: x=${bbox.x}, y=${bbox.y} -> Scaled: x=${scaledX.toFixed(0)}, y=${scaledY.toFixed(0)}`);
    }

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw each face
    faces.forEach((face) => {
      const { bbox, recognized, person } = face;
      
      // Scale coordinates from image space to display space
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
      const label = person?.name || (face.unknown_id || 'Unknown');
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
    
    // Draw detection region AFTER faces so it stays on top
    if (enableRegionFilter) {
      ctx.strokeStyle = '#00ffff';
      ctx.lineWidth = 3;
      ctx.setLineDash([10, 5]);
      ctx.strokeRect(detectionRegion.x, detectionRegion.y, detectionRegion.width, detectionRegion.height);
      ctx.setLineDash([]);
      
      // Draw 4 corner resize handles
      const handleSize = 12;
      ctx.fillStyle = '#00ffff';
      // Top-left
      ctx.fillRect(detectionRegion.x - handleSize/2, detectionRegion.y - handleSize/2, handleSize, handleSize);
      // Top-right
      ctx.fillRect(detectionRegion.x + detectionRegion.width - handleSize/2, detectionRegion.y - handleSize/2, handleSize, handleSize);
      // Bottom-left
      ctx.fillRect(detectionRegion.x - handleSize/2, detectionRegion.y + detectionRegion.height - handleSize/2, handleSize, handleSize);
      // Bottom-right
      ctx.fillRect(detectionRegion.x + detectionRegion.width - handleSize/2, detectionRegion.y + detectionRegion.height - handleSize/2, handleSize, handleSize);
      
      // Draw label
      ctx.fillStyle = 'rgba(0, 255, 255, 0.3)';
      ctx.fillRect(detectionRegion.x, detectionRegion.y - 25, 150, 25);
      ctx.fillStyle = '#00ffff';
      ctx.font = 'bold 14px Arial';
      ctx.fillText('Detection Region', detectionRegion.x + 5, detectionRegion.y - 8);
    }
  }, [enableRegionFilter, detectionRegion]);

  const processFrame = useCallback(async () => {
    if (!webcamRef.current) return;

    const videoElement = webcamRef.current.video;
    if (!videoElement) return;

    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    // Get display dimensions
    const videoRect = videoElement.getBoundingClientRect();
    const displayWidth = videoRect.width;
    const displayHeight = videoRect.height;
    const srcWidth = videoElement.videoWidth;
    const srcHeight = videoElement.videoHeight;

    setIsProcessing(true);
    const requestStart = performance.now();
    try {
      // Always send full image to backend
      const result = await api.detectAndRecognize(imageSrc);
      const requestEnd = performance.now();
      const roundTrip = requestEnd - requestStart;
      
      if (result.latency) {
        console.log(`[LATENCY] Round-trip: ${roundTrip.toFixed(2)}ms | Backend: ${result.latency.total_ms}ms (detect: ${result.latency.detection_ms}ms, recognize: ${result.latency.recognition_ms}ms) | Network: ${(roundTrip - result.latency.total_ms).toFixed(2)}ms`);
      }
      
      // Filter faces client-side if region filter is enabled
      let filteredFaces = result.faces;
      if (enableRegionFilter) {
        const regionInSrc = {
          x: Math.round(detectionRegion.x / displayWidth * srcWidth),
          y: Math.round(detectionRegion.y / displayHeight * srcHeight),
          width: Math.round(detectionRegion.width / displayWidth * srcWidth),
          height: Math.round(detectionRegion.height / displayHeight * srcHeight)
        };
        
        console.log('[FILTER] Region in source coords:', regionInSrc);
        console.log('[FILTER] Total faces detected:', result.faces.length);
        
        filteredFaces = result.faces.filter(face => {
          const faceCenter = {
            x: face.bbox.x + face.bbox.w / 2,
            y: face.bbox.y + face.bbox.h / 2
          };
          const inside = faceCenter.x >= regionInSrc.x &&
                 faceCenter.x <= regionInSrc.x + regionInSrc.width &&
                 faceCenter.y >= regionInSrc.y &&
                 faceCenter.y <= regionInSrc.y + regionInSrc.height;
          console.log(`[FILTER] Face at (${faceCenter.x}, ${faceCenter.y}): ${inside ? 'INSIDE' : 'OUTSIDE'}`);
          return inside;
        });
        
        console.log('[FILTER] Faces after filtering:', filteredFaces.length);
      }
      
      // Normalize tracking_id to trackingId
      const normalizedFaces = filteredFaces.map(face => ({
        ...face,
        trackingId: face.tracking_id || face.trackingId
      }));
      
      setDetectedFaces(normalizedFaces);
      drawBoundingBoxes(normalizedFaces, videoElement, result.image_width, result.image_height);
      setError('');
    } catch (err: any) {
      console.error('Detection error:', err);
      setError('Detection failed');
    } finally {
      setIsProcessing(false);
    }
  }, [isProcessing, drawBoundingBoxes, enableRegionFilter, detectionRegion]);

  const startRealTimeDetection = () => {
    stopRealTimeDetection();
    realTimeIntervalRef.current = setInterval(() => {
      processFrame();
    }, detectionInterval);
  };

  const stopRealTimeDetection = () => {
    if (realTimeIntervalRef.current) {
      clearInterval(realTimeIntervalRef.current);
      realTimeIntervalRef.current = null;
    }
  };

  // Restart real-time detection when interval changes
  useEffect(() => {
    if (isRealTime) {
      startRealTimeDetection();
    }
  }, [detectionInterval]);

  // Mouse handlers for detection region
  const [resizeCorner, setResizeCorner] = useState<string>('');

  const handleCanvasMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!enableRegionFilter) return;
    
    const canvas = e.currentTarget;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const handleSize = 15;
    const region = detectionRegion;
    
    // Check if clicking on any corner resize handles
    const onTopLeft = x >= region.x - handleSize/2 && x <= region.x + handleSize/2 &&
                      y >= region.y - handleSize/2 && y <= region.y + handleSize/2;
    const onTopRight = x >= region.x + region.width - handleSize/2 && x <= region.x + region.width + handleSize/2 &&
                       y >= region.y - handleSize/2 && y <= region.y + handleSize/2;
    const onBottomLeft = x >= region.x - handleSize/2 && x <= region.x + handleSize/2 &&
                         y >= region.y + region.height - handleSize/2 && y <= region.y + region.height + handleSize/2;
    const onBottomRight = x >= region.x + region.width - handleSize/2 && x <= region.x + region.width + handleSize/2 &&
                          y >= region.y + region.height - handleSize/2 && y <= region.y + region.height + handleSize/2;
    
    if (onTopLeft) {
      setIsResizing(true);
      setResizeCorner('topLeft');
      setDragStart({ x, y });
    } else if (onTopRight) {
      setIsResizing(true);
      setResizeCorner('topRight');
      setDragStart({ x, y });
    } else if (onBottomLeft) {
      setIsResizing(true);
      setResizeCorner('bottomLeft');
      setDragStart({ x, y });
    } else if (onBottomRight) {
      setIsResizing(true);
      setResizeCorner('bottomRight');
      setDragStart({ x, y });
    } else if (x >= region.x && x <= region.x + region.width &&
               y >= region.y && y <= region.y + region.height) {
      setIsDragging(true);
      setDragStart({ x: x - region.x, y: y - region.y });
    }
  };

  const handleCanvasMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!enableRegionFilter) return;
    
    const canvas = e.currentTarget;
    if (!canvas) return;
    
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    if (isDragging) {
      const newX = Math.max(0, Math.min(x - dragStart.x, canvas.width - detectionRegion.width));
      const newY = Math.max(0, Math.min(y - dragStart.y, canvas.height - detectionRegion.height));
      setDetectionRegion(prev => ({
        ...prev,
        x: newX,
        y: newY
      }));
    } else if (isResizing) {
      const minSize = 50;
      
      if (resizeCorner === 'topLeft') {
        const deltaX = x - dragStart.x;
        const deltaY = y - dragStart.y;
        setDetectionRegion(prev => ({
          x: Math.max(0, prev.x + deltaX),
          y: Math.max(0, prev.y + deltaY),
          width: Math.max(minSize, prev.width - deltaX),
          height: Math.max(minSize, prev.height - deltaY)
        }));
        setDragStart({ x, y });
      } else if (resizeCorner === 'topRight') {
        const deltaY = y - dragStart.y;
        setDetectionRegion(prev => ({
          ...prev,
          y: Math.max(0, prev.y + deltaY),
          width: Math.max(minSize, x - prev.x),
          height: Math.max(minSize, prev.height - deltaY)
        }));
        setDragStart({ x, y });
      } else if (resizeCorner === 'bottomLeft') {
        const deltaX = x - dragStart.x;
        setDetectionRegion(prev => ({
          ...prev,
          x: Math.max(0, prev.x + deltaX),
          width: Math.max(minSize, prev.width - deltaX),
          height: Math.max(minSize, y - prev.y)
        }));
        setDragStart({ x, y });
      } else if (resizeCorner === 'bottomRight') {
        setDetectionRegion(prev => ({
          ...prev,
          width: Math.max(minSize, x - prev.x),
          height: Math.max(minSize, y - prev.y)
        }));
      }
    }
  };

  const handleCanvasMouseUp = () => {
    setIsDragging(false);
    setIsResizing(false);
    setResizeCorner('');
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
        drawBoundingBoxes(result.faces, videoElement, result.image_width, result.image_height);
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

  // Video processing functions
  const handleVideoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedVideo(file);
      const url = URL.createObjectURL(file);
      setVideoUrl(url);
      setDetectedFaces([]);
      setIsVideoPlaying(false);
      videoProcessingRef.current = false;
    }
  };

  const clearVideo = () => {
    if (videoUrl) {
      URL.revokeObjectURL(videoUrl);
    }
    setUploadedVideo(null);
    setVideoUrl(null);
    setDetectedFaces([]);
    setIsVideoPlaying(false);
    setIsVideoProcessing(false);
    videoProcessingRef.current = false;
    if (videoInputRef.current) {
      videoInputRef.current.value = '';
    }
  };

  const processVideoFrame = useCallback(async () => {
    if (!videoRef.current || !videoProcessingRef.current) return;
    
    const video = videoRef.current;
    if (video.paused || video.ended) {
      videoProcessingRef.current = false;
      setIsVideoProcessing(false);
      return;
    }

    // Create a canvas to capture the current frame
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = video.videoWidth;
    tempCanvas.height = video.videoHeight;
    const tempCtx = tempCanvas.getContext('2d');
    if (!tempCtx) return;

    tempCtx.drawImage(video, 0, 0);
    const frameData = tempCanvas.toDataURL('image/jpeg', 0.8);

    try {
      // Always send full image to backend
      const videoRect = video.getBoundingClientRect();
      const displayWidth = videoRect.width;
      const displayHeight = videoRect.height;
      const srcWidth = video.videoWidth;
      const srcHeight = video.videoHeight;
      
      const result = await api.detectAndRecognize(frameData);
      
      // Filter faces client-side if region filter is enabled
      let filteredFaces = result.faces;
      if (enableRegionFilter) {
        const regionInSrc = {
          x: Math.round(detectionRegion.x / displayWidth * srcWidth),
          y: Math.round(detectionRegion.y / displayHeight * srcHeight),
          width: Math.round(detectionRegion.width / displayWidth * srcWidth),
          height: Math.round(detectionRegion.height / displayHeight * srcHeight)
        };
        
        filteredFaces = result.faces.filter(face => {
          const faceCenter = {
            x: face.bbox.x + face.bbox.w / 2,
            y: face.bbox.y + face.bbox.h / 2
          };
          return faceCenter.x >= regionInSrc.x &&
                 faceCenter.x <= regionInSrc.x + regionInSrc.width &&
                 faceCenter.y >= regionInSrc.y &&
                 faceCenter.y <= regionInSrc.y + regionInSrc.height;
        });
      }
      
      // Normalize tracking_id to trackingId
      const normalizedFaces = filteredFaces.map(face => ({
        ...face,
        trackingId: face.tracking_id || face.trackingId
      }));
      
      setVideoDetectedFaces(normalizedFaces);
      
      // Draw bounding boxes on video canvas
      const canvas = videoCanvasRef.current;
      if (canvas) {
        const ctx = canvas.getContext('2d');
        if (ctx) {
          const videoRect = video.getBoundingClientRect();
          canvas.width = videoRect.width;
          canvas.height = videoRect.height;
          
          const scaleX = videoRect.width / video.videoWidth;
          const scaleY = videoRect.height / video.videoHeight;
          
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          
          normalizedFaces.forEach((face) => {
            const { bbox, recognized, person, unknown_id } = face;
            const x = bbox.x * scaleX;
            const y = bbox.y * scaleY;
            const w = bbox.w * scaleX;
            const h = bbox.h * scaleY;

            const color = recognized ? '#00ff00' : '#ff0000';
            ctx.strokeStyle = color;
            ctx.lineWidth = 3;
            ctx.strokeRect(x, y, w, h);

            const label = person?.name || (unknown_id || 'Unknown');
            ctx.fillStyle = color;
            ctx.fillRect(x, y - 25, w, 25);
            ctx.fillStyle = '#000';
            ctx.font = 'bold 14px Arial';
            ctx.fillText(label, x + 5, y - 8);
          });
          
          // Draw detection region on video if enabled
          if (enableRegionFilter) {
            ctx.strokeStyle = '#00ffff';
            ctx.lineWidth = 3;
            ctx.setLineDash([10, 5]);
            ctx.strokeRect(detectionRegion.x, detectionRegion.y, detectionRegion.width, detectionRegion.height);
            ctx.setLineDash([]);
            
            // Draw 4 corner resize handles
            const handleSize = 12;
            ctx.fillStyle = '#00ffff';
            // Top-left
            ctx.fillRect(detectionRegion.x - handleSize/2, detectionRegion.y - handleSize/2, handleSize, handleSize);
            // Top-right
            ctx.fillRect(detectionRegion.x + detectionRegion.width - handleSize/2, detectionRegion.y - handleSize/2, handleSize, handleSize);
            // Bottom-left
            ctx.fillRect(detectionRegion.x - handleSize/2, detectionRegion.y + detectionRegion.height - handleSize/2, handleSize, handleSize);
            // Bottom-right
            ctx.fillRect(detectionRegion.x + detectionRegion.width - handleSize/2, detectionRegion.y + detectionRegion.height - handleSize/2, handleSize, handleSize);
            
            // Draw label
            ctx.fillStyle = 'rgba(0, 255, 255, 0.3)';
            ctx.fillRect(detectionRegion.x, detectionRegion.y - 25, 150, 25);
            ctx.fillStyle = '#00ffff';
            ctx.font = 'bold 14px Arial';
            ctx.fillText('Detection Region', detectionRegion.x + 5, detectionRegion.y - 8);
          }
        }
      }
    } catch (err) {
      console.error('Video frame processing error:', err);
    }

    // Continue processing if video is still playing
    if (videoProcessingRef.current && !video.paused && !video.ended) {
      setTimeout(processVideoFrame, 100); // Process at ~10fps
    }
  }, [enableRegionFilter, detectionRegion]);

  const toggleVideoProcessing = () => {
    if (!videoRef.current) return;

    if (isVideoProcessing) {
      // Stop processing
      videoProcessingRef.current = false;
      setIsVideoProcessing(false);
      videoRef.current.pause();
      setIsVideoPlaying(false);
    } else {
      // Start processing
      videoProcessingRef.current = true;
      setIsVideoProcessing(true);
      videoRef.current.play();
      setIsVideoPlaying(true);
      processVideoFrame();
    }
  };

  const handleVideoPlay = () => {
    setIsVideoPlaying(true);
    if (!isVideoProcessing) {
      videoProcessingRef.current = true;
      setIsVideoProcessing(true);
      processVideoFrame();
    }
  };

  const handleVideoPause = () => {
    setIsVideoPlaying(false);
  };

  const handleVideoEnded = () => {
    setIsVideoPlaying(false);
    videoProcessingRef.current = false;
    setIsVideoProcessing(false);
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
              className={`${styles.modeButton} ${mode === 'video' ? styles.active : ''}`}
              onClick={() => setMode('video')}
            >
              🎬 Video
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
                  mirrored={true}
                  className={styles.webcam}
                  videoConstraints={{
                    width: 640,
                    height: 480,
                    facingMode: 'user',
                  }}
                />
                {mode === 'recognize' && (
                  <canvas 
                    ref={canvasRef} 
                    className={styles.canvas}
                    onMouseDown={handleCanvasMouseDown}
                    onMouseMove={handleCanvasMouseMove}
                    onMouseUp={handleCanvasMouseUp}
                    onMouseLeave={handleCanvasMouseUp}
                    style={{ 
                      cursor: isDragging || isResizing ? 'grabbing' : (enableRegionFilter ? 'pointer' : 'default'),
                      pointerEvents: enableRegionFilter ? 'auto' : 'none'
                    }}
                  />
                )}
              </div>
            </div>
          )}

          {mode === 'recognize' && (
            <div className={styles.controls}>
              <div className={styles.toggleContainer}>
                <label className={styles.toggleLabel}>
                  <input
                    type="checkbox"
                    checked={enableRegionFilter}
                    onChange={(e) => setEnableRegionFilter(e.target.checked)}
                  />
                  Enable Detection Region
                </label>
              </div>
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
              
              {isRealTime && (
                <div className={styles.sliderContainer}>
                  <label className={styles.sliderLabel}>
                    Detection Speed: {(1000/detectionInterval).toFixed(0)} FPS ({detectionInterval}ms)
                  </label>
                  <input
                    type="range"
                    min="30"
                    max="200"
                    step="10"
                    value={detectionInterval}
                    onChange={(e) => setDetectionInterval(Number(e.target.value))}
                    className={styles.slider}
                  />
                  <div className={styles.sliderLabels}>
                    <span>Fast (33 FPS)</span>
                    <span>Slow (5 FPS)</span>
                  </div>
                </div>
              )}
              
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
                <div className={styles.statItem}>
                  <span className={styles.statNumber}>{detectedFaces.length}</span>
                  <span className={styles.statLabel}>Total Faces</span>
                </div>
                <div className={styles.statItem + ' ' + styles.statKnown}>
                  <span className={styles.statNumber}>{detectedFaces.filter(f => f.recognized).length}</span>
                  <span className={styles.statLabel}>Known</span>
                </div>
                <div className={styles.statItem + ' ' + styles.statUnknown}>
                  <span className={styles.statNumber}>{detectedFaces.filter(f => !f.recognized).length}</span>
                  <span className={styles.statLabel}>Unknown</span>
                </div>
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
                <label htmlFor="registerImageUpload" className={styles.uploadLabel}>
                  📁 Or upload an image
                </label>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  className={styles.fileInput}
                  id="registerImageUpload"
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

          {mode === 'video' && (
            <div className={styles.videoMode}>
              <h2>🎬 Video Face Recognition</h2>
              <p className={styles.videoDescription}>
                Upload a video file to detect and recognize faces in real-time playback.
              </p>
              
              {!videoUrl ? (
                <div className={styles.uploadSection}>
                  <input
                    ref={videoInputRef}
                    type="file"
                    accept="video/*"
                    onChange={handleVideoUpload}
                    className={styles.fileInput}
                    id="videoUpload"
                  />
                  <label htmlFor="videoUpload" className={styles.uploadLabel}>
                    📁 Choose Video File
                  </label>
                  <p className={styles.uploadHint}>Supports MP4, WebM, MOV, AVI</p>
                </div>
              ) : (
                <>
                  <div className={styles.videoWrapper}>
                    <video
                      ref={videoRef}
                      src={videoUrl}
                      className={styles.videoPlayer}
                      onPlay={handleVideoPlay}
                      onPause={handleVideoPause}
                      onEnded={handleVideoEnded}
                      controls
                    />
                    <canvas ref={videoCanvasRef} className={styles.videoCanvas}
                      onMouseDown={handleCanvasMouseDown}
                      onMouseMove={handleCanvasMouseMove}
                      onMouseUp={handleCanvasMouseUp}
                      onMouseLeave={handleCanvasMouseUp}
                      style={{ 
                        cursor: isDragging || isResizing ? 'grabbing' : (enableRegionFilter ? 'pointer' : 'default'),
                        pointerEvents: enableRegionFilter ? 'auto' : 'none'
                      }}
                    />
                  </div>
                  
                  <div className={styles.videoControls}>
                    <div className={styles.toggleContainer}>
                      <label className={styles.toggleLabel}>
                        <input
                          type="checkbox"
                          checked={enableRegionFilter}
                          onChange={(e) => setEnableRegionFilter(e.target.checked)}
                        />
                        Enable Detection Region
                      </label>
                    </div>
                    <button
                      onClick={toggleVideoProcessing}
                      className={`${styles.processButton} ${isVideoProcessing ? styles.processing : ''}`}
                    >
                      {isVideoProcessing ? '⏹️ Stop Processing' : '▶️ Start Processing'}
                    </button>
                    <button onClick={clearVideo} className={styles.clearButton}>
                      🗑️ Clear Video
                    </button>
                  </div>

                  <div className={styles.stats}>
                    <div className={styles.statItem}>
                      <span className={styles.statNumber}>{detectedFaces.length}</span>
                      <span className={styles.statLabel}>Total Faces</span>
                    </div>
                    <div className={styles.statItem + ' ' + styles.statKnown}>
                      <span className={styles.statNumber}>{detectedFaces.filter(f => f.recognized).length}</span>
                      <span className={styles.statLabel}>Known</span>
                    </div>
                    <div className={styles.statItem + ' ' + styles.statUnknown}>
                      <span className={styles.statNumber}>{detectedFaces.filter(f => !f.recognized).length}</span>
                      <span className={styles.statLabel}>Unknown</span>
                    </div>
                  </div>
                </>
              )}
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

        {(mode === 'recognize' || mode === 'video') && (
          <div className={styles.rightPanel}>
            <h2>Detected Faces</h2>
            <div className={styles.facesList}>
              {(mode === 'recognize' ? detectedFaces : videoDetectedFaces).length === 0 ? (
                <div className={styles.emptyState}>No faces detected yet</div>
              ) : (
                (mode === 'recognize' ? detectedFaces : videoDetectedFaces)
                  .sort((a, b) => (a.trackingId || 0) - (b.trackingId || 0))
                  .map((face, index) => (
                <div 
                  key={face.trackingId || index} 
                  className={`${styles.faceCard} ${face.recognized ? styles.recognized : styles.unknown}`}
                >
                  <div className={styles.faceCardHeader}>
                    {face.recognized ? '✅' : '❌'} Face #{face.trackingId || (index + 1)}
                  </div>
                  <div className={styles.faceCardBody}>
                    <p><strong>Name:</strong> {face.person?.name || face.unknown_id || 'Unknown'}</p>
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
              ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
