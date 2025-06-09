Hands-On Coding and Integration (2–4 Hours,
Python)
Goal
Build a small Python application that consumes a public API—in this case, the
Rick and Morty API - processes or transforms the data, and outputs specific
fields in a CSV file.
Project Description
1. Use the Rick and Morty API
Base URL: https://rickandmortyapi.com
Endpoints of interest:
/character (for Rick and Morty characters)
/location (for places in the show)
/episode (for episode data)
2. Fetch characters from the /character endpoint.
Each character object includes fields like id , name , status , species , type ,
gender , origin , location , and episode references.
3. Fetch character locations details from the /location endpoint.
Each location object includes fields like id , name , type , dimension
4. Extract specific fields for each character and write them to a CSV:
id
name
Customer Engineer Exercise 1
status (Alive, Dead, or unknown)
species
origin.name (the name of their origin location)
location id
5. Extract specific fields for each location and write them to a CSV:
id
name
type
dimension
6. Provide a way to get all info about a character (including the location details).
7. Handle errors gracefully and document any assumptions or limitations (e.g., if
you only fetch the first page of characters or handle pagination to gather all
pages).
Requirements
Language: Python.
Data Output:
CSV files containing the fields listed above.
Each row should represent one character / location from the Rick and
Morty API.
Instructions/Documentation:
Include a README.md that explains:
1. How to install dependencies (requirements.txt or specific pip commands).
2. How to run your Python script (e.g., python main.py ).
3. Any additional configuration (if needed).
Optional (but encouraged):
Customer Engineer Exercise 2
Pagination: The Rick and Morty API results are paginated. Show how you
handle subsequent pages to retrieve all characters.
Tests: Include at least one test (unit test or functional test) that checks
core functionality.
What We’re Looking For
Code Quality: Readability, organization, and maintainability in Python.
Error Handling: Dealing gracefully with network or data-related errors (e.g.,
invalid response structures).
Documentation: Clear instructions on how to run, test, and extend the code.
Correctness & Completeness: Ensure that the output CSV has the specified
fields and that the program runs as documented.