devtools::install_github("jjesusfilho/tjsp")

library(tjsp)

baixar_cjpg(diretorio = "/home/guilherme/Unicamp/IC_2021/Downloads", livre = "homofobia",inicio = "31/10/2018",fim = "30/10/2019")

jpg_table <- ler_cjpg(diretorio = "/home/guilherme/Unicamp/IC_2021/Downloads")

library(jsonlite)
library(rvest)
json_table_jpg <- toJSON(jpg_table,pretty = TRUE)

jpg_file <- file("/home/guilherme/Unicamp/IC_2021/Downloads/test_jpg.json")
write(json_table_jpg,jpg_file)
close(jpg_file)

#################################################2º grau####################################################################################
baixar_cjsg(diretorio = "/home/guilherme/Unicamp/IC_2021/Downloads", livre = "homofobia",inicio = "31/10/2018",fim = "30/10/2019")

jsg_table <- ler_cjsg(diretorio = "/home/guilherme/Unicamp/IC_2021/Downloads")
#Lê inteiro teor

#links = paste("https://esaj.tjsp.jus.br/cjsg/getArquivo.do?cdAcordao=",jsg_table$cdacordao,"&cdForo=0",sep="")
#for (i in 1:nrow(jsg_table)){
#  link = paste("https://esaj.tjsp.jus.br/cjsg/getArquivo.do?cdAcordao=",jsg_table[i,10],"&cdForo=0",sep="")
#  html = read_html(link)
#}

json_table_jsg <- toJSON(jsg_table,pretty=TRUE)

jsg_file <- file("/home/guilherme/Unicamp/IC_2021/Downloads/test_jsg.json")
write(json_table_jsg,jsg_file)
close(jsg_file)

