# random-road-network-generation
This repo (mainly implemented in Python) is to generate random road network in city scenarios using procedural modeling. 

> The main idea came from Parish and Muller's [Procedural Modeling of Cities](https://cgl.ethz.ch/Downloads/Publications/Papers/2001/p_Par01.pdf), where they developed the L-systems as procedural modeling, and global goals and local constraints were utilized to control the parameters (only introduce some basic princples here).

In this repo we implement the generic procedural modeling in Python, and supplement it with the Monte-Carlo simulation method in city morphogenesis. The roads generated include two-level main roads and three-level road network in total. 

The generation result is formatted in OSM files, which is easy to visualize and put into various projects. 
Some basic parameters are placed in `src/Constants.py`, simple tuning on the parameters can impose obvious shift on the generation result. 

Also, the repo provides some methods to debug the generating process, including visualizations. Hope it can help during your play.

# Usage

### Deploy
- **python 3.9**
- matplotlib==3.3.3
- noise==1.2.2
- numpy==1.16.2
- Pyqtree==1.0.0

Install the dependencies (if necessary) before using
```bash
pip install -r requirements.txt
```


### Run
You can easily run the process with `run.sh`
```bash
# ./run.sh
Namespace(debug=False, road_num=2000, generate=True, osm_filename='test.osm', plt_filename='test.png')

Start generating city...
 2000 / 2000
Done generate, segment num=2000, road num=799

Writing OSM file...
Written to ../runtime/out/test.osm

Drawing...
Saved to ../runtime/out/test.png
All done
```

### Pro
For those who are interested in developing or debugging the project, some pro instructions are provided.

`run.sh` is a well-sealed runtime shell, which will create basic running environment and run `python src/test.py`.
The detail parameters of test.py are listed below:


```bash
# python src/test.py --help
usage: test.py [-h] [--debug DEBUG] [--road_num ROAD_NUM]
               [--generate GENERATE] [--osm_filename OSM_FILENAME]
               [--plt_filename PLT_FILENAME]

A random road generator

optional arguments:
  -h, --help            show this help message and exit
  --debug DEBUG         Is using debug mode
  --road_num ROAD_NUM   Road number to generate
  --generate GENERATE   Should generate road OSM file
  --osm_filename OSM_FILENAME
                        Output OSM file name
  --plt_filename PLT_FILENAME
                        Output OSM file name
```

In `./runtime`, there are log files and output files. The output files include OSM file (i.e. the generation result) and some debug pics which reveals how the road are organized geologically.

```bash
runtime
├── log
│   ├── road-gen-DEBUG.log
│   └── road-gen-INFO.log
└── out
    ├── test.osm
    └── test.png
```

The core logic of procedural modeling is placed in `src/City.py`, which includes the implementation of local constrains and global goals. Generation parameters are placed in `src/Constants.py`. Logic with OSM are in `src/external/OSMGenerator.py`, and abstract road structure are in `src/external/BaseTypes.py`

Hope this instruction will help in your development!
