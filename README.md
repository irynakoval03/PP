# PP
## To install pyenv:
Powershell or Git Bash:
```bash
git clone https://github.com/pyenv-win/pyenv-win.git "$HOME/.pyenv"
```
or cmd.exe:
```bat
git clone https://github.com/pyenv-win/pyenv-win.git "%USERPROFILE%\.pyenv"
```

## Finish the installation:
1. Add **PYENV** and **PYENV_HOME** to your *Environment Variables*:  
  Using either PowerShell or Windows 8/above Terminal run:
  ```bat
  [System.Environment]::SetEnvironmentVariable('PYENV',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")  
  [System.Environment]::SetEnvironmentVariable('PYENV_HOME',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
  ```
2. Now add the following paths to your user **PATH** variable in order to access the pyenv command. Run the following in PowerShell or Windows 8/above Terminal:
  ```bat
  [System.Environment]::SetEnvironmentVariable('path', $env:USERPROFILE + "\.pyenv\pyenv-win\bin;" + $env:USERPROFILE + "\.pyenv\pyenv-win\shims;" + [System.Environment]::GetEnvironmentVariable('path', "User"),"User")
  ```
3. Close and reopen your terminal app and run
  ```bat
  pyenv --version
  ```
5. Now run the command from home directory
  ```bat
  pyenv rehash
  ```

## Create and activate virtual enviroment
 1.  Now run the command
  ```bat
  python -m venv ./env
  ```
 2. Run the command
  ```bat
  source ./env/Scripts/activate
  ```
 ## To add 'Flask' in dependencies of project:
 1. To install and upgrade pip(from home directory) run the command
   ```bat
   python -m pip install --upgrade pip
   ```
 2. To install flask(from home directory):
  ```bat
  pip install flask
  ```
  
## To  use a production WSGI server (use Waitress):
  1. https://stackoverflow.com/questions/54200746/cant-install-uwsgi-on-cygwin
  2. To install WSGI(Waitress) from cygwin terminal:
   ```bat
   pip install waitress
   ```
  4. To start web service:
   ```bat
   waitress-serve --call 'app:create_app'
   ```
