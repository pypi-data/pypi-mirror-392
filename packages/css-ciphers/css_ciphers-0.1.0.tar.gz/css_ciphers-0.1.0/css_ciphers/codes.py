def print_cipher_a():
    code = """
body {
    background: #222;
    color: #0f0;
    font-family: monospace;
}
"""
    print(code.strip())


def print_cipher_b():
    code = """
.container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
}
"""
    print(code.strip())

def help():
    code = """
    print_caesar_cipher()
    print_hill_cipher()
    print_playfair_cipher()
    print_rail_fence_cipher()
    print_columnar_transposition_cipher()
    print_double_columnar_transposition_cipher()
    print_vigenere_cipher()
    print_monoalphabetic_substitution_cipher()
    print_polyalphabetic_cipher()
    print_diffie_hellman()
    print_RSA()
    print_hash_generation()
    print_exp8()
    print_pgp()

"""
    print(code.strip())

def print_caesar_cipher():
    code = """
def caesar_encrypt(text, key):
    result = ""
    for char in text:
        if char.isalpha():
            shift = 65 if char.isupper() else 97
            result += chr((ord(char) - shift + key) % 26 + shift)
        else:
            result += char
    return result

def caesar_decrypt(cipher, key):
    return caesar_encrypt(cipher, -key)

text = input("Enter text: ")
key = int(input("Enter key: "))

enc = caesar_encrypt(text, key)
dec = caesar_decrypt(enc, key)

print("Encrypted:", enc)
print("Decrypted:", dec)

    """
    print(code.strip())


def print_hill_cipher():
    code = """
def matrix_mod_inv(matrix, modulus):
    # 2x2 matrix inverse mod 26
    a, b = matrix[0]
    c, d = matrix[1]

    det = (a * d - b * c) % modulus
    det_inv = pow(det, -1, modulus)  # modular inverse of determinant

    inv_matrix = [
        [( d * det_inv) % modulus, (-b * det_inv) % modulus],
        [(-c * det_inv) % modulus, ( a * det_inv) % modulus]
    ]
    return inv_matrix


def matrix_mult(matrix, vector, modulus):
    result = []
    for row in matrix:
        val = sum(row[i] * vector[i] for i in range(len(vector))) % modulus
        result.append(val)
    return result


def hill_encrypt(text, key_matrix):
    text = text.upper().replace(" ", "")
    
    # Padding: if odd length add X
    if len(text) % 2 != 0:
        text += "X"

    cipher = ""
    for i in range(0, len(text), 2):
        block = [ord(c) - 65 for c in text[i:i+2]]
        result = matrix_mult(key_matrix, block, 26)
        cipher += ''.join(chr(num + 65) for num in result)

    return cipher


def hill_decrypt(cipher, key_matrix):
    inv_matrix = matrix_mod_inv(key_matrix, 26)
    text = ""

    for i in range(0, len(cipher), 2):
        block = [ord(c) - 65 for c in cipher[i:i+2]]
        result = matrix_mult(inv_matrix, block, 26)
        text += ''.join(chr(num + 65) for num in result)

    return text


plaintext = input("Enter plaintext: ").upper().replace(" ", "")
print("Enter 2x2 Key Matrix values:")

a = int(input("a: "))
b = int(input("b: "))
c = int(input("c: "))
d = int(input("d: "))

key_matrix = [[a, b],
              [c, d]]

cipher = hill_encrypt(plaintext, key_matrix)
print("Encrypted Text:", cipher)

decrypted = hill_decrypt(cipher, key_matrix)
print("Decrypted Text:", decrypted)

"""
    print(code.strip())

  

