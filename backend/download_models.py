"""
Model Downloader for InsightFace Models

Downloads SCRFD and ArcFace models from InsightFace model zoo.
Models are from the buffalo_l model pack.
"""

import os
import urllib.request
import zipfile
import shutil
from pathlib import Path

# Model URLs - Using InsightFace's official model hosting
# These are from the buffalo_l model pack
MODELS = {
    'det_10g.onnx': {
        'url': 'https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip',
        'source_path': 'buffalo_l/det_10g.onnx',
        'size_mb': 16,
        'description': 'SCRFD face detector with landmarks'
    },
    'w600k_r50.onnx': {
        'url': 'https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip',
        'source_path': 'buffalo_l/w600k_r50.onnx',
        'size_mb': 166,
        'description': 'ArcFace face recognition model'
    }
}

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
BUFFALO_ZIP_URL = 'https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip'


def download_file(url: str, dest_path: str, description: str = "file") -> bool:
    """Download a file with progress indication."""
    try:
        print(f"⬇ Downloading {description}...")
        print(f"  URL: {url}")
        print(f"  Destination: {dest_path}")
        
        # Create a custom opener with headers to avoid 403 errors
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        
        # Download with progress
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, downloaded * 100 / total_size)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\r  Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='', flush=True)
        
        urllib.request.urlretrieve(url, dest_path, progress_hook)
        print()  # New line after progress
        return True
    except Exception as e:
        print(f"\n✗ Failed to download: {e}")
        return False


def extract_models_from_zip(zip_path: str, models_dir: str) -> bool:
    """Extract required model files from the buffalo_l zip."""
    try:
        print(f"📦 Extracting models from {zip_path}...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # List files in zip
            file_list = zip_ref.namelist()
            
            # Extract det_10g.onnx
            det_source = 'buffalo_l/det_10g.onnx'
            if det_source in file_list:
                print(f"  Extracting {det_source}...")
                zip_ref.extract(det_source, models_dir)
                # Move to correct location
                src = os.path.join(models_dir, det_source)
                dst = os.path.join(models_dir, 'det_10g.onnx')
                if os.path.exists(src):
                    shutil.move(src, dst)
                    print(f"  ✓ det_10g.onnx extracted")
            
            # Extract w600k_r50.onnx
            rec_source = 'buffalo_l/w600k_r50.onnx'
            if rec_source in file_list:
                print(f"  Extracting {rec_source}...")
                zip_ref.extract(rec_source, models_dir)
                # Move to correct location
                src = os.path.join(models_dir, rec_source)
                dst = os.path.join(models_dir, 'w600k_r50.onnx')
                if os.path.exists(src):
                    shutil.move(src, dst)
                    print(f"  ✓ w600k_r50.onnx extracted")
        
        # Clean up buffalo_l folder
        buffalo_dir = os.path.join(models_dir, 'buffalo_l')
        if os.path.exists(buffalo_dir):
            shutil.rmtree(buffalo_dir)
        
        return True
    except Exception as e:
        print(f"✗ Failed to extract models: {e}")
        return False


def check_and_download_models(models_dir: str = None) -> dict:
    """
    Check if models exist and download if missing.
    
    Returns:
        dict with 'scrfd' and 'arcface' keys indicating success/failure
    """
    if models_dir is None:
        models_dir = MODELS_DIR
    
    os.makedirs(models_dir, exist_ok=True)
    
    scrfd_path = os.path.join(models_dir, 'det_10g.onnx')
    arcface_path = os.path.join(models_dir, 'w600k_r50.onnx')
    
    result = {
        'scrfd': os.path.exists(scrfd_path),
        'arcface': os.path.exists(arcface_path)
    }
    
    # Check if models already exist
    if result['scrfd'] and result['arcface']:
        print("✓ All models already present")
        return result
    
    # Need to download
    missing = []
    if not result['scrfd']:
        missing.append('SCRFD (det_10g.onnx)')
    if not result['arcface']:
        missing.append('ArcFace (w600k_r50.onnx)')
    
    print(f"\n{'='*60}")
    print("Missing models detected:")
    for m in missing:
        print(f"  - {m}")
    print(f"{'='*60}")
    print("\nDownloading InsightFace buffalo_l model pack...")
    print("This may take a few minutes (~180MB download)\n")
    
    # Download the zip file
    zip_path = os.path.join(models_dir, 'buffalo_l.zip')
    
    if download_file(BUFFALO_ZIP_URL, zip_path, "InsightFace buffalo_l models"):
        # Extract models
        if extract_models_from_zip(zip_path, models_dir):
            # Clean up zip file
            try:
                os.remove(zip_path)
                print("✓ Cleaned up temporary files")
            except:
                pass
            
            # Verify extraction
            result['scrfd'] = os.path.exists(scrfd_path)
            result['arcface'] = os.path.exists(arcface_path)
            
            if result['scrfd'] and result['arcface']:
                print("\n✓ All models downloaded and extracted successfully!")
            else:
                print("\n⚠ Some models may not have been extracted correctly")
    else:
        print("\n✗ Failed to download models")
        print("\nAlternative: Download manually from:")
        print("  https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip")
        print(f"  Extract det_10g.onnx and w600k_r50.onnx to: {models_dir}")
    
    return result


def download_using_insightface():
    """
    Alternative method: Use insightface package to download models.
    This requires the insightface package to be installed.
    """
    try:
        import insightface
        from insightface.app import FaceAnalysis
        
        print("Using insightface package to download models...")
        
        # This will download buffalo_l models to ~/.insightface/models/
        app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
        
        # Copy models to our models directory
        home = os.path.expanduser('~')
        buffalo_dir = os.path.join(home, '.insightface', 'models', 'buffalo_l')
        
        if os.path.exists(buffalo_dir):
            det_src = os.path.join(buffalo_dir, 'det_10g.onnx')
            rec_src = os.path.join(buffalo_dir, 'w600k_r50.onnx')
            
            if os.path.exists(det_src):
                shutil.copy(det_src, os.path.join(MODELS_DIR, 'det_10g.onnx'))
                print(f"✓ Copied det_10g.onnx")
            
            if os.path.exists(rec_src):
                shutil.copy(rec_src, os.path.join(MODELS_DIR, 'w600k_r50.onnx'))
                print(f"✓ Copied w600k_r50.onnx")
            
            return True
    except ImportError:
        print("insightface package not installed, using direct download")
    except Exception as e:
        print(f"Failed to use insightface: {e}")
    
    return False


if __name__ == '__main__':
    print("="*60)
    print("InsightFace Model Downloader")
    print("="*60)
    print()
    
    result = check_and_download_models()
    
    print()
    print("="*60)
    print("Status:")
    print(f"  SCRFD (det_10g.onnx):     {'✓ Ready' if result['scrfd'] else '✗ Missing'}")
    print(f"  ArcFace (w600k_r50.onnx): {'✓ Ready' if result['arcface'] else '✗ Missing'}")
    print("="*60)
