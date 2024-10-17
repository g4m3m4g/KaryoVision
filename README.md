# KaryoVision

KaryoVision is an innovative web application designed to enhance genetic analysis by allowing users to upload images of chromosomes. Upon inputting a chromosome image, the application automatically identifies and counts the total number of chromosomes, providing a detailed report on the quantity of chromosomes present at each specific position. Leveraging advanced algorithms, KaryoVision goes beyond simple counting by predicting potential genetic disorders associated with the observed chromosomal patterns. This user-friendly tool aims to empower individuals and researchers alike, offering insights into genetic health and facilitating informed decision-making in genetic studies.
## Installation

Make sure you have ``git`` ``python`` ``pip`` installed

```bash
git clone https://github.com/g4m3m4g/KaryoVision.git
```
```bash
cd KaryoVision
```
```bash
pip install -r requirements.txt
```


## Usage

- Rename ``` template.env ``` to ``` .env ```
- Add your roboflow API_KEY 

### Run

```python
streamlit run app.py
```


[MIT](https://choosealicense.com/licenses/mit/)
