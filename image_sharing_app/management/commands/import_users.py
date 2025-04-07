import csv
import os
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from image_sharing_app.models import UserProfile
from django.utils.dateparse import parse_datetime
from django.core.management.base import CommandError

class Command(BaseCommand):
    help = 'Import users and user profiles from CSV'

    def add_arguments(self, parser):
        parser.add_argument('--input', type=str, required=True, help='Input CSV file path')
        parser.add_argument('--skip-existing', action='store_true', help='Skip existing users')
        
    def handle(self, *args, **options):
        input_file = options['input']
        skip_existing = options['skip_existing']
        
        if not os.path.exists(input_file):
            self.stdout.write(self.style.ERROR(f'Input file {input_file} does not exist'))
            return
            
        users_created = 0
        users_updated = 0
        users_skipped = 0
        
        required_fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 
                          'is_staff', 'is_superuser', 'date_joined', 'last_login', 'bio', 
                          'created_at', 'updated_at']
        
        try:
            with open(input_file, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                # Validate CSV headers
                missing_fields = [field for field in required_fields if field not in reader.fieldnames]
                if missing_fields:
                    missing_fields_str = ', '.join(missing_fields)
                    raise CommandError(
                        f"CSV file is missing required columns: {missing_fields_str}\n\n"
                        f"Required columns are: {', '.join(required_fields)}\n\n"
                        f"Found columns: {', '.join(reader.fieldnames or [])}"
                    )
                
                for row in reader:
                    try:
                        username = row['username']
                        
                        # Check if user exists
                        try:
                            user = User.objects.get(username=username)
                            if skip_existing:
                                users_skipped += 1
                                continue
                            else:
                                # Update existing user
                                users_updated += 1
                        except User.DoesNotExist:
                            # Create new user
                            user = User(username=username)
                            users_created += 1
                        
                        # Update user fields
                        user.email = row['email']
                        user.first_name = row['first_name']
                        user.last_name = row['last_name']
                        user.is_active = row['is_active'].lower() in ('true', 'yes', '1', 't', 'y')
                        user.is_staff = row['is_staff'].lower() in ('true', 'yes', '1', 't', 'y')
                        user.is_superuser = row['is_superuser'].lower() in ('true', 'yes', '1', 't', 'y')
                        
                        if row['date_joined'] and row['date_joined'] != 'None':
                            user.date_joined = parse_datetime(row['date_joined'])
                        
                        if row['last_login'] and row['last_login'] != 'None':
                            user.last_login = parse_datetime(row['last_login'])
                        
                        # Save user without hashing the password - password will need to be reset
                        user.save()
                        
                        # Update profile
                        try:
                            profile = user.profile
                        except UserProfile.DoesNotExist:
                            profile = UserProfile(user=user)
                        
                        profile.bio = row['bio']
                        
                        if row['created_at'] and row['created_at'] != 'None':
                            profile.created_at = parse_datetime(row['created_at'])
                            
                        if row['updated_at'] and row['updated_at'] != 'None':
                            profile.updated_at = parse_datetime(row['updated_at'])
                        
                        profile.save()
                    except KeyError as e:
                        # Handle missing fields in individual rows
                        row_num = reader.line_num
                        raise CommandError(f"Row {row_num}: Missing required field '{e.args[0]}'")
                    except Exception as e:
                        # Handle other errors in individual rows
                        row_num = reader.line_num
                        raise CommandError(f"Error processing row {row_num}: {str(e)}")
        except csv.Error as e:
            raise CommandError(f"CSV parsing error: {str(e)}")
        except UnicodeDecodeError:
            raise CommandError("Unable to decode the CSV file. Please ensure it's saved in UTF-8 format.")
        except Exception as e:
            # Catch-all for other errors
            if 'KeyError' in str(e):
                field = str(e).replace("KeyError: ", "").replace("'", "")
                raise CommandError(
                    f"Error: The CSV file is missing the required column '{field}'.\n\n"
                    f"Required columns are: {', '.join(required_fields)}"
                )
            else:
                raise CommandError(f"An unexpected error occurred: {str(e)}")
                
        self.stdout.write(self.style.SUCCESS(
            f'Import complete: {users_created} users created, {users_updated} users updated, {users_skipped} users skipped'
        )) 