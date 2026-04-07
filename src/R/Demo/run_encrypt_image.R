# run_encrypt_image.R
# Encrypt a grayscale PNG image using a PRBG-generated key

source("helpers_image.R")

input_image_path <- "~/Desktop/Models/Chaos-based PRBG encryption model/Data/input/fractal.png"
key_path <- "~/Desktop/Models/Chaos-based PRBG encryption model/Data/generated/key_correct.txt"
output_encrypted_path <- "~/Desktop/Models/Chaos-based PRBG encryption model/Data/generated/encrypted_img.png"

encrypt_image_with_key(
  input_image_path = input_image_path,
  key_path = key_path,
  output_image_path = output_encrypted_path
)

setwd("~/Desktop/Models/Chaos-based PRBG encryption model/R (PRBG)/Demo")
