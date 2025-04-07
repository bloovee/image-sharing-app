from django.contrib import admin
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
from django.core.management import call_command
from .models import Image, Comment, UserProfile
import os
import csv
import io
import tempfile
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils.safestring import mark_safe

# Create functions for the data management views
def data_management_view(request):
    return TemplateResponse(
        request,
        "admin/data_management.html",
        context={
            'title': 'Data Management',
            'opts': UserProfile._meta,
            'users_count': User.objects.count(),
            'images_count': Image.objects.count(),
            'comments_count': Comment.objects.count(),
        }
    )

def export_all_view(request):
    if request.method == 'POST':
        export_type = request.POST.get('export_type', 'all')
        
        if export_type == 'all':
            # Create a zip file containing all exports
            import zipfile
            from io import BytesIO
            
            # Create a BytesIO buffer to store the zip file
            zip_buffer = BytesIO()
            
            # Create a zip file in the buffer
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Export users
                users_buffer = StringIOWrapper()
                export_users_to_csv(users_buffer)
                zip_file.writestr('users_export.csv', users_buffer.getvalue())
                
                # Export images
                images_buffer = StringIOWrapper()
                export_images_to_csv(images_buffer)
                zip_file.writestr('images_export.csv', images_buffer.getvalue())
                
                # Export comments
                comments_buffer = StringIOWrapper()
                export_comments_to_csv(comments_buffer)
                zip_file.writestr('comments_export.csv', comments_buffer.getvalue())
            
            # Reset the buffer position to the beginning
            zip_buffer.seek(0)
            
            # Create the HttpResponse object with the appropriate ZIP header
            response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename="all_data_export.zip"'
            return response
            
        elif export_type == 'users':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
            export_users_to_csv(response)
            return response
            
        elif export_type == 'images':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="images_export.csv"'
            export_images_to_csv(response)
            return response
            
        elif export_type == 'comments':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="comments_export.csv"'
            export_comments_to_csv(response)
            return response
        
    return TemplateResponse(
        request,
        "admin/export_all.html",
        context={
            'title': 'Export Data',
            'opts': UserProfile._meta,
        }
    )

class StringIOWrapper(io.StringIO):
    """A wrapper for StringIO that returns the value as bytes when needed."""
    def getvalue(self):
        val = super().getvalue()
        return val.encode('utf-8') if isinstance(val, str) else val

def export_users_to_csv(output):
    """Export all users to a CSV file."""
    writer = csv.writer(output)
    # Write headers
    writer.writerow([
        'id', 'username', 'email', 'first_name', 'last_name', 
        'is_active', 'is_staff', 'is_superuser', 'date_joined', 
        'last_login', 'bio', 'created_at', 'updated_at'
    ])
    
    # Write user data
    for user in User.objects.all():
        try:
            profile = UserProfile.objects.get(user=user)
            writer.writerow([
                user.id, user.username, user.email, user.first_name, user.last_name,
                user.is_active, user.is_staff, user.is_superuser, user.date_joined,
                user.last_login, profile.bio, profile.created_at, profile.updated_at
            ])
        except UserProfile.DoesNotExist:
            # Skip users without profiles
            pass

def export_images_to_csv(output):
    """Export all images to a CSV file."""
    writer = csv.writer(output)
    # Write headers
    writer.writerow([
        'id', 'title', 'image_path', 'description', 'author_id', 
        'author_username', 'created_at', 'like_count'
    ])
    
    # Write image data
    for image in Image.objects.all().annotate(like_count=Count('likes')):
        writer.writerow([
            image.id, image.title, image.image.name, image.description,
            image.author.id, image.author.username, image.created_at,
            image.like_count
        ])

def export_comments_to_csv(output):
    """Export all comments to a CSV file."""
    writer = csv.writer(output)
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

