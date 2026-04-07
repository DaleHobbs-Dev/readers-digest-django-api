# Bash Scripts for Web Development

Bash scripts are a powerful tool for automating repetitive tasks in web development. They allow you to codify sequences of terminal commands so that they can be executed reliably and consistently with a single command, rather than manually typing them each time. This is especially useful in development workflows where you frequently need to reset databases, run migrations, or seed data.

## What is a Bash Script and Why Are They Useful?

A bash script is a plain text file containing a sequence of terminal commands that are executed automatically, in order, when the script is run. Instead of typing the same 5–10 commands manually every time you need to perform a repetitive task, you write them once in a `.sh` file and run the whole thing with a single command.

In your Readers Digest project, the `seed_database.sh` script automates the process of wiping your SQLite database, removing old migrations, regenerating them fresh, and reloading all your fixture data. Without this script, you would need to type each of those commands individually every time you wanted a clean slate — which during active development can be dozens of times a day. The script saves time, reduces human error (forgetting a step or running them out of order), and makes it easy for any teammate to reset the database the same way you do.

---

## How to Create an Executable Bash Script

### Step 1 — Create the file

Create a new file with the `.sh` extension in your project directory:

```bash
touch seed_database.sh
```

### Step 2 — Add the shebang line

Open the file and add this as the very first line. It tells the OS to use Bash to interpret the script:

```bash
#!/bin/bash
```

### Step 3 — Write your commands

Add the commands you want to automate, one per line. You can add comments with `#` to explain what each section does:

```bash
#!/bin/bash

# Reset the database by removing the existing SQLite file
rm db.sqlite3

# Remove old migrations so they get regenerated fresh
rm -rf ./digestapi/migrations

# Run initial Django migrations for built-in tables (auth, admin, etc.)
python3 manage.py migrate

# Generate new migrations based on your current models
python3 manage.py makemigrations digestapi

# Apply those new migrations to the database
python3 manage.py migrate digestapi

# Load seed data fixtures in order
python3 manage.py loaddata users
python3 manage.py loaddata tokens
python3 manage.py loaddata books
python3 manage.py loaddata categories
```

### Step 4 — Make the file executable

By default, your OS won't allow the file to be run as a program. This command grants your user permission to execute it:

```bash
chmod u+x ./seed_database.sh
```

### Step 5 — Run it

```bash
./seed_database.sh
```

That's it — every command in the file runs automatically in sequence.

---

## Common Uses for Bash Scripts in Web Development

Bash scripts are used throughout both frontend and backend development anywhere a sequence of commands needs to be repeated reliably. Here are the most common places you'll encounter them:

### Backend — Database Seeding and Resets

Exactly like your project. During development, you frequently need to wipe a database and reload known test data. A script that drops tables, reruns migrations, and loads fixtures lets every developer on a team start from the same state with one command.

### Backend — Project Setup / Onboarding

A `setup.sh` or `install.sh` script that a new developer runs after cloning a repo. It might install dependencies, create a virtual environment, copy a `.env.example` file, run initial migrations, and seed the database — everything needed to go from a fresh clone to a running app without reading a long README.

### Backend — Environment Variable Configuration

Scripts that export environment variables or copy `.env` files into the right place before starting a server, ensuring the app always launches with the correct configuration for development vs. production.

### Frontend — Build and Deploy Pipelines

Scripts that run a sequence of build steps: compiling TypeScript, bundling assets, running tests, and then copying the output to a deployment directory or pushing to a hosting service. Tools like Vercel and Netlify use bash scripts under the hood for this.

### Frontend — Development Server Startup

A script that starts multiple processes at once — for example, starting a React frontend dev server and a separate backend API server in parallel, so a developer only needs to run one command to get the entire full-stack app running locally.

### General — Running Test Suites

A script that sets up a test database, runs your full test suite, and then tears the test database back down — keeping test runs isolated and repeatable across any machine.

### General — Scheduled Tasks (Cron Jobs)

Bash scripts are commonly paired with cron (a Unix job scheduler) to run automated tasks on a timer — for example, backing up a database every night, clearing a cache every hour, or sending a daily report email.

### General — CI/CD Pipelines

Continuous Integration and Continuous Deployment (CI/CD) pipelines automate the process of testing, building, and deploying code whenever changes are pushed to a repository. Bash scripts are often used to define the exact sequence of steps that should happen in these pipelines. By putting the steps into a script, you ensure that the same sequence of commands runs every time the pipeline executes, whether that's installing dependencies, running tests, building the project, or deploying it to a server. This makes the pipeline predictable and repeatable, reducing the chance of errors caused by manual execution of commands or differences between developer environments. By putting the steps into a bash script, you can run the exact same sequence locally to verify that the pipeline will behave as expected before it ever runs in the automated CI/CD environment. This local testing helps catch issues early and ensures that what works on a developer's machine will also work when the pipeline runs in the cloud. In tools like GitHub Actions, CircleCI, or Jenkins, the actual steps that run on every push to a repository (install dependencies, run linter, run tests, build, deploy) are often bash scripts. They ensure the same process runs consistently in an automated cloud environment as it does on a developer's local machine. By encapsulating these steps in a script, you reduce the chance of human error and make the CI/CD pipeline easier to maintain, since the same script can be run locally for testing or debugging before it ever runs in the cloud.
