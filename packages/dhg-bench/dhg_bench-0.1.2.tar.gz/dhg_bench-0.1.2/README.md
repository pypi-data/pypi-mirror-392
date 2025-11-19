# DHG-Bench

DHG-Bench is a unified library for Deep Hypergraph Learning (DHGL), built on [PyTorch](https://pytorch.org/) and [PyTorch Geometric](https://www.pyg.org/)
. It integrates 17 state-of-the-art hypergraph neural network (HNN) algorithms and 22 hypergraph datasets with diverse characteristics.

## <span id="installation">📦 Installation</span>

Follow the steps below to install and configure **DHG-Bench** properly for your local environment.

### Required Dependencies:

**DHG-Bench** needs the following requirements to be satisfied beforehand:

* Python>=3.9.21
* Pytorch>=2.2.2
* torch_geometric>=2.6.1
* torch-cluster>=1.6.3
* torch-scatter>=2.1.2
* torch-sparse>=0.6.18
* torch-spline-conv>=1.2.2
* deeprobust==0.2.11
* ipdb==0.13.13
* numpy==1.24.3

### Installation with pip [Recommended]

```python
pip install dhg-bench
```
### Installation for local development

```python
# download the resporitary
cd dhgbench
# install required dependencies
```

### Download Datasets

We include benchmark datasets in the data.zip archive. Users can simply extract the archive with

```bash
unzip data.zip
```
to obtain the data directory. The project structure should look like the following:

```bash
DHG-Bench
  ├── data
  │   ├── fair_data
  │   ├── hete_data
  |   ├── hgcls_data
  │   ├── trad_data
  |   └── ...
  └── dhgbench
  │   ├── lib_dataset
  │   ├── lib_models
  |   ├── lib_utils
  │   ├── lib_yamls
  │   ├── parameter_parser.py
  └── └── ...
   ```

## <span id="quick-start">🚀 Quick Start</span>

The following demonstrates show how to quickly run **HGNN** algorithm on the **Cora** dataset for the **node classification task**.

#### Step 1: Import Package

```python
from dhgbench.parameter_parser import parameter_parser,method_config,set_task_args
from dhgbench.lib_utils.exp_agent import ExpAgent
from dhgbench.lib_models.HNN.preprocessing import algo_preprocessing
from dhgbench.lib_dataset.data_base import HyperDataset
from dhgbench.lib_dataset.preprocessing import data_processing
```

#### Step 2: Load and Set Up Configuration

```python
args = parameter_parser() 
args.dname, args.method, args.task_type, args.is_default = 'cora', 'HGNN', 'node_cls', False
args = method_config(args) 
args = set_task_args(args) 
```

Note that The **is_default** parameter indicates whether to use the model’s default configuration. If set to False, the model will instead load parameter settings specific to the given dataset. All model parameter files are provided in the lib_yamls directory.

#### Step 3: Load and Preprocess Dataset

```python
data=HyperDataset(args) 

if args.task_type == 'hg_cls':
    data = data.multi_hypergraphs 
else:
    data = data_processing(args,data)
    data._initialization_()
    data = algo_preprocessing(data,args)
```

#### Step 4: Training and Evaluation

```python
agent = ExpAgent(args)
agent.running(args.task_type,data)
```

## ⚙️ Configuration Argument Options

You can flexibly configure experiments with the following key parameters:

#### `task_type`

Specifies the type of task:

```
'node_cls', 'edge_pred', or 'hg_cls'
```

#### `dname`

Supported datasets include:

Node-level datasets:

```
'cora', 'pubmed', 'coauthor_cora','coauthor_dblp', 'ModelNet40', 'zoo', 'yelp', 'walmart-trips-100', 'trivago', 'actor','amazon', 'pokec', 'twitch', 'german', 'bail', 'credit'
```

Edge-level datasets:

```
'cora', 'pubmed', 'coauthor_cora', 'coauthor_dblp', 'actor', 'pokec'
```


Graph-level datasets:

```
'RHG_3', 'RHG_10', 'IMDB_dir_form', 'IMDB_dir_genre', 'stream_player', 'twitter_friend'
```

#### `method`

The algorithm to run. Supported algorithms include:

- **Spectral-based methods:**

  ```
  'HGNN','HyperGCN','HCHA','LEGCN','HyperND','HJRL','SheafHyperGNN','PhenomNN','DPHGNN','TFHNN'
  ```

- **Spatial-based methods:**

  ```
  'HNHN', 'UniGCNII', 'AllSetformer', 'EDHNN', 'HyperGT'
  ```

- **Tensor-based methods:**

  ```
  'EHNN', 'TMPHN'
  ```

You can also manually modify the configuration files located in lib_yamls directory for fine-grained control over hyperparameters.