def import_all_view(request):
    if request.method == 'POST' and 'csv_file' in request.FILES:
        csv_file = request.FILES['csv_file']
        
        # Create a temporary file to store the CSV content
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
            for chunk in csv_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name
        
        try:
            # Process import
            import_type = request.POST.get('import_type', 'users')
            skip_existing = request.POST.get('skip_existing', False) == 'on'
            skip_missing_files = request.POST.get('skip_missing_files', False) == 'on'
            
            try:
                if import_type == 'users':
                    call_command('import_users', input=temp_path, skip_existing=skip_existing)
                    messages.success(request, 'Users imported successfully')
                elif import_type == 'images':
                    call_command('import_images', input=temp_path, skip_existing=skip_existing, skip_missing_files=skip_missing_files)
                    messages.success(request, 'Images imported successfully')
                elif import_type == 'comments':
                    call_command('import_comments', input=temp_path, skip_existing=skip_existing)
                    messages.success(request, 'Comments imported successfully')
            except Exception as e:
                error_message = str(e)
                
                # Format the error message for display
                if 'CSV file is missing required columns' in error_message or 'missing the required column' in error_message:
                    # CSV column structure errors
                    messages.error(request, mark_safe(f'<strong>CSV Format Error:</strong> {error_message.replace(chr(10), "<br>")}'))
                elif 'Missing required field' in error_message or 'Error processing row' in error_message:
                    # Row-specific errors
                    messages.error(request, mark_safe(f'<strong>Data Error:</strong> {error_message}'))
                elif 'User' in error_message and 'not found' in error_message:
                    # Missing referenced user
                    messages.error(request, mark_safe(
                        f'<strong>Reference Error:</strong> {error_message}<br><br>'
                        f'<span class="text-warning">Make sure to import users first before importing images or comments.</span>'
                    ))
                elif 'Parent image' in error_message and 'not found' in error_message:
                    # Missing referenced image
                    messages.error(request, mark_safe(
                        f'<strong>Reference Error:</strong> {error_message}<br><br>'
                        f'<span class="text-warning">Make sure to import images before importing comments.</span>'
                    ))
                else:
                    # Generic error
                    messages.error(request, f'Error during import: {error_message}')
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        return HttpResponseRedirect("/admin/data-management/")
        
    return TemplateResponse(
        request,
        "admin/import_all.html",
        context={
            'title': 'Import Data',
            'opts': UserProfile._meta,
        }
    )

def export_selected_users_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="selected_users.csv"'
    
    writer = csv.writer(response)
    # Write headers
    writer.writerow([
        'id', 'username', 'email', 'first_name', 'last_name', 
        'is_active', 'is_staff', 'is_superuser', 'date_joined', 
        'last_login', 'bio', 'created_at', 'updated_at'
    ])
    
    # Write user data
    for user_profile in queryset:
        user = user_profile.user
        writer.writerow([
            user.id, user.username, user.email, user.first_name, user.last_name,
            user.is_active, user.is_staff, user.is_superuser, user.date_joined,
            user.last_login, user_profile.bio, user_profile.created_at, user_profile.updated_at
        ])
    
    return response
export_selected_users_as_csv.short_description = "Export selected users to CSV"

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'bio')
    actions = [export_selected_users_as_csv]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-users/', self.admin_site.admin_view(self.export_users), name='export_users'),
            path('import-users/', self.admin_site.admin_view(self.import_users), name='import_users'),
        ]
        return custom_urls + urls
    
    def export_users(self, request):
        if request.method == 'POST':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
            export_users_to_csv(response)
            return response
            
        return TemplateResponse(
            request,
            "admin/export_users.html",
            context={
                'title': 'Export Users',
                'opts': self.model._meta,
            }
        )
    
    def import_users(self, request):
        if request.method == 'POST' and request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']
            
            # Create a temporary file to store the CSV content
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                for chunk in csv_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            try:
                # Process import
                skip_existing = request.POST.get('skip_existing', False) == 'on'
                call_command('import_users', input=temp_path, skip_existing=skip_existing)
                
                messages.success(request, 'Users imported successfully')
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
            return HttpResponseRedirect("../")
            
        return TemplateResponse(
            request,
            "admin/import_users.html",
            context={
                'title': 'Import Users',
                'opts': self.model._meta,
            }
        )

