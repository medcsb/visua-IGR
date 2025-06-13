# Running the project :
Each visualisation is its own Notebook to run it you simply run each block in the notebook making sure the necessary libraries are installed.
### libs needed :
- altair
- pandas
- geopandas

# visua 2 :
![alt text](media/visua2-sketch.png)
This was the sketch for visualization 2, we opted for a different approach where you can hover on different departments to see the largest used name in that department, the number of times it was used and the same for the least used name.

![alt text](media/visua2-version1.0.png)
This version is the one we decided on for this first delivrable.

To explore whether certain names are more popular in specific regions, this visualization aggregates the data across all years and displays, for each department, the most frequently used name along with its count. This approach provides an immediate overview of regional patterns by highlighting dominant names in each area. While it doesn’t capture changes over time, it effectively answers the question of whether certain names have a strong regional presence or if popular names are consistently widespread across the country. By focusing on the top name per department, the visualization makes regional contrasts easy to spot at a glance.
### strengths :
- Allows for quickly identifying the most popular name per department.

- Makes it easy to spot departments that have high number of top names.

### Weakneses :
- Doesn’t provide information about the distribution of other names within each department (e.g., how dominant the top name is compared to the others).

- Lacks temporal context — there’s no way to explore how name usage changes over time, as the visualization only shows a static snapshot.

