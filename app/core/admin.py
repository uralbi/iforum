from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from core import models
from django.utils.html import format_html
from django.db.models import Count


class IforumUserAdmin(UserAdmin):
    fieldsets = (
        ('Main', {"fields": ("email", "password")}),
        (_("Personal info"),
            {"fields": ("username", "first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"),
            {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            _('Main info'),
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )
    list_display = ("id", "email", "username",
                    "first_name", "last_name", "is_staff")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email",)


class ViewFilter(admin.SimpleListFilter):
    title = 'Views'
    parameter_name = 'views'

    def lookups(self, request, model_admin):
        return [
            ('<100', 'Less than 100'),
            ('100-1K', '100 to 1K'),
            ('1K-10K', '1k to 10k'),
            ('>10K', 'Greater than 10k'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '<100':
            return queryset.filter(views__lt=100)
        elif self.value() == '100-1K':
            return queryset.filter(views__gte=100, views__lt=1000)
        elif self.value() == '1K-10K':
            return queryset.filter(views__gte=1000, views__lt=10000)
        elif self.value() == '>10K':
            return queryset.filter(views__gt=10000)


class TagAssignFilter(admin.SimpleListFilter):
    title = 'Assigned'
    parameter_name = 'posts'

    def lookups(self, request, model_admin):
        return [
            ('0', 'Not Assigned'),
            ('0-10', '0 to 10'),
            ('10-100', '10 to 100'),
            ('>100', 'More than 100'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.annotate(posts_count=Count('posts')) \
                .filter(posts_count=0)
        elif self.value() == '0-10':
            return queryset.annotate(posts_count=Count('posts')) \
                .filter(posts_count__gt=0, posts_count__lte=10)
        elif self.value() == '10-100':
            return queryset.annotate(posts_count=Count('posts')) \
                .filter(posts_count__gt=10, posts_count__lte=100)
        elif self.value() == '>100':
            return queryset.annotate(posts_count=Count('posts')) \
                .filter(posts_count__gt=100)


class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "title", "content", "images",
                    "tags_n", "published_at", "created_at", "views")
    list_filter = ['author', 'published_at', 'created_at', ViewFilter]
    filter_horizontal = ('tags',)
    prepopulated_fields = {"slug": ("title",)}

    def tags_n(self, obj):
        return obj.tags.count()

    def images(self, obj):
        return obj.images.count()

    def get_changeform_initial_data(self, request):
        """
        Returns the initial data for the change form.
        """
        initial = super().get_changeform_initial_data(request)
        if not initial.get('slug'):
            initial['slug'] = f"{initial.get('title')}_{initial.get('id')}"
        return initial


class TagAdmin(admin.ModelAdmin):
    list_display = ('value', 'assigned')
    list_filter = (TagAssignFilter, 'value')

    def assigned(self, obj):
        return obj.posts.count()


class GalleryAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'thumbnail', 'created_at')
    list_filter = ['post', ]

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: \
                               50px; max-width: 80px; border-radius: 4px; \
                               align: center;"/>'.format(obj.image.url))
        else:
            return '[x]'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'content', 'content_type', 'object_id', 'created_at', 'modified_at')
    list_filter = ['creator', ]


admin.site.register(models.User, IforumUserAdmin)
admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Gallery, GalleryAdmin)
admin.site.register(models.Comment, CommentAdmin)