def export_selected_images_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="selected_images.csv"'
    
    writer = csv.writer(response)
    # Write headers
    writer.writerow([
        'id', 'title', 'image_path', 'description', 'author_id', 
        'author_username', 'created_at', 'like_count'
    ])
    
    # Write image data
    for image in queryset:
        writer.writerow([
            image.id, image.title, image.image.name, image.description,
            image.author.id, image.author.username, image.created_at,
            image.likes.count()
        ])
    
    return response
export_selected_images_as_csv.short_description = "Export selected images to CSV"

class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'total_likes')
    list_filter = ('created_at', 'author')
    search_fields = ('title', 'description', 'author__username')
    actions = [export_selected_images_as_csv]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-images/', self.admin_site.admin_view(self.export_images), name='export_images'),
            path('import-images/', self.admin_site.admin_view(self.import_images), name='import_images'),
        ]
        return custom_urls + urls
    
    def export_images(self, request):
        if request.method == 'POST':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="images_export.csv"'
            export_images_to_csv(response)
            return response
            
        return TemplateResponse(
            request,
            "admin/export_images.html",
            context={
                'title': 'Export Images',
                'opts': self.model._meta,
            }
        )
    
    def import_images(self, request):
        if request.method == 'POST' and request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']
            
            # Create a temporary file to store the CSV content
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                for chunk in csv_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            try:
                # Process import
                skip_existing = request.POST.get('skip_existing', False) == 'on'
                skip_missing_files = request.POST.get('skip_missing_files', False) == 'on'
                call_command('import_images', input=temp_path, skip_existing=skip_existing, skip_missing_files=skip_missing_files)
                
                messages.success(request, 'Images imported successfully')
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            
            return HttpResponseRedirect("../")
            
        return TemplateResponse(
            request,
            "admin/import_images.html",
            context={
                'title': 'Import Images',
                'opts': self.model._meta,
            }
        )

def export_selected_comments_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="selected_comments.csv"'
    
    writer = csv.writer(response)
    # Write headers
    writer.writerow([
        'id', 'parent_image_id', 'parent_image_title', 'author_id', 
        'author_username', 'content', 'created_at'
    ])
    
    # Write comment data
    for comment in queryset:
        writer.writerow([
            comment.id, comment.parent_image.id, comment.parent_image.title,
            comment.author.id, comment.author.username, comment.content,
            comment.created_at
        ])
    
    return response
export_selected_comments_as_csv.short_description = "Export selected comments to CSV"

class CommentAdmin(admin.ModelAdmin):
    list_display = ('parent_image', 'author', 'content', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username', 'parent_image__title')
    actions = [export_selected_comments_as_csv]
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('export-comments/', self.admin_site.admin_view(self.export_comments), name='export_comments'),
            path('import-comments/', self.admin_site.admin_view(self.import_comments), name='import_comments'),
        ]
        return custom_urls + urls
    
    def export_comments(self, request):
        if request.method == 'POST':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="comments_export.csv"'
            export_comments_to_csv(response)
            return response
            
        return TemplateResponse(
            request,
            "admin/export_comments.html",
            context={
                'title': 'Export Comments',
                'opts': self.model._meta,
            }
        )
    
    def import_comments(self, request):
        if request.method == 'POST' and request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']
            
            # Create a temporary file to store the CSV content
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                for chunk in csv_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            try:
                # Process import
                skip_existing = request.POST.get('skip_existing', False) == 'on'
                call_command('import_comments', input=temp_path, skip_existing=skip_existing)
                
                messages.success(request, 'Comments imported successfully')
            finally:
                # Clean up the temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            
            return HttpResponseRedirect("../")
            
        return TemplateResponse(
            request,
            "admin/import_comments.html",
            context={
                'title': 'Import Comments',
                'opts': self.model._meta,
            }
        )

# Register your models here.
admin.site.register(Image, ImageAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

# Export admin_view functions for use in URLconf
admin_data_management_view = admin.site.admin_view(data_management_view)
admin_export_all_view = admin.site.admin_view(export_all_view)
admin_import_all_view = admin.site.admin_view(import_all_view)
