1. download python
<pre>
https://www.python.org/downloads/release/python-3100/
https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe
</pre>

2. install python
install python in the default location

3. download gitbash
<pre>
https://git-scm.com/download/win
https://github.com/git-for-windows/git/releases/download/v2.40.0.windows.1/Git-2.40.0-64-bit.exe
</pre>
install in default location

4. create directories and install venv
create the following directories
<pre>
C:/ecomsense/venv
</pre>
cd to ecomesense
<pre>
python -m venv venv
</pre>
5. activate the venv
<pre>
cd venv</br>
. Scripts/activate
</pre>
notice that the prompt is now changed to (venv)
== IMPORTANT, go to next step 5 only if this happened ==

6. install the requirements
from kite-order directory run</br>
<pre>
pip install -r requirements.txt
</pre>
7. install kite-order
<pre>git clone https://github.com/pannet1/kite-order.git</pre>

8. create confid directory
cd c:\ecomsense\venv\confid 
store the credentials in zerodha.yaml</br>
create another directory kite_order</br>
store MIS.yaml and NRML.yaml here

9. create shortcut for run_algo
cd the kite-order</br>
then create shortcut for run_algo


