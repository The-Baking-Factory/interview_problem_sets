# interview_problem_sets

### Update Packages

```bash
# access the package servers and check to see if any of your installed packages have new versions available
sudo apt-get update
# install the updates
sudo apt dist-upgrade
# clean up any old versions of packages that were just replaced
sudo apt autoremove
# check if your system needs to be rebooted
cat /var/run/reboot-required
# restart machine if needed from prior command
sudo reboot
```

### Setup

```bash
# install rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
# include cargo bin in PATH
source $HOME/.cargo/env
# test preinstalled python3
python3 --version
# install pip if needed
sudo apt install python3-pip
pip3 —-version
# check g++ version and install packages
g++ -v
sudo apt install build-essential
sudo apt-get install manpages-dev
sudo apt-get install libcurl4-openssl-dev libssl-dev uuid-dev zlib1g-dev libpulse-dev
# install latest cmake
wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | sudo tee /usr/share/keyrings/kitware-archive-keyring.gpg >/dev/null
echo 'deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ focal main' | sudo tee /etc/apt/sources.list.d/kitware.list >/dev/null
sudo apt-get install cmake
cmake --version
# install nlohmann_json
sudo apt-get install nlohmann-json3-dev
# install sqlite3
sudo apt-get install sqlite3 libsqlite3-dev
# install log4cplus
sudo apt-get install liblog4cplus-dev
# install google test
sudo apt-get install libgtest-dev
cd /usr/src/gtest
sudo cmake CMakeLists.txt
sudo make
# install redis
cd ~
sudo apt install redis-server
sudo systemctl status redis-server
# install python packages
python3 -m pip install -U git+https://github.com/Rapptz/discord.py
python3 -m pip install -U python-dotenv
python3 -m pip install -U python-daemon
python3 -m pip install -U yahooquery
python3 -m pip install -U asyncio
python3 -m pip install -U requests
# clone repo
git clone <Repo>
# switch branch if needed
# move all the relevant env files
```

### Compiling and Running

#### dbops

```bash
# starting from repo directory
cd dbops
cmake ./
make
chmod +x run.sh
# if needed
mkdir dat
cd dat
mkdir coins
```

#### rust api

```bash
# if needed
cargo install
# if needed, lookup pid for target build process and kill
sudo ps aux
sudo kill -9 <PID>
# enter api directory
cd api/
# clear logs if needed
: > api_logs.log
# compile release build
cargo build --release
# run build
nohup ./target/release/botzie > api_logs.log 2>&1 &
# or if dev
cargo run
```
