#!/usr/bin/env Rscript
# fetch_cmc_listings.R
#
# Pulls historical CMC coin listings (top universe + prices + market cap)
# for each target_date in our schedule. Writes one CSV per date to data/raw/.
#
# Survivorship-bias-free: crypto2's historical endpoint includes coins that
# have since been delisted or untracked.
#
# Usage:
#   Rscript src/fetch_cmc_listings.R
#   Rscript src/fetch_cmc_listings.R --start 2014-01-01 --end 2024-12-31 --step 30
#   Rscript src/fetch_cmc_listings.R --single-date 2022-06-01

suppressPackageStartupMessages({
  if (!require("crypto2", quietly = TRUE)) {
    install.packages("crypto2", repos = "https://cloud.r-project.org")
    library(crypto2)
  }
  if (!require("dplyr", quietly = TRUE)) {
    install.packages("dplyr", repos = "https://cloud.r-project.org")
    library(dplyr)
  }
  library(crypto2)
  library(dplyr)
})

# -------- argument parsing (minimal, no extra deps) --------
args <- commandArgs(trailingOnly = TRUE)
get_arg <- function(name, default = NULL) {
  i <- which(args == paste0("--", name))
  if (length(i) && i < length(args)) args[i + 1] else default
}

start_date <- get_arg("start", "2014-01-01")
end_date   <- get_arg("end",   "2024-12-31")
step_days  <- as.integer(get_arg("step", "30"))
single_date <- get_arg("single-date", NULL)

# -------- output dir --------
# Resolve project root: assume this script lives at <root>/src/fetch_cmc_listings.R
# Use the script's own path when run with Rscript, else fall back to cwd.
this_file <- (function() {
  ca <- commandArgs(trailingOnly = FALSE)
  m <- regmatches(ca, regexec("--file=(.+)", ca))
  for (mm in m) if (length(mm) >= 2) return(normalizePath(mm[2], mustWork = FALSE))
  NA_character_
})()

if (!is.na(this_file) && file.exists(this_file)) {
  proj_root <- normalizePath(file.path(dirname(this_file), ".."), mustWork = FALSE)
} else {
  proj_root <- getwd()
}
out_dir <- file.path(proj_root, "data", "raw")
log_dir <- file.path(proj_root, "logs")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
dir.create(log_dir, showWarnings = FALSE, recursive = TRUE)

log_file <- file.path(log_dir, "fetch_cmc_listings.log")
log_msg <- function(msg) {
  ts <- format(Sys.time(), "%Y-%m-%d %H:%M:%S")
  line <- paste0(ts, " ", msg)
  cat(line, "\n")
  cat(line, "\n", file = log_file, append = TRUE)
}

# -------- schedule --------
build_schedule <- function(start, end, step) {
  s <- as.Date(start); e <- as.Date(end)
  seq(s, e, by = step)
}

if (!is.null(single_date)) {
  schedule <- as.Date(single_date)
} else {
  schedule <- build_schedule(start_date, end_date, step_days)
}

log_msg(sprintf("Schedule: %d dates from %s to %s (step %dd)",
                length(schedule), as.character(min(schedule)),
                as.character(max(schedule)), step_days))

# -------- fetch loop --------
fetch_one <- function(target_date) {
  out_file <- file.path(out_dir, sprintf("listings_%s.csv", format(target_date, "%Y%m%d")))
  if (file.exists(out_file)) {
    info <- file.info(out_file)
    if (info$size > 100) {
      log_msg(sprintf("skip %s (already exists, %d bytes)", target_date, info$size))
      return(invisible(TRUE))
    }
  }

  d <- format(target_date, "%Y%m%d")
  log_msg(sprintf("fetching %s ...", target_date))
  t0 <- Sys.time()

  result <- tryCatch({
    crypto2::crypto_listings(
      which = "historical",
      quote = TRUE,
      start_date = d,
      end_date = d,
      limit = 50000
    )
  }, error = function(e) {
    log_msg(sprintf("ERROR fetching %s: %s", target_date, conditionMessage(e)))
    NULL
  })

  if (is.null(result) || nrow(result) == 0) {
    log_msg(sprintf("FAIL %s: no rows returned", target_date))
    return(invisible(FALSE))
  }

  result$snapshot_date <- as.character(target_date)
  write.csv(result, out_file, row.names = FALSE)

  dur <- as.numeric(Sys.time() - t0, units = "secs")
  log_msg(sprintf("ok   %s: %d rows -> %s (%.1fs)",
                  target_date, nrow(result), basename(out_file), dur))
  invisible(TRUE)
}

# -------- run --------
n_ok <- 0
n_fail <- 0
for (i in seq_along(schedule)) {
  d <- schedule[i]
  ok <- fetch_one(d)
  if (isTRUE(ok)) n_ok <- n_ok + 1 else n_fail <- n_fail + 1
}

log_msg(sprintf("DONE: %d ok, %d fail", n_ok, n_fail))
