# PP
#To install pyenv:
Powershell or Git Bash: git clone https://github.com/pyenv-win/pyenv-win.git "$HOME/.pyenv"
Or cmd.exe: git clone https://github.com/pyenv-win/pyenv-win.git "%USERPROFILE%\.pyenv"
##Finish the installation:
1. Add PYENV and PYENV_HOME to your Environment Variables:
Using either PowerShell or Windows 8/above Terminal run:
  [System.Environment]::SetEnvironmentVariable('PYENV',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
  [System.Environment]::SetEnvironmentVariable('PYENV_HOME',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
2. Now add the following paths to your USER PATH variable in order to access the pyenv command. Run the following in PowerShell or Windows 8/above Terminal:
  [System.Environment]::SetEnvironmentVariable('path', $env:USERPROFILE + "\.pyenv\pyenv-win\bin;" + $env:USERPROFILE + "\.pyenv\pyenv-win\shims;" +    [System.Environment]::GetEnvironmentVariable('path', "User"),"User")
3. Close and reopen your terminal app and run pyenv --version
4. Now run the pyenv rehash from home directory
5. Run pyenv to see list of commands it supports.

##Create and activate virtual enviroment
 1.python -m venv ./env
 2.source ./env/bin/activate
 To add 'Flask' in dependencies of project:
 1.To install and upgrade pip(from home directory):
  python -m pip install --upgrade pip
 2.To install flask(from home directory):
  pip install flask
 
C:\Users\iryna\OneDrive\PROJECTS\PP>pyenv global 3.7.9
  (from project file)python -m venv ./env
C:\Users\iryna\OneDrive\PROJECTS\PP\env\Scripts>activate
(env) C:\Users\iryna\OneDrive\PROJECTS\PP\env\Scripts>

https://stackoverflow.com/questions/54200746/cant-install-uwsgi-on-cygwin
To  use a production WSGI server (use Waitress):
  1.https://stackoverflow.com/questions/54200746/cant-install-uwsgi-on-cygwin
  2.pip install waitress
  3.waitress-serve --call 'app:create_app'
