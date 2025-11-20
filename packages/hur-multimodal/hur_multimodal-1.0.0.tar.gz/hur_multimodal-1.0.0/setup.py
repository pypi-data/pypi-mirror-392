"""
The “Hur-MultiModal” is a multimodal architecture for large language models (LLMs/LMMs) that can be trained on modest hardware without GPU need.
When a GPU is connected to the “Hur-MultiModal” architecture, it will significantly boost the network's performance,
but this is not mandatory since the architecture itself was built with specific functions for training and tuning directly on the CPU.
The architecture also features support for infinite context window, which makes it possible to maintain conversations without any token limit.
The network's performance increase occurs thanks to the possibility of training the model without using backpropagation.
Since the architecture has training resources for direct calculations in a single step with semantic comparison and weights adjustment by division with HurNet networks,
this makes it significantly lighter and faster than traditional multimodal network architectures.
This is 100% original code developed by Sapiens Technology® to add multimodality support to neural networks of the HurModel architecture.
Any modification, sharing, or public comment on the technical specifications of this architecture is strictly prohibited,
and the author will be subject to legal action initiated by our legal team.
"""
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
from setuptools import setup, find_packages
package_name = 'hur_multimodal'
version = '1.0.0'
setup(
    name=package_name,
    version=version,
    author='SAPIENS TECHNOLOGY',
    packages=find_packages(),
    install_requires=[
        'hurnet-torch==1.1.0',
        'sapiens-tokenizer==1.1.7',
        'sapiens-embedding==1.1.1',
        'sapiens-attention==1.0.7',
        'sapiens-infinite-context-window==1.0.5',
        'sapiens-generalization==1.0.1',
        'scn==1.0.9',
        'torch==2.4.1',
        'requests==2.31.0',
        'ijson==3.3.0',
        'tqdm==4.67.1',
        'pillow==10.3.0',
        'INFINITE-CONTEXT-WINDOW==3.0.2'
    ],
    url='https://github.com/sapiens-technology/HurMultiModal',
    license='Proprietary Software'
)
"""
The “Hur-MultiModal” is a multimodal architecture for large language models (LLMs/LMMs) that can be trained on modest hardware without GPU need.
When a GPU is connected to the “Hur-MultiModal” architecture, it will significantly boost the network's performance,
but this is not mandatory since the architecture itself was built with specific functions for training and tuning directly on the CPU.
The architecture also features support for infinite context window, which makes it possible to maintain conversations without any token limit.
The network's performance increase occurs thanks to the possibility of training the model without using backpropagation.
Since the architecture has training resources for direct calculations in a single step with semantic comparison and weights adjustment by division with HurNet networks,
this makes it significantly lighter and faster than traditional multimodal network architectures.
This is 100% original code developed by Sapiens Technology® to add multimodality support to neural networks of the HurModel architecture.
Any modification, sharing, or public comment on the technical specifications of this architecture is strictly prohibited,
and the author will be subject to legal action initiated by our legal team.
"""
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