def print_playfair_cipher():
    code = """
def generate_matrix(key):
    key = key.upper().replace("J", "I")
    matrix = []
    used = set()

    for ch in key:
        if ch.isalpha() and ch not in used:
            used.add(ch)
            matrix.append(ch)

    for ch in "ABCDEFGHIKLMNOPQRSTUVWXYZ":
        if ch not in used:
            used.add(ch)
            matrix.append(ch)

    matrix5 = [matrix[i:i+5] for i in range(0, 25, 5)]
    return matrix5

def show_matrix(matrix):
    print("5x5 Key Matrix:")
    for row in matrix:
        print(" ".join(row))
    print()

def prepare_text_encrypt(text):
    text = text.upper().replace(" ", "").replace("J", "I")
    result = ""
    i = 0
    while i < len(text):
        a = text[i]
        b = text[i+1] if i+1 < len(text) else 'X'
        if a == b:
            result += a + 'X'
            i += 1
        else:
            result += a + b
            i += 2
    if len(result) % 2 != 0:
        result += 'X'
    return result

def find_pos(matrix, ch):
    for i in range(5):
        for j in range(5):
            if matrix[i][j] == ch:
                return i, j

def encrypt(text, matrix):
    text = prepare_text_encrypt(text)
    cipher = ""
    for i in range(0, len(text), 2):
        a, b = text[i], text[i+1]
        r1, c1 = find_pos(matrix, a)
        r2, c2 = find_pos(matrix, b)

        if r1 == r2:
            cipher += matrix[r1][(c1+1) % 5]
            cipher += matrix[r2][(c2+1) % 5]
        elif c1 == c2:
            cipher += matrix[(r1+1) % 5][c1]
            cipher += matrix[(r2+1) % 5][c2]
        else:
            cipher += matrix[r1][c2]
            cipher += matrix[r2][c1]
    return cipher

def decrypt(cipher, matrix):
    plain = ""
    for i in range(0, len(cipher), 2):
        a, b = cipher[i], cipher[i+1]
        r1, c1 = find_pos(matrix, a)
        r2, c2 = find_pos(matrix, b)

        if r1 == r2:
            plain += matrix[r1][(c1-1) % 5]
            plain += matrix[r2][(c2-1) % 5]
        elif c1 == c2:
            plain += matrix[(r1-1) % 5][c1]
            plain += matrix[(r2-1) % 5][c2]
        else:
            plain += matrix[r1][c2]
            plain += matrix[r2][c1]
    return plain

text = input("Enter plaintext: ")
key = input("Enter key: ")

matrix = generate_matrix(key)
show_matrix(matrix)

cipher = encrypt(text, matrix)
print("Encrypted:", cipher)

plain = decrypt(cipher, matrix)
print("Decrypted:", plain)


"""
    print(code.strip())
  

def print_rail_fence_cipher():
    code = """
def rail_fence_encrypt(text, key):
    rail = ['' for _ in range(key)]
    row = 0
    direction = 1

    for char in text:
        rail[row] += char
        row += direction
        if row == 0 or row == key - 1:
            direction *= -1

    return "".join(rail)

def rail_fence_decrypt(cipher, key):
    rail_len = len(cipher)
    rail = [['' for _ in range(rail_len)] for _ in range(key)]

    row, direction = 0, 1
    for i in range(rail_len):
        rail[row][i] = '*'
        row += direction
        if row == 0 or row == key - 1:
            direction *= -1

    index = 0
    for r in range(key):
        for c in range(rail_len):
            if rail[r][c] == '*' and index < rail_len:
                rail[r][c] = cipher[index]
                index += 1

    result = ""
    row, direction = 0, 1
    for i in range(rail_len):
        result += rail[row][i]
        row += direction
        if row == 0 or row == key - 1:
            direction *= -1

    return result

text = input("Enter text: ")
key = int(input("Enter key (rails): "))

enc = rail_fence_encrypt(text, key)
dec = rail_fence_decrypt(enc, key)

print("Encrypted:", enc)
print("Decrypted:", dec)


"""
    print(code.strip())

  
