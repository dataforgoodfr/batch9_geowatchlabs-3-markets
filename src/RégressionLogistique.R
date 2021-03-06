#import des tables des enqu�tes aupr�s des m�nages
fsms_juin_2015 = read.spss('C:/Users/Mariem/Documents/1. Statistics & Data science/5. Data for good/Mauritania FSMS data-20210422T155253Z-001/Mauritania FSMS data/2015/Juin/Donn�es_FSMS_juin_15.sav', use.value.labels = TRUE, to.data.frame = TRUE)
fsms_decembre_2015 = read.spss('C:/Users/Mariem/Documents/1. Statistics & Data science/5. Data for good/Mauritania FSMS data-20210422T155253Z-001/Mauritania FSMS data/2015/Decembre/Donn�es FSMS Jan16_18_02.sav', use.value.labels = TRUE, to.data.frame = TRUE)
fsms_juin_2014 = read.spss('C:/Users/Mariem/Documents/1. Statistics & Data science/5. Data for good/Mauritania FSMS data-20210422T155253Z-001/Mauritania FSMS data/2014/Juin/Donn�es_FSMS_juin_2014.sav', use.value.labels = TRUE, to.data.frame = TRUE)
fsms_decembre_2014 = read.spss('C:/Users/Mariem/Documents/1. Statistics & Data science/5. Data for good/Mauritania FSMS data-20210422T155253Z-001/Mauritania FSMS data/2014/Decembre/Donn�es_FSMS_24_06_15.sav', use.value.labels = TRUE, to.data.frame = TRUE)
fsms_juin_2013 = read.spss('C:/Users/Mariem/Documents/1. Statistics & Data science/5. Data for good/Mauritania FSMS data-20210422T155253Z-001/Mauritania FSMS data/2013/Juin/FSMS_HH_juil13b_1.sav', use.value.labels = TRUE, to.data.frame = TRUE)
fsms_decembre_2013 = read.spss('C:/Users/Mariem/Documents/1. Statistics & Data science/5. Data for good/Mauritania FSMS data-20210422T155253Z-001/Mauritania FSMS data/2013/Decembre/Donn�es FSMS 13Dec_20_01_14.sav', use.value.labels = TRUE, to.data.frame = TRUE)
fsms_juin_2012 = read.spss('C:/Users/Mariem/Documents/1. Statistics & Data science/5. Data for good/Mauritania FSMS data-20210422T155253Z-001/Mauritania FSMS data/2012/Juin/Donn�es_FSMS_juil_12.sav', use.value.labels = TRUE, to.data.frame = TRUE)
fsms_decembre_2012 = read.spss('C:/Users/Mariem/Documents/1. Statistics & Data science/5. Data for good/Mauritania FSMS data-20210422T155253Z-001/Mauritania FSMS data/2012/Decembre/Donnes_FSMSdec12_HH_commun.sav', use.value.labels = TRUE, to.data.frame = TRUE)
fsms_juin_2011 = read.spss('C:/Users/Mariem/Documents/1. Statistics & Data science/5. Data for good/Mauritania FSMS data-20210422T155253Z-001/Mauritania FSMS data/2011/Juin11/Donn�es_FSMS_16_08_11.sav', use.value.labels = TRUE, to.data.frame = TRUE)
fsms_decembre_2011 = read.spss('C:/Users/Mariem/Documents/1. Statistics & Data science/5. Data for good/Mauritania FSMS data-20210422T155253Z-001/Mauritania FSMS data/2011/Decembre11/Donn�es_FSMS_nov11_26_12.sav', use.value.labels = TRUE, to.data.frame = TRUE)

##fsms Juin 2015

#cr�er la variable revenu par individu
fsms_juin_2015$revenu_individu <- fsms_juin_2015$revenu_mens/fsms_juin_2015$tailmen

#discr�tiser la variable revenu par individu(Quantiles)
for (i in 1:nrow(fsms_juin_2015)){
  if (fsms_juin_2015$revenu_individu[i]<=4000) {fsms_juin_2015$revenu_indiv_disc[i] <- "inf � 4000"}
  else if (fsms_juin_2015$revenu_individu[i]>4000 && fsms_juin_2015$revenu_individu[i]<=7500){fsms_juin_2015$revenu_indiv_disc[i] <- "Entre 4000 et 7500"}
  else if (fsms_juin_2015$revenu_individu[i]>7500 && fsms_juin_2015$revenu_individu[i]<=12500){fsms_juin_2015$revenu_indiv_disc[i] <- "Entre 7500 et 12500"}
  else if (fsms_juin_2015$revenu_individu[i]>12500){fsms_juin_2015$revenu_indiv_disc[i] <- "sup � 12500"}
}

#cr�er la variable betail
fsms_juin_2015$betail <- fsms_juin_2015$Q4_1+fsms_juin_2015$Q4_2+fsms_juin_2015$Q4_3+fsms_juin_2015$Q4_4


#discr�tiser la variable betail(m�diane=4)
for (i in 1:nrow(fsms_juin_2015)){
  if (fsms_juin_2015$betail[i]<=4) {fsms_juin_2015$betail_disc[i] <- "inf � 4"}
  else if (fsms_juin_2015$betail[i]>4){fsms_juin_2015$betail_disc[i] <- "sup � 4"}
}

#cr�er la variable sum_stock (mil, sorg, mais, riz, ble)
fsms_juin_2015$sum_stock <- fsms_juin_2015$Sum_mil +fsms_juin_2015$Sum_sorg + fsms_juin_2015$Sum_mais + fsms_juin_2015$Sum_riz + fsms_juin_2015$Sum_ble

#discr�tiser la variable SUM_STOCK(m�diane=24)
for (i in 1:nrow(fsms_juin_2015)){
  if (fsms_juin_2015$sum_stock[i]<=24) {fsms_juin_2015$sum_stock_disc[i] <- "inf � 24"}
  else if (fsms_juin_2015$sum_stock[i]>24){fsms_juin_2015$sum_stock_disc[i] <- "sup � 24"}
}
#r�gression logistique
fsms_juin_2015$FCG_28_42 <- factor(fsms_juin_2015$FCG_28_42, c("Acceptable", "A la limite", "Pauvre"), ordered = TRUE)
freq(fsms_juin_2015$FCG_28_42)
library(ordinal)
rego <- clm(FCG_28_42 ~ wilaya + MILIEU + tailmen + revenu_indiv_disc + sum_stock_disc + betail_disc, data = fsms_juin_2015)
summary(rego)