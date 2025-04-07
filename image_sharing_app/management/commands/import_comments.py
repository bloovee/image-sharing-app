import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from image_sharing_app.models import Image, Comment
from django.utils.dateparse import parse_datetime

class Command(BaseCommand):
    help = 'Import comments from CSV'

    def add_arguments(self, parser):
        parser.add_argument('--input', type=str, required=True, help='Input CSV file path')
        parser.add_argument('--skip-existing', action='store_true', help='Skip existing comments')
        
    def handle(self, *args, **options):
        input_file = options['input']
        skip_existing = options['skip_existing']
        
        if not os.path.exists(input_file):
            self.stdout.write(self.style.ERROR(f'Input file {input_file} does not exist'))
            return
            
        comments_created = 0
        comments_updated = 0
        comments_skipped = 0
        missing_users = 0
        missing_images = 0
        
        with open(input_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                comment_id = row['id']
                parent_image_id = row['parent_image_id']
                parent_image_title = row['parent_image_title']
                author_id = row['author_id']
                author_username = row['author_username']
                content = row['content']
                created_at = row['created_at']
                
                # Check for parent image
                try:
                    parent_image = Image.objects.get(id=parent_image_id)
                except Image.DoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f'Skipping comment: Parent image id {parent_image_id} not found'
                    ))
                    missing_images += 1
                    continue
                
                # Check for author
                try:
                    author = User.objects.get(id=author_id)
                except User.DoesNotExist:
                    try:
                        author = User.objects.get(username=author_username)
                    except User.DoesNotExist:
                        self.stdout.write(self.style.WARNING(
                            f'Skipping comment: User {author_username} not found'
                        ))
                        missing_users += 1
                        continue
                
                # Check if comment exists
                try:
                    comment = Comment.objects.get(id=comment_id)
                    if skip_existing:
                        comments_skipped += 1
                        continue
                    else:
                        # Update existing comment
                        comments_updated += 1
                except Comment.DoesNotExist:
                    # Create new comment
                    comment = Comment(id=comment_id)
                    comments_created += 1
                
                # Update comment fields
                comment.parent_image = parent_image
                comment.author = author
                comment.content = content
                
                # Set created_at if provided
                if created_at and created_at != 'None':
                    comment.created_at = parse_datetime(created_at)
                
                # Save the comment
                comment.save()
                
        self.stdout.write(self.style.SUCCESS(
            f'Import complete: {comments_created} comments created, {comments_updated} comments updated, '
            f'{comments_skipped} comments skipped, {missing_users} missing users, {missing_images} missing images'
        )) 