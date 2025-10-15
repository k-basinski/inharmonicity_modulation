library(readr)
library(lme4)
library(lmerTest)
library(emmeans)


df <- read_csv("collected_results.csv")
df$jitter <- factor(df$jitter)
m1 <- lmer("perc_correct ~ jitter + (1|pid)", data = df)
anova(m1)
em <- emmeans(m1, 'jitter')
pairs(em)
