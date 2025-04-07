import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from image_sharing_app.models import Image, UserProfile
from django.utils.dateparse import parse_datetime
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

class Command(BaseCommand):
    help = 'Import images from CSV'

    def add_arguments(self, parser):
        parser.add_argument('--input', type=str, required=True, help='Input CSV file path')
        parser.add_argument('--skip-existing', action='store_true', help='Skip existing images')
        parser.add_argument('--skip-missing-files', action='store_true', help='Skip entries with missing image files')
        parser.add_argument('--create-missing-users', action='store_true', help='Create missing users as placeholders')
        
    def handle(self, *args, **options):
        input_file = options['input']
        skip_existing = options['skip_existing']
        skip_missing_files = options['skip_missing_files']
        create_missing_users = options['create_missing_users']
        
        if not os.path.exists(input_file):
            self.stdout.write(self.style.ERROR(f'Input file {input_file} does not exist'))
            return
            
        images_created = 0
        images_updated = 0
        images_skipped = 0
        missing_users = 0
        missing_files = 0
        users_created = 0
        
        with open(input_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                image_id = row['id']
                title = row['title']
                image_path = row['image_path']
                description = row['description']
                author_id = row['author_id']
                author_username = row['author_username']
                created_at = row['created_at']
                
                # Check for author
                try:
                    author = User.objects.get(id=author_id)
                except User.DoesNotExist:
                    try:
                        author = User.objects.get(username=author_username)
                    except User.DoesNotExist:
                        if create_missing_users:
                            # Create a placeholder user
                            username = author_username or f"placeholder_{author_id}"
                            author = User.objects.create(
                                username=username,
                                first_name="Placeholder",
                                last_name="User",
                                email=f"{username}@placeholder.com"
                            )
                            
                            # Create a user profile for the placeholder user
                            UserProfile.objects.create(
                                user=author,
                                bio=f"Placeholder user created during import (original ID: {author_id})"
                            )
                            
                            users_created += 1
                            self.stdout.write(self.style.WARNING(
                                f'Created placeholder user: {username}'
                            ))
                        else:
                            self.stdout.write(self.style.WARNING(
                                f'Skipping image "{title}": User {author_username} (ID: {author_id}) not found'
                            ))
                            missing_users += 1
                            continue
                
                # Check if image exists
                try:
                    image = Image.objects.get(id=image_id)
                    if skip_existing:
                        images_skipped += 1
                        continue
                    else:
                        # Update existing image
                        images_updated += 1
                except Image.DoesNotExist:
                    # Create new image
                    image = Image(id=image_id)
                    images_created += 1
                
                # Update image fields
                image.title = title
                image.description = description
                image.author = author
                
                # Handle image file
                if image_path and not default_storage.exists(image_path):
                    if skip_missing_files:
                        self.stdout.write(self.style.WARNING(
                            f'Image file {image_path} not found, skipping'
                        ))
                        missing_files += 1
                        continue
                    else:
                        # Create an empty file as placeholder
                        image.image.save(os.path.basename(image_path), ContentFile(b''), save=False)
                else:
                    # Keep the existing image path
                    image.image.name = image_path
                
                # Set created_at if provided
                if created_at and created_at != 'None':
                    image.created_at = parse_datetime(created_at)
                
                # Save the image
                image.save()
                
        self.stdout.write(self.style.SUCCESS(
            f'Import complete: {images_created} images created, {images_updated} images updated, '
            f'{images_skipped} images skipped, {users_created} users created, '
            f'{missing_users} missing users, {missing_files} missing files'
        )) 