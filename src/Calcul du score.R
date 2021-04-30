#import des libraries
library(foreign)

#import des tables FSMS
fsms_juin_2015 = read.spss('C:/Users/Mariem/Documents/1. Statistics & Data science/5. Data for good/Mauritania FSMS data-20210422T155253Z-001/Mauritania FSMS data/2015/Juin/Données_FSMS_juin_15.sav', use.value.labels = TRUE, to.data.frame = TRUE)

#nom des colonnes
colnames(fsms_juin_2015)

#garder les variables qui permettent de calculer le score
score_fsms_juin_2015 <- fsms_juin_2015[, c("NUMQUEST", "Adbase1", "Adbase2", "Pulses", "Legumes", "Fruits", "Proteismall", "Viand_poiss", "smallai", "Laitiers", "Sucre", "Huile", "Other")]

#calcul des sub-scores
score_fsms_juin_2015$score_cereales_et_tubercules <- score_fsms_juin_2015$Adbase1+score_fsms_juin_2015$Adbase2
for (i in 1:nrow(score_fsms_juin_2015)){
if (score_fsms_juin_2015$score_cereales_et_tubercules[i]>7) {score_fsms_juin_2015$score_cereales_et_tubercules[i] <- 7}
}
score_fsms_juin_2015$score_pois <- score_fsms_juin_2015$Pulses
score_fsms_juin_2015$score_legumes <- score_fsms_juin_2015$Legumes
score_fsms_juin_2015$score_fruits <- score_fsms_juin_2015$Fruits
score_fsms_juin_2015$score_viande_poisson <- score_fsms_juin_2015$Viand_poiss
score_fsms_juin_2015$score_lait <- score_fsms_juin_2015$Laitiers
score_fsms_juin_2015$score_sucre <- score_fsms_juin_2015$Sucre
score_fsms_juin_2015$score_huile <- score_fsms_juin_2015$Huile

#calcul du score final
score_fsms_juin_2015$Score_final <- 2*score_fsms_juin_2015$score_cereales_et_tubercules + 3*score_fsms_juin_2015$score_pois + score_fsms_juin_2015$score_fruits + 1*score_fsms_juin_2015$score_legumes  + 4*score_fsms_juin_2015$score_viande_poisson + 4*score_fsms_juin_2015$score_lait + 0.5*score_fsms_juin_2015$score_sucre + 0.5*score_fsms_juin_2015$score_huile

#appréciation du score
score_fsms_juin_2015$FCS = c()
for (i in 1:nrow(score_fsms_juin_2015)){
  if (score_fsms_juin_2015$Score_final[i]<21) {score_fsms_juin_2015$FCS[i] <- "Consommation alimentaire pauvre"}
  else if (score_fsms_juin_2015$Score_final[i]>21.5 && score_fsms_juin_2015$Score_final[i]<35 ) {score_fsms_juin_2015$FCS[i] <- "Consommation alimentaire limitée"}
  else if (score_fsms_juin_2015$Score_final[i]>35) {score_fsms_juin_2015$FCS[i] <- "Consommation alimentaire acceptable"}
}

#distribution de la variable score_final
summary(score_fsms_juin_2015$Score_final)

#fréquances des appréciations du score
table(score_fsms_juin_2015$FCS)
