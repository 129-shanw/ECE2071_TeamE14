def calculate_checksum(text):
    checksum = 0
    for char in text:
        checksum ^= ord(char)  # XOR each character's ASCII value
    return checksum

# Example usage with the string "Test"
text = "I hate ECE2071 E14_0"
checksum = calculate_checksum(text)

print(f"Checksum for '{text}': {checksum} (Decimal), {hex(checksum)} (Hexadecimal)")