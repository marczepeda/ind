# Investigational New Drug (IND) Application
Like DrugBank, but free. Only accessible through CLI for now...
## Command Line Interface
```shell
ind -h # or ind <TAB>
```
## Instructions
### Install
1. Download Anaconda.
    - Mac: https://docs.anaconda.com/anaconda/install/mac-os/
    - Windows: https://docs.anaconda.com/anaconda/install/windows/
    - Linux: https://docs.anaconda.com/anaconda/install/linux/
2. Download Git: https://github.com/git-guides/install-git
3. Clone ind from github:
    ```shell
    cd ~
    mkdir git
    cd git
    git clone https://github.com/marczepeda/ind.git
    cd ind 
    ```
4. Make the environment and install ind:
    ```shell
    conda env create -f ind.yml # When conda asks you to proceed, type "y"
    conda activate ind
    pip install -e . # Include the "."
    ind autocomplete # Optional: set up ind autocomplete; follow CLI instructions
    conda deactivate
    ```
5. (Optional) Download openBB: https://docs.openbb.co/platform/installation
    - Register for an account and sign in.
    - Mac/Windows: https://my.openbb.co/app/platform/downloads

### Update
1. Enter environment & delete ind:
    ```shell
    cd ~/git/ind
    conda activate ind
    pip uninstall -y ind
    rm -rf build/ dist/ *.egg-info
    ```
2. Pull latest version from github and install edms:
    ```shell
    git pull origin main
    pip install -e . # Include the "."
    conda deactivate
    ```