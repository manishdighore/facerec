# Troubleshooting Guide

## Common Issues and Solutions

### Backend Issues

#### 1. Python not found
**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
- Install Python from https://www.python.org/downloads/
- During installation, check "Add Python to PATH"
- Restart your terminal after installation

#### 2. Virtual environment activation fails
**Error**: `cannot be loaded because running scripts is disabled`

**Solution**:
Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 3. TensorFlow/DeepFace installation fails
**Error**: Various TensorFlow-related errors

**Solutions**:
- Ensure you have Python 3.8-3.11 (3.12 may have compatibility issues)
- Try installing manually:
  ```bash
  pip install tensorflow
  pip install tf-keras
  pip install deepface
  ```
- On Windows, you may need Microsoft Visual C++ Redistributable

#### 4. OpenCV import error
**Error**: `ImportError: DLL load failed while importing cv2`

**Solution**:
```bash
pip uninstall opencv-python
pip install opencv-python==4.9.0.80
```

#### 5. Port 5000 already in use
**Error**: `Address already in use`

**Solution**:
- Find and kill the process using port 5000:
  ```powershell
  netstat -ano | findstr :5000
  taskkill /PID <PID> /F
  ```
- Or change the port in `backend/app.py`:
  ```python
  app.run(debug=True, host='0.0.0.0', port=5001)  # Change port
  ```

#### 6. Face detection fails
**Error**: Recognition not working, no faces detected

**Solutions**:
- Ensure good lighting
- Face should be clearly visible and not too small
- Try setting `enforce_detection=False` in `app.py` (already set)
- Adjust your distance from camera

#### 7. Recognition too strict/loose
**Issue**: Too many false positives or false negatives

**Solution**:
Adjust threshold in `backend/app.py` (line ~75):
```python
threshold = 0.6  # Default

# For stricter matching (fewer false positives):
threshold = 0.5

# For looser matching (more false positives):
threshold = 0.7
```

### Frontend Issues

#### 1. Node.js/npm not found
**Error**: `'node' is not recognized` or `'npm' is not recognized`

**Solution**:
- Install Node.js from https://nodejs.org/
- Choose LTS version
- Restart terminal after installation

#### 2. Port 3000 already in use
**Issue**: Another app using port 3000

**Solution**:
- Next.js will automatically offer to use port 3001
- Press 'y' to accept
- Update `.env.local` if you use a different backend port

#### 3. Webcam not accessible
**Error**: Webcam shows black screen or permission denied

**Solutions**:
- Grant browser permission to access camera
- Check if another app is using the camera (Zoom, Teams, etc.)
- Try a different browser (Chrome/Edge recommended)
- Check Windows camera privacy settings:
  - Settings → Privacy → Camera
  - Enable "Allow apps to access your camera"

#### 4. CORS errors
**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solutions**:
- Ensure backend is running
- Check that flask-cors is installed: `pip show flask-cors`
- Verify API URL in `.env.local` matches backend URL

#### 5. API connection fails
**Error**: `Network Error` or `Failed to fetch`

**Solutions**:
- Verify backend is running on http://localhost:5000
- Check backend console for errors
- Try accessing http://localhost:5000/api/health in browser
- Disable antivirus/firewall temporarily to test

#### 6. Images not capturing
**Issue**: getScreenshot returns null

**Solutions**:
- Wait a few seconds after page load for camera to initialize
- Ensure webcam is properly connected
- Try refreshing the page
- Check browser console for errors

### Database Issues

#### 1. people.json corrupted
**Error**: JSON parse error

**Solution**:
Replace `backend/database/people.json` with:
```json
[]
```

#### 2. Images not saving
**Error**: Permission denied or file not found

**Solutions**:
- Ensure `backend/database/faces/` folder exists
- Check write permissions on the folder
- Run backend as administrator if needed

#### 3. Cannot delete person
**Error**: Permission error when deleting

**Solution**:
- Close any programs that might be accessing the images
- Ensure no other process is using the files
- Check folder permissions

### Performance Issues

#### 1. Slow recognition
**Issue**: Takes too long to recognize faces

**Solutions**:
- First request is slow (model loading) - this is normal
- For faster recognition, try different models:
  ```python
  model_name='Facenet'  # Faster than VGG-Face
  model_name='Facenet512'  # Good balance
  ```
- Reduce image quality in webcam settings
- Limit number of people in database

#### 2. High memory usage
**Issue**: Backend consuming too much RAM

**Solutions**:
- Models are loaded once and cached
- Consider using lighter models
- Restart backend periodically if needed

### Browser Compatibility

#### Recommended Browsers
- ✅ Google Chrome (best)
- ✅ Microsoft Edge (best)
- ⚠️ Firefox (may have webcam issues)
- ❌ Safari (WebRTC limitations)
- ❌ Internet Explorer (not supported)

### Model-Specific Issues

#### 1. Wrong person identified
**Issue**: System identifies wrong person

**Solutions**:
- Add more images per person (modify backend to support multiple images)
- Adjust threshold (lower = stricter)
- Ensure good quality reference images
- Try different models (VGG-Face, Facenet, etc.)

#### 2. Same person not identified
**Issue**: System doesn't recognize registered person

**Solutions**:
- Check lighting conditions (should be similar to registration)
- Face angle should be similar
- Remove glasses if worn during registration
- Register multiple angles/conditions
- Increase threshold (but watch for false positives)

## Getting Help

### Check Logs

**Backend logs**: Check the terminal running `python app.py`
- Look for error traces
- Note any warnings

**Frontend logs**: Open browser Developer Tools (F12)
- Check Console tab for errors
- Check Network tab for failed requests

### Debug Mode

Backend is already in debug mode. For more verbose output, add:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Backend Separately

Test backend API with curl or Postman:
```bash
# Health check
curl http://localhost:5000/api/health

# Get people
curl http://localhost:5000/api/people
```

### Reset Everything

If all else fails:
```bash
# Delete virtual environment
rmdir /s backend\venv

# Delete node_modules
rmdir /s frontend\node_modules

# Delete database
del backend\database\people.json
echo [] > backend\database\people.json

# Re-run setup
setup.bat
```

## Still Having Issues?

1. Check Python version: `python --version` (should be 3.8-3.11)
2. Check Node version: `node --version` (should be 18+)
3. Ensure all dependencies installed correctly
4. Check antivirus/firewall settings
5. Try running as administrator
6. Check system requirements:
   - Windows 10/11
   - 4GB RAM minimum (8GB recommended)
   - Webcam (internal or external)
   - Modern browser

## Useful Commands

```powershell
# Check Python packages
pip list

# Update pip
python -m pip install --upgrade pip

# Reinstall specific package
pip uninstall deepface
pip install deepface

# Check Node packages
npm list

# Clear npm cache
npm cache clean --force

# Reinstall frontend dependencies
rmdir /s node_modules
npm install

# Check ports in use
netstat -ano | findstr :5000
netstat -ano | findstr :3000
```
