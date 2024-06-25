Tạo môi trường ảo và cài đặt các gói cần thiết:
sudo apt update
sudo apt install git python3.12-venv
git clone https://github.com/vanbay01nd/Scan-BTC-TLG.git
cd Scan-BTC-TLG
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
