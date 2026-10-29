from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.conf import settings
from django.core.mail import send_mail
import os
import hmac
import hashlib
from PyPDF2 import PdfReader
from docx import Document
import secrets
import random
from django.http import HttpResponse
from django.utils.encoding import smart_str


SECRET_KEY = None
CAESAR_SHIFT = None

def generate_keys():
    global SECRET_KEY, CAESAR_SHIFT
    SECRET_KEY = secrets.token_bytes(32)     
    CAESAR_SHIFT = random.randint(1, 25)

def index(request):
    return render(request, 'index.html')

def userRegistration(request):
    if request.method == 'POST':
        userName = request.POST.get('userName')
        userEmail = request.POST.get('userEmail')
        password = request.POST.get('password')
        confirmPassword = request.POST.get('confirmPassword')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender')
        contact = request.POST.get('contact')
        state = request.POST.get('state')
        country = request.POST.get('country')

        # Check if email already exists
        if UserModel.objects.filter(userEmail=userEmail).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')  # Replace with your registration page name

        # Check if passwords match
        if password != confirmPassword:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        # Save the user
        new_user = UserModel(
            userName=userName,
            userEmail=userEmail,
            password=password,  # You may use hashing here
            confirmPassword=confirmPassword,
            dob=dob,
            gender=gender,
            contact=contact,
            state=state,
            country=country
        )
        new_user.save()
        messages.success(request, 'Registration successful!')
        return redirect('userLogin')

    return render(request, 'register.html')


def userLogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = UserModel.objects.get(userEmail=email, password=password)
            request.session['user_id'] = user.userID
            request.session['user_email'] = user.userEmail
            request.session['login'] = 'user'
            messages.success(request, 'Login successful!')
            return redirect('homePage')
        except UserModel.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
            return redirect('userLogin')

    return render(request, 'userlogin.html')

def homePage(request):
    login = request.session['login']
    userMail = request.session['user_email']
    if login == 'user':
        userN = UserModel.objects.get(userEmail=userMail)
        userName = userN.userName
    else:
        userName=None
    return render(request, 'home.html', {'login':login, 'userName':userName})

def cloudLogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email == 'cloud@gmail.com' and password == 'cloud':
            request.session['user_email'] = 'cloud@gmail.com'
            request.session['login'] = 'cloud'
            return redirect('homePage')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('cloudLogin')
    return render(request, 'cloudLogin.html')

def logout(request):
    del request.session['login']
    request.session.pop('user_email', None)
    return redirect('index')

def uploadFiles(request):
    login = request.session['login']
    userMail = request.session['user_email']
    userN = UserModel.objects.get(userEmail=userMail)
    if request.method == 'POST':
        try:
            
            uploaded_file = request.FILES.get('file')
            print('======uploaded_file', uploaded_file)
            fileName = request.POST.get('fileName')
            UploadedDocument.objects.create(
                fileName=fileName,
                file=uploaded_file,
                uplodedBy=userMail
            )

            messages.success(request, "File uploaded, Successfully")
            return redirect('uploadFiles')
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return render(request, 'uploadFiles.html', {'login':login, 'userName':userN.userName})