def print_columnar_transposition_cipher():
    code = """
def get_order(key):
    order = sorted(list(enumerate(key)), key=lambda x: x[1])
    return [idx for idx, _ in order]

def encrypt(plaintext, key):
    plaintext = plaintext.replace(" ", "").upper()
    cols = len(key)
    rows = -(-len(plaintext) // cols)
    padded = plaintext.ljust(rows * cols, 'X')
    matrix = [padded[i:i+cols] for i in range(0, len(padded), cols)]
    order = get_order(key)
    cipher = ""
    for col in order:
        for row in matrix:
            cipher += row[col]
    return cipher

def decrypt(ciphertext, key):
    ciphertext = ciphertext.replace(" ", "").upper()
    cols = len(key)
    rows = len(ciphertext) // cols
    order = get_order(key)
    matrix = [[""] * cols for _ in range(rows)]
    index = 0
    for col in order:
        for row in range(rows):
            matrix[row][col] = ciphertext[index]
            index += 1
    plaintext = "".join("".join(row) for row in matrix)
    return plaintext

plaintext = input("Enter plaintext: ")
key = input("Enter key: ").upper()

cipher = encrypt(plaintext, key)
print("Encrypted Text:", cipher)

decrypted = decrypt(cipher, key)
print("Decrypted Text:", decrypted)



"""
    print(code.strip())

  
def print_double_columnar_transposition_cipher():
    code = """
def get_order(key):
    order = sorted(list(enumerate(key)), key=lambda x: x[1])
    return [idx for idx, _ in order]

def encrypt_once(plaintext, key):
    plaintext = plaintext.replace(" ", "").upper()
    cols = len(key)
    rows = -(-len(plaintext) // cols)
    padded = plaintext.ljust(rows * cols, 'X')
    matrix = [padded[i:i+cols] for i in range(0, len(padded), cols)]
    order = get_order(key)
    cipher = ""
    for col in order:
        for row in matrix:
            cipher += row[col]
    return cipher

def decrypt_once(ciphertext, key):
    ciphertext = ciphertext.replace(" ", "").upper()
    cols = len(key)
    rows = len(ciphertext) // cols
    order = get_order(key)
    matrix = [[""] * cols for _ in range(rows)]
    index = 0
    for col in order:
        for row in range(rows):
            matrix[row][col] = ciphertext[index]
            index += 1
    plaintext = "".join("".join(row) for row in matrix)
    return plaintext

def double_encrypt(plaintext, key1, key2):
    first = encrypt_once(plaintext, key1)
    second = encrypt_once(first, key2)
    return second

def double_decrypt(ciphertext, key1, key2):
    first = decrypt_once(ciphertext, key2)
    second = decrypt_once(first, key1)
    return second

plaintext = input("Enter plaintext: ")
key1 = input("Enter key 1: ").upper()
key2 = input("Enter key 2: ").upper()

cipher = double_encrypt(plaintext, key1, key2)
print("Encrypted Text:", cipher)

decrypted = double_decrypt(cipher, key1, key2)
print("Decrypted Text:", decrypted)


"""
    print(code.strip())

  
def print_vigenere_cipher():
    code = """
def generate_key(text, key):
    key = key.upper()
    key = list(key)
    if len(key) < len(text):
        key = key * (len(text) // len(key)) + key[:len(text) % len(key)]
    return "".join(key)

def encrypt(text, key):
    text = text.upper().replace(" ", "")
    key = generate_key(text, key)
    cipher = ""
    for t, k in zip(text, key):
        cipher += chr((ord(t) + ord(k) - 2*65) % 26 + 65)
    return cipher

def decrypt(cipher, key):
    cipher = cipher.upper().replace(" ", "")
    key = generate_key(cipher, key)
    text = ""
    for c, k in zip(cipher, key):
        text += chr((ord(c) - ord(k) + 26) % 26 + 65)
    return text

plaintext = input("Enter plaintext: ")
key = input("Enter key: ")

cipher = encrypt(plaintext, key)
print("Encrypted:", cipher)

decrypted = decrypt(cipher, key)
print("Decrypted:", decrypted)
"""
    print(code.strip())

  
