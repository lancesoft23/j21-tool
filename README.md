# j21-tool
An experimental python script to convert Java 11 and 21 back and forth.

## Install
### install locally from sources

```
git clone https://github.com/lancesoft23/j21-tool.git
cd j21-tool
python setup.py install
```

## Usage
Upgrade to Java 21
``` 
python -m j21tool --java21 -o <output_dir> <project_dir>
```

Downgrade to Java 11
``` 
python -m j21tool --java11 -o <output_dir> <project_dir>
```

 * <i>project_dir</i> the base directory of a Java project.

## Changes
- Sep 2023, Initial project, Lance Liang
