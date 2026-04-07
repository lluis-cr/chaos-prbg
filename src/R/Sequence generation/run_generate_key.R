# run_generate_key.R
# Example runner for generating correct and wrong keys

source("helpers_prbg.R")

# ---------------------------
# Parameters
# ---------------------------

params <- list(
  x0 = 0.08036413710741597,
  r = 3.999,
  k = 6,
  b = 10,
  n_iter = 184320,
  t_discard = 100000
)

wrong_params <- params
wrong_params$r <- 3.888

# ---------------------------
# Generate correct key
# ---------------------------

bitstring_correct <- do.call(generate_bitstring, params)

# ---------------------------
# Generate wrong key
# ---------------------------

bitstring_wrong <- do.call(generate_bitstring, wrong_params)

# ---------------------------
# Save them
# ---------------------------

output_dir <- "~/Desktop/Models/Chaos-based PRBG encryption model/Data/generated"
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

save_bitstring(bitstring_correct, file.path(output_dir, "key_correct.txt"))
save_bitstring(bitstring_wrong, file.path(output_dir, "key_wrong.txt"))