# Investment Dashboard Project Guide

## Development Commands

### Backend (Python/FastAPI)
```bash
# Setup environment
python -m venv env
source env/bin/activate  # Linux/Mac
.\env\Scripts\activate   # Windows

# Install dependencies
pip install -r backend/requirements.txt
pip install -r backend/tests/requirements-test.txt

# Run server
cd backend
uvicorn app:app --reload

# Run tests
pytest                   # All tests
pytest tests/test_client_queries.py  # Single test file
pytest -xvs tests/test_client_queries.py::test_function_name  # Single test
```

### Frontend (Next.js)
```bash
# Setup
cd frontend
npm install

# Development
npm run dev

# Linting
npm run lint

# Build
npm run build
```

# ABOUT THE PROJECT
- this project is NOT for major usage.. it is for a SMALL INDEPENDENT FIRM, with a max use of 5 non-concurrent users. 
- this app is for the investment management firm (Hohimer Wealth Management) to manage payments from their clients (companies) 401k plans that their clients offer to their employees. 
- there is NO need for ANY security or authentication. **THIS APP IS ENTIRELY OFFLINE**
- This app will be installed on each user's computer.
- Each user has the same access to the shared OneDrive on their system.
- the database is fully populated and READY FOR DIRECT QUERYING. 
- determine the dependencies on your own. suggest any libraries that you think would be VERYY helpful in making the app more consistent and the code more lightweight... don't suggest stuff just for the hell of it though if its going to add potential complexities. 


### SQLITE DIRECT QUERIES ONLY > NO SQLALCHEMY
(sqlalchemy is an overkill for a project like this. direct sql is sufficient) 

#  TIMELINE:
- The most important part of this app is the PAYMENT MANAGEMENT... That is why WE ARE BUILDING IT FIRST.
- After we finish the PAYMENT MANAGEMENT Page you will move on to the other pages. The other pages are identified via the frontend's sidebar.
- the reason i say all of this is because I dont want to reach a point in the future i dont want any surprises where I have to do massive changes to integrate the next phases of development. You should focus on the HERE AND NOW, but also prepare for the future. 

# ABOUT THE BLUEPRINT:
- never treat the guidelines as firm instructions. they are intended to be like a non-developer "client" explaining what they want to the experienced developer. 
- Always share BETTER ideas with the user... after understanding the general purpose, if you can think of a way to accomplish the task in a more consistent, safer way... WITH LESS CODE... and MORE MAINTAINABLE... then ALWAYYS SUGGEST THAT.
- always confirm with the user of any assumptions you are making about things that could make the app more CONSTRICTING... such as verifications. The blueprint carefully mapped out most verifications, however, some OBVIOUS one's are likely going to be needed too add. You decide... if its OBVIOUS then do it... if its very opinion based, then ask the user what they want. 

# ABOUT THE CODE
- Maintainability is important.
- aim for semi novice friendly file structure, but at the same time, as TRIM as possible. MORE CODE DOES NOT EQUAL BETTER.
- don't overcomplicate. don't be overzealous. call the shots when enough is enough. remember... this app is low stakes.
- always ensure there is NO conflicting logic. Always confirm with certainty that the code you are writing is absolutely nessesary and not duplication or unneeded fluff. 
- the number one rule is NO OVERSIGHTS. Measure first cut once... ask for clarification and preference if needed. 
- study 3x more context collateral files than you think you need to before beginning a task - you are NOTORIOUS for not gaining enough context.  
- YOU DECIDE THE FILE / FOLDER SYSYTEM

# RULE FOR CODE COMMENTS:
- minimal code comments. 
- do not state what the thing is unless its not obvious
- comments are NOT for the user to read - no human being will ever look at the code.
- the only entities looking at the code will be LLM AGENTS SUCH AS YOYURSELF. LLM AGENTS ALREADYY KNOW WHAT THE CODE DOES.
- Comments should not explain obvious code logic—only what an LLM would miss because it lacks full project context.
- LLM AGENTS SUCK AT CONTEXT – Code comments should be REMINDERS of important details outside the current file that help maintain accuracy and avoid oversights. These should include: Dependencies on other files, functions, or APIs, Assumptions about incoming data or external states, Workarounds for known issues or quirks in related code, Any hidden logic that isn’t obvious just from reading the function, Required order of execution or interactions with other modules. make your comments like a human jotting down things for their future self.. like "DONT FORGET TO..." 


## Code Style Guidelines
- **Python**: Use type annotations, minimal, and consistent error handling with specific exceptions
- **TypeScript**: Use strict mode with proper interfaces and type definitions
- **Imports**: Standard library first, third-party packages second, local modules last
- **Components**: Functional components with TypeScript interfaces using Shadcn/UI
- **Database**: Direct SQL queries in dedicated query files (no ORM)
- **API Pattern**: Layered architecture (routers → services → database)
- **Styling**: Tailwind CSS with consistent class naming
- **Error Handling**: Structured error responses with meaningful messages