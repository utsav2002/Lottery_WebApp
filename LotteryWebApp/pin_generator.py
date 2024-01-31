# This generates 5 random pins for 2FA
import pyotp
for i in range(5):
    print(pyotp.random_base32())