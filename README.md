1. download python
https://www.python.org/downloads/release/python-3100/
https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe

2. install python
install python in the default location

2. download gitbash
https://git-scm.com/download/win
https://github.com/git-for-windows/git/releases/download/v2.40.0.windows.1/Git-2.40.0-64-bit.exe
install in default location

3. create directories and install venv
create the following directories
C:/ecomesense/venv

cd to ecomesense
python -m venv venv

4. activate the venv
cd venv
. Scripts/activate
notice that the prompt is now changed
IMPORTANT, go to next step 5 only if this happened

5. install the requirements
from kite-order directory run
pip install -r requirements.txt

4. install kite-order
git clone https://github.com/pannet1/kite-order.git


5. create confid directory
store the credentials in zerodha.yaml
create another directory kite_order
store MIS.yaml and NRML.yaml here

6. create shortcut for run_algo
cd the kite-order
then create shortcut for run_algo


