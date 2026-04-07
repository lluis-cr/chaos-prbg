# run_misdecrypt_image.R
# Decrypt the encrypted image with:
# 1) the correct key
# 2) a wrong key
# to demonstrate key sensitivity

source("helpers_image.R")

encrypted_image_path <- "~/Desktop/Models/Chaos-based PRBG encryption model/Data/generated/encrypted_img.png"
correct_key_path <- "~/Desktop/Models/Chaos-based PRBG encryption model/Data/generated/key_correct.txt"
wrong_key_path <- "~/Desktop/Models/Chaos-based PRBG encryption model/Data/generated/key_wrong.txt"

output_correct_path <- "~/Desktop/Models/Chaos-based PRBG encryption model/Data/generated/decrypted_correct.png"
output_wrong_path <- "~/Desktop/Models/Chaos-based PRBG encryption model/Data/generated/decrypted_wrong.png"

decrypt_image_with_key(
  encrypted_image_path = encrypted_image_path,
  key_path = correct_key_path,
  output_image_path = output_correct_path
)

decrypt_image_with_key(
  encrypted_image_path = encrypted_image_path,
  key_path = wrong_key_path,
  output_image_path = output_wrong_path
)

cat("Correct decryption saved to:", output_correct_path, "\n")
cat("Wrong-key decryption saved to:", output_wrong_path, "\n")