def print_monoalphabetic_substitution_cipher():
    code = """
def encrypt(text, key):
    text = text.upper().replace(" ", "")
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    cipher = ""
    for ch in text:
        cipher += key[alphabet.index(ch)]
    return cipher

def decrypt(cipher, key):
    cipher = cipher.upper().replace(" ", "")
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    text = ""
    for ch in cipher:
        text += alphabet[key.index(ch)]
    return text

plaintext = input("Enter plaintext: ")
key = input("Enter substitution key (26 letters): ").upper()

cipher = encrypt(plaintext, key)
print("Encrypted:", cipher)

decrypted = decrypt(cipher, key)
print("Decrypted:", decrypted)
"""
    print(code.strip())

  
def print_polyalphabetic_cipher():
    code = """
def encrypt(text, key_list):
    text = text.upper().replace(" ", "")
    cipher = ""
    k = len(key_list)
    for i, ch in enumerate(text):
        shift = key_list[i % k]
        cipher += chr((ord(ch) - 65 + shift) % 26 + 65)
    return cipher

def decrypt(cipher, key_list):
    cipher = cipher.upper().replace(" ", "")
    text = ""
    k = len(key_list)
    for i, ch in enumerate(cipher):
        shift = key_list[i % k]
        text += chr((ord(ch) - 65 - shift) % 26 + 65)
    return text

plaintext = input("Enter plaintext: ")
key_str = input("Enter numeric key sequence (e.g., 3 1 4 2): ")

key_list = list(map(int, key_str.split()))

cipher = encrypt(plaintext, key_list)
print("Encrypted:", cipher)

decrypted = decrypt(cipher, key_list)
print("Decrypted:", decrypted)


"""
    print(code.strip())

