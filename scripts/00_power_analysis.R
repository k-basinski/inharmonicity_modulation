library(lme4)

params <- list(
    n = 50,
    a = .3,
    intercept_sd = 1,
    noise = 2,
    conditions = 8
)




make_person <- function(sub_id, params) {
    # IV & DV
    x <- c(0:(params$conditions-1))
    y <- params$a * x + rnorm(=length(x), mean=0, sd=params$intercept_sd) + rnorm(n=length(x), mean=0, sd=params$noise)
    x <- factor(x)
    d <- data.frame('sub' = sub_id, 'cond' = x, 'y' = y)
    return(d)
}

make_person_2 <- function(sub_id, params) {
    # IV & DV
    # simulate 2uV difference only in one condition
    x_y <- c(0, 0, 0, 0, 0, 0, 0, 2)
    x <- c(0:(params$conditions-1))
    y <- x_y + rnorm(=length(x), mean=0, sd=params$intercept_sd) + rnorm(n=length(x), mean=0, sd=params$noise)
    x <- factor(x)
    d <- data.frame('sub' = sub_id, 'cond' = x, 'y' = y)
    return(d)
}


simulate_one_run <- function(n) {
  # simulate data
  person_list <- lapply(1:n, make_person, params)
  d <- do.call(rbind, person_list)

  # fit models - make sure they're correct
  m0 <- suppressMessages(lmer(y ~ 1 + (1|sub), data = d, REML = FALSE))
  m1 <- suppressMessages(lmer(y ~ cond + (1|sub), data = d, REML = FALSE))

  # perform likelihood ratio test
  test <- anova(m0,m1, refit=TRUE)
  test_pval <- test$`Pr(>Chisq)`[2]
  
  df <- data.frame(n, test_pval)
  return(df)
}



simulate <- function(ns, no_of_sims) {
  # init empty data frame
  df <- data.frame()
  for (s in 1:no_of_sims) {
    sim_list <- lapply(ns, simulate_one_run)
    d <- do.call(rbind, sim_list)
    df <- rbind(df, d)
  }
  return(df)
}

ns <- seq(from = 10, to = 20, by = 2)
n_sims <- 1000
res <- simulate(ns, n_sims)

res$pass <- res$test_pval < .05

power_df <- aggregate(res$pass, by = list(res$n), FUN = sum)
power_df$n <- power_df$Group.1
power_df$power <- power_df$x / n_sims
power_df
plot(power_df$n, power_df$power, type="b")
abline(h=.8)
