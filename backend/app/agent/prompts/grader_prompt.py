grader_prompt = """
You are a grader assessing relevance of a retrieved document to a user query.
Here is the retrieved document: \n\n {context} \n\n
Here is the user query: {query} \n
If the document contains keyword(s) or semantic meaning related to the user query, grade it as relevant.
Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the query.
"""
