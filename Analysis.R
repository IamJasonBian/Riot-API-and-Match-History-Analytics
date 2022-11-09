source("Endpoint_func.R")
source("Item_func.R")


key = "RGAPI-67f20909-15ef-4c0e-94bc-9e072d70c642"

getSummonerByName('jakeateworld', key = key)

encrypted_account_id <- getSummonerByName('jakeateworld', key =key)$puuid
encrypted_account_id

matchID_example <- getGameByPuuid(encrypted_account_id, key = key)[[1]]
matchID_example

matches <- getGameByPuuid(encrypted_account_id, key = key)

Game_example <- getGameByMatchID(matchID_example, key = key)
Game_example


df <- item_analysis(name = "JAKEATEWORLD", key = key)

df$Status <- ifelse(df$win_percent > df$total_win_rate, "Green", ifelse(df$total_win_rate < df$total_win_rate, "Red", "Yellow"))
df$ID <- 1:nrow(df)

df <- df[order(df$occur, decreasing = TRUE),]

#Write Locally
write.csv(df, file = 'item_analysis.csv')

plot_df <- head(df, n = 30)

library(ggplot2)

ggplot(data = plot_df, aes(x=ID, y=win_percent, label = name))  +
  geom_point(aes(colour = Status, size = occur), alpha = 0.5) + 
  geom_text(aes(x=ID, y=win_percent, label = name), angle = 45, nudge_y = 0.1, nudge_x = 0.1, size = 3) +
  scale_x_continuous(expand = c(.1, .1)) +
  scale_y_continuous(expand = c(.1, .1)) +
  scale_color_manual(name = "Total Win Rate", 
                     values = c("Red" = "Red", "Green" = "Green", "Yellow" = "Yellow"),
                     labels = c("Above Total Win Rate", "Below Total Win Rate", "At Total Win Rate")) + theme_bw()
  


