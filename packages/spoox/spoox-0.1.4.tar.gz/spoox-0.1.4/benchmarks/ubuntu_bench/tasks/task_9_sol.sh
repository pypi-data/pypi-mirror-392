# 1. query api and get correct jokes count
mkdir ~/jokes_count
curl -s "https://api.chucknorris.io/jokes/search?query=linux" | jq '.total' > ~/jokes_count/count.md