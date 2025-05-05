library(readr)
library(dplyr)
library(lme4)
library(lmerTest)
library(emmeans)
library(broom)

df_all <- read_csv("results/csv/mismatch_peaks.csv")

# select just mismatch 1
dm1 <- df_all %>% filter(mismatch == "mismatch_1" )
dm1 <- df_all %>% filter(mismatch == "mismatch_1" & jitter_no != 0)


dvs <- c(
    "mmn_amp",
    "mmn_lat",
    "p3_amp",
    "p3_lat"
)

for (dv in dvs) {
    paste("\n\n* ", dv, ":\n") %>%
        toupper() %>%
        cat()

    f0 <- paste(dv, " ~ (1 | pid)")
    f1 <- paste(dv, " ~ jitter_no + (1 | pid)")
    f2 <- paste(dv, " ~ poly(jitter_no, 2) + (1 | pid)")
    f3 <- paste(dv, " ~ poly(jitter_no, 3) + (1 | pid)")
    f4 <- paste(dv, " ~ poly(jitter_no, 4) + (1 | pid)")
    m0 <- lmer(f0, data = dm1)
    m1 <- lmer(f1, data = dm1)
    m2 <- lmer(f2, data = dm1)
    m3 <- lmer(f3, data = dm1)
    m4 <- lmer(f4, data = dm1)
    log_like_test <- anova(m0, m1, m2, m3, m4, refit = TRUE)
    print(log_like_test)
    fname <- paste("results/csv/",dv ,"_loglikelihood.csv", sep="")
    log_like_test %>% broom::tidy() %>% write_csv(fname)
}
lmer(f0, data = dm1)

# now factors

for (dv in dvs) {
    paste("\n\n* ", dv, ":\n") %>%
        toupper() %>%
        cat()
    dm1$jitter <- factor(dm1$jitter)
    f0 <- paste(dv, " ~ (1 | pid)")
    f1 <- paste(dv, " ~ jitter + (1 | pid)")
    f2 <- paste(dv, " ~ poly(jitter, 2) + (1 | pid)")
    f3 <- paste(dv, " ~ poly(jitter, 3) + (1 | pid)")
    f4 <- paste(dv, " ~ poly(jitter, 4) + (1 | pid)")
    m0 <- lmer(f0, data = dm1)
    m1 <- lmer(f1, data = dm1)
    m2 <- lmer(f2, data = dm1)
    m3 <- lmer(f3, data = dm1)
    m4 <- lmer(f4, data = dm1)
    log_like_test <- anova(m0, m1, m2, m3, m4, refit = TRUE)
    print(log_like_test)

    log_like_test %>% broom::tidy() %>% write_csv(fname)
}
