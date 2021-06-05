from urllib.parse import unquote

CHARACTER_MAP = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def decipher(encrypted_url: str):
    
    s1, s2 = encrypted_url[:9], encrypted_url[9:]
    crypto = 0
    
    decrypted = ""
    index = 0
    
    for index, character in enumerate(s2, 1):
        crypto <<= 6

        if character in CHARACTER_MAP:
            crypto |= CHARACTER_MAP.index(character)

        if index and not (index % 4):
            decrypted, crypto = decrypted + chr((0xff0000 & crypto) >> 16) + chr((0xff00 & crypto) >> 8) + chr(0xff & crypto), 0
        
    if index % 4 and not (index % 2):
        crypto >>= 4
        decrypted += chr(crypto)

    if index % 4 and not (index % 3):
        decrypted += chr((65280 & crypto) >> 8) + chr(255 & crypto)
            
    decrypted = unquote(decrypted)
    mapper = {byte_index: byte_index for byte_index in range(0x100)}
    xcrypto = 0

    for byte_index in range(0x100):
        xcrypto = (xcrypto + mapper.get(byte_index) + ord(s1[byte_index % len(s1)])) % 0x100
        mapper[byte_index], mapper[xcrypto] = mapper[xcrypto], mapper[byte_index]

    xcryptoz, xcryptoy = 0, 0
    
    cipher = ""
    
    for character in decrypted:
        xcryptoy = (xcryptoy + 1) % 0x100
        xcryptoz = (xcryptoz + mapper.get(xcryptoy)) % 0x100
        mapper[xcryptoy], mapper[xcryptoz] = mapper[xcryptoz], mapper[xcryptoy]
        appendlet = chr(ord(character) ^ mapper[(mapper[xcryptoy] + mapper[xcryptoz]) % 0x100])
        if appendlet.isascii():
            cipher += appendlet
        
    return cipher