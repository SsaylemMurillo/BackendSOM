from django.db import models

class KohonenConfig(models.Model):
    neurons = models.IntegerField()
    competition_type = models.CharField(max_length=100)
    iterations = models.IntegerField()

    def __str__(self):
        return f"Config {self.id}: {self.neurons} neurons"
    
class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}: {self.name} uploaded on {self.upload_date}"
    
class ImageVector(models.Model):
    image = models.ForeignKey('Image', on_delete=models.CASCADE) 
    vector = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vector for {self.image.name}"