def print_diffie_hellman():
    code = """
def diffie_hellman(p, g, a, b):
    A = pow(g, a, p)   # Alice sends A
    B = pow(g, b, p)   # Bob sends B

    secret1 = pow(B, a, p)   # Alice computes shared secret
    secret2 = pow(A, b, p)   # Bob computes shared secret

    return A, B, secret1, secret2

p = int(input("Enter prime number p: "))
g = int(input("Enter primitive root g: "))
a = int(input("Enter Alice's private key a: "))
b = int(input("Enter Bob's private key b: "))

A, B, secret1, secret2 = diffie_hellman(p, g, a, b)

print("Alice sends A =", A)
print("Bob sends B =", B)
print("Shared Secret (Alice computes):", secret1)
print("Shared Secret (Bob computes):", secret2)


----OR----
import secrets
import hashlib
import sys

class DiffieHellmanLab:
    def __init__(self):
        self.p = None
        self.g = None
        self.a = None  # Alice's private key
        self.A = None  # Alice's public key
        self.b = None  # Bob's private key
        self.B = None  # Bob's public key
        self.shared_secret_A = None
        self.shared_secret_B = None
        self.symmetric_key = None

    def run(self):
        while True:
            print("--- Diffie-Hellman Key Exchange Lab ---")
            print("1) Select / Generate Public Parameters (p, g)")
            print("2) Generate Keys for Alice and Bob")
            print("3) Compute Shared Secret")
            print("4) Derive Symmetric Key & Demo Encrypt/Decrypt")
            print("5) Exit")
            
            choice = input("Enter choice: ")

            if choice == '1':
                self.step_1_parameters()
            elif choice == '2':
                self.step_2_generate_keys()
            elif choice == '3':
                self.step_3_compute_secret()
            elif choice == '4':
                self.step_4_demo_encryption()
            elif choice == '5':
                print("Exiting.")
                sys.exit()
            else:
                print("Invalid choice.")

    def step_1_parameters(self):
        print("--- Step 1: Public Parameters ---")
        print("A) Use Standard 2048-bit MODP Group (RFC 3526) - Recommended for Security")
        print("B) Generate smaller prime (Demo/Speed)")
        
        sub_choice = input("Select option (A/B): ").upper()
        
        if sub_choice == 'A':
            # RFC 3526 2048-bit MODP Group
            self.p = int("FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1
            29024E088A67CC74020BBEA63B139B22514A08798E3404DD
            EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245
            E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED
            EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D
            C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F
            83655D23DCA3AD961C62F356208552BB9ED529077096966D
            670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B
            E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9
            DE2BCBF6955817183995497CEA956AE515D2261898FA0510
            15728E5A8AACAA68FFFFFFFFFFFFFFFF
            ".replace().replace('[write slash n here and doc string]', ''), 16)
            self.g = 2
            print(f"[*] Standard parameters selected.")
            print(f"[*] g = {self.g}")
            print(f"[*] p (first 50 digits) = {str(self.p)[:50]}...")
            
        elif sub_choice == 'B':
            # Small prime for manual verification/demo
            print("[*] Generating 512-bit safe prime... (this may take a moment)")
            # Using a fixed safe prime for demo reliability to avoid lag during lab
            self.p = 639817038649168399603704235784493088759024526692173718362230893703439865259631305644870259945273014636210375181083420335113769523075842925931268581
            self.g = 2
            print(f"[*] Demo parameters set.")
            print(f"[*] p = {self.p}")
            print(f"[*] g = {self.g}")
        
        # Reset keys if params change
        self.a, self.A, self.b, self.B = None, None, None, None
        self.shared_secret_A, self.symmetric_key = None, None

    def step_2_generate_keys(self):
        if not self.p or not self.g:
            print("[!] Error: Please select parameters (Option 1) first.")
            return

        print("--- Step 2: Key Generation ---")
        
        # Alice generates private key a in [2, p-2]
        # Using secrets module for cryptographic randomness 
        self.a = 2 + secrets.randbelow(self.p - 3)
        self.A = pow(self.g, self.a, self.p) # Efficient modular exponentiation
        
        # Bob generates private key b in [2, p-2]
        self.b = 2 + secrets.randbelow(self.p - 3)
        self.B = pow(self.g, self.b, self.p)

        print("[*] Keys Generated.")
        print(f"[*] Alice's Public Key (A) = {str(self.A)[:50]}...")
        print(f"[*] Bob's Public Key (B)   = {str(self.B)[:50]}...")
        
        show_priv = input("Display private keys (a, b)? (y/n): ")
        if show_priv.lower() == 'y':
            print(f"[*] Alice's Private Key (a) = {self.a}")
            print(f"[*] Bob's Private Key (b)   = {self.b}")
        else:
            print("[*] Private keys hidden.")

    def step_3_compute_secret(self):
        if not self.A or not self.B:
            print("[!] Error: Please generate keys (Option 2) first.")
            return

        print("--- Step 3: Compute Shared Secret ---")
        
        # Alice computes secret
        self.shared_secret_A = pow(self.B, self.a, self.p)
        
        # Bob computes secret
        self.shared_secret_B = pow(self.A, self.b, self.p)
        
        print(f"[*] Alice computes: B^a mod p = {str(self.shared_secret_A)[:50]}...")
        print(f"[*] Bob computes:   A^b mod p = {str(self.shared_secret_B)[:50]}...")
        
        if self.shared_secret_A == self.shared_secret_B:
            print("[SUCCESS] Shared secrets match!")
        else:
            print("[FAIL] Secrets do not match (Check implementation).")

    def step_4_demo_encryption(self):
        if not self.shared_secret_A:
            print("[!] Error: Please compute shared secret (Option 3) first.")
            return

        print("--- Step 4: Encryption Demo ---")
        
        # 1. Key Derivation Function (SHA-256)
        # Convert integer secret to bytes
        secret_bytes = str(self.shared_secret_A).encode('utf-8')
        # Hash to get 256-bit symmetric key
        self.symmetric_key = hashlib.sha256(secret_bytes).digest()
        
        print(f"[*] Derived Symmetric Key (SHA-256) Hex: {self.symmetric_key.hex()}")
        
        # 2. Encryption (Simple XOR Stream)
        plaintext = input("Enter a short message to encrypt: ")
        plaintext_bytes = plaintext.encode('utf-8')
        
        # XOR encryption logic
        ciphertext = bytearray()
        for i, byte in enumerate(plaintext_bytes):
            key_byte = self.symmetric_key[i % len(self.symmetric_key)]
            ciphertext.append(byte ^ key_byte)
            
        print(f"[*] Ciphertext (Hex): {ciphertext.hex()}")
        
        # 3. Decryption (XOR again)
        recovered_bytes = bytearray()
        for i, byte in enumerate(ciphertext):
            key_byte = self.symmetric_key[i % len(self.symmetric_key)]
            recovered_bytes.append(byte ^ key_byte)
            
        try:
            recovered_text = recovered_bytes.decode('utf-8')
            print(f"[*] Recovered Plaintext: {recovered_text}")
        except UnicodeDecodeError:
            print("[!] Error decoding recovered text.")

if __name__ == "__main__":
    lab = DiffieHellmanLab()
    lab.run()
"""
    print(code.strip())

  
