import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from settings import CLOUDINARY_API_KEY,CLOUDINARY_API_SECRET,CLOUDINARY_NAME

# Configuration       
cloudinary.config( 
    cloud_name = CLOUDINARY_NAME, 
    api_key = CLOUDINARY_API_KEY, 
    api_secret = CLOUDINARY_API_SECRET, # Click 'View Credentials' below to copy your API secret
    secure=True
)

def upload_file_to_cloudinary(file, filename):
    """
    Upload a file to Cloudinary.

    Args:
        file (file-like object): The file to be uploaded.
        filename (str): The desired filename for the uploaded file.

    Returns:
        str: The URL of the uploaded image.
    """
    r = cloudinary.uploader.upload(
        file, public_id=f'NotesApp/{filename}', overwrite=True
        )
    return cloudinary.CloudinaryImage(
        f'NotesApp/{filename}').build_url(
            width=250, height=250, crop='fill', version=r.get('version')
        )