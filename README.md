1. download python
<code>
https://www.python.org/downloads/release/python-3100/
https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe
</code>

2. install python
install python in the default location

3. download gitbash
<code>
https://git-scm.com/download/win
https://github.com/git-for-windows/git/releases/download/v2.40.0.windows.1/Git-2.40.0-64-bit.exe
</code>
install in default location

3. create directories and install venv
create the following directories
<code>
C:/ecomesense/venv
</code>
cd to ecomesense
<code>
python -m venv venv
</code>
4. activate the venv
<code>
cd venv<br>
. Scripts/activate
</code>
notice that the prompt is now changed
=IMPORTANT, go to next step 5 only if this happened=

5. install the requirements
from kite-order directory run<br>
<code>
pip install -r requirements.txt
</code>
4. install kite-order
<code>git clone https://github.com/pannet1/kite-order.git</code>

5. create confid directory
store the credentials in zerodha.yaml<br>
create another directory kite_order<br>
store MIS.yaml and NRML.yaml here

6. create shortcut for run_algo
cd the kite-order<br>
then create shortcut for run_algo