def print_RSA():
    code = """
import secrets, math

def is_probable_prime(n, k=8):
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    for sp in small_primes:
        if n == sp:
            return True
        if n % sp == 0:
            return False
    s, d = 0, n - 1
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for __ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits):
    while True:
        p = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(p):
            return p

def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        return None
    return x % m

def rsa_keygen(bits):
    p = generate_prime(bits)
    q = generate_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    while True:
        e = secrets.randbelow(phi - 2) + 2
        if math.gcd(e, phi) == 1:
            break
    d = modinv(e, phi)
    return (e, n), (d, n)

def rsa_encrypt(msg, pub):
    e, n = pub
    return pow(msg, e, n)

def rsa_decrypt(cipher, priv):
    d, n = priv
    return pow(cipher, d, n)

def menu():
    pub = None
    priv = None

    while True:
        print("==== RSA Menu ====")
        print("1) Generate RSA Keys")
        print("2) Encrypt Message")
        print("3) Decrypt Message")
        print("0) Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            bits = int(input("Enter key size (e.g., 128, 256): "))
            pub, priv = rsa_keygen(bits)
            print("Public key:", pub)
            print("Private key:", priv)

        elif choice == "2":
            if pub is None:
                print("Generate keys first.")
                continue
            msg = int(input("Enter message (integer): "))
            ct = rsa_encrypt(msg, pub)
            print("Ciphertext:", ct)

        elif choice == "3":
            if priv is None:
                print("Generate keys first.")
                continue
            ct = int(input("Enter ciphertext: "))
            pt = rsa_decrypt(ct, priv)
            print("Decrypted message:", pt)

        elif choice == "0":
            break

        else:
            print("Invalid choice.")

if __name__ == "_main_":
    menu()


"""
    print(code.strip())

  
def print_hash_generation():
    code = """
# -------- HASH GENERATION AND CHECKSUM VERIFICATION --------

import hashlib
import os
import sys

def compute_hashes(filename):
    hashes = {
        "MD5": hashlib.md5(),
        "SHA1": hashlib.sha1(),
        "SHA256": hashlib.sha256(),
        "SHA512": hashlib.sha512()
    }
    with open(filename, "rb") as f:
        while chunk := f.read(4096):
            for h in hashes.values():
                h.update(chunk)
    return {name: h.hexdigest() for name, h in hashes.items()}

def save_hash_report(filename, hashes):
    with open("hash_report.txt", "w") as report:
        report.write(f"Hash Report for file: {filename}\n")
        report.write("-" * 50 + "\n")
        for algo, value in hashes.items():
            report.write(f"{algo}: {value}\n")
    print("[+] Hash report saved as hash_report.txt")

def create_checksum_file(filename, sha256_hash):
    checksum_filename = f"{filename}.sha256"
    with open(checksum_filename, "w") as f:
        f.write(f"{sha256_hash}  {filename}\n")
    print(f"[+] Checksum file created: {checksum_filename}")

def verify_checksum(filename):
    checksum_filename = f"{filename}.sha256"
    if not os.path.exists(checksum_filename):
        print("[-] No checksum file found. Run in 'generate' mode first.")
        return
    with open(checksum_filename, "r") as f:
        stored_hash, stored_filename = f.read().strip().split("  ")

    recomputed_hash = compute_hashes(filename)["SHA256"]

    if recomputed_hash == stored_hash:
        print("[✓] Checksum OK (Authentic)")
    else:
        print("[✗] Checksum FAILED (Tampered)")

# ---------------- Main Execution ----------------
if _name_ == "_main_":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python exp5.py generate <filename>")
        print("  python exp5.py verify <filename>")
        sys.exit(1)

    mode, filename = sys.argv[1], sys.argv[2]

    if mode == "generate":
        hashes = compute_hashes(filename)
        save_hash_report(filename, hashes)
        create_checksum_file(filename, hashes["SHA256"])
    elif mode == "verify":
        verify_checksum(filename)
    else:
        print("Invalid mode. Use 'generate' or 'verify'.")

# Create a second file (example.txt):
This is a large sample file for demonstrating cryptographic hash generation.
The purpose of this file is to provide enough content (more than 3 hundred characters)
so that it can be used as a proper test case for MD5, SHA-1, SHA-256, and SHA-512 hash functions.
We will compute all the hash values and verify the integrity using checksum files.
"""
    print(code.strip())

  
