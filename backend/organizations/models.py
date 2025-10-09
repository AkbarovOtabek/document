from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default="")
    badge = models.CharField(max_length=50, blank=True,
                             default="")
    time_create = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Organization(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    address = models.CharField(max_length=300)
    lotus = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    category = models.ForeignKey(
        Category, related_name='organizations', on_delete=models.CASCADE)
    logo = models.ImageField(
        upload_to='organization_logos/', null=True, blank=True)
    time_create = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-time_create']

    def __str__(self):
        return self.name
