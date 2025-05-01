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
    - Check using command line terminal: git version
3. Download openBB: https://docs.openbb.co/platform/installation
    - Register for an account and sign in.
    - Mac/Windows: https://my.openbb.co/app/platform/downloads
4. Make environment: write the following in a command line terminal...
    ```shell
    cd ~
    conda create --name ind python=3.12.2
    # When conda asks you to proceed, type "y"
    
    conda activate ind
    mkdir git
    cd git
    ```
5. Download dependencies: write the following in a command line terminal...
    ```shell
    conda install pip
    
    pip install -U scikit-learn # Also, installs numpy, pandas, matplotlib, seaborn, scipy.
    
    conda install -c conda-forge statsmodels
    conda install anaconda::requests
    conda install conda-forge::adjusttext
    conda install -c conda-forge git
    ```
6. Install ind: write the following in a command line terminal...
    ```shell
    git clone https://github.com/marczepeda/ind.git
    cd ind
    pip install -e .
    # Include the "."
    
    conda deactivate
    ```
### Update
1. Enter environment & delete ind: write the following in a command line terminal...
    ```shell
    cd ~
    cd git
    conda activate ind
    pip uninstall ind
    # Enter 'Y' when prompted
    
    rm -r ind
    # Enter 'Y' three times to completely remove the folder
    ```
2. Install ind: write the following in a command line terminal...
    ```shell
    git clone https://github.com/marczepeda/ind.git
    cd ind
    pip install -e .
    # Include the "."

    conda deactivate
    ```