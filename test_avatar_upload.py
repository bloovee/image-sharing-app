#!/usr/bin/env python

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from image_sharing_app.models import UserProfile
from django.core.files import File
import tempfile
import shutil

def test_avatar_upload():
    print("Testing avatar upload...")
    
    # Get the admin user
    try:
        user = User.objects.get(username='admin')
        print(f"Found user: {user.username}")
    except User.DoesNotExist:
        print("Admin user not found, creating...")
        user = User.objects.create_user('admin', 'admin@example.com', 'adminpassword')
        print(f"Created user: {user.username}")
    
    # Ensure user has a profile
    try:
        profile = user.profile
        print(f"Found profile for {user.username}")
    except UserProfile.DoesNotExist:
        print(f"Profile for {user.username} not found, creating...")
        profile = UserProfile.objects.create(user=user)
        print(f"Created profile for {user.username}")
    
    # Create a test image file
    print("Creating test image file...")
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        # Get a sample image or create a blank one
        try:
            # Copy a sample image if available
            shutil.copy('/app/static/img/sample.jpg', temp_file.name)
        except:
            # Create a blank file if no sample available
            temp_file.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xdb\x00C\x01\t\t\t\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0\x00\x11\x08\x00d\x00d\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xfe\xfe(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00')
        
    print(f"Created test file: {temp_file.name}")
    
    # Update the profile with the test avatar
    try:
        with open(temp_file.name, 'rb') as img_file:
            print(f"Opening file: {temp_file.name}")
            profile.avatar.save('test_avatar.jpg', File(img_file), save=True)
        print(f"Avatar updated: {profile.avatar.name}")
        print(f"Avatar URL: {profile.avatar.url}")
        print(f"Avatar path: {profile.avatar.path}")
        
        # Verify that the file exists on disk
        if os.path.exists(profile.avatar.path):
            print(f"Avatar file exists on disk at: {profile.avatar.path}")
        else:
            print(f"Avatar file DOES NOT exist on disk at: {profile.avatar.path}")
            
    except Exception as e:
        print(f"Error updating avatar: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    # Cleanup
    try:
        os.unlink(temp_file.name)
        print(f"Cleaned up temporary file: {temp_file.name}")
    except:
        pass

if __name__ == "__main__":
    test_avatar_upload()
