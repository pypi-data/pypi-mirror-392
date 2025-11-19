# 1. install Flask
python -m pip install flask --quiet

# 2. override existing server script with flask server script
cp -f /opt/server.py ~/hello_world_server/app/server.py

# 3. run server in the background
nohup python hello_world_server/app/server.py >/dev/null 2>&1 & echo $! > hello_world_server/app/server.pid