from urllib.parse import unquote


def decipher(encrypted_uri):
    """
    Credits to: https://github.com/anime-dl/anime-downloader/blob/master/anime_downloader/sites/nineanime.py#L70
    """
    str1 = encrypted_uri[:9]
    str2 = encrypted_uri[9:]

    encodedNum = 0
    counter = 0
    part1 = ""

    for char in str2:
        encodedNum <<= 6

        try:
            letterNum = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'.index(char)
            encodedNum |= letterNum
        except:
            pass

        counter += 1

        if counter == 4:
            part1 += chr((16711680 & encodedNum) >> 16)
            part1 += chr((65280 & encodedNum) >> 8)
            part1 += chr(255 & encodedNum)

            encodedNum = 0
            counter = 0

    if counter == 2:
        encodedNum >>= 4
        part1 += chr(encodedNum)
    elif counter == 3:
        encodedNum >>2
        part1 += chr((65280 & encodedNum) >> 8)
        part1 += chr(255 & encodedNum)

    try:
        part1 = unquote(part1)
    except:
        pass

    arr = {}
    i = 0
    byteSize = 256
    final = ""

    for c in range(byteSize):
        arr[c] = c

    x = 0
    for c in range(byteSize):
        x = (x + arr[c] + ord(str1[c % len(str1)])) % byteSize
        i = arr[c]
        arr[c] = arr[x]
        arr[x] = i

    x = 0
    d = 0

    for s in range(len(part1)):
        d = (d + 1) % byteSize
        x = (x + arr[d]) % byteSize

        i = arr[d]
        arr[d] = arr[x]
        arr[x] = i

        final += chr(ord(part1[s]) ^ arr[(arr[d] + arr[x]) % byteSize])

    return final