# 1. activate venv
source virtuals/net_venv/bin/activate

# 2. install httpie in venv
pip install httpie

# 3. add http to path and use venv httpie bin
export PATH="$HOME/virtuals/net_venv/bin:$PATH"
echo 'export PATH="$HOME/virtuals/net_venv/bin:$PATH"' >> "$HOME/.bashrc"

# 4. fetch and save test data
#http https://jsonplaceholder.typicode.com/todos/4 > response.json
cp /opt/expected_response.json ~/response.json