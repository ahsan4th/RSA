import streamlit as st
import random

def is_prime(n, k=5):
    """
    Miller-Rabin primality test.
    Returns True if n is probably prime, False otherwise.
    """
    if n <= 1 or n == 4:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    # Write n-1 as 2^s * d
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2

    # Repeat k times
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits):
    """
    Generates a probable prime number of the given bit length.
    """
    while True:
        p = random.getrandbits(bits)
        # Ensure the number is odd and within the bit length range
        p |= (1 << bits - 1) | 1 # Set MSB and LSB to 1
        if is_prime(p):
            return p

def gcd(a, b):
    """
    Calculates the Greatest Common Divisor (GCD) of a and b using Euclidean algorithm.
    """
    while b:
        a, b = b, a % b
    return a

def mod_inverse(a, m):
    """
    Calculates the modular multiplicative inverse of a modulo m using Extended Euclidean Algorithm.
    Returns x such that (a * x) % m == 1.
    """
    m0 = m
    y = 0
    x = 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        t = m
        m = a % m
        a = t
        t = y
        y = x - q * y
        x = t
    if x < 0:
        x = x + m0
    return x

def generate_keypair(bits=1024):
    """
    Generates an RSA public and private key pair.
    Returns ((n, e), (n, d)).
    """
    st.info(f"Step 1: Generating two large prime numbers (p and q) of {bits // 2} bits each...")
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)

    while p == q: # Ensure p and q are distinct
        q = generate_prime(bits // 2)

    n = p * q
    phi = (p - 1) * (q - 1)

    st.success(f"Generated p = {p}\nGenerated q = {q}")
    st.info(f"Step 2: Calculate n = p * q = {n}\n"
            f"Step 3: Calculate Euler's totient function phi(n) = (p-1)*(q-1) = {phi}")

    # Choose e such that 1 < e < phi and gcd(e, phi) = 1
    st.info("Step 4: Choose public exponent (e) such that 1 < e < phi and gcd(e, phi) = 1.")
    e = random.randint(2, phi - 1)
    while gcd(e, phi) != 1:
        e = random.randint(2, phi - 1)

    # Calculate d, the modular multiplicative inverse of e modulo phi
    st.info("Step 5: Calculate private exponent (d) as the modular multiplicative inverse of e modulo phi.")
    d = mod_inverse(e, phi)

    st.success(f"Public exponent (e) = {e}\nPrivate exponent (d) = {d}")

    return ((n, e), (n, d))

def encrypt(public_key, plaintext):
    """
    Encrypts the plaintext using the public key.
    Converts string to integers, encrypts each, returns list of integers.
    Note: This is a simplified character-by-character encryption for demonstration.
          In real RSA, entire messages/blocks are converted to numbers and padded.
    """
    n, e = public_key

    encrypted_msg_chars = []

    for char in plaintext:
        char_as_int = ord(char)
        # Check if character's ASCII value is too large for the key's 'n' value
        # This check is mostly for conceptual understanding in this simple demo,
        # as 'n' will usually be much larger than any char value in real RSA.
        if char_as_int >= n:
            st.error(f"Error: Character '{char}' (ASCII: {char_as_int}) is too large for the current key (n={n})."
                     " This simplified demo requires `ord(char) < n`. Please consider a larger key size"
                     " or a simpler message (e.g., ASCII characters).")
            return [] # Indicate error

        encrypted_char = pow(char_as_int, e, n)
        encrypted_msg_chars.append(encrypted_char)

    return encrypted_msg_chars

def decrypt(private_key, ciphertext):
    """
    Decrypts the ciphertext using the private key.
    Converts list of integers back to string.
    """
    n, d = private_key

    decrypted_chars = []
    for char_code in ciphertext:
        decrypted_char_int = pow(char_code, d, n)
        decrypted_chars.append(chr(decrypted_char_int))

    return "".join(decrypted_chars)

# --- Streamlit Application ---

st.set_page_config(page_title="RSA Cryptography Demo", layout="wide")

st.title("🔐 RSA Cryptography")
st.write("This application demonstrates the basic principles of RSA encryption and decryption.")

# Initialize session state for keys and messages
if 'public_key' not in st.session_state:
    st.session_state.public_key = None
if 'private_key' not in st.session_state:
    st.session_state.private_key = None
if 'encrypted_msg' not in st.session_state:
    st.session_state.encrypted_msg = []
if 'original_msg' not in st.session_state:
    st.session_state.original_msg = ""
if 'decrypted_msg' not in st.session_state:
    st.session_state.decrypted_msg = ""

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["1. Key Generation", "2. Encryption", "3. Decryption & Verification"])

