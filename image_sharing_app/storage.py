from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
import boto3
import logging

logger = logging.getLogger(__name__)

class MediaStorage(S3Boto3Storage):
    """
    Custom storage backend for S3 that explicitly avoids using ACLs.
    For use with buckets that have 'Bucket owner enforced' setting.
    """
    location = 'media'
    file_overwrite = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure we never send ACLs
        self.default_acl = None
    
    def _get_write_parameters(self, name, content=None, headers=None, **kwargs):
        params = super()._get_write_parameters(name, content, headers, **kwargs)
        # Remove any ACL parameters
        if 'ACL' in params:
            del params['ACL']
        return params
        
    def _save(self, name, content):
        """
        Override _save method to directly use boto3 client without ACL
        """
        # Use the parent class method to get available name
        cleaned_name = self.get_available_name(name)
        name = self.location + '/' + cleaned_name
        
        params = {'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': name, 'Body': content}
        
        # Set content type for the file
        content_type = getattr(content, 'content_type', None)
        if content_type:
            params['ContentType'] = content_type
            
        # Set content disposition for the file - helps with downloads
        params['ContentDisposition'] = 'inline'
            
        # Get the boto3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        try:
            s3.put_object(**params)
            logger.info(f"Successfully uploaded {name} to S3 without ACL")
        except Exception as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            raise
            
        return cleaned_name 