source("Endpoint_func.R")
source("Item_func.R")


key = "RGAPI-fbccf05d-d936-45b3-a744-cc2c268b887b"

getSummonerByName('jakeateworld', key = "RGAPI-fbccf05d-d936-45b3-a744-cc2c268b887b")

encrypted_account_id <- getSummonerByName('jakeateworld', key =key)$accountId
encrypted_account_id

matchID_example <- getGameBySummonerID(encrypted_account_id, key = key)$matches[[1]]$gameId
matchID_example

match_list <- getGameByMatchID(matchID_example, key = key)


df <- item_analysis(champion = "Zed", name = "JAKEATEWORLD", key = key)

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
  