def encryptFile(request, fileID):
    login = request.session['login']
    userMail = request.session['user_email']

    generate_keys()
    print(f"SECRET_KEY: {SECRET_KEY}")
    print(f"CAESAR_SHIFT: {CAESAR_SHIFT}")

    filePath = UploadedDocument.objects.get(fileID=fileID)
    raw_text = read_uploaded_file(filePath.file)
    blocks = split_into_blocks(raw_text)

    # Encrypt + HMAC for each block
    encrypted1 = caesar_cipher_encrypt(blocks[0], CAESAR_SHIFT)
    encrypted2 = caesar_cipher_encrypt(blocks[1], CAESAR_SHIFT)
    encrypted3 = caesar_cipher_encrypt(blocks[2], CAESAR_SHIFT)
    hmac1 = generate_hmac(encrypted1, SECRET_KEY)
    hmac2 = generate_hmac(encrypted2, SECRET_KEY)
    hmac3 = generate_hmac(encrypted3, SECRET_KEY)
    
    # Save in DB
    BlockOne.objects.create(encrypted=encrypted1, hmac=hmac1, key_used=CAESAR_SHIFT, uploadedBy=userMail, fileID=filePath, secret_key_used=SECRET_KEY)
    BlockTwo.objects.create(encrypted=encrypted2, hmac=hmac2, key_used=CAESAR_SHIFT, uploadedBy=userMail, fileID=filePath, secret_key_used=SECRET_KEY)
    BlockThree.objects.create(encrypted=encrypted3, hmac=hmac3, key_used=CAESAR_SHIFT, uploadedBy=userMail, fileID=filePath, secret_key_used=SECRET_KEY)

    filePath.fileStatus = 'encrypted'
    filePath.save()
    messages.success(request, 'File enceypted successfully')

    return redirect('viewFiles')



# ========= Cryptography Logic =============

