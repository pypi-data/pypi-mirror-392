# 1. copy sample solution index.js and package.json
cp -f /opt/index_fixed.js ~/node_server/index.js
cp -f /opt/package.json ~/node_server/package.json

# 2. install node.js and npm
sudo apt install -y ca-certificates curl gnupg
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# 3. install package.json - includes pm2 command setup
cd node_server
npm install

# 4. start server in the background using pm2
npm run start-background