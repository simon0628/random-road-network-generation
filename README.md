# random-road-network-generation
This repo (mainly implemented in Python) is to generate random road network in city scenarios using procedural modeling. 

> The main idea came from Parish and Muller's [Procedural Modeling of Cities](https://cgl.ethz.ch/Downloads/Publications/Papers/2001/p_Par01.pdf), where they developed the L-systems as procedural modeling, and global goals and local constraints were utilized to control the parameters (only introduce some basic princples here).

In this repo we implement the generic procedural modeling in Python, and supplement it with the Monte-Carlo simulation method in city morphogenesis. The roads generated include two-level main roads and three-level road network in total. 

The generation result is formatted in OSM files, which is easy to visualize and put into various projects. 
Some basic parameters are placed in `src/Constants.py`, simple tuning on the parameters can impose obvious shift on the generation result. 

Also, the repo provides some methods to debug the generating process, including visualizations. Hope it can help during your play.

# Usage
```bash
pip install -r requirements.txt
./run.sh
```
### Environment
- python 3.7
- Unix based OS
