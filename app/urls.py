from django.urls import path
from . views import *

urlpatterns = [
    path('', index, name='index' ),
    path('userRegistration/', userRegistration, name='userRegistration'),
    path('userLogin/', userLogin, name='userLogin'),
    path('homePage/', homePage, name='homePage'),
    path('cloudLogin/', cloudLogin, name='cloudLogin'),
    path('logout/', logout, name='logout'),
    path('uploadFiles/', uploadFiles, name='uploadFiles'),
    path('encryptFile/<int:fileID>/', encryptFile, name='encryptFile'),
    path('viewFiles/', viewFiles, name='viewFiles'),
    path('deleteUploadedFile/<int:fileID>/', deleteUploadedFile, name='deleteUploadedFile'),
    path('downloadRequests/<int:fileID>/', downloadRequests, name='downloadRequests'),
    path('viewDownloadRequests/', viewDownloadRequests, name='viewDownloadRequests'),
    path('approveRequest/<int:requestID>/<int:fileID>/', approveRequest, name='approveRequest'),
    path('rejectRequest/<int:requestID>/<int:fileID>/', rejectRequest, name='rejectRequest'),
    path('decryptFile/<int:fileID>/', decryptFile, name='decryptFile'),
    path('otp/', otp, name='otp'),
    path('sendOTP/<int:fileID>/', sendOTP, name='sendOTP'),
    path('downloadDecrypted/<int:fileID>/', downloadDecrypted, name='downloadDecrypted'),
    path('view_all_users/', view_all_users, name='view_all_users'),
    path('view_user_uploaded_files/', view_user_uploaded_files, name='view_user_uploaded_files'),
    path('forgotPassword/', forgotPassword, name='forgotPassword'),
    path('enterOtp/<str:userEmail>/', enterOtp, name='enterOtp'),
    path('newPassword/<str:userEmail>/', newPassword, name='newPassword'),
    path('deleteUser/<int:userID>/', deleteUser, name='deleteUser')

]