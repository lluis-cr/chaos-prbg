# helpers_prbg.R
# Reusable functions for:
# logistic map -> deep-zoom -> scale-based binarization -> bitstring export

# ---------------------------
# Core chaotic map
# ---------------------------

f_logistic <- function(x, r) {
  r * x * (1 - x)
}

# ---------------------------
# Sequence generation
# ---------------------------

generate_logistic_sequence <- function(x0, r, total_n) {
  if (!is.numeric(x0) || length(x0) != 1 || x0 <= 0 || x0 >= 1) {
    stop("x0 must be a single numeric value in (0, 1).")
  }
  
  if (!is.numeric(r) || length(r) != 1 || r <= 0 || r > 4) {
    stop("r must be a single numeric value in (0, 4].")
  }
  
  if (!is.numeric(total_n) || length(total_n) != 1 || total_n < 2) {
    stop("total_n must be an integer >= 2.")
  }
  
  total_n <- as.integer(total_n)
  
  vals <- numeric(total_n)
  vals[1] <- x0
  
  for (i in 2:total_n) {
    vals[i] <- f_logistic(vals[i - 1], r)
  }
  
  vals
}

apply_deep_zoom <- function(sequence, k) {
  if (!is.numeric(k) || length(k) != 1 || k < 0) {
    stop("k must be a non-negative integer.")
  }
  
  k <- as.integer(k)
  (sequence * (10^k)) %% 1
}

s_deep_zoom <- function(x0, r, k, n_iter, t_discard) {
  if (!is.numeric(n_iter) || length(n_iter) != 1 || n_iter < 1) {
    stop("n_iter must be an integer >= 1.")
  }
  
  if (!is.numeric(t_discard) || length(t_discard) != 1 || t_discard < 0) {
    stop("t_discard must be an integer >= 0.")
  }
  
  n_iter <- as.integer(n_iter)
  t_discard <- as.integer(t_discard)
  total_n <- n_iter + t_discard
  
  vals <- generate_logistic_sequence(x0 = x0, r = r, total_n = total_n)
  vals <- vals[(t_discard + 1):total_n]
  
  apply_deep_zoom(vals, k)
}

# ---------------------------
# Binarization
# ---------------------------

binary2b <- function(sequence, b) {
  if (!is.numeric(b) || length(b) != 1 || b < 1) {
    stop("b must be an integer >= 1.")
  }
  
  b <- as.integer(b)
  
  ints <- floor(sequence * (2^b))
  
  # Clamp in case of floating-point edge effects
  ints[ints < 0] <- 0
  ints[ints > (2^b - 1)] <- 2^b - 1
  
  vapply(
    ints,
    function(z) {
      paste(rev(as.integer(intToBits(z))[1:b]), collapse = "")
    },
    character(1)
  )
}

concatenate_bits <- function(bit_chunks) {
  paste(bit_chunks, collapse = "")
}

generate_bit_chunks <- function(x0, r = 3.999, k = 6, b = 10,
                                n_iter = 1000, t_discard = 100000) {
  seq_vals <- s_deep_zoom(
    x0 = x0,
    r = r,
    k = k,
    n_iter = n_iter,
    t_discard = t_discard
  )
  
  binary2b(seq_vals, b)
}

generate_bitstring <- function(x0, r = 3.999, k = 6, b = 10,
                               n_iter = 1000, t_discard = 100000) {
  bit_chunks <- generate_bit_chunks(
    x0 = x0,
    r = r,
    k = k,
    b = b,
    n_iter = n_iter,
    t_discard = t_discard
  )
  
  concatenate_bits(bit_chunks)
}

# ---------------------------
# File helpers
# ---------------------------

save_bitstring <- function(bitstring, output_file) {
  writeLines(bitstring, con = output_file, useBytes = TRUE)
  cat("Saved bitstring to:", output_file, "\n")
  cat("Bit length:", nchar(bitstring), "\n")
}

read_bitstring <- function(input_file) {
  paste(readLines(input_file, warn = FALSE), collapse = "")
}

save_bit_chunks <- function(bit_chunks, output_file) {
  writeLines(bit_chunks, con = output_file, useBytes = TRUE)
  cat("Saved bit chunks to:", output_file, "\n")
  cat("Number of chunks:", length(bit_chunks), "\n")
}