def print_exp8():
    code = """
# -------- EXPERIMENT 8 --------
sudo iptables -L


sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT


sudo iptables -L



sudo iptables -A INPUT -p tcp --dport 22 -j
ACCEPT 

sudo iptables -A INPUT -p tcp --dport 80
-j ACCEPT

sudo iptables -L


sudo iptables -A INPUT -s 192.168.1.100 -j DROP

sudo iptables -L



sudo iptables-save > rules.v4

sudo iptables -L


ssh user@192.168.1.100

curl http://192.168.1.100


ping 192.168.1.100


"""
    print(code.strip())

  
def print_pgp():
    code = """
# -------- EXPERIMENT 6 --------

0. Install PGP / GPG
--------------------
Linux (Ubuntu/Debian):
sudo apt update
sudo apt install gnupg


0. Setup
--------
mkdir pgp_lab
cd pgp_lab
gpg --version

1. Generate PGP Key Pairs
-------------------------
gpg --full-generate-key
Choose:
1 (RSA+RSA)
4096 bits
0 expiry
Name: Alice Example
Email: alice@example.com

Repeat for Bob Example.

List keys:
gpg --list-keys
gpg --list-secret-keys

2. Export / Import Keys
-----------------------
Alice exports:
gpg --armor --export alice@example.com > alice_pub.asc

Bob exports:
gpg --armor --export bob@example.com > bob_pub.asc

Import:
gpg --import alice_pub.asc
gpg --import bob_pub.asc

3. Revocation Certificate
-------------------------
Alice:
gpg --output alice-revoke.asc --gen-revoke alice@example.com
Bob:
gpg --output bob-revoke.asc --gen-revoke bob@example.com

4. Encrypt / Decrypt Files
--------------------------
Create file:
echo "Hello Alice" > message.txt

Bob encrypts for Alice:
gpg --encrypt --recipient alice@example.com --armor -o message_to_alice.asc message.txt

Alice decrypts:
gpg --output decrypted.txt --decrypt message_to_alice.asc

5. Digital Signatures
---------------------
Detached signature:
gpg --output report.sig --detach-sign report.pdf

Verify:
gpg --verify report.sig report.pdf

Clearsign:
gpg --clearsign message.txt
Verify:
gpg --verify message.txt.asc

6. Encrypt + Sign Together
--------------------------
Alice:
gpg --encrypt --sign --recipient bob@example.com --armor -o message_to_bob.asc message.txt

Bob decrypts:
gpg --decrypt message_to_bob.asc

7. Trust Management
-------------------
Sign Bob's key:
gpg --sign-key bob@example.com

Set trust:
gpg --edit-key bob@example.com
trust
quit

8. Revoke Key
-------------
gpg --import alice-revoke.asc
"""
    print(code.strip())