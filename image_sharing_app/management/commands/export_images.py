import csv
import os
from django.core.management.base import BaseCommand
from image_sharing_app.models import Image

class Command(BaseCommand):
    help = 'Export images to CSV'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, default='images_export.csv', help='Output CSV file path')
        
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
                'id', 'title', 'image_path', 'description', 'author_id', 
                'author_username', 'created_at', 'like_count'
            ])
            
            # Write image data
            for image in Image.objects.all():
                writer.writerow([
                    image.id, image.title, image.image.name, image.description,
                    image.author.id, image.author.username, image.created_at,
                    image.likes.count()
                ])
                
        self.stdout.write(self.style.SUCCESS(f'Successfully exported {Image.objects.count()} images to {output_file}')) 