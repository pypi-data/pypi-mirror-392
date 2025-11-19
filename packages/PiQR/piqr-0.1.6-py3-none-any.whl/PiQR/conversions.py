def binary_to_string(bits):
    # Convert a list of binary strings (bits) to their corresponding ASCII characters.
    return [chr(int(i, 2)) for i in bits]

def binary_to_int(bits):
    # Convert a list of binary strings (bits) to a list of integers.
    int_list = []
    for n in bits:
        dec_value = binary_to_float(n)
        int_list.append(dec_value)  # Append the converted decimal value to the list.

    return int_list  # Return the list of integers.

def binary_to_decimal(n):
    # Function to convert binary to ASCII value
    num = str(n)  # Convert the binary input to string for processing.
    dec_value = 0  # Initialize decimal value to accumulate the result.

    # Initialize base value to 1, which represents 2^0.
    base1 = 1

    len1 = len(num)  # Get the length of the binary string.
    # Iterate over the binary string from right to left.
    for i in range(len1 - 1, -1, -1):
        if (num[i] == '1'):  # If the current bit is '1', add the current base to the decimal value.
            dec_value += base1
        base1 = base1 * 2  # Move to the next base (2^n).

    return dec_value;

def binary_to_hex(bits):
    # Convert a list of binary strings (bits) to their corresponding hexadecimal representations.
    char = [chr(int(i, 2)) for i in bits]  # Convert binary to characters.
    # Format each character's ASCII value as a two-digit hexadecimal string.
    return ["{0:02x}".format(ord(i)) for i in char]

def int_to_binary(bits):
    # Convert a list of integers to a list of 8-bit binary strings.
    binary_list = []
    for num in bits:
        # Format the integer as binary and zero-fill to ensure it is 8 bits long.
        binary_data = format(int(num), 'b').zfill(8)
        binary_list.append(binary_data)  # Append the binary string to the list.

    return binary_list  # Return the list of binary strings.

def int_to_hex(bits):
    # Convert a list of integers to their hexadecimal representation by first converting to binary.
    return binary_to_hex(int_to_binary(bits))
