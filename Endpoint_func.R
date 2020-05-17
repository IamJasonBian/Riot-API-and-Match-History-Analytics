require(RCurl)
require(rjson)
require(stringr)



#Builds the API url with an embeded API key and returns the json output
getRIOT <- function(version, key=NULL, base, type=NULL, id=NULL, attr=NULL, params=NULL, region="na", static=TRUE, parse=TRUE) {
  
  if(is.null(key)){
    
    print("Please provide a RIOT API key input")
    return(0)
  }
  
  if (static)
    
    uri <- "https://na1.api.riotgames.com/lol"
  else
    
    uri <- "https://na1.api.riotgames.com/lol"
  uri <- sprintf("%s/%s/%s",uri,version,base)
  if (!is.null(type))
    uri <- sprintf("%s/%s",uri,type)
  if (!is.null(id))
    uri <- sprintf("%s/%s",uri,id)
  if (!is.null(attr))
    uri <- sprintf("%s/%s",uri,attr)
  uri <- sprintf("%s?api_key=%s", uri, key)
  if (!is.null(params))
    uri <- sprintf("%s%s",uri,params)
  print(paste0("Parsing from endpoint: ", uri))
  j <- getURI(uri)
  if (parse)
    
    #from Json automatically parses the output as parse is set to TRUE
    fromJSON(j)
  else
    #prints the value of j
    j
}

#Functions for additional inputs parameters needed in the API url string
getSummonerByName <- function(summonerName, key) 
  getRIOT(version="summoner/v4", key = key, base="summoners/by-name", id=str_replace_all(tolower(summonerName)," ",""), static=FALSE)

getGameBySummonerID <- function(id, key) 
  getRIOT(version="match/v4", key = key, base="matchlists/by-account", id=id, static=FALSE)

getGameByMatchID <- function(id, key) 
  getRIOT(version="match/v4", key = key, base="matches", id=id, static=FALSE)