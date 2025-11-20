import pyotp
key = "UOKOZUJ4ETBDVIV4HBKK5V335DPBK3UX"
totp = pyotp.TOTP(key)

if __name__ == '__main__':
    print(totp.now())
