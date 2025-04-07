import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from image_sharing_app.models import UserProfile

class Command(BaseCommand):
    help = 'Export users and user profiles to CSV'

    def add_arguments(self, parser):
        parser.add_argument('--output', type=str, default='users_export.csv', help='Output CSV file path')
        
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
                'id', 'username', 'email', 'first_name', 'last_name', 
                'is_active', 'is_staff', 'is_superuser', 'date_joined', 
                'last_login', 'bio', 'created_at', 'updated_at'
            ])
            
            # Write user data
            for user in User.objects.all():
                try:
                    profile = user.profile
                    bio = profile.bio
                    profile_created_at = profile.created_at
                    profile_updated_at = profile.updated_at
                except UserProfile.DoesNotExist:
                    bio = ''
                    profile_created_at = None
                    profile_updated_at = None
                
                writer.writerow([
                    user.id, user.username, user.email, user.first_name, user.last_name,
                    user.is_active, user.is_staff, user.is_superuser, user.date_joined,
                    user.last_login, bio, profile_created_at, profile_updated_at
                ])
                
        self.stdout.write(self.style.SUCCESS(f'Successfully exported {User.objects.count()} users to {output_file}')) 