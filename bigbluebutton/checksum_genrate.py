import hashlib


def generate_sha1_hash(data):
    # Create a new SHA-1 hash object
    sha1_hash = hashlib.sha1()

    # Update the hash object with the bytes-like object of the input data
    sha1_hash.update(data.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    return sha1_hash.hexdigest()


def checksum_genration(prameters,shearscreatekey):
    mtext = prameters+shearscreatekey

    return generate_sha1_hash(mtext)
