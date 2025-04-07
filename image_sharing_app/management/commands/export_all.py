import os
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Export all data (users, images, comments) to CSV files'

    def add_arguments(self, parser):
        parser.add_argument('--output-dir', type=str, default='data_export', help='Output directory for CSV files')
        
    def handle(self, *args, **options):
        output_dir = options['output_dir']
        
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Export users
        users_output = os.path.join(output_dir, 'users_export.csv')
        call_command('export_users', output=users_output)
        
        # Export images
        images_output = os.path.join(output_dir, 'images_export.csv')
        call_command('export_images', output=images_output)
        
        # Export comments
        comments_output = os.path.join(output_dir, 'comments_export.csv')
        call_command('export_comments', output=comments_output)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully exported all data to {output_dir}')) 