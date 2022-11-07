source("Endpoint_func.R")
source("Item_func.R")


key = "RGAPI-949fa3d6-5c89-423a-8f5a-47a8a850174c"

getSummonerByName('jakeateworld', key = key)

encrypted_account_id <- getSummonerByName('jakeateworld', key =key)$puuid
encrypted_account_id

matchID_example <- getGameByPuuid(encrypted_account_id, key = key)[[1]]
matchID_example

match_list <- getGameByPuuid(encrypted_account_id, key = key)

df <- item_analysis(champion = "Riven", name = "JAKEATEWORLD", key = key)

df$Status <- ifelse(df$win_percent > df$champion_winrate, "Green", ifelse(df$win_percent < df$champion_winrate, "Red", "Yellow"))
df$ID <- 1:nrow(df)

head(df, n = 50)

library(ggplot2)

ggplot(data = df, aes(x=ID, y=win_percent, label = name))  +
  geom_point(aes(colour = Status, size = occur), alpha = 0.5) + 
  geom_text(aes(x=ID, y=win_percent, label = name), angle = 45, nudge_y = 0.1, nudge_x = 0.1, size = 3) +
  scale_x_continuous(expand = c(.1, .1)) +
  scale_y_continuous(expand = c(.1, .1)) +
  scale_color_manual(name = "Champion Specific Win Rate", 
                     values = c("Red" = "Red", "Green" = "Green", "Yellow" = "Yellow"),
                     labels = c("Above Champion Win Rate", "Below Champion Win Rate", "At Champion Win Rate")) + theme_bw()
  


