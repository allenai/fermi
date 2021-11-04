# Fermi Problems: A New Reasoning Challenge for AI

This repository provides the following two datasets:
- RealFP @ `./data/realFP`. A collection of 928 fermi problems and their solutions expressed in the form a program.
- SynthFP @ `.data/synthFP`. An auxilliary set of 10000 templated fermi questions, created by the authors.

Code for compiling the program in the dataset and computing the accuracy metric is provided in `eval_utils.py`. For more details on the datasets, please refer to our paper: [How Much Coffee Was Consumed During EMNLP 2019? Fermi Problems: A New Reasoning Challenge for AI](https://arxiv.org/abs/2110.14207).

## Inference

You can download a model finetuned on the `realFP` dataset [here](https://drive.google.com/file/d/1C_JnoHotqT12yheNZCKg1IirHUCHp1ve/view?usp=sharing). Answers to your fermi questions can be obtained by executing the following command: `python inference --question your_question_here`. Make sure to check `requirements.txt` for any dependencies.

If you use the datasets or any other content shared in this repository, please cite our work: 
```
@article{kalyan2021much,
  title={How Much Coffee Was Consumed During EMNLP 2019? Fermi Problems: A New Reasoning Challenge for AI},
  author={Kalyan, Ashwin and Kumar, Abhinav and Chandrasekaran, Arjun and Sabharwal, Ashish and Clark, Peter},
  journal={arXiv preprint arXiv:2110.14207},
  year={2021}
}
```