# --- Section 1: Key Generation ---
if page == "1. Key Generation":
    st.header("1. Key Generation 🔑")
    st.markdown("Generate a pair of public and private RSA keys. The larger the key size, the more secure, but longer it takes to generate.")

    key_bits = st.slider("Select Key Size (bits)", min_value=128, max_value=2048, value=512, step=128)
    st.caption(f"This will generate two primes of {key_bits // 2} bits each, resulting in an `n` of approximately {key_bits} bits.")

    if st.button("Generate RSA Key Pair", type="primary"):
        with st.spinner("Generating keys... This may take a moment for larger sizes."):
            public, private = generate_keypair(key_bits)
            st.session_state.public_key = public
            st.session_state.private_key = private
            st.success("Keys generated successfully!")

            st.markdown("---")
            st.subheader("Generated Keys:")
            st.write(f"**Public Key (n, e):**")
            st.code(f"n = {public[0]}\ne = {public[1]}")
            st.write(f"**Private Key (n, d):**")
            st.code(f"n = {private[0]}\nd = {private[1]}")
            st.warning("🚨 Keep your private key secret!")

# --- Section 2: Encryption ---
elif page == "2. Encryption":
    st.header("2. Encryption 🔒")
    st.write("Enter the message you want to encrypt using the generated public key.")

    if st.session_state.public_key:
        n_pub, e_pub = st.session_state.public_key
        st.info(f"Current Public Key: `(n={n_pub}, e={e_pub})`")

        message_to_encrypt = st.text_area(
            "Plaintext Message",
            st.session_state.original_msg if st.session_state.original_msg else "Halo, ini adalah pesan rahasia dari Matematika Diskrit!",
            height=100
        )
        st.session_state.original_msg = message_to_encrypt # Update original_msg in session state

        if st.button("Encrypt Message", type="primary"):
            if not st.session_state.public_key:
                st.warning("🚫 Please generate keys in the 'Key Generation' section first.")
            else:
                encrypted_data = encrypt(st.session_state.public_key, message_to_encrypt)
                if encrypted_data: # Only update if encryption was successful (no character too large error)
                    st.session_state.encrypted_msg = encrypted_data
                    st.success("Message encrypted successfully!")
                    st.subheader("Encrypted Message:")
                    st.code(str(st.session_state.encrypted_msg))
                    st.info("This is a list of integers, each representing an encrypted character.")
                else:
                    st.error("Encryption failed. Please check the error message above regarding character size.")
    else:
        st.warning("🚫 Please generate keys in the 'Key Generation' section first to enable encryption.")


# --- Section 3: Decryption & Verification ---
elif page == "3. Decryption & Verification":
    st.header("3. Decryption & Verification ✅")
    st.write("The encrypted message from the previous step will be used automatically for decryption.")

    if st.session_state.private_key and st.session_state.encrypted_msg:
        n_priv, d_priv = st.session_state.private_key
        st.info(f"Current Private Key: `(n={n_priv}, d={d_priv})`")
        st.write(f"**Encrypted Message to Decrypt:**")
        st.code(str(st.session_state.encrypted_msg))

        if st.button("Decrypt Message", type="primary"):
            if not st.session_state.private_key:
                st.warning("🚫 Please generate keys first.")
            elif not st.session_state.encrypted_msg:
                st.warning("🚫 No message to decrypt. Please encrypt a message in the 'Encryption' section first.")
            else:
                decrypted_message = decrypt(st.session_state.private_key, st.session_state.encrypted_msg)
                st.session_state.decrypted_msg = decrypted_message
                st.success("Message decrypted successfully!")
                st.subheader("Decrypted Message:")
                st.code(decrypted_message)

                st.markdown("---")
                st.subheader("Verification")
                if st.session_state.original_msg == st.session_state.decrypted_msg:
                    st.success("🎉 Verification: Decryption Successful! The original message matches the decrypted message.")
                else:
                    st.error("❌ Verification: Decryption Failed! The original message DOES NOT match the decrypted message.")
                    st.write(f"**Original Message:** `{st.session_state.original_msg}`")
                    st.write(f"**Decrypted Message:** `{st.session_state.decrypted_msg}`")
    else:
        if not st.session_state.private_key:
            st.warning("🚫 Please generate keys in the 'Key Generation' section.")
        if not st.session_state.encrypted_msg:
            st.warning("🚫 Please encrypt a message in the 'Encryption' section.")

        if st.session_state.private_key and not st.session_state.encrypted_msg:
            st.info("Once you encrypt a message, it will automatically appear here for decryption.")

st.sidebar.markdown("---")
st.sidebar.caption("💡 Tip: Navigate through sections using the sidebar.")
st.markdown("---")
st.caption("Note: This is a simplified RSA implementation for educational purposes. "
           "Real-world RSA implementations use more complex padding schemes (e.g., OAEP) "
           "and typically encrypt symmetric keys (which then encrypt the message) rather than raw messages directly. "
           "Character-by-character encryption as done here is inefficient and has security limitations.")
