# market-analysis
This script demonstrates how to use a combination of LLM API calls and websearch to perform an online market research. 

The script works as follows:
- We ask the LLM to provide a list of submarkets for a given market e.g. we ask for all submarkets of the tourism market.
- The LLM provides a list of submarkets like leisure tourism, sports tourism, medical tourism an educational tourism.
- Define a set of KPI (key performance indicators) like average duration of stay, money spent, country of origin.
- For each combination of submarket and KPI generate perform a websearch e.g. "Average duration of stay in educational tourism in 2024".
- For the Top n websites obtained by the websearch we obtain the text content of the website.
- For each of these texts query the LLM again with the promot "Given the following document answer the following question. Document: <website text>. Question: What is the average duration of stay in educational tourism in 2024?"
- The reponses obtained are our KPI.

The are some aspects missing in the script, e.g. error handling. However, you may use it as a staring point for your own project. The core idea is that we combine websearch (in this case via the bing API) with the abilities of LLMs to provide good answers.

A video describing the process on a conceptual level is provided here: ki-seminare.de [Video in German]
