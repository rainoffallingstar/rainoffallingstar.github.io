
library(tidyverse)
library(readxl)
library(ggplot2)
library(MASS)
library(survival)
library(DT)

# 数据清洗
crf <- read_excel("cmvnpue_reshape.xlsx")
gender_level <- c("M","F")
clinial_finding_level <- c("nagetive","fever","cough","sputum","wetrales")
sputum_result_level <- c("positive","nagetive")

crf2 <- mutate(crf,
               genders=factor(gender,levels=gender_level),
               clinical_findings=factor(clinical_finding,levels=clinial_finding_level),
               sputum_results=factor(sputum_result,levels=sputum_result_level),
               ages=as.numeric(age),
               day_afterHCT=as.numeric(days_afterHCT),
               end_points=factor(endpoints,levels = c("infection","uninfection"))
)
attach(crf2)
str(crf2)

datatable(crf2)




# 对年龄的分析
summary(crf2$ages)
hist(crf2$ages)
# 对移植术后发病的分布分析
summary(crf2$day_afterHCT)
hist(crf2$day_afterHCT)

# 对于性别、症状的总分析

ggplot(data = crf2) +
  geom_bar(mapping=aes(x = genders, fill =clinical_findings))
ggplot(data = crf2) +
  geom_bar(mapping=aes(x = clinical_findings, fill =genders))
plot(crf2$day_afterHCT,crf2$cmv_blood_DNA)

dna = as.numeric(crf2$cmv_blood_DNA)

summary(dna)
