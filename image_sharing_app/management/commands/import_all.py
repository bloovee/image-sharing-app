import os
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Import all data (users, images, comments) from CSV files'

    def add_arguments(self, parser):
        parser.add_argument('--input-dir', type=str, required=True, help='Input directory with CSV files')
        parser.add_argument('--skip-existing', action='store_true', help='Skip existing records')
        parser.add_argument('--skip-missing-files', action='store_true', help='Skip entries with missing image files')
        
    def handle(self, *args, **options):
        input_dir = options['input_dir']
        skip_existing = options['skip_existing']
        skip_missing_files = options['skip_missing_files']
        
        if not os.path.exists(input_dir):
            self.stdout.write(self.style.ERROR(f'Input directory {input_dir} does not exist'))
            return
            
        # Import users first
        users_input = os.path.join(input_dir, 'users_export.csv')
        if os.path.exists(users_input):
            self.stdout.write(self.style.NOTICE('Importing users...'))
            skip_arg = '--skip-existing' if skip_existing else ''
            call_command('import_users', input=users_input, skip_existing=skip_existing)
        else:
            self.stdout.write(self.style.WARNING(f'Users file {users_input} not found, skipping'))
        
        # Import images next
        images_input = os.path.join(input_dir, 'images_export.csv')
        if os.path.exists(images_input):
            self.stdout.write(self.style.NOTICE('Importing images...'))
            call_command('import_images', input=images_input, skip_existing=skip_existing, 
                        skip_missing_files=skip_missing_files)
        else:
            self.stdout.write(self.style.WARNING(f'Images file {images_input} not found, skipping'))
        
        # Import comments last
        comments_input = os.path.join(input_dir, 'comments_export.csv')
        if os.path.exists(comments_input):
            self.stdout.write(self.style.NOTICE('Importing comments...'))
            call_command('import_comments', input=comments_input, skip_existing=skip_existing)
        else:
            self.stdout.write(self.style.WARNING(f'Comments file {comments_input} not found, skipping'))
        
        self.stdout.write(self.style.SUCCESS(f'All data imports completed')) 