# helpers_image.R
# Reusable functions for image <-> bit conversion and XOR encryption/decryption

library(png)

read_grayscale_png <- function(path) {
  img <- readPNG(path)
  
  if (length(dim(img)) == 3) {
    img <- 0.299 * img[, , 1] + 0.587 * img[, , 2] + 0.114 * img[, , 3]
  }
  
  img
}

image_to_bits <- function(img_matrix) {
  pixel_vals <- as.integer(round(img_matrix * 255))
  pixel_vals[pixel_vals < 0] <- 0
  pixel_vals[pixel_vals > 255] <- 255
  
  bits <- unlist(lapply(pixel_vals, function(v) {
    rev(as.integer(intToBits(v))[1:8])
  }))
  
  list(bits = bits, dims = dim(img_matrix))
}

bits_to_image <- function(bits, dims) {
  if (length(bits) %% 8 != 0) {
    stop("Bit length must be divisible by 8.")
  }
  
  bit_matrix <- matrix(bits, ncol = 8, byrow = TRUE)
  
  vals <- apply(bit_matrix, 1, function(b) {
    sum(b * 2^(7:0))
  })
  
  matrix(vals / 255, nrow = dims[1], ncol = dims[2], byrow = FALSE)
}

read_key_bits <- function(path) {
  key_string <- paste(readLines(path, warn = FALSE), collapse = "")
  key_chars <- strsplit(key_string, "")[[1]]
  
  if (!all(key_chars %in% c("0", "1"))) {
    stop("Key file contains non-binary characters.")
  }
  
  as.integer(key_chars)
}

xor_bits <- function(a, b) {
  if (length(a) != length(b)) {
    stop(sprintf("Length mismatch: %d vs %d", length(a), length(b)))
  }
  
  as.integer((a + b) %% 2)
}

encrypt_image_with_key <- function(input_image_path, key_path, output_image_path) {
  img <- read_grayscale_png(input_image_path)
  img_bits_info <- image_to_bits(img)
  
  image_bits <- img_bits_info$bits
  dims <- img_bits_info$dims
  key_bits <- read_key_bits(key_path)
  
  if (length(key_bits) != length(image_bits)) {
    stop(sprintf(
      "Key length (%d) does not match image bit length (%d).",
      length(key_bits), length(image_bits)
    ))
  }
  
  cat("Image dimensions:", paste(dims, collapse = " x "), "\n")
  cat("Total image bits:", length(image_bits), "\n")
  cat("Total key bits:", length(key_bits), "\n")
  
  encrypted_bits <- xor_bits(image_bits, key_bits)
  encrypted_img <- bits_to_image(encrypted_bits, dims)
  
  writePNG(encrypted_img, target = output_image_path)
  cat("Encrypted image saved to:", output_image_path, "\n")
}

decrypt_image_with_key <- function(encrypted_image_path, key_path, output_image_path) {
  enc_img <- read_grayscale_png(encrypted_image_path)
  enc_bits_info <- image_to_bits(enc_img)
  
  enc_bits <- enc_bits_info$bits
  dims <- enc_bits_info$dims
  key_bits <- read_key_bits(key_path)
  
  if (length(key_bits) != length(enc_bits)) {
    stop(sprintf(
      "Key length (%d) does not match encrypted image bit length (%d).",
      length(key_bits), length(enc_bits)
    ))
  }
  
  decrypted_bits <- xor_bits(enc_bits, key_bits)
  decrypted_img <- bits_to_image(decrypted_bits, dims)
  
  writePNG(decrypted_img, target = output_image_path)
  cat("Decrypted image saved to:", output_image_path, "\n")
}