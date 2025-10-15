library(knitr)

round_p <- function(x) {
  return(ifelse(x < 0.001, "<.001", as.character(x)))
}

# function to round saved values
table_rounding <- function(tbl) {
    for(nm in names(tbl)) {
      ifelse(nm %in% c("p_raw", "p_adj_fdr", "p", "p[GG]", "p-value"), digits <- 3, digits <-2)
    if(class(tbl[[nm]]) != "character" & class(tbl[[nm]]) != "factor") {
      tbl[[nm]] <- round(tbl[[nm]], digits = digits)
    }
  }
  for(p in c("p_raw", "p_adj_fdr", "p", "p[GG]", "p-value")) {
     if(p %in% names(tbl)) {
        tbl[[p]] <- round_p(tbl[[p]])
     }
  }
  
  return(tbl)
}

write_to_nice_tables <- function (table, file_name, title = "") {
  rounded <- table_rounding(as.data.frame(table))
  out <- kable(rounded, digits = 3, row.names = TRUE)
  heading <- paste0("\n## ", title, "\n")
  write(heading, file_name, append = TRUE)
  write(out, file_name, append = TRUE)
}

save_mixed_model <- function(model_summary, model_name, output_dir, nice_tables_file){
  file_connection <- file(paste0(output_dir, "/", model_name, ".txt"), open = "w+")
  writeLines("NULL MODEL", file_connection)
  writeLines(paste0("\nAIC: ", model_summary$AIC), file_connection)
  writeLines(paste0("BIC: ", model_summary$BIC), file_connection)
  writeLines(paste0("Loglik: ", model_summary$logLik, "\n"), file_connection)
  out <- capture.output(print(model_summary))
  writeLines(out, file_connection)
  writeLines("\nFixed effects", file_connection)
  out <- capture.output(write.csv(table_rounding(as.data.frame(model_summary$tTable))))
  writeLines(out, file_connection)
  close(file_connection)

  write_to_nice_tables(model_summary$tTable,
                       nice_tables_file,
                       title = paste0(model_name, " - fixed effects")
  )
}

