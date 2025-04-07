import csv
import os
from django.core.management.base import BaseCommand
from image_sharing_app.models import Comment

class Command(BaseCommand):
    help = 'Export comments to CSV'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, default='comments_export.csv', help='Output CSV file path')
        
    def handle(self, *args, **options):
        output_file = options['output']
        
        # Ensure the directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write headers
            writer.writerow([
                'id', 'parent_image_id', 'parent_image_title', 'author_id', 
                'author_username', 'content', 'created_at'
            ])
            
            # Write comment data
            for comment in Comment.objects.all():
                writer.writerow([
                    comment.id, comment.parent_image.id, comment.parent_image.title,
                    comment.author.id, comment.author.username, comment.content,
                    comment.created_at
                ])
                
        self.stdout.write(self.style.SUCCESS(f'Successfully exported {Comment.objects.count()} comments to {output_file}')) 