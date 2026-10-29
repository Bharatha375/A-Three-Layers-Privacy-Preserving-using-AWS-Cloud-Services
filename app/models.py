from django.db import models
import os

# Create your models here.

class UserModel(models.Model):
    userID = models.AutoField(primary_key=True)
    userName = models.CharField(max_length=50, null=True)
    userEmail = models.EmailField(null=True)
    password = models.CharField(max_length=50)
    confirmPassword = models.CharField(max_length=50, null=True)
    dob = models.DateField(null=True)
    gender = models.CharField(max_length=50, null=True)
    contact = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    otp = models.IntegerField(null=True)

    def __str__(self):
        return self.userName

    class Meta:
        db_table = 'UserModel'

class UploadedDocument(models.Model):
    fileID = models.AutoField(primary_key=True)
    fileName = models.CharField(max_length=50, null=True)
    file = models.FileField(upload_to=os.path.join('static', 'files'), default='No file')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uplodedBy = models.EmailField(null=True)
    fileStatus = models.CharField(max_length=50, default='pending')
    otp = models.CharField(max_length=50, null=True)
    download_Request_status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        return self.userName

    class Meta:
        db_table = 'UploadedDocument'

class BlockOne(models.Model):
    blockID = models.AutoField(primary_key=True)
    content = models.TextField(null=True)
    encrypted = models.TextField(null=True)
    hmac = models.CharField(max_length=64,null=True)
    key_used = models.CharField(max_length=100, null=True)
    uploadedBy = models.EmailField(null=True)
    secret_key_used = models.BinaryField(null=True)
    fileID = models.ForeignKey(UploadedDocument, on_delete=models.CASCADE, null=True)
    
    

    class Meta:
        db_table = 'BlockOne'

class BlockTwo(models.Model):
    blockID = models.AutoField(primary_key=True)
    content = models.TextField(null=True)
    encrypted = models.TextField(null=True)
    hmac = models.CharField(max_length=64, null=True)
    key_used = models.CharField(max_length=100, null=True)
    uploadedBy = models.EmailField(null=True)
    secret_key_used = models.BinaryField(null=True)
    fileID = models.ForeignKey(UploadedDocument, on_delete=models.CASCADE, null=True)
    

    class Meta:
        db_table = 'BlockTwo'

class BlockThree(models.Model):
    blockID = models.AutoField(primary_key=True)
    content = models.TextField(null=True)
    encrypted = models.TextField(null=True)
    hmac = models.CharField(max_length=64, null=True)
    key_used = models.CharField(max_length=100, null=True)
    uploadedBy = models.EmailField(null=True)
    secret_key_used = models.BinaryField(null=True)
    fileID = models.ForeignKey(UploadedDocument, on_delete=models.CASCADE, null=True)
    

    class Meta:
        db_table = 'BlockThree'

class userDownloadedHistory(models.Model):
    historyID = models.AutoField(primary_key=True)
    date_and_time = models.DateTimeField(auto_now_add=True)
    uploaded_userMail = models.EmailField(null=True)
    fileName = models.CharField(max_length=50, null=True)
    downloaded_user = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = 'userDownloadedHistory'

class userDownloadRequests(models.Model):
    requestID = models.AutoField(primary_key=True)
    requested_file_name = models.CharField(max_length=50, null=True)
    requested_user = models.EmailField(null=True)
    status = models.CharField(max_length=50, default='pending')
    fileID = models.IntegerField(null=True)

    class Meta:
        db_table = 'userDownloadRequests'
    




