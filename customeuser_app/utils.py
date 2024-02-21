import pyotp


def return_secret_key(username: str):
    import hashlib
    user = str(username)
    key = hashlib.sha224(user.encode()).hexdigest()
    modify_key = ''
    for item in key:
        if item not in ['0', '1', '8', '9']:
            modify_key += item
    return modify_key.upper()


def send_otp(request):
    username = request.session['username']
    key = return_secret_key(username)
    totp = pyotp.TOTP(key)
    otp = totp.now()
    request.session['otp_secret_key'] = totp.secret
    print(f'Your one time password is {otp}')


def get_client_ip(request):
    """
    Get user's IP
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    return ip
