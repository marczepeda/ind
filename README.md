# Investigational New Drug (IND) Application
## Package Organization
- gen: input/output, data wrangling, generating plots, and statistics.
    ```shell
    import ind.gen.io as io
    import ind.gen.tidy as t
    import ind.gen.plot as p
    import ind.gen.stat as st
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
    conda deactivate
    ```
7. (Optional) Download openBB: https://docs.openbb.co/platform/installation
    - Register for an account and sign in.
    - Mac/Windows: https://my.openbb.co/app/platform/downloads
### Update
1. Enter environment & delete ind:
    ```shell
    cd ~
    cd git
    conda activate ind
    pip uninstall ind # Enter 'Y' when prompted
    rm -rf ind
    ```
2. Clone ind from github and install ind:
    ```shell
    git clone https://github.com/marczepeda/ind.git
    cd ind
    pip install -e . # Include the "."
    conda deactivate
    ```