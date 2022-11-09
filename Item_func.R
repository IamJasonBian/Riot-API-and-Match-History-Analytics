item_analysis <- function(name, key){
  
  #Pull from Data Dragon (Static Pull)
  r = getURL('http://ddragon.leagueoflegends.com/cdn/12.21.1/data/en_US/item.json')
  item_master_list = fromJSON(r)
  
  r = getURL('http://ddragon.leagueoflegends.com/cdn/12.21.1/data/en_US/champion.json')
  champion_master_list = fromJSON(r)
  
  
  #Test whether the API is working currently for provided key (Dynamic Pull)
  response = getSummonerByName(name, key)

  if(length(response$status) != 0){
  
    if(response$status$status_code == 429){
        print("Server Timeout, retry later")
      return(0)
      
    }else if(response$status$status_code == 404){
        print('Summoner with that name not found.')
      return(0)
      
    }else if(response$status$status_code == 403){
        print('An invalid API key was provided with the API request.')
      return(0)
    }
    else{
      print("Other error")
    }
  }
  
  me = response
  
  encrypted_account_id <- me$puuid
  my_matches <- getGameByPuuid(encrypted_account_id, key = key)

  if(length(my_matches) == 0){
    print("You have played no games in the current season!")
  }
  
  #Find the items bought when the games were played in the champion_games list
  item_dict= list()
  item_list = list()
  champion_list = list()
  
  win_list = c()
  game_counter = 0
  
  for(i in my_matches){
    match = getGameByMatchID(i, key)
    for(j in 1:10){
      
      if(match$metadata$participants[[j]] == encrypted_account_id){
        break
      }
    }
    
    player = match$info$participants[[j]]
    
    #convert i to character to create key value pair
    i <- as.character(i)
    win_list <- c(win_list, player$win)
    item_dict[[i]] <- c(player$item0, player$item1, player$item2,
                                     player$item3, player$item4, player$item5,
                                     player$item6)
    
    item_list <- c(item_list, c(player$item0, player$item1, player$item2,
                                player$item3, player$item4, player$item5,
                                player$item6))
    
    game_counter = game_counter + 1
    champion_list <- c(champion_list, c(player$championName))
  }
  
  #return(champion_list)
  
  
  
  #Find relationship between items and win rate-------------------------
  
  #First we convert item_list to a unique list
  item_list_df <- data.frame(matrix(unlist(item_list), nrow=length(item_list), byrow=T))
  names(item_list_df) <- c("value") 
  
  item_list_uniq <- unique(item_list)
  item_list_uniq <- item_list_uniq[item_list_uniq!=0]
  
  item_name_uniq <- c()
  #Convert each item id into it's actual name
  for(i in item_list_uniq){
    item_name_uniq <- c(item_name_uniq, item_master_list$data[[as.character(i)]]$name)
  }
  
  
  #use the links dataframe to store item name and win rate associated with the item
  links = data.frame(name =character(), win_percent = double(), occur = double())
  
  #Your overall champion win rate
  total_win_rate = sum(win_list)/game_counter
  
  
  print(paste0("Current champion win rate is ", total_win_rate, " at a game count of ", game_counter))
  
  for(i in 1:length(item_list_uniq)){
    
    count_win <- 0
    occur <- 0

    
    for(j in 1:length(win_list)){
      count <- 0
      
      #Count occurances of the item through all game items
      for(k in 1:length(item_dict[[j]])){
        
        
        if(item_dict[[j]][k] == item_list_uniq[i][[1]]){
          
           count <- count + 1
        }
      }
      
      #Count single occurance of item
      if(count > 0){
        occur = occur + 1
      }
      
      
      if(win_list[[j]] == TRUE & count > 0){
        
        count_win = count_win + 1
      }
    }
    
    links <- rbind(links, data.frame(name = item_name_uniq[i], win_percent = count_win/occur, occur = occur))
    
  }
  
  links$total_win_rate <- total_win_rate
  return(links)
    
  
  }