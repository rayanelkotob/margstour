# Read the multi-line base64 string from a file
with open("encoded-key.txt", "r") as file:
    multi_line_string = file.read()

# Replace newline characters to make it a single line
single_line_string = "".join(multi_line_string.splitlines())

# Save the single-line string to a new file
with open("encoded_key_single_line.txt", "w") as file:
    file.write(single_line_string)

print("Single-line base64 string saved to 'encoded_credentials_single_line.txt'")