# --- File Read ---
def read_uploaded_file(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[-1].lower()
    if ext == '.txt':
        return uploaded_file.read().decode('utf-8', errors='ignore')
    elif ext == '.pdf':
        return "\n".join([p.extract_text() or "" for p in PdfReader(uploaded_file).pages])
    elif ext == '.docx':
        return "\n".join([p.text for p in Document(uploaded_file).paragraphs])
    else:
        raise ValueError("Unsupported format.")

# --- Caesar Cipher ---
def caesar_cipher_encrypt(text, CAESAR_SHIFT):

    shift = CAESAR_SHIFT

    encrypted = []
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            encrypted.append(chr((ord(c) - base + shift) % 26 + base))
        else:
            encrypted.append(c)
    return ''.join(encrypted)

# --- Split into 3 blocks ---
def split_into_blocks(text):
    words = text.split()
    part = len(words) // 3
    return [
        " ".join(words[:part]),
        " ".join(words[part:2*part]),
        " ".join(words[2*part:])
    ]

# --- HMAC ---
def generate_hmac(data, SECRET_KEY):
    return hmac.new(SECRET_KEY, data.encode(), hashlib.sha256).hexdigest()

def viewFiles(request):
    login = request.session['login']
    userMail = request.session['user_email']
    userN = UserModel.objects.get(userEmail=userMail)
    userFiles = UploadedDocument.objects.filter(uplodedBy=userMail)
    if request.method == 'POST':
        filter_status = request.POST.get('filter')
        userFiles = UploadedDocument.objects.filter(uplodedBy=userMail, fileStatus=filter_status)
        return render(request, 'view_files.html', {
        'login': login,
        'files': userFiles,
        'userName': userN.userName
        })
    
    return render(request, 'view_files.html', {'login':login, 'files':userFiles, 'userName':userN.userName})

def deleteUploadedFile(request, fileID):
    deleteFile = UploadedDocument.objects.get(fileID=fileID)
    deleteFile.delete()
    messages.success(request, 'File removed sucessfully')
    return redirect('viewFiles')


# ----------- Decrypt the text ------------------

def caesar_cipher_decrypt(text, shift):
    shift = int(shift)  # ensure it's an integer
    decrypted = []
    for c in text:
        if c.isalpha():
            base = ord('A') if c.isupper() else ord('a')
            decrypted.append(chr((ord(c) - base - shift) % 26 + base))
        else:
            decrypted.append(c)
    return ''.join(decrypted)


def decryptFile(request, fileID):
    login = request.session['login']
    userMail = request.session['user_email']
    userN = UserModel.objects.get(userEmail=userMail)

    file = UploadedDocument.objects.get(fileID=fileID)

    # Get all three blocks
    block1 = BlockOne.objects.get(fileID=file)
    block2 = BlockTwo.objects.get(fileID=file)
    block3 = BlockThree.objects.get(fileID=file)

    # Verify HMACs
    if (generate_hmac(block1.encrypted, block1.secret_key_used) != block1.hmac or
        generate_hmac(block2.encrypted, block2.secret_key_used) != block2.hmac or
        generate_hmac(block3.encrypted, block3.secret_key_used) != block3.hmac):
        messages.error(request, "Integrity check failed. One or more blocks may have been tampered with.")
        return redirect('viewFiles')

    # Decrypt
    text1 = caesar_cipher_decrypt(block1.encrypted, block1.key_used)
    text2 = caesar_cipher_decrypt(block2.encrypted, block2.key_used)
    text3 = caesar_cipher_decrypt(block3.encrypted, block3.key_used)

    full_text = text1 + "\n" + text2 + "\n" + text3

    return render(request, 'decrypted_files.html', {
        'login': login,
        'userName': userN.userName,
        'fileName': file.fileName,
        'fileID': fileID,
        'decryptedText': full_text
    })

def downloadRequests(request, fileID):
    getFileData = UploadedDocument.objects.get(fileID=fileID)
    is_exists = userDownloadRequests.objects.filter(fileID=fileID, requested_user=getFileData.uplodedBy).exists()
    if is_exists:
        messages.error(request, 'You alrady send request for download')
        return redirect('viewFiles')
    else:
        userDownloadRequests.objects.create(
            requested_file_name=getFileData.fileName,
            requested_user=getFileData.uplodedBy,
            fileID=fileID
        )
        messages.error(request, 'Request send successfully')
        return redirect('viewFiles')
    
def viewDownloadRequests(request):
    login = request.session['login']
    userMail = request.session['user_email']
    getAllrequests = userDownloadRequests.objects.filter(status='pending')
    return render(request, 'viewDownloadRequests.html', {'login':login, 'requests':getAllrequests})

def approveRequest(request, requestID, fileID):
    getRequestDetails = userDownloadRequests.objects.get(requestID=requestID)
    getFileDetails = UploadedDocument.objects.get(fileID=fileID)

    getRequestDetails.status = 'accepted'
    getFileDetails.download_Request_status = 'accepted'

    getRequestDetails.save()
    getFileDetails.save()

    messages.success(request, 'Request accepted')
    return redirect('viewDownloadRequests')


def rejectRequest(request, requestID, fileID):
    getRequestDetails = userDownloadRequests.objects.get(requestID=requestID)
    getFileDetails = UploadedDocument.objects.get(fileID=fileID)

    getRequestDetails.status = 'rejected'
    getFileDetails.download_Request_status = 'rejected'

    getRequestDetails.save()
    getFileDetails.save()

    messages.success(request, 'Request rejected')
    return redirect('viewDownloadRequests')

def sendOTP(request, fileID):
    user = UploadedDocument.objects.get(fileID=fileID)
    otp = random.randint(100000,999999)
    user.otp = otp
    email_subject = 'OTP Details'
    email_message = f'Hello {user.uplodedBy},\n\nWelcome To Our Website!\n\nHere are your OTP details:\nEmail: {user.uplodedBy}\nOTP: {user.otp}\n\nPlease keep this information safe.\n\nBest regards,\nYour Website Team'
    send_mail(email_subject, email_message, settings.EMAIL_HOST_USER, [user.uplodedBy])
    user.save()
    return redirect('otp')

def otp(request):
    login = request.session['login']
    userMail = request.session['user_email']
    if request.method == "POST":
        print('-----')
        email = request.session['user_email']
        print(email)
        otp1 = request.POST['otp1']
        otp2 = request.POST['otp2']
        otp3 = request.POST['otp3']
        otp4 = request.POST['otp4']
        otp5 = request.POST['otp5']
        otp6 = request.POST['otp6']
        otp = int(otp1+otp2+otp3+otp4+otp5+otp6)
        # otp = int(otp1+otp2+otp3+otp4)
        if UploadedDocument.objects.filter(uplodedBy=email, otp=otp).exists():
            getDetail = UploadedDocument.objects.get(otp=otp)
            return redirect('decryptFile', fileID=getDetail.fileID)
        else:
            messages.success(request, 'Invalid Passsword!')
            return redirect('otp')
    return render(request, 'otp.html', {'login':login})


def downloadDecrypted(request, fileID):
    try:
        file = UploadedDocument.objects.get(fileID=fileID)
    

        block1 = BlockOne.objects.get(fileID=file)
        block2 = BlockTwo.objects.get(fileID=file)
        block3 = BlockThree.objects.get(fileID=file)

        # Verify HMACs
        if (generate_hmac(block1.encrypted, block1.secret_key_used) != block1.hmac or
            generate_hmac(block2.encrypted, block2.secret_key_used) != block2.hmac or
            generate_hmac(block3.encrypted, block3.secret_key_used) != block3.hmac):
            return HttpResponse("HMAC verification failed", status=403)

        # Decrypt
        text1 = caesar_cipher_decrypt(block1.encrypted, block1.key_used)
        text2 = caesar_cipher_decrypt(block2.encrypted, block2.key_used)
        text3 = caesar_cipher_decrypt(block3.encrypted, block3.key_used)

        full_text = f"{text1}\n{text2}\n{text3}"

        # Return as downloadable file
        response = HttpResponse(full_text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{smart_str(file.fileName)}_decrypted.txt"'
        return response

    except UploadedDocument.DoesNotExist:
        return HttpResponse("File not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
    
def view_all_users(request):
    login = request.session['login']
    userMail = request.session['user_email']
    allUsers = UserModel.objects.all()

    return render(request, 'view_users.html', {'users':allUsers, 'login':login})

def deleteUser(request, userID):
    getUserData = UserModel.objects.get(userID=userID)
    getUserData.delete()
    messages.success(request, 'User removed successfully')
    return redirect(view_all_users)

def view_user_uploaded_files(request):
    login = request.session['login']
    userMail = request.session['user_email']

    get_all_files = UploadedDocument.objects.all()
    return render(request, 'cloud_view_all_files.html', {'login':login, 'get_all_files':get_all_files})

def forgotPassword(req):
    if req.method == 'POST':
        userEmail = req.POST.get('studentmail') 
        if userEmail:

            userDetails = UserModel.objects.get(userEmail=userEmail)
            otp = random.randint(100000, 999999)
            userDetails.otp = otp
            userDetails.save()
            email_subject = 'Forgot password otp'
            email_message = f'Hello {userDetails.userName},\n\nThank you for registering with us!\n\nHere are your OTP details:\n\nOTP: {otp}\n\nPlease keep this otp safe and don\'t share anyone.\n\nBest regards,\nYour Website Team'
            send_mail(email_subject, email_message, settings.EMAIL_HOST_USER, [userDetails.userEmail])
            return render(req, 'enterOtp.html', {'userEmail':userEmail})
    return render(req, 'forgotpass.html')

def enterOtp(req, userEmail):
    if req.method == 'POST':
        userDetails = UserModel.objects.get(userEmail=userEmail)
        otp = req.POST.get('otp')
        if int(otp) == userDetails.otp:
            return render(req, 'newPassword.html', {'userEmail':userEmail})
        else:
            messages.error(req, 'Invalid otp')
            return redirect('enterOtp', userEmail=userEmail)
    return render(req, 'enterOtp.html')

def newPassword(req, userEmail):
    if req.method == 'POST':
        nPassword = req.POST.get('Npass')
        cPassword = req.POST.get('Cpass')
        if nPassword == cPassword:
            userDetails = UserModel.objects.get(userEmail=userEmail)
            userDetails.password=nPassword
            userDetails.confirmPassword=nPassword
            userDetails.save()
            messages.success(req, 'Password changed successfully')
            return redirect('userLogin')
        else:
            messages.error(req, 'Password not match')
            return redirect('newPassword', userEmail=userEmail)
    return render(req, 'newPassword.html', {'userEmail':userEmail})







