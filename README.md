# Visualization | Group 36
## 💡 About
This is the project of group 36 for the couse JBI100, Visualization. Based on a dataset provided by the course, the goal is to create an interactive visualization tool based on what's disucssed in the course.
## 🧑🏽‍💻 Project Setup
Please note that the data used inside this dashboard hasn't been included in this repository. The user is expected to place the raw data files in the correct directories before running this tool. The following lines will provide the correct structure of this placement:


Create the directory `data` within `src/`. Download [player data](https://www.kaggle.com/datasets/swaptr/fifa-world-cup-2022-player-data) and extract the content of the archive there.
After doing so, a collection of `.csv` and a single `.json` file should be placed within `src/data` (relative to the root of the repository).



The dashboard makes use of different player images. We use [Fifa 2022 Player Image Dataset](https://www.kaggle.com/datasets/soumendraprasad/fifa-2022-all-players-image-dataset) for this purpose.
To make the image files available for the app, create the directory `player_images` in `src/assets` .
Download the dataset archive and extract the contents. After extraction the contents of `Images/Images` (relative to the root of the ZIP archive) must be placed in src/app/assets/player_images.
After correct placement of both archive the directory structure of your project should like the following:

````
  ⫶
- notebooks/
- src/
      ⫶
    - assets/
        - player_images/
            - Group A/
            - Group B/
            - Group C/
              ⫶
        - icons/
          ⫶
    |-- app.py
      ⫶
  ⫶

````


## 📝 References
The player data used across the project is sourced from [FIFA World Cup 2022 Player Data](https://www.kaggle.com/datasets/swaptr/fifa-world-cup-2022-player-data) available on Kaggle licensed under [ODbL](https://opendatacommons.org/licenses/odbl/1